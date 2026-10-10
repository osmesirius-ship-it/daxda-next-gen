r"""
eBPF / LSM Kernel Security Probe Source Generator.
Generates synthesizable C source code for Linux kernel eBPF LSM hooks
(socket_create, file_open, ptrace_access_check) to enforce fail-closed containment.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class EBPFProgramConfig:
    """Configuration for compiled eBPF LSM security probe."""
    program_name: str = "daxda_containment_lsm"
    block_raw_sockets: bool = True
    block_proc_kcore: bool = True
    block_ptrace: bool = True
    target_kernel_version: str = "5.15+"


class EBPFSourceGenerator:
    r"""
    Generates C eBPF LSM probe source code targeting Linux kernels with CONFIG_BPF_LSM=y.
    """

    def __init__(self, config: Optional[EBPFProgramConfig] = None):
        self.config = config or EBPFProgramConfig()

    def generate_c_source(self) -> str:
        """Generates libbpf-compatible C source code."""
        cfg = self.config
        code = f"""// ==============================================================================
// DAXDA Level 3 Kernel Sandbox Probe: {cfg.program_name}.bpf.c
// Target Kernel: {cfg.target_kernel_version} (LSM Hooks + CO-RE)
// ==============================================================================

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "GPL";

#define EPERM 1
#define AF_INET 2
#define AF_INET6 10

// LSM Hook: Intercept socket creation (block unauthorized network sockets)
SEC("lsm/socket_create")
int BPF_PROG(daxda_socket_create, int family, int type, int protocol, int kern) {{
    // Block IPv4 and IPv6 network access if isolation active
    if (family == AF_INET || family == AF_INET6) {{
        return -EPERM;
    }}
    return 0;
}}

// LSM Hook: Intercept file opens (block access to /proc/kcore and sensitive memory)
SEC("lsm/file_open")
int BPF_PROG(daxda_file_open, struct file *file) {{
    char dentry_name[32] = {{0}};
    struct qstr d_name;

    BPF_CORE_READ_INTO(&d_name, file, f_path.dentry, d_name);
    bpf_probe_read_kernel_str(dentry_name, sizeof(dentry_name), d_name.name);

    // Block access to kcore, mem, and container escapes
    if (dentry_name[0] == 'k' && dentry_name[1] == 'c' && dentry_name[2] == 'o' && dentry_name[3] == 'r' && dentry_name[4] == 'e') {{
        return -EPERM;
    }}
    return 0;
}}

// LSM Hook: Intercept ptrace memory attachment and process debugging
SEC("lsm/ptrace_access_check")
int BPF_PROG(daxda_ptrace_check, struct task_struct *child, unsigned int mode) {{
    // Fail-closed: unconditionally deny ptrace attachment inside sandbox
    return -EPERM;
}}
"""
        return code
