"""DAXDA Guard Governance Decorator (decorator.py).
Provides single-line governance decoration: @daxda_guard.enforce_governance(domain='finance')
"""

import functools
import time
from typing import Callable, Any, Optional
from .core import DAXDAGuardCore, GovernanceReceipt


class GovernanceViolationError(RuntimeError):
    """Raised when an enterprise action violates fail-closed governance rules."""
    def __init__(self, receipt: GovernanceReceipt):
        super().__init__(f"Governance Gate Violation: {receipt.verdict} ({receipt.decision_rule})")
        self.receipt = receipt


def enforce_governance(domain: str = "general", raise_on_block: bool = True) -> Callable:
    """Single-line Python decorator enforcing synchronous fail-closed DAXDA Guard governance."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            core = DAXDAGuardCore()
            
            input_summary = f"{func.__name__}(args_count={len(args)}, kwargs_keys={list(kwargs.keys())})"
            receipt = core.evaluate(domain, input_summary)

            if not receipt.publication_permitted:
                if raise_on_block:
                    raise GovernanceViolationError(receipt)
                else:
                    return {
                        "status": "BLOCKED",
                        "verdict": receipt.verdict,
                        "receipt": receipt
                    }

            # Execute underlying enterprise function
            result = func(*args, **kwargs)

            # If result is dict, attach cryptographic authority receipt
            if isinstance(result, dict):
                result["_daxda_authority_receipt"] = {
                    "verdict": receipt.verdict,
                    "reconstruction_loss": receipt.reconstruction_loss,
                    "sha256": receipt.authority_sha256
                }

            return result

        return wrapper
    return decorator
