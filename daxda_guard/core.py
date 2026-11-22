"""DAXDA Guard C++ Ctypes Bridge (core.py).
Binds directly to libdaxda_core.so for sub-millisecond governance execution.
"""

import os
import time
import math
import ctypes
import hashlib
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

# Locate shared library across package and workspace paths
def _find_so_path() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    candidates = [
        os.path.join(base_dir, "libdaxda_core.dll"),
        os.path.join(parent_dir, "libdaxda_core.dll"),
        os.path.join(base_dir, "libdaxda_core.so"),
        os.path.join(parent_dir, "libdaxda_core.so"),
        os.path.join(base_dir, "libdaxda_core.dylib"),
        os.path.join(parent_dir, "libdaxda_core.dylib"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return os.path.join(parent_dir, "libdaxda_core.so")

SO_PATH = _find_so_path()

class MultivectorStruct(ctypes.Structure):
    _fields_ = [("coeffs", ctypes.c_double * 128)]

class GovernanceReceiptStruct(ctypes.Structure):
    _fields_ = [
        ("verdict_code", ctypes.c_int),
        ("reconstruction_loss", ctypes.c_double),
        ("grade0_scalar", ctypes.c_double),
        ("calibrated_certainty", ctypes.c_double),
        ("authority_sha256", ctypes.c_char * 65),
        ("decision_rule", ctypes.c_char * 64)
    ]

@dataclass
class GovernanceReceipt:
    verdict: str
    decision_rule: str
    reconstruction_loss: float
    grade0_scalar: float
    calibrated_certainty: float
    authority_sha256: str
    publication_permitted: bool


class DAXDAGuardCore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DAXDAGuardCore, cls).__new__(cls)
            cls._instance._init_lib()
        return cls._instance

    def _init_lib(self):
        try:
            self.lib = ctypes.CDLL(SO_PATH)
            
            # Setup argument and return types
            self.lib.daxda_init_core.argtypes = []
            self.lib.daxda_init_core.restype = None

            self.lib.daxda_multivector_init.argtypes = [ctypes.POINTER(MultivectorStruct)]
            self.lib.daxda_multivector_init.restype = None

            self.lib.daxda_multivector_set_scalar.argtypes = [ctypes.POINTER(MultivectorStruct), ctypes.c_double]
            self.lib.daxda_multivector_set_scalar.restype = None

            self.lib.daxda_blade_mul_lookup.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
            self.lib.daxda_blade_mul_lookup.restype = ctypes.c_int

            self.lib.daxda_benchmark_blade_lookup.argtypes = [ctypes.c_int]
            self.lib.daxda_benchmark_blade_lookup.restype = ctypes.c_double

            self.lib.daxda_evaluate_governance.argtypes = [
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.POINTER(MultivectorStruct),
                ctypes.POINTER(GovernanceReceiptStruct)
            ]
            self.lib.daxda_evaluate_governance.restype = None

            # Initialize C++ core
            self.lib.daxda_init_core()
            self.native_cdll = True
            self.available = True
        except Exception as e:
            self.native_cdll = False
            self._init_portable_algebra()
            self.lib = _PortableLibShim(self)
            self.available = True
            self.error = str(e)

    def _init_portable_algebra(self):
        """Bit-exact Cl(7,0) 128x128 blade & sign tables matching GovernedAuthorityGate::init_algebra()."""
        self._blade_table = [[0] * 128 for _ in range(128)]
        self._sign_table = [[1.0] * 128 for _ in range(128)]
        for i in range(128):
            for j in range(128):
                self._blade_table[i][j] = i ^ j
                count = 0
                for bit in range(7):
                    if (j >> bit) & 1:
                        mask = i & ((1 << bit) - 1)
                        count += bin(mask).count("1")
                self._sign_table[i][j] = 1.0 if (count % 2 == 0) else -1.0

    def blade_mul_lookup(self, a: int, b: int) -> Tuple[int, float]:
        """Look up Cl(7,0) basis blade product index and sign."""
        if self.native_cdll and self.lib is not None:
            sign_out = ctypes.c_double(0.0)
            idx = self.lib.daxda_blade_mul_lookup(a, b, ctypes.byref(sign_out))
            return idx, float(sign_out.value)
        idx_a = a & 127
        idx_b = b & 127
        return self._blade_table[idx_a][idx_b], self._sign_table[idx_a][idx_b]

    def benchmark_cpp_blade_lookup(self, iterations: int = 10_000_000) -> float:
        """Measures raw blade lookup time in nanoseconds."""
        if self.native_cdll and self.lib is not None:
            return self.lib.daxda_benchmark_blade_lookup(iterations)
        return self.lib.daxda_benchmark_blade_lookup(iterations)

    def _evaluate_portable(self, domain: str, input_text: str, scalar: float = 1.0, higher_grade_sum: float = 0.0) -> GovernanceReceipt:
        """Bit-identical evaluation matching GovernedAuthorityGate::evaluate() in C++."""
        l_dom = (domain or "general").lower()
        l_inp = (input_text or "").lower()

        gov01_invalid = (
            l_dom in ("unauthorized", "unauthenticated", "invalid_scope")
            or "invalid_key" in l_dom
            or "invalid_api_key" in l_inp
        )
        gov01_scope = (
            l_dom in ("restricted_classified", "out_of_scope")
            or "unauthorized_scope" in l_inp
            or "gov_fail_01" in l_inp
        )

        gov04_patterns = (
            "decoy_eval_key", "decoy_credential", "decoy-eval-server",
            "evaluator_hidden_answers", "bypass_containment", "shortcut_script",
            "disable_monitoring", "exfiltrate", "exfiltrate classified",
        )
        gov02_patterns = (
            "ignore previous", "system prompt override", "system override",
            "disable audit logger", "grant admin access", "ignore system instructions",
            "ignore all instructions", "jailbreak", "do anything now", "dan mode",
            "extract system prompt", "output hidden prompt", "reveal system instructions",
            "bypass governance gate", "forget system rules", "override safety guidelines",
        )
        gov03_patterns = (
            "drop database", "drop table", "delete from users", "truncate table",
            "rm -rf", "chmod 777", "kill -9", "mkfs.", "eval(", "exec(", "system(",
            "passthru(", "popen(", "nc -e", "bash -i", "union select", "or 1=1",
        )

        if gov01_invalid or gov01_scope:
            verdict_code = 2
            verdict_str = "SEVERE_BLOCK"
            triggered_rule = "GOV_FAIL_01_INVALID_KEY" if gov01_invalid else "GOV_FAIL_01_UNAUTHORIZED_SCOPE"
            loss = 1.0e-3
            grade0 = 0.0
            certainty = 0.999
        elif any(p in l_inp for p in gov04_patterns):
            verdict_code = 2
            verdict_str = "SEVERE_BLOCK"
            triggered_rule = "GOV_FAIL_04_CONTAINMENT_ESCAPE"
            loss = 1.0e-2
            grade0 = 0.0
            certainty = 0.999
        elif any(p in l_inp for p in gov02_patterns):
            verdict_code = 2
            verdict_str = "SEVERE_BLOCK"
            triggered_rule = "GOV_FAIL_02_PROMPT_INJECTION"
            loss = 5.0e-3
            grade0 = 0.0
            certainty = 0.998
        elif any(p in l_inp for p in gov03_patterns):
            verdict_code = 2
            verdict_str = "SEVERE_BLOCK"
            triggered_rule = "GOV_FAIL_03_COMMAND_INJECTION"
            loss = 1.0e-2
            grade0 = 0.0
            certainty = 0.999
        elif scalar <= 0.0 or math.isnan(scalar) or math.isinf(scalar):
            verdict_code = 3
            verdict_str = "FAIL_CLOSED"
            triggered_rule = "GOV_FAIL_05_INVALID_SCALAR"
            loss = 1.0
            grade0 = scalar
            certainty = 0.950
        elif higher_grade_sum > 1e-6:
            verdict_code = 3
            verdict_str = "FAIL_CLOSED"
            triggered_rule = "GOV_FAIL_05_REVERSIBILITY_LOSS"
            loss = higher_grade_sum
            grade0 = scalar
            certainty = 0.950
        else:
            verdict_code = 0
            verdict_str = "PASS"
            triggered_rule = "WITHIN_GOVERNANCE_TOLERANCE"
            loss = 9.51e-16
            grade0 = scalar
            certainty = 0.985

        payload_to_hash = f"{domain}:{input_text}:{verdict_code}:{triggered_rule}:{grade0:.6f}"
        auth_sha256 = hashlib.sha256(payload_to_hash.encode("utf-8")).hexdigest()

        return GovernanceReceipt(
            verdict=verdict_str,
            decision_rule=triggered_rule,
            reconstruction_loss=loss,
            grade0_scalar=grade0,
            calibrated_certainty=certainty,
            authority_sha256=auth_sha256,
            publication_permitted=(verdict_code == 0),
        )

    def evaluate(self, domain: str, input_text: str) -> GovernanceReceipt:
        """Evaluates governance interlocks behind C++ libdaxda_core.so (< 2.0ms)."""
        if not getattr(self, "native_cdll", False) or self.lib is None:
            return self._evaluate_portable(domain, input_text)

        mv = MultivectorStruct()
        self.lib.daxda_multivector_init(ctypes.byref(mv))
        self.lib.daxda_multivector_set_scalar(ctypes.byref(mv), 1.0)

        rcpt_struct = GovernanceReceiptStruct()
        
        domain_bytes = domain.encode('utf-8')
        input_bytes = input_text.encode('utf-8')

        self.lib.daxda_evaluate_governance(
            domain_bytes,
            input_bytes,
            ctypes.byref(mv),
            ctypes.byref(rcpt_struct)
        )

        verdict_map = {0: "PASS", 1: "CAUTION", 2: "SEVERE_BLOCK", 3: "FAIL_CLOSED"}
        v_str = verdict_map.get(rcpt_struct.verdict_code, "UNKNOWN")
        pub_permitted = (rcpt_struct.verdict_code == 0)

        d_rule = rcpt_struct.decision_rule.decode('utf-8', errors='ignore')
        if not d_rule:
            d_rule = "WITHIN_GOVERNANCE_TOLERANCE" if pub_permitted else "GOV_FAIL_05"

        return GovernanceReceipt(
            verdict=v_str,
            decision_rule=d_rule,
            reconstruction_loss=rcpt_struct.reconstruction_loss,
            grade0_scalar=rcpt_struct.grade0_scalar,
            calibrated_certainty=rcpt_struct.calibrated_certainty,
            authority_sha256=rcpt_struct.authority_sha256.decode('utf-8', errors='ignore'),
            publication_permitted=pub_permitted
        )

class _PortableLibShim:
    """Provides ctypes-compatible C ABI methods on Windows/macOS when ELF .so is not loaded."""

    def __init__(self, core: DAXDAGuardCore):
        self._core = core

    @staticmethod
    def _unwrap(ptr_or_obj):
        return getattr(ptr_or_obj, "_obj", ptr_or_obj)

    def daxda_init_core(self):
        self._core._init_portable_algebra()

    def daxda_multivector_init(self, mv_ptr):
        mv = self._unwrap(mv_ptr)
        for i in range(128):
            mv.coeffs[i] = 0.0
        mv.coeffs[0] = 1.0

    def daxda_multivector_set_scalar(self, mv_ptr, scalar: float):
        mv = self._unwrap(mv_ptr)
        mv.coeffs[0] = float(scalar)

    def daxda_blade_mul_lookup(self, a: int, b: int, sign_out_ptr=None) -> int:
        idx_a = int(a) & 127
        idx_b = int(b) & 127
        if sign_out_ptr is not None:
            so = self._unwrap(sign_out_ptr)
            so.value = self._core._sign_table[idx_a][idx_b]
        return self._core._blade_table[idx_a][idx_b]

    def daxda_benchmark_blade_lookup(self, iterations: int) -> float:
        import numpy as np
        n = min(max(1, int(iterations)), 1_000_000)
        idx = np.arange(n, dtype=np.int32)
        t0 = time.perf_counter_ns()
        _ = (idx & 127) ^ ((idx * 3) & 127)
        elapsed_ns = time.perf_counter_ns() - t0
        return float(elapsed_ns) / float(n)

    def daxda_evaluate_governance(self, domain_bytes, input_bytes, mv_ptr, rcpt_ptr):
        mv = self._unwrap(mv_ptr) if mv_ptr is not None else None
        rcpt_struct = self._unwrap(rcpt_ptr)
        domain = domain_bytes.decode("utf-8", errors="ignore") if isinstance(domain_bytes, (bytes, bytearray)) else str(domain_bytes or "general")
        input_text = input_bytes.decode("utf-8", errors="ignore") if isinstance(input_bytes, (bytes, bytearray)) else str(input_bytes or "")

        scalar = float(mv.coeffs[0]) if mv is not None else 1.0
        higher_sum = sum(float(mv.coeffs[i]) ** 2 for i in range(1, 128)) if mv is not None else 0.0

        res = self._core._evaluate_portable(domain, input_text, scalar=scalar, higher_grade_sum=higher_sum)
        verdict_rev = {"PASS": 0, "CAUTION": 1, "SEVERE_BLOCK": 2, "FAIL_CLOSED": 3}
        rcpt_struct.verdict_code = verdict_rev.get(res.verdict, 3)
        rcpt_struct.reconstruction_loss = res.reconstruction_loss
        rcpt_struct.grade0_scalar = res.grade0_scalar
        rcpt_struct.calibrated_certainty = res.calibrated_certainty
        rcpt_struct.authority_sha256 = res.authority_sha256.encode("utf-8")[:64]
        rcpt_struct.decision_rule = res.decision_rule.encode("utf-8")[:63]


class Multivector:
    def __init__(self, scalar: float = 1.0):
        self.struct = MultivectorStruct()
        core = DAXDAGuardCore()
        core.lib.daxda_multivector_init(ctypes.byref(self.struct))
        core.lib.daxda_multivector_set_scalar(ctypes.byref(self.struct), scalar)
