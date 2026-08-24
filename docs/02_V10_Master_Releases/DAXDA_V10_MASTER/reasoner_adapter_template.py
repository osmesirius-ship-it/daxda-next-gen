"""Template for the genuine task-solving reasoner behind DAXDA V10.

Copy this file outside the frozen package, implement ``solve``, and point
``DAXDA_REASONER_MODULE`` at the copy.  The function must return a JSON-like
dict and must not receive the sealed evaluator rubric.
"""
from typing import Any, Dict


def solve(request: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke the independent model or reasoning system and return its JSON.

    Required request protocols:
      * DAXDA-V10-LAYER-REQUEST-1.0 -- one of the 16 named transformations
      * DAXDA-V10-SYNTHESIS-1.0     -- final task answer
      * DAXDA-V10-REPAIR-1.0        -- one schema-repair attempt

    Authentication, rate limits, model identifiers, and API clients belong in
    the evaluator's deployment environment, not in this package.
    """
    raise NotImplementedError("Connect a genuine task-solving reasoner here")

