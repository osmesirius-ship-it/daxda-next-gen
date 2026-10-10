"""
DAXDA Next-Gen State-of-the-Art Waveform & Multimodal Resonance Package.
Provides high-fidelity acoustic DSP, 2D spatial wavefields, cymatic Chladni resonance,
bidirectional image <-> audio sonification, Clifford Cl(16,4) blade projection,
and audio-reactive video rendering.
"""

from .waveform_dsp import AcousticWaveformAnalyzer, AnalyticSignalResult, CWTResult, STFTResult
from .image_wavefield import ImageWavefieldTransformer, SpatialWavefieldResult, GaborEnergyField
from .cross_modal_sonification import CrossModalTransformer
from .multivector_bridge import GeometricWaveformBridge, ResonanceMetrics
from .visualizer_renderer import WaveformVideoRenderer

__all__ = [
    "AcousticWaveformAnalyzer",
    "AnalyticSignalResult",
    "CWTResult",
    "STFTResult",
    "ImageWavefieldTransformer",
    "SpatialWavefieldResult",
    "GaborEnergyField",
    "CrossModalTransformer",
    "GeometricWaveformBridge",
    "ResonanceMetrics",
    "WaveformVideoRenderer",
]
