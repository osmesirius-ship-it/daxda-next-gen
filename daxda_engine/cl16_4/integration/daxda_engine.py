"""
Cl(16,4) Integration with DAXDA Engine
======================================

Provides hooks and integration points between Cl(16,4) validator
and the existing DAXDA neural-symbolic engine.
"""

from typing import Dict, Any, List, Optional
from ..validation.validator import HyperValidator, ValidationRequest, ValidationResult
from ..combinatorics.cl_space import ClSpace, ClConfig


class Cl16_4EngineIntegration:
    """
    Integration layer between Cl(16,4) validator and DAXDA engine.
    
    Provides:
    - Decision validation hook for DAXDA engine
    - Agent decision mapping to Cl(16,4) space
    - Validation result integration with DAXDA governance
    """
    
    def __init__(self, validator: Optional[HyperValidator] = None):
        self.validator = validator or HyperValidator()
        self.space = self.validator.space
    
    def validate_agent_decision(self, agent_id: str, decision: Dict[str, Any]) -> ValidationResult:
        """
        Validate an agent decision using Cl(16,4) space.
        
        Args:
            agent_id: Unique agent identifier
            decision: Agent decision as dictionary
        
        Returns:
            ValidationResult with validation outcome
        """
        # Extract decision vector from agent decision
        decision_vector = self._extract_decision_vector(decision)
        
        # Create validation request
        request = ValidationRequest(
            agent_id=agent_id,
            decision_vector=decision_vector,
            context={"raw_decision": decision}
        )
        
        # Validate and return result
        return self.validator.validate(request)
    
    def _extract_decision_vector(self, decision: Dict[str, Any]) -> List[float]:
        """
        Extract 16-dimensional vector from agent decision.
        
        Supports multiple formats:
        - Direct 16-element list/array
        - Dictionary with 16 keys
        - Nested structure that can be flattened
        """
        # If it's already a list/array of 16 elements
        if isinstance(decision, (list, tuple)) and len(decision) == 16:
            return list(float(x) for x in decision)
        
        # If it's a dictionary, extract values
        if isinstance(decision, dict):
            values = list(decision.values())
            if len(values) == 16:
                return list(float(x) for x in values)
            # Try to flatten
            flat = self._flatten_dict(decision)
            if len(flat) >= 16:
                return flat[:16]
        
        # Default: create a neutral vector
        return [0.5] * 16
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> List[float]:
        """Flatten a nested dictionary to a list of values."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).values())
            else:
                try:
                    items.append(float(v))
                except (ValueError, TypeError):
                    items.append(0.5)
        return items
    
    def get_cl16_4_coordinates(self, decision: Dict[str, Any]) -> Optional[ClConfig]:
        """
        Get the Cl(16,4) coordinates for an agent decision.
        
        Args:
            decision: Agent decision
        
        Returns:
            ClConfig if valid, None otherwise
        """
        decision_vector = self._extract_decision_vector(decision)
        return self.space.map_to_config(decision_vector)
    
    def validate_and_integrate(self, agent_id: str, decision: Dict[str, Any],
                             governance_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Full validation with DAXDA governance integration.
        
        Args:
            agent_id: Agent identifier
            decision: Agent decision
            governance_context: Additional governance context
        
        Returns:
            Integrated validation result with governance metadata
        """
        # Step 1: Validate using Cl(16,4)
        result = self.validate_agent_decision(agent_id, decision)
        
        # Step 2: Integrate with governance context
        integrated = {
            "cl16_4_validation": result.to_dict(),
            "governance": {
                "agent_id": agent_id,
                "decision_hash": self._hash_decision(decision),
                "validation_passed": result.is_valid,
                "config": str(result.config.indices) if result.config else None,
                "timestamp": result.timestamp
            },
            **governance_context
        }
        
        return integrated
    
    def _hash_decision(self, decision: Dict[str, Any]) -> str:
        """Create a hash of the decision for tracking."""
        import hashlib
        import json
        try:
            data = json.dumps(decision, sort_keys=True)
            return hashlib.sha256(data.encode()).hexdigest()[:16]
        except:
            return hashlib.sha256(str(decision).encode()).hexdigest()[:16]
    
    def batch_validate(self, agent_decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Batch validate multiple agent decisions.
        
        Args:
            agent_decisions: List of {agent_id, decision} dictionaries
        
        Returns:
            List of integrated validation results
        """
        results = []
        for item in agent_decisions:
            agent_id = item.get("agent_id", "unknown")
            decision = item.get("decision", {})
            context = item.get("context", {})
            
            integrated = self.validate_and_integrate(agent_id, decision, context)
            results.append(integrated)
        
        return results


# Singleton instance
ENGINE_INTEGRATION = Cl16_4EngineIntegration()
