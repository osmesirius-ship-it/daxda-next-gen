"""
DAXDA Level 4 — Next-Gen Recursive Subsystems
==============================================

Level 4 of the DAXDA Decision Audit & Execution Domain Architecture.
Unites:
- Domain 1: Cl(128,32) Multivector Algebra & Anyonic Braid Compiler
- Domain 2: 6D Calabi-Yau Chrono Metric & Novikov CTC Consistency Solver
- Domain 3: Neuromorphic Spiking Fabric & AER Mesh Routing
- Domain 4: Zero-Knowledge Kernel Containment & Enclave Attestation
- Domain 5: Global Pan-Psychometrics & Collective Phi MIP Engine
- Orchestrator: Level 4 Cl(32,8) Validator Map & Certification Report
"""

from . import cl128_32
from . import calabi_yau_chrono
from . import neuromorphic_fabric
from . import zk_kernel_containment
from . import collective_phi
from . import orchestrator

__all__ = [
    "cl128_32",
    "calabi_yau_chrono",
    "neuromorphic_fabric",
    "zk_kernel_containment",
    "collective_phi",
    "orchestrator",
]
