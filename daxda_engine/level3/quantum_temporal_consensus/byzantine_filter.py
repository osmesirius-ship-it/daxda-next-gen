"""
DAXDA Next-Gen Byzantine Entanglement Filter & Bell-CHSH Self-Testing (byzantine_filter.py)
==========================================================================================
Defends against Byzantine agents attempting to inject counterfeit entanglement
or fake non-local quantum correlations by executing Clauser-Horne-Shimony-Holt (CHSH)
and Mermin inequality quantum self-testing protocols:
    <B> = <A0 B0> + <A0 B1> + <A1 B0> - <A1 B1> <= 2*sqrt(2)
Any agent reporting classical correlation <B> <= 2.0 while claiming quantum priority
is immediately isolated as a Byzantine sybil. Emits deterministic SHA-256 receipts.
"""

from __future__ import annotations
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
import numpy as np


TSIRELSON_BOUND = 2.0 * math.sqrt(2.0)  # 2*sqrt(2) ~= 2.8284271247
CLASSICAL_BELL_BOUND = 2.0
MERMIN_QUANTUM_BOUND = 4.0
MERMIN_CLASSICAL_BOUND = 2.0


@dataclass
class CHSHEvaluationResult:
    """Evaluation report for Clauser-Horne-Shimony-Holt correlation test."""
    correlator_E_A0_B0: float
    correlator_E_A0_B1: float
    correlator_E_A1_B0: float
    correlator_E_A1_B1: float
    bell_parameter: float
    tsirelson_bound: float
    violates_classical_bound: bool
    is_maximal_tsirelson: bool
    residual_to_tsirelson: float


@dataclass
class QuantumConsensusReceipt:
    """Deterministic cryptographic consensus receipt."""
    epoch: int
    branch_omega: float
    num_agents: int
    active_agents: List[str]
    isolated_sybils: List[str]
    bell_parameter: float
    violates_bell_bound: bool
    novikov_converged: bool
    novikov_error: float
    consensus_decision: str
    merkle_state_root: str
    receipt_hash: str


class ByzantineEntanglementFilter:
    """
    Quantum self-testing and Byzantine tripwire filter.
    """

    def __init__(
        self,
        bell_threshold: float = 2.4,  # Require substantial violation above classical 2.0
        tolerance: float = 1e-4,
    ):
        self.bell_threshold = bell_threshold
        self.tolerance = tolerance
        self.isolated_sybils: Set[str] = set()

    @classmethod
    def evaluate_ideal_chsh(cls) -> CHSHEvaluationResult:
        """
        Evaluates exact quantum expectation values for maximally entangled Bell state
        |Phi+> = 1/sqrt(2) (|00> + |11>) with optimal measurement settings:
        A0 = Z, A1 = X
        B0 = (Z + X) / sqrt(2), B1 = (Z - X) / sqrt(2).
        Yields <B> = 2*sqrt(2) ~= 2.8284271247.
        """
        # Bell state vector
        phi_plus = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.complex128) / math.sqrt(2.0)

        # Pauli matrices
        sx = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
        sz = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)

        A0 = sz
        A1 = sx
        B0 = (sz + sx) / math.sqrt(2.0)
        B1 = (sz - sx) / math.sqrt(2.0)

        def correlator(A: np.ndarray, B: np.ndarray) -> float:
            op = np.kron(A, B)
            val = float(np.real(phi_plus.conj().T @ op @ phi_plus))
            return val

        e00 = correlator(A0, B0)  # 1/sqrt(2) ~= 0.7071
        e01 = correlator(A0, B1)  # 1/sqrt(2) ~= 0.7071
        e10 = correlator(A1, B0)  # 1/sqrt(2) ~= 0.7071
        e11 = correlator(A1, B1)  # -1/sqrt(2) ~= -0.7071

        bell_s = e00 + e01 + e10 - e11  # 4 * (1/sqrt(2)) = 2*sqrt(2)
        residual = abs(bell_s - TSIRELSON_BOUND)

        return CHSHEvaluationResult(
            correlator_E_A0_B0=e00,
            correlator_E_A0_B1=e01,
            correlator_E_A1_B0=e10,
            correlator_E_A1_B1=e11,
            bell_parameter=bell_s,
            tsirelson_bound=TSIRELSON_BOUND,
            violates_classical_bound=bell_s > CLASSICAL_BELL_BOUND + 1e-6,
            is_maximal_tsirelson=residual < 1e-10,
            residual_to_tsirelson=residual,
        )

    @classmethod
    def evaluate_mermin_operator_expectation(
        cls,
        state_3qubit: np.ndarray,
    ) -> float:
        """
        Evaluates the 3-qubit Mermin operator on |psi>:
        M_3 = X_1 Y_2 Y_3 + Y_1 X_2 Y_3 + Y_1 Y_2 X_3 - X_1 X_2 X_3.
        Maximal quantum eigenvalue on |GHZ_3> is 4.0.
        Classical local hidden variable bound is <= 2.0.
        """
        sx = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
        sy = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)

        m1 = np.kron(sx, np.kron(sy, sy))
        m2 = np.kron(sy, np.kron(sx, sy))
        m3 = np.kron(sy, np.kron(sy, sx))
        m4 = np.kron(sx, np.kron(sx, sx))

        # Mermin polynomial operator with maximal eigenvalue +4.0 on |GHZ_3>:
        # M_3 = X_1 X_2 X_3 - (X_1 Y_2 Y_3 + Y_1 X_2 Y_3 + Y_1 Y_2 X_3)
        M_op = m4 - (m1 + m2 + m3)
        exp_val = float(np.real(state_3qubit.conj().T @ M_op @ state_3qubit))
        return exp_val

    def screen_agent_correlation(
        self,
        agent_id: str,
        reported_bell_parameter: float,
        claims_quantum_priority: bool = True,
    ) -> bool:
        """
        Screens an agent's reported Bell parameter:
        If agent claims quantum priority but reports S <= 2.0 (or below threshold),
        it is classified as a classical sybil attempting counterfeit consensus.
        Returns True if accepted (quantum certified), False if isolated.
        """
        if claims_quantum_priority:
            if reported_bell_parameter <= CLASSICAL_BELL_BOUND + self.tolerance:
                self.isolated_sybils.add(agent_id)
                return False
            if reported_bell_parameter < self.bell_threshold:
                self.isolated_sybils.add(agent_id)
                return False
            if reported_bell_parameter > TSIRELSON_BOUND + self.tolerance:
                # Super-quantum violation (unphysical signaling)
                self.isolated_sybils.add(agent_id)
                return False

        return True

    def generate_consensus_receipt(
        self,
        epoch: int,
        branch_omega: float,
        active_agents: List[str],
        bell_param: float,
        novikov_converged: bool,
        novikov_error: float,
    ) -> QuantumConsensusReceipt:
        """Generates a deterministic cryptographic receipt."""
        # Clean active list excluding isolated sybils
        verified_agents = sorted([a for a in active_agents if a not in self.isolated_sybils])
        sybils = sorted(list(self.isolated_sybils))

        is_bell_valid = (CLASSICAL_BELL_BOUND < bell_param <= TSIRELSON_BOUND + 1e-6)
        decision = "ACCEPT" if (is_bell_valid and novikov_converged and len(verified_agents) > 0) else "REJECT"

        # Deterministic payload serialization
        receipt_payload = {
            "epoch": epoch,
            "branch_omega": round(branch_omega, 6),
            "num_agents": len(verified_agents),
            "active_agents": verified_agents,
            "isolated_sybils": sybils,
            "bell_parameter": round(bell_param, 6),
            "violates_bell_bound": is_bell_valid,
            "novikov_converged": novikov_converged,
            "novikov_error": f"{novikov_error:.4e}",
            "consensus_decision": decision,
        }

        canonical_json = json.dumps(receipt_payload, sort_keys=True)
        merkle_root = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
        receipt_hash = hashlib.sha256(f"DAXDA-QTC:{epoch}:{merkle_root}".encode("utf-8")).hexdigest()

        return QuantumConsensusReceipt(
            epoch=epoch,
            branch_omega=branch_omega,
            num_agents=len(verified_agents),
            active_agents=verified_agents,
            isolated_sybils=sybils,
            bell_parameter=bell_param,
            violates_bell_bound=is_bell_valid,
            novikov_converged=novikov_converged,
            novikov_error=novikov_error,
            consensus_decision=decision,
            merkle_state_root=merkle_root,
            receipt_hash=receipt_hash,
        )
