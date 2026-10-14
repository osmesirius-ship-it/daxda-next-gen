"""
DAXDA BioForge VR: Core Medical Discoveries Engine
===================================================
Models the authentic DAXDA medical discoveries documented in the repository:
1. Multiple Sclerosis (MS) Axon Remyelination (GPR17 / CN045 / EBV Nullification)
2. Bioelectric Cellular Regeneration Chamber (V_mem Reversal & 670nm ATP Boost)
3. Neuro-fMRI 360-Cortical Connectome Synchronization (Double-Gamma HRF & CKA)
4. Riemannian BCI Motor Recovery (S_d++ Covariance Manifold & Karcher Flow)
5. Quantum Psychometrics & Cognitive Equilibrium (Wang-Busemeyer QQ Invariant)

Provides procedural state machines, interactive bio-entities, and validation logic
for hands-first spatial VR execution.
"""

from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

class MedicalDiscoveryId(str, Enum):
    MS_REMYELINATION = "MS_REMYELINATION"
    CELLULAR_REGEN_BED = "CELLULAR_REGEN_BED"
    NEURO_FMRI_CONNECTOME = "NEURO_FMRI_CONNECTOME"
    RIEMANNIAN_BCI_RECOVERY = "RIEMANNIAN_BCI_RECOVERY"
    QUANTUM_PSYCHOMETRICS = "QUANTUM_PSYCHOMETRICS"

@dataclass
class MedicalDiscoveryMetadata:
    discovery_id: MedicalDiscoveryId
    name: str
    target_condition: str
    scientific_mechanism: str
    primary_molecule_or_hardware: str
    biological_action_summary: str
    target_metric_label: str
    baseline_metric_val: float
    target_metric_val: float
    unit: str

DISCOVERY_CATALOG: Dict[MedicalDiscoveryId, MedicalDiscoveryMetadata] = {
    MedicalDiscoveryId.MS_REMYELINATION: MedicalDiscoveryMetadata(
        discovery_id=MedicalDiscoveryId.MS_REMYELINATION,
        name="Multiple Sclerosis Remyelination",
        target_condition="Demyelination & EBV-Induced T-Cell Inflammation",
        scientific_mechanism="Cl(16,4) geometric phase-shift binding CN045 to GPR17 receptor, triggering OPC differentiation",
        primary_molecule_or_hardware="CN045 Maturation Ligand & GPR17 Antagonist",
        biological_action_summary="Binds GPR17 receptor pocket, nullifies EBV inflammatory cascade, and wraps myelin sheath around axon",
        target_metric_label="Nerve Conduction Velocity",
        baseline_metric_val=12.4,
        target_metric_val=118.5,
        unit="m/s"
    ),
    MedicalDiscoveryId.CELLULAR_REGEN_BED: MedicalDiscoveryMetadata(
        discovery_id=MedicalDiscoveryId.CELLULAR_REGEN_BED,
        name="Cellular Regeneration Chamber",
        target_condition="Tissue Senescence & Bioelectric Decoherence",
        scientific_mechanism="Phase-conjugate RF destructive interference on senescent cells + 670nm NIR Cytochrome C Oxidase activation",
        primary_molecule_or_hardware="128-Channel SQUID Bioelectric Array & 670nm VECSEL NIR Diodes",
        biological_action_summary="Scans resting membrane potential (V_mem), triggers apoptosis in high-entropy senescent cells, and accelerates mitochondrial ATP +400%",
        target_metric_label="Intracellular ATP Output",
        baseline_metric_val=100.0,
        target_metric_val=485.0,
        unit="pmol/cell"
    ),
    MedicalDiscoveryId.NEURO_FMRI_CONNECTOME: MedicalDiscoveryMetadata(
        discovery_id=MedicalDiscoveryId.NEURO_FMRI_CONNECTOME,
        name="360-Parcel Neuro-fMRI Alignment",
        target_condition="Cognitive Desynchronization & Hemodynamic Lag",
        scientific_mechanism="Double-gamma Hemodynamic Response Function (HRF) deconvolution and Centered Kernel Alignment (CKA)",
        primary_molecule_or_hardware="7T fMRI Cortical Connectome & CKA HSIC Kernel",
        biological_action_summary="Aligns neural timecourses across all 360 Glasser cortical parcels to restore inter-hemispheric phase coupling",
        target_metric_label="Representational Similarity (CKA)",
        baseline_metric_val=0.42,
        target_metric_val=0.98,
        unit="CKA Score"
    ),
    MedicalDiscoveryId.RIEMANNIAN_BCI_RECOVERY: MedicalDiscoveryMetadata(
        discovery_id=MedicalDiscoveryId.RIEMANNIAN_BCI_RECOVERY,
        name="Riemannian BCI Motor Recovery",
        target_condition="Post-Stroke Motor Cortex Hemiparesis",
        scientific_mechanism="Affine-Invariant Riemannian Metric (AIRM) on S_d++ manifold with Fréchet geometric mean Karcher flow",
        primary_molecule_or_hardware="64-Channel EEG Covariance Array & Riemannian Tangent Projector",
        biological_action_summary="Aligns covariance matrices on curved SPD manifold to lock sensorimotor mu-rhythm (10Hz) and induce neuroplasticity",
        target_metric_label="Mu-Rhythm Sensorimotor Coherence",
        baseline_metric_val=0.28,
        target_metric_val=0.94,
        unit="Coherence Index"
    ),
    MedicalDiscoveryId.QUANTUM_PSYCHOMETRICS: MedicalDiscoveryMetadata(
        discovery_id=MedicalDiscoveryId.QUANTUM_PSYCHOMETRICS,
        name="Quantum Psychometric Equilibrium",
        target_condition="Severe PTSD & Cognitive Order Bias Decoherence",
        scientific_mechanism="Density matrix rho in D(H) with Lüders state projection verifying Wang-Busemeyer QQ-equality invariant",
        primary_molecule_or_hardware="Quantum Density Matrix Operator & Tomographic Bloch Projector",
        biological_action_summary="Reorients measurement projection axes to nullify cognitive order bias (q_diff < 1e-15) and stabilize mental state",
        target_metric_label="Wang-Busemeyer QQ Invariant Delta",
        baseline_metric_val=0.384,
        target_metric_val=0.000,
        unit="q_diff Error"
    )
}

@dataclass
class BioInteractiveEntity:
    entity_id: str
    name: str
    entity_type: str  # 'molecule', 'receptor', 'laser_node', 'cell', 'neural_parcel', 'density_vector'
    position: Tuple[float, float, float]
    target_socket: Optional[Tuple[float, float, float]] = None
    is_docked: bool = False
    is_held: bool = False
    charge: float = 1.0

class MedicalDiscoveryProcedure:
    """
    Simulates the interactive, hands-first execution of a selected DAXDA medical discovery.
    """
    def __init__(self, discovery_id: MedicalDiscoveryId):
        self.metadata = DISCOVERY_CATALOG[discovery_id]
        self.discovery_id = discovery_id
        self.progress: float = 0.0  # 0.0 to 1.0 (100% completed)
        self.current_metric_val: float = self.metadata.baseline_metric_val
        self.is_completed: bool = False
        self.entities: Dict[str, BioInteractiveEntity] = {}
        self.log_messages: List[str] = []
        self._init_procedure()

    def _init_procedure(self):
        cx, cy, cz = (0.0, 1.05, -0.38)  # Seated 0.60m desk center

        if self.discovery_id == MedicalDiscoveryId.MS_REMYELINATION:
            # Axon receptor + CN045 ligand
            self.entities["gpr17_receptor"] = BioInteractiveEntity(
                "gpr17_receptor", "GPR17 Receptor Pocket", "receptor",
                (cx, cy, cz), target_socket=(cx, cy, cz), is_docked=True
            )
            self.entities["cn045_ligand"] = BioInteractiveEntity(
                "cn045_ligand", "CN045 Maturation Ligand", "molecule",
                (cx - 0.14, cy - 0.05, cz + 0.08), target_socket=(cx, cy, cz)
            )
            self.log_messages.append("Axon demyelination detected. Grasp CN045 ligand and dock into GPR17 receptor pocket.")

        elif self.discovery_id == MedicalDiscoveryId.CELLULAR_REGEN_BED:
            # Senescent cell cluster + NIR 670nm diode
            self.entities["senescent_cell"] = BioInteractiveEntity(
                "senescent_cell", "High-Entropy Senescent Cell", "cell",
                (cx - 0.06, cy, cz), target_socket=(cx - 0.06, cy, cz), is_docked=True
            )
            self.entities["nir_laser_670nm"] = BioInteractiveEntity(
                "nir_laser_670nm", "670nm VECSEL Photobiomodulator", "laser_node",
                (cx + 0.14, cy - 0.04, cz + 0.06), target_socket=(cx - 0.06, cy, cz)
            )
            self.log_messages.append("Bioelectric V_mem decoherence detected. Aim 670nm NIR laser to energize mitochondria.")

        elif self.discovery_id == MedicalDiscoveryId.NEURO_FMRI_CONNECTOME:
            # Left & Right hemisphere cortical parcels
            self.entities["left_parcel"] = BioInteractiveEntity(
                "left_parcel", "Glasser Left Broca Parcel (Area 44)", "neural_parcel",
                (cx - 0.09, cy + 0.04, cz), target_socket=(cx, cy, cz)
            )
            self.entities["right_parcel"] = BioInteractiveEntity(
                "right_parcel", "Glasser Right Homologue Parcel", "neural_parcel",
                (cx + 0.09, cy + 0.04, cz), target_socket=(cx, cy, cz)
            )
            self.log_messages.append("Hemodynamic delay detected across 360 parcels. Align parcels with dual-hand pinch.")

        elif self.discovery_id == MedicalDiscoveryId.RIEMANNIAN_BCI_RECOVERY:
            # Covariance matrix on SPD manifold
            self.entities["covariance_state"] = BioInteractiveEntity(
                "covariance_state", "Deviant Covariance Matrix (Sensorimotor)", "density_vector",
                (cx + 0.12, cy - 0.06, cz + 0.06), target_socket=(cx, cy, cz)
            )
            self.log_messages.append("Stroke motor impairment. Pull covariance state to Fréchet geometric mean on S_d++.")

        elif self.discovery_id == MedicalDiscoveryId.QUANTUM_PSYCHOMETRICS:
            # Quantum density operator
            self.entities["bloch_state"] = BioInteractiveEntity(
                "bloch_state", "Decoherent Density Matrix State rho", "density_vector",
                (cx - 0.12, cy + 0.06, cz + 0.06), target_socket=(cx, cy, cz)
            )
            self.log_messages.append("Cognitive context order bias detected. Rotate projection axes to satisfy Wang-Busemeyer QQ invariant.")

    def interact_pinch_entity(self, hand_pos: Tuple[float, float, float], grab_radius: float = 0.065) -> Optional[str]:
        hx, hy, hz = hand_pos
        for e_id, ent in self.entities.items():
            if not ent.is_docked:
                ex, ey, ez = ent.position
                dist = math.sqrt((hx - ex)**2 + (hy - ey)**2 + (hz - ez)**2)
                if dist <= grab_radius:
                    ent.is_held = True
                    return e_id
        return None

    def update_held_entity(self, entity_id: str, new_pos: Tuple[float, float, float]):
        if entity_id in self.entities:
            self.entities[entity_id].position = new_pos

    def release_entity(self, entity_id: str, snap_dist: float = 0.06) -> bool:
        if entity_id not in self.entities:
            return False
        ent = self.entities[entity_id]
        ent.is_held = False

        if ent.target_socket:
            tx, ty, tz = ent.target_socket
            ex, ey, ez = ent.position
            dist = math.sqrt((ex - tx)**2 + (ey - ty)**2 + (ez - tz)**2)
            if dist <= snap_dist:
                # Snap into target receptor / alignment zone!
                ent.position = ent.target_socket
                ent.is_docked = True
                self._advance_progress(0.60)
                self.log_messages.append(f"Successfully docked {ent.name} into biological target!")
                return True
        return False

    def apply_wrist_dial_modulation(self, angle_delta_rad: float):
        """
        Wrist dial rotation applies phase tuning, frequency adjustments, or optical laser focus.
        """
        step = abs(angle_delta_rad) * 0.4
        self._advance_progress(step)

    def _advance_progress(self, amount: float):
        self.progress = min(1.0, self.progress + amount)
        # Interpolate metric value toward target
        t = self.progress
        b_val = self.metadata.baseline_metric_val
        t_val = self.metadata.target_metric_val
        self.current_metric_val = b_val + (t_val - b_val) * t

        if self.progress >= 0.999:
            self.is_completed = True
            self.current_metric_val = t_val
            self.log_messages.append(f"Medical Discovery Procedure Successful: {self.metadata.name} fully calibrated!")

    def export_state_json(self) -> Dict:
        return {
            "discovery_id": self.discovery_id.value,
            "name": self.metadata.name,
            "target_condition": self.metadata.target_condition,
            "scientific_mechanism": self.metadata.scientific_mechanism,
            "progress": round(self.progress, 3),
            "is_completed": self.is_completed,
            "metric_label": self.metadata.target_metric_label,
            "current_metric_val": round(self.current_metric_val, 2),
            "target_metric_val": self.metadata.target_metric_val,
            "unit": self.metadata.unit,
            "entities": {
                e_id: {
                    "name": e.name,
                    "pos": e.position,
                    "is_docked": e.is_docked,
                    "is_held": e.is_held
                }
                for e_id, e in self.entities.items()
            },
            "latest_log": self.log_messages[-1] if self.log_messages else ""
        }
