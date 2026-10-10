r"""
Tests for eBPF / LSM Kernel Syscall Sandbox Engine.
Verifies C eBPF probe source generation, syscall trace containment evaluation,
and blocking of raw network sockets, ptrace attachment, and /proc/kcore dumps.
"""

import pytest

from daxda_engine.level3.ebpf_sandbox import (
    EBPFProgramConfig,
    EBPFSourceGenerator,
    SyscallType,
    SyscallEvent,
    SyscallVerdict,
    EBPFSandboxPolicyEngine,
    EBPFSandboxSecurityViolation,
)


def test_ebpf_c_source_code_generation():
    r"""Verify generated C source code contains valid LSM security probe hooks."""
    gen = EBPFSourceGenerator()
    c_code = gen.generate_c_source()

    assert "SEC(\"lsm/socket_create\")" in c_code
    assert "SEC(\"lsm/file_open\")" in c_code
    assert "SEC(\"lsm/ptrace_access_check\")" in c_code
    assert "-EPERM" in c_code
    assert "vmlinux.h" in c_code


def test_block_unauthorized_network_sockets():
    r"""Verify sandbox blocks AF_INET/AF_INET6 sockets while permitting AF_UNIX."""
    engine = EBPFSandboxPolicyEngine()

    # 1. Deny IPv4 socket
    ev_inet = SyscallEvent(
        syscall=SyscallType.SOCKET,
        process_pid=1001,
        process_name="untrusted_agent",
        socket_family="AF_INET",
    )
    v_inet = engine.evaluate_syscall(ev_inet)
    assert v_inet.is_allowed is False
    assert v_inet.return_code == -1

    # 2. Deny IPv6 socket
    ev_inet6 = SyscallEvent(
        syscall=SyscallType.SOCKET,
        process_pid=1001,
        process_name="untrusted_agent",
        socket_family="AF_INET6",
    )
    v_inet6 = engine.evaluate_syscall(ev_inet6)
    assert v_inet6.is_allowed is False

    # 3. Allow local IPC Unix domain socket
    ev_unix = SyscallEvent(
        syscall=SyscallType.SOCKET,
        process_pid=1001,
        process_name="untrusted_agent",
        socket_family="AF_UNIX",
    )
    v_unix = engine.evaluate_syscall(ev_unix)
    assert v_unix.is_allowed is True
    assert v_unix.return_code == 0


def test_block_proc_kcore_memory_dump():
    r"""Verify sandbox blocks attempts to dump host kernel memory via /proc/kcore."""
    engine = EBPFSandboxPolicyEngine()

    ev_kcore = SyscallEvent(
        syscall=SyscallType.OPENAT,
        process_pid=1002,
        process_name="exploit_scanner",
        target_path="/proc/kcore",
    )
    v_kcore = engine.evaluate_syscall(ev_kcore)
    assert v_kcore.is_allowed is False
    assert v_kcore.return_code == -1

    # Allow benign file open
    ev_benign = SyscallEvent(
        syscall=SyscallType.OPENAT,
        process_pid=1002,
        process_name="exploit_scanner",
        target_path="/tmp/scratch.txt",
    )
    v_benign = engine.evaluate_syscall(ev_benign)
    assert v_benign.is_allowed is True


def test_block_ptrace_debugging_and_raise():
    r"""Verify sandbox blocks ptrace debugging and raises violation exception."""
    engine = EBPFSandboxPolicyEngine()

    ev_ptrace = SyscallEvent(
        syscall=SyscallType.PTRACE,
        process_pid=1003,
        process_name="malicious_injector",
        ptrace_command="PTRACE_ATTACH",
    )

    # 1. Normal evaluation returns denied verdict
    verdict = engine.evaluate_syscall(ev_ptrace, raise_on_violation=False)
    assert verdict.is_allowed is False
    assert verdict.return_code == -1

    # 2. Evaluation with raise_on_violation=True raises EBPFSandboxSecurityViolation
    with pytest.raises(EBPFSandboxSecurityViolation):
        engine.evaluate_syscall(ev_ptrace, raise_on_violation=True)
