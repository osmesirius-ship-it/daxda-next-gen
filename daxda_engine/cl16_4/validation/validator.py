"""
HyperValidator - Cl(16,4) Validation Engine
==========================================

Main validation engine that maps agent decisions to Cl(16,4) configurations
and validates against multi-dimensional constraints.
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import hashlib
import json
from datetime import datetime

from ..combinatorics.cl_space import ClSpace, ClConfig
from ..combinatorics.constraints import ConstraintSystem, ConstraintResult


@dataclass
class ValidationRequest:
    """A request to validate an agent decision."""
    agent_id: str
    decision_vector: List[float]  # 16-dimensional decision vector
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    request_id: str = field(default="")
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = hashlib.sha256(
                f"{self.agent_id}{self.timestamp}".encode()
            ).hexdigest()[:16]


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    request_id: str
    config: Optional[ClConfig]
    is_valid: bool
    constraints: ConstraintResult
    validation_time_ms: float
    timestamp: str
    cert_hash: str = field(default="")
    
    def __post_init__(self):
        self.cert_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        data = {
            "request_id": self.request_id,
            "is_valid": self.is_valid,
            "timestamp": self.timestamp,
            "config": str(self.config.indices) if self.config else "None"
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        return {
            "request_id": self.request_id,
            "is_valid": self.is_valid,
            "config": str(self.config.indices) if self.config else None,
            "constraints": {
                "passed": self.constraints.passed,
                "failed": self.constraints.failed,
                "score": self.constraints.score
            },
            "validation_time_ms": self.validation_time_ms,
            "timestamp": self.timestamp,
            "cert_hash": self.cert_hash
        }


class HyperValidator:
    """
    Main validation engine for Cl(16,4) governance.
    
    Provides:
    - Real-time validation of agent decisions
    - Mapping from continuous decision vectors to Cl(16,4) configurations
    - Multi-dimensional constraint checking
    - Cryptographic validation certificates
    """
    
    def __init__(self, space: Optional[ClSpace] = None, 
                 constraints: Optional[ConstraintSystem] = None):
        self.space = space or ClSpace(n=16, k=4)
        self.constraints = constraints or ConstraintSystem(space=self.space)
        self._stats = {
            "total_validations": 0,
            "valid_count": 0,
            "invalid_count": 0,
            "total_time_ms": 0.0
        }
    
    def validate(self, request: ValidationRequest) -> ValidationResult:
        """
        Validate an agent decision against Cl(16,4) space.
        
        Args:
            request: ValidationRequest containing agent decision
        
        Returns:
            ValidationResult with validation outcome
        """
        start_time = time.perf_counter()
        
        # Step 1: Map decision vector to Cl(16,4) configuration
        config = self._map_to_config(request.decision_vector)
        
        # Step 2: Check constraints
        if config:
            constraints_result = self.constraints.check_config(config)
            is_valid = not constraints_result.failed
        else:
            constraints_result = None
            is_valid = False
        
        # Step 3: Update stats
        self._stats["total_validations"] += 1
        if is_valid:
            self._stats["valid_count"] += 1
        else:
            self._stats["invalid_count"] += 1
        
        validation_time_ms = (time.perf_counter() - start_time) * 1000
        self._stats["total_time_ms"] += validation_time_ms
        
        # Create dummy constraints result if config is None
        if constraints_result is None:
            constraints_result = ConstraintResult(
                config=None,
                passed=[],
                failed=["mapping_failed"],
                soft_failed=[],
                score=0.0
            )
        
        result = ValidationResult(
            request_id=request.request_id,
            config=config,
            is_valid=is_valid,
            constraints=constraints_result,
            validation_time_ms=validation_time_ms,
            timestamp=datetime.utcnow().isoformat()
        )
        
        return result
    
    def validate_batch(self, requests: List[ValidationRequest]) -> List[ValidationResult]:
        """Validate a batch of requests."""
        return [self.validate(req) for req in requests]
    
    def _map_to_config(self, vector: List[float]) -> Optional[ClConfig]:
        """
        Map a 16-dimensional decision vector to Cl(16,4) configuration.
        
        Args:
            vector: 16-dimensional vector of agent decision values
        
        Returns:
            Mapped ClConfig or None if invalid
        """
        if len(vector) != 16:
            return None
        
        # Normalize vector to [0, 1] range
        min_val = min(vector)
        max_val = max(vector)
        if max_val - min_val == 0:
            normalized = [0.5] * 16
        else:
            normalized = [(v - min_val) / (max_val - min_val) for v in vector]
        
        # Map to configuration
        return self.space.map_to_config(normalized)
    
    def get_stats(self) -> Dict:
        """Get validation statistics."""
        avg_time = (self._stats["total_time_ms"] / self._stats["total_validations"]) \
                  if self._stats["total_validations"] > 0 else 0
        return {
            **self._stats,
            "avg_validation_time_ms": avg_time
        }
    
    def reset_stats(self) -> None:
        """Reset validation statistics."""
        self._stats = {
            "total_validations": 0,
            "valid_count": 0,
            "invalid_count": 0,
            "total_time_ms": 0.0
        }
    
    def validate_with_certificate(self, request: ValidationRequest) -> Tuple[ValidationResult, str]:
        """
        Validate and generate a signed certificate.
        
        Returns:
            Tuple of (ValidationResult, certificate_json)
        """
        result = self.validate(request)
        
        certificate = {
            "type": "daxda_cl16_4_validation_certificate",
            "version": "1.0.0",
            "request": {
                "request_id": request.request_id,
                "agent_id": request.agent_id,
                "timestamp": request.timestamp
            },
            "result": result.to_dict(),
            "validator": {
                "name": "HyperValidator",
                "version": "1.0.0",
                "space": f"Cl({self.space.n},{self.space.k})"
            }
        }
        
        return result, json.dumps(certificate, indent=2)


# Singleton instance
VALIDATOR = HyperValidator()
