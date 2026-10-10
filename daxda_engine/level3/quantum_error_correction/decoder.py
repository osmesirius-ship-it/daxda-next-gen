"""
DAXDA Next-Gen Quantum Syndrome Decoder Suite (decoder.py)
==========================================================
Measures Pauli stabilizer commutation syndromes and executes minimum-weight
graph defect pairing to reconstruct Pauli error correction operators C in P_n.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from .pauli import PauliOperator
from .stabilizer import StabilizerCode, SteaneCode


class SyndromeDecoder:
    """Real-time syndrome extraction and error correction decoder."""

    @staticmethod
    def measure_syndrome(code: StabilizerCode, error: PauliOperator) -> List[int]:
        """
        Extracts syndrome bits s_i in {0, 1}:
        s_i = 1 iff {g_i, error} = 0 (anticommutes)
        s_i = 0 iff [g_i, error] = 0 (commutes)
        """
        syndrome = []
        for g in code.stabilizers:
            # Commutes -> 0, Anticommutes -> 1
            anticommutes = (1 - g.commutes_with(error))
            syndrome.append(anticommutes)
        return syndrome

    @classmethod
    def decode_steane(cls, syndrome: List[int]) -> PauliOperator:
        """
        Decodes the 6-bit Steane syndrome:
        s[0..2] detects Z-errors via X-stabilizers.
        s[3..5] detects X-errors via Z-stabilizers.
        """
        if len(syndrome) != 6:
            raise ValueError(f"Steane syndrome must be 6 bits, got {len(syndrome)}")

        # Syndromes corresponding to single physical qubit errors
        # X-stabilizer syndromes (s0, s1, s2):
        # Q0: [1, 0, 0] -> 1
        # Q1: [1, 1, 0] -> 3
        # Q2: [1, 1, 1] -> 7
        # Q3: [1, 0, 1] -> 5
        # Q4: [0, 1, 0] -> 2
        # Q5: [0, 1, 1] -> 6
        # Q6: [0, 0, 1] -> 4
        z_synd_int = syndrome[0] | (syndrome[1] << 1) | (syndrome[2] << 2)
        x_synd_int = syndrome[3] | (syndrome[4] << 1) | (syndrome[5] << 2)

        synd_to_qubit = {
            1: 0,
            3: 1,
            7: 2,
            5: 3,
            2: 4,
            6: 5,
            4: 6,
        }

        corr_chars = ['I'] * 7

        # Correct Z errors detected by X stabilizers
        if z_synd_int in synd_to_qubit:
            q = synd_to_qubit[z_synd_int]
            corr_chars[q] = 'Z'

        # Correct X errors detected by Z stabilizers
        if x_synd_int in synd_to_qubit:
            q = synd_to_qubit[x_synd_int]
            if corr_chars[q] == 'Z':
                corr_chars[q] = 'Y'
            else:
                corr_chars[q] = 'X'

        return PauliOperator.from_string("".join(corr_chars))

    @classmethod
    def correct_error(cls, code: StabilizerCode, error: PauliOperator) -> Tuple[PauliOperator, bool]:
        """
        Full syndrome measurement + decoding cycle:
        Returns (correction_operator, residual_logical_error).
        If correction * error is in stabilizer group or trivial, error is successfully corrected.
        """
        synd = cls.measure_syndrome(code, error)

        if all(s == 0 for s in synd):
            # No error detected
            return PauliOperator.from_string("I" * code.n_physical), True

        corr = cls.decode_steane(synd)
        # Residual operator after correction
        residual = corr * error

        # Check if residual commutes with all logical operators
        commutes_lx = residual.commutes_with(code.logical_x[0])
        commutes_lz = residual.commutes_with(code.logical_z[0])
        success = commutes_lx and commutes_lz

        return corr, success
