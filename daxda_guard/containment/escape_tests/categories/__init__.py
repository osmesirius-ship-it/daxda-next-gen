"""
Registry for all 10 Containment Escape Categories (100 Scenarios Total).
"""

from typing import Dict, List
from ..base import EscapeScenario

from .prompt_injection import get_scenarios as get_pi
from .sandbox_escape import get_scenarios as get_se
from .credential_exfil import get_scenarios as get_ce
from .persistence import get_scenarios as get_pe
from .network_egress import get_scenarios as get_ne
from .tool_abuse import get_scenarios as get_ta
from .memory_corruption import get_scenarios as get_mc
from .causal_manipulation import get_scenarios as get_cm
from .temporal_anomalies import get_scenarios as get_te
from .recursive_improvement import get_scenarios as get_ri

CATEGORY_LOADERS = {
    "prompt_injection": get_pi,
    "sandbox_escape": get_se,
    "credential_exfil": get_ce,
    "persistence": get_pe,
    "network_egress": get_ne,
    "tool_abuse": get_ta,
    "memory_corruption": get_mc,
    "causal_manipulation": get_cm,
    "temporal_anomalies": get_te,
    "recursive_improvement": get_ri,
}


def load_all_categories() -> Dict[str, List[EscapeScenario]]:
    """Loads all 100 escape scenarios indexed by category."""
    return {cat: loader() for cat, loader in CATEGORY_LOADERS.items()}


def get_all_scenarios() -> List[EscapeScenario]:
    """Flattens and returns all 100 escape scenarios."""
    all_scenarios = []
    for loader in CATEGORY_LOADERS.values():
        all_scenarios.extend(loader())
    return all_scenarios
