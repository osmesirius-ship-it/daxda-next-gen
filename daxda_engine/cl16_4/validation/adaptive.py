"""
Adaptive Constraint Manager for Cl(16,4)
========================================

Dynamically adjusts validation strictness based on runtime conditions
and threat levels.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import time
import json
import hashlib
from enum import Enum

from ..combinatorics.cl_space import ClSpace, ClConfig
from ..combinatorics.constraints import ConstraintSystem, Constraint


class ThreatLevel(Enum):
    """Validation threat levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ConstraintProfile:
    """A profile defining constraint settings for a specific threat level."""
    name: str
    threat_level: ThreatLevel
    constraints: Dict[str, Dict[str, Any]]  # constraint_name -> settings
    description: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "threat_level": self.threat_level.value,
            "constraints": self.constraints,
            "description": self.description
        }


@dataclass
class AdaptiveConfig:
    """Configuration for adaptive constraint management."""
    current_profile: str = "default"
    profiles: Dict[str, ConstraintProfile] = field(default_factory=dict)
    auto_adjust: bool = True
    adjustment_interval: float = 60.0  # seconds
    metrics_window: int = 100  # number of recent validations to consider


class AdaptiveConstraintManager:
    """
    Manages dynamic adjustment of constraints based on runtime conditions.
    
    Provides:
    - Threat-level-based constraint profiles
    - Automatic adjustment based on validation metrics
    - Runtime constraint modification
    - Audit logging of constraint changes
    """
    
    def __init__(self, space: Optional[ClSpace] = None,
                 constraint_system: Optional[ConstraintSystem] = None):
        self.space = space or ClSpace(n=16, k=4)
        self.constraint_system = constraint_system or ConstraintSystem(space=self.space)
        self.config = AdaptiveConfig()
        self._metrics: List[Dict] = []
        self._history: List[Dict] = []
        self._last_adjustment = time.time()
        
        self._initialize_profiles()
    
    def _initialize_profiles(self) -> None:
        """Initialize default constraint profiles."""
        
        # Low threat profile - minimal constraints
        self.config.profiles["low"] = ConstraintProfile(
            name="low",
            threat_level=ThreatLevel.LOW,
            constraints={
                "unique_dimensions": {"enabled": True, "severity": "hard"},
                "sorted_order": {"enabled": False},
                "min_spread": {"enabled": False}
            },
            description="Minimal constraints for low-risk scenarios"
        )
        
        # Medium threat profile - balanced constraints
        self.config.profiles["medium"] = ConstraintProfile(
            name="medium",
            threat_level=ThreatLevel.MEDIUM,
            constraints={
                "unique_dimensions": {"enabled": True, "severity": "hard"},
                "sorted_order": {"enabled": True, "severity": "soft"},
                "min_spread": {"enabled": True, "severity": "soft"}
            },
            description="Balanced constraints for normal operations"
        )
        
        # High threat profile - strict constraints
        self.config.profiles["high"] = ConstraintProfile(
            name="high",
            threat_level=ThreatLevel.HIGH,
            constraints={
                "unique_dimensions": {"enabled": True, "severity": "hard"},
                "sorted_order": {"enabled": True, "severity": "hard"},
                "min_spread": {"enabled": True, "severity": "hard"}
            },
            description="Strict constraints for high-risk scenarios"
        )
        
        # Critical threat profile - maximum constraints
        self.config.profiles["critical"] = ConstraintProfile(
            name="critical",
            threat_level=ThreatLevel.CRITICAL,
            constraints={
                "unique_dimensions": {"enabled": True, "severity": "hard"},
                "sorted_order": {"enabled": True, "severity": "hard"},
                "min_spread": {"enabled": True, "severity": "hard"}
            },
            description="Maximum constraints for critical scenarios"
        )
        
        self.config.current_profile = "medium"
    
    def set_profile(self, profile_name: str) -> bool:
        """Set the current constraint profile."""
        if profile_name not in self.config.profiles:
            return False
        
        old_profile = self.config.current_profile
        self.config.current_profile = profile_name
        self._log_change("profile_change", old_profile, profile_name)
        self._apply_profile(profile_name)
        return True
    
    def _apply_profile(self, profile_name: str) -> None:
        """Apply the specified constraint profile."""
        profile = self.config.profiles[profile_name]
        
        for constraint_name, settings in profile.constraints.items():
            if constraint_name in self.constraint_system.constraints:
                # Update existing constraint
                if not settings.get("enabled", True):
                    self.constraint_system.remove_constraint(constraint_name)
            else:
                # Add new constraint if enabled
                if settings.get("enabled", True):
                    # This would need to be implemented based on constraint type
                    pass
    
    def set_threat_level(self, level: ThreatLevel) -> bool:
        """Set threat level and activate corresponding profile."""
        for name, profile in self.config.profiles.items():
            if profile.threat_level == level:
                return self.set_profile(name)
        return False
    
    def get_current_profile(self) -> Optional[ConstraintProfile]:
        """Get the current active profile."""
        return self.config.profiles.get(self.config.current_profile)
    
    def get_threat_level(self) -> ThreatLevel:
        """Get current threat level."""
        profile = self.get_current_profile()
        if profile:
            return profile.threat_level
        return ThreatLevel.MEDIUM
    
    def record_metric(self, metric: Dict) -> None:
        """Record a validation metric for analysis."""
        self._metrics.append(metric)
        
        # Trim old metrics
        if len(self._metrics) > self.config.metrics_window:
            self._metrics = self._metrics[-self.config.metrics_window:]
        
        # Auto-adjust if enabled
        if self.config.auto_adjust:
            self._check_auto_adjustment()
    
    def _check_auto_adjustment(self) -> None:
        """Check if constraints should be auto-adjusted."""
        now = time.time()
        if now - self._last_adjustment < self.config.adjustment_interval:
            return
        
        # Calculate metrics
        if self._metrics:
            failure_rate = sum(1 for m in self._metrics if not m.get("is_valid", True)) / len(self._metrics)
            
            # Adjust based on failure rate
            if failure_rate > 0.3:  # High failure rate
                self.set_threat_level(ThreatLevel.HIGH)
            elif failure_rate > 0.1:  # Medium failure rate
                self.set_threat_level(ThreatLevel.MEDIUM)
            elif failure_rate < 0.01:  # Very low failure rate
                self.set_threat_level(ThreatLevel.LOW)
            else:
                self.set_threat_level(ThreatLevel.MEDIUM)
        
        self._last_adjustment = now
    
    def add_dynamic_constraint(self, name: str, condition: Dict, 
                              severity: str = "hard") -> None:
        """Add a dynamic constraint that can be enabled/disabled by profile."""
        self.constraint_system.register_constraint(
            name=name,
            description=f"Dynamic constraint: {condition}",
            check_func=self._create_check_func(condition),
            severity=severity
        )
        
        # Add to all profiles as enabled by default
        for profile in self.config.profiles.values():
            profile.constraints[name] = {"enabled": True, "severity": severity}
    
    def _create_check_func(self, condition: Dict):
        """Create a check function from a condition dictionary."""
        def check_func(config: ClConfig) -> bool:
            for key, value in condition.items():
                if key == "min_sum":
                    if sum(config.indices) < value:
                        return False
                elif key == "max_sum":
                    if sum(config.indices) > value:
                        return False
                elif key == "contains":
                    if not any(i in config.indices for i in value):
                        return False
                elif key == "excludes":
                    if any(i in config.indices for i in value):
                        return False
            return True
        return check_func
    
    def enable_constraint(self, name: str) -> bool:
        """Enable a constraint in all profiles."""
        for profile in self.config.profiles.values():
            if name in profile.constraints:
                profile.constraints[name]["enabled"] = True
        return True
    
    def disable_constraint(self, name: str) -> bool:
        """Disable a constraint in all profiles."""
        for profile in self.config.profiles.values():
            if name in profile.constraints:
                profile.constraints[name]["enabled"] = False
        return True
    
    def _log_change(self, change_type: str, old_value: Any, new_value: Any) -> None:
        """Log a constraint change for audit purposes."""
        log_entry = {
            "timestamp": time.time(),
            "change_type": change_type,
            "old_value": str(old_value),
            "new_value": str(new_value),
            "hash": hashlib.sha256(f"{change_type}{old_value}{new_value}".encode()).hexdigest()[:16]
        }
        self._history.append(log_entry)
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Get recent change history."""
        return self._history[-limit:]
    
    def get_audit_report(self) -> Dict:
        """Generate a comprehensive audit report."""
        return {
            "current_profile": self.config.current_profile,
            "current_threat_level": self.get_threat_level().value,
            "profiles": {name: profile.to_dict() for name, profile in self.config.profiles.items()},
            "active_constraints": list(self.constraint_system.constraints.keys()),
            "recent_history": self.get_history(50),
            "metrics_summary": self._summarize_metrics()
        }
    
    def _summarize_metrics(self) -> Dict:
        """Summarize recent metrics."""
        if not self._metrics:
            return {}
        
        valid_count = sum(1 for m in self._metrics if m.get("is_valid", True))
        invalid_count = len(self._metrics) - valid_count
        avg_score = sum(m.get("score", 0) for m in self._metrics) / len(self._metrics)
        
        return {
            "total": len(self._metrics),
            "valid": valid_count,
            "invalid": invalid_count,
            "valid_rate": valid_count / len(self._metrics),
            "avg_score": avg_score
        }
    
    def save_config(self, path: str) -> None:
        """Save current configuration to file."""
        config_data = {
            "current_profile": self.config.current_profile,
            "profiles": {name: profile.to_dict() for name, profile in self.config.profiles.items()},
            "auto_adjust": self.config.auto_adjust,
            "adjustment_interval": self.config.adjustment_interval,
            "metrics_window": self.config.metrics_window
        }
        with open(path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def load_config(self, path: str) -> None:
        """Load configuration from file."""
        with open(path, 'r') as f:
            config_data = json.load(f)
        
        self.config.current_profile = config_data.get("current_profile", "medium")
        self.config.auto_adjust = config_data.get("auto_adjust", True)
        self.config.adjustment_interval = config_data.get("adjustment_interval", 60.0)
        self.config.metrics_window = config_data.get("metrics_window", 100)
        
        for name, profile_data in config_data.get("profiles", {}).items():
            self.config.profiles[name] = ConstraintProfile(
                name=profile_data["name"],
                threat_level=ThreatLevel(profile_data["threat_level"]),
                constraints=profile_data["constraints"],
                description=profile_data.get("description", "")
            )
        
        self._apply_profile(self.config.current_profile)


# Singleton instance
ADAPTIVE_MANAGER = AdaptiveConstraintManager()
