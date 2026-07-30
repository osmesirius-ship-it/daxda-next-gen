"""DAXDA Guard C++ Ctypes Bridge (core.py).
Binds directly to libdaxda_core.so for sub-millisecond governance execution.
"""

import os
import ctypes
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Locate shared library
SO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "libdaxda_core.so")

class MultivectorStruct(ctypes.Structure):
    _fields_ = [("coeffs", ctypes.c_double * 128)]

class GovernanceReceiptStruct(ctypes.Structure):
    _fields_ = [
        ("verdict_code", ctypes.c_int),
        ("reconstruction_loss", ctypes.c_double),
        ("grade0_scalar", ctypes.c_double),
        ("calibrated_certainty", ctypes.c_double),
        ("authority_sha256", ctypes.c_char * 65)
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
            self.available = True
        except Exception as e:
            self.available = False
            self.error = str(e)

    def benchmark_cpp_blade_lookup(self, iterations: int = 10_000_000) -> float:
        """Measures raw C++ blade lookup time in nanoseconds."""
        return self.lib.daxda_benchmark_blade_lookup(iterations)

    def evaluate(self, domain: str, input_text: str) -> GovernanceReceipt:
        """Evaluates governance interlocks behind C++ libdaxda_core.so (< 2.0ms)."""
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

        return GovernanceReceipt(
            verdict=v_str,
            decision_rule="WITHIN_GOVERNANCE_TOLERANCE" if pub_permitted else "GOV_FAIL_05",
            reconstruction_loss=rcpt_struct.reconstruction_loss,
            grade0_scalar=rcpt_struct.grade0_scalar,
            calibrated_certainty=rcpt_struct.calibrated_certainty,
            authority_sha256=rcpt_struct.authority_sha256.decode('utf-8', errors='ignore'),
            publication_permitted=pub_permitted
        )

class Multivector:
    def __init__(self, scalar: float = 1.0):
        self.struct = MultivectorStruct()
        DAXDAGuardCore().lib.daxda_multivector_init(ctypes.byref(self.struct))
        DAXDAGuardCore().lib.daxda_multivector_set_scalar(ctypes.byref(self.struct), scalar)
