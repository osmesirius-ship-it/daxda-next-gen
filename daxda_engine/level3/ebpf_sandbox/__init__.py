r"""
DAXDA Level 3: eBPF / LSM Kernel Syscall Sandbox Engine.
Implements C eBPF LSM probe source generation, tracepoint event evaluation,
and non-bypassable containment policies blocking network sockets and memory dumping.
"""

from .bpf_source_generator import (
    EBPFProgramConfig,
    EBPFSourceGenerator,
)
from .policy_engine import (
    SyscallType,
    SyscallEvent,
    SyscallVerdict,
    EBPFSandboxPolicyEngine,
    EBPFSandboxSecurityViolation,
)

__all__ = [
    "EBPFProgramConfig",
    "EBPFSourceGenerator",
    "SyscallType",
    "SyscallEvent",
    "SyscallVerdict",
    "EBPFSandboxPolicyEngine",
    "EBPFSandboxSecurityViolation",
]
