from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class RoleConfig:
    role: str
    gpu_ids: List[int]
    model_name: str


# 17-GPU role map
# 0: control plane (orchestrator + DA-X)
# 1-6: reasoning pool
# 7-12: simulation pool
# 13-15: validation pool
# 16: shadow verifier
ROLE_MAP: Dict[str, RoleConfig] = {
    "orchestrator": RoleConfig("orchestrator", [0], "mistralai/Mistral-7B-Instruct-v0.2"),
    "reasoning": RoleConfig("reasoning", [1, 2, 3, 4, 5, 6], "mistralai/Mistral-7B-Instruct-v0.2"),
    "simulation": RoleConfig("simulation", [7, 8, 9, 10, 11, 12], "mistralai/Mistral-7B-Instruct-v0.2"),
    "validation": RoleConfig("validation", [13, 14, 15], "mistralai/Mistral-7B-Instruct-v0.2"),
    "shadow": RoleConfig("shadow", [16], "meta-llama/Llama-2-7b-chat-hf"),
}


DEFAULT_WEIGHTS = {
    "wL": 0.25,
    "wA": 0.20,
    "wP": 0.20,
    "wF": 0.20,
    "wT": 0.15,
}

THRESHOLDS = {
    "accept": 0.75,
    "recurse_floor": 0.55,
}
