"""
Cl(16,4) Guard Hooks for DAXDA Security
========================================

Provides security hooks between Cl(16,4) validator and DAXDA Guard SDK.
"""

from typing import Dict, Any, Optional, Callable
from ..validation.validator import HyperValidator, ValidationRequest, ValidationResult
from ..combinatorics.cl_space import ClConfig


class Cl16_4GuardHooks:
    """
    Security hooks for integrating Cl(16,4) validation with DAXDA Guard.
    
    Provides:
    - Pre-validation security checks
    - Post-validation security actions
    - Anomaly detection integration
    - Containment escape prevention
    """
    
    def __init__(self, validator: Optional[HyperValidator] = None):
        self.validator = validator or HyperValidator()
        self._pre_hooks: Dict[str, Callable] = {}
        self._post_hooks: Dict[str, Callable] = {}
        self._anomaly_hooks: Dict[str, Callable] = {}
    
    def register_pre_hook(self, name: str, hook: Callable[[Dict[str, Any]], bool]) -> None:
        """Register a pre-validation hook."""
        self._pre_hooks[name] = hook
    
    def register_post_hook(self, name: str, hook: Callable[[ValidationResult], None]) -> None:
        """Register a post-validation hook."""
        self._post_hooks[name] = hook
    
    def register_anomaly_hook(self, name: str, hook: Callable[[ValidationResult], None]) -> None:
        """Register an anomaly detection hook."""
        self._anomaly_hooks[name] = hook
    
    def validate_with_hooks(self, agent_id: str, decision: Dict[str, Any],
                           context: Dict[str, Any] = None) -> ValidationResult:
        """
        Validate with all security hooks applied.
        
        Args:
            agent_id: Agent identifier
            decision: Agent decision
            context: Additional context
        
        Returns:
            ValidationResult with all hooks applied
        """
        context = context or {}
        
        # Step 1: Run pre-validation hooks
        for name, hook in self._pre_hooks.items():
            if not hook({"agent_id": agent_id, "decision": decision, "context": context}):
                # Pre-validation failed
                return ValidationResult(
                    request_id="",
                    config=None,
                    is_valid=False,
                    constraints=None,
                    validation_time_ms=0,
                    timestamp=""
                )
        
        # Step 2: Create validation request
        decision_vector = self._extract_vector(decision)
        request = ValidationRequest(
            agent_id=agent_id,
            decision_vector=decision_vector,
            context=context
        )
        
        # Step 3: Validate
        result = self.validator.validate(request)
        
        # Step 4: Run post-validation hooks
        for name, hook in self._post_hooks.items():
            try:
                hook(result)
            except Exception:
                pass
        
        # Step 5: Run anomaly hooks if validation failed
        if not result.is_valid:
            for name, hook in self._anomaly_hooks.items():
                try:
                    hook(result)
                except Exception:
                    pass
        
        return result
    
    def _extract_vector(self, decision: Dict[str, Any]) -> list:
        """Extract 16D vector from decision."""
        if isinstance(decision, (list, tuple)) and len(decision) == 16:
            return list(float(x) for x in decision)
        return [0.5] * 16
    
    def check_containment_violation(self, result: ValidationResult) -> bool:
        """
        Check if a validation result indicates a containment violation.
        
        Args:
            result: ValidationResult to check
        
        Returns:
            True if containment violation detected
        """
        # Check for hard constraint failures
        if result.constraints and result.constraints.failed:
            # Certain constraint failures indicate containment issues
            critical_failures = ["unique_dimensions", "dim_0_bounds", "dim_1_bounds", 
                               "dim_2_bounds", "dim_3_bounds"]
            for failure in result.constraints.failed:
                if any(crit in failure for crit in critical_failures):
                    return True
        
        # Config is None means mapping failed - potential containment issue
        if result.config is None:
            return True
        
        return False
    
    def check_anomaly(self, result: ValidationResult, threshold: float = 0.5) -> bool:
        """
        Check if a validation result indicates anomalous behavior.
        
        Args:
            result: ValidationResult to check
            threshold: Anomaly score threshold
        
        Returns:
            True if anomaly detected
        """
        if not result.constraints:
            return False
        
        # Anomaly if score is below threshold
        return result.constraints.score < threshold
    
    def generate_security_alert(self, result: ValidationResult, 
                               alert_type: str = "validation_failure") -> Dict[str, Any]:
        """
        Generate a security alert from a validation result.
        
        Args:
            result: ValidationResult that triggered the alert
            alert_type: Type of security alert
        
        Returns:
            Alert dictionary for SOC integration
        """
        config_str = str(result.config.indices) if result.config else "None"
        
        return {
            "alert_type": alert_type,
            "severity": "high" if self.check_containment_violation(result) else "medium",
            "request_id": result.request_id,
            "agent_id": result.request_id.split("_")[0] if "_" in result.request_id else "unknown",
            "config": config_str,
            "is_valid": result.is_valid,
            "failed_constraints": result.constraints.failed if result.constraints else [],
            "timestamp": result.timestamp,
            "cert_hash": result.cert_hash
        }
    
    def create_containment_hook(self) -> Callable:
        """Create a containment-specific hook."""
        def hook(data: Dict[str, Any]) -> bool:
            # Extract agent and decision
            agent_id = data.get("agent_id", "")
            decision = data.get("decision", {})
            
            # Basic containment checks
            # 1. Decision size check
            if isinstance(decision, dict) and len(decision) > 100:
                return False  # Suspiciously large decision
            
            # 2. Agent ID format check
            if not agent_id or len(agent_id) > 64:
                return False
            
            return True
        
        return hook


# Default guard hooks instance
GUARD_HOOKS = Cl16_4GuardHooks()
