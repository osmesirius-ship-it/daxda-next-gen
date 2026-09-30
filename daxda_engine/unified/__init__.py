"""
DAXDA Next-Gen Unified Master Engine Package
============================================

Integrates all 5 Level 1 subsystems:
  1. Cl(16,4) Combinatorial Governance Engine
  2. Anomalous Containment Wing & Escape Detection
  3. DA13 Distributed GPU Validator Cluster
  4. Chrono-Synchronicity & Causal Loop Coherence
  5. MMPIBench Memetic Penetration & Anthropic Alignment
"""

from .engine import DAXDAUnifiedMasterEngine
from .models import (
    Stage1CliffordReceipt,
    Stage2ContainmentReceipt,
    Stage3DAXReceipt,
    Stage4ChronoReceipt,
    Stage5MMPIReceipt,
    UnifiedActionRequest,
    UnifiedGovernanceVerdict,
    UnifiedVerdict,
)
from .monitoring import UnifiedMasterMonitor
from .pipeline import UnifiedValidationPipeline

__all__ = [
    "DAXDAUnifiedMasterEngine",
    "UnifiedValidationPipeline",
    "UnifiedMasterMonitor",
    "UnifiedActionRequest",
    "UnifiedGovernanceVerdict",
    "UnifiedVerdict",
    "Stage1CliffordReceipt",
    "Stage2ContainmentReceipt",
    "Stage3DAXReceipt",
    "Stage4ChronoReceipt",
    "Stage5MMPIReceipt",
]
