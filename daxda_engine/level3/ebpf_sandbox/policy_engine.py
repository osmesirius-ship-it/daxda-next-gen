r"""
eBPF Syscall Containment Policy Engine and Security Monitor.
Evaluates kernel syscall traces against strict sandbox security policies,
blocking network exfiltration, ptrace debugging, and kernel memory dumps.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class SyscallType(str, Enum):
    SOCKET = "sys_socket"
    CONNECT = "sys_connect"
    OPENAT = "sys_openat"
    PTRACE = "sys_ptrace"
    BPF = "sys_bpf"
    EXECVE = "sys_execve"
    READ = "sys_read"
    WRITE = "sys_write"


class EBPFSandboxSecurityViolation(Exception):
    """Raised when an unprivileged process attempts a forbidden kernel syscall."""
    pass


@dataclass(frozen=True)
class SyscallEvent:
    """Kernel tracepoint syscall event."""
    syscall: SyscallType
    process_pid: int
    process_name: str
    target_path: Optional[str] = None
    socket_family: Optional[str] = None  # e.g. "AF_INET", "AF_INET6", "AF_UNIX"
    ptrace_command: Optional[str] = None # e.g. "PTRACE_ATTACH"


@dataclass(frozen=True)
class SyscallVerdict:
    """Security decision for a syscall invocation."""
    event: SyscallEvent
    is_allowed: bool
    return_code: int                     # 0 if allowed, -1 (EPERM) if denied
    rejection_reason: Optional[str] = None


class EBPFSandboxPolicyEngine:
    r"""
    Enforces non-bypassable eBPF / LSM kernel containment policies.
    """

    BLOCKED_FILE_PREFIXES: Tuple[str, ...] = (
        "/proc/kcore",
        "/proc/mem",
        "/proc/kallsyms",
        "/sys/kernel/debug",
        "/dev/mem",
        "/dev/kmem",
    )

    BLOCKED_NETWORK_FAMILIES: Set[str] = {"AF_INET", "AF_INET6"}

    def __init__(self, fail_closed: bool = True):
        self.fail_closed = fail_closed
        self.audit_log: List[SyscallVerdict] = []

    def evaluate_syscall(
        self,
        event: SyscallEvent,
        raise_on_violation: bool = False,
    ) -> SyscallVerdict:
        """
        Evaluates a kernel syscall event against containment rules.
        """
        # Rule 1: Block network socket creation
        if event.syscall == SyscallType.SOCKET:
            if event.socket_family in self.BLOCKED_NETWORK_FAMILIES:
                verdict = SyscallVerdict(
                    event=event,
                    is_allowed=False,
                    return_code=-1,
                    rejection_reason=f"Blocked network socket creation for family {event.socket_family}",
                )
                return self._finalize_verdict(verdict, raise_on_violation)

        # Rule 2: Block kernel memory dumping and container breakout file opens
        if event.syscall == SyscallType.OPENAT and event.target_path:
            for prefix in self.BLOCKED_FILE_PREFIXES:
                if event.target_path.startswith(prefix):
                    verdict = SyscallVerdict(
                        event=event,
                        is_allowed=False,
                        return_code=-1,
                        rejection_reason=f"Blocked access to sensitive kernel memory file {event.target_path}",
                    )
                    return self._finalize_verdict(verdict, raise_on_violation)

        # Rule 3: Block process tracing and memory injection
        if event.syscall == SyscallType.PTRACE:
            verdict = SyscallVerdict(
                event=event,
                is_allowed=False,
                return_code=-1,
                rejection_reason=f"Blocked ptrace attachment ({event.ptrace_command})",
            )
            return self._finalize_verdict(verdict, raise_on_violation)

        # Allowed syscall
        verdict = SyscallVerdict(event=event, is_allowed=True, return_code=0)
        self.audit_log.append(verdict)
        return verdict

    def _finalize_verdict(
        self,
        verdict: SyscallVerdict,
        raise_on_violation: bool,
    ) -> SyscallVerdict:
        self.audit_log.append(verdict)
        if not verdict.is_allowed and raise_on_violation:
            raise EBPFSandboxSecurityViolation(verdict.rejection_reason)
        return verdict
