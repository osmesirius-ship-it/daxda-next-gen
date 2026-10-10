from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Ensure package root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from daxda_engine.cl16_4.recursive_self_improvement import run_recursive_self_improvement

app = FastAPI(
    title="DAXDA Next-Gen Cl(16,4) Engine",
    description="Autonomous Geometric AGI Containment Node",
    version="12.0.1-GOVERNED"
)

class EngineResponse(BaseModel):
    status: str
    cycle_timestamp: str
    passed_proposals: int
    blocked_proposals: int
    cycle_duration_ms: float

@app.get("/")
def read_root():
    return {"message": "DAXDA Cl(16,4) Engine Online. Use /run-cycle to execute the Recursive Self-Improvement loop."}

@app.post("/run-cycle", response_model=EngineResponse)
def execute_cycle():
    try:
        report = run_recursive_self_improvement()
        return {
            "status": "SUCCESS",
            "cycle_timestamp": report["cycle_timestamp"],
            "passed_proposals": report["passed_proposals"],
            "blocked_proposals": report["blocked_proposals"],
            "cycle_duration_ms": report["cycle_duration_ms"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from daxda_engine.waveforms import (
    AcousticWaveformAnalyzer,
    CrossModalTransformer,
    GeometricWaveformBridge,
    ImageWavefieldTransformer,
)
import base64
import numpy as np

class AudioTransformRequest(BaseModel):
    audio_base64: Optional[str] = None
    sample_rate: int = 22050

class ImageTransformRequest(BaseModel):
    image_base64: Optional[str] = None
    duration_sec: float = 3.0

class ResonanceRequest(BaseModel):
    audio_base64: Optional[str] = None
    image_base64: Optional[str] = None

@app.get("/waveforms/status")
def waveform_status():
    return {
        "status": "ONLINE",
        "subsystem": "DAXDA SOTA Multimodal Waveform Engine",
        "transforms": ["Hilbert Analytic Signal", "Morlet CWT", "STFT & Mel Filterbanks", "2D Gabor Wavefields", "Chladni Plate Cymatics", "Bidirectional Optical Sonification"],
        "cl16_4_grounding": "ACTIVE"
    }

@app.post("/waveforms/transform-audio")
def transform_audio(req: AudioTransformRequest):
    try:
        analyzer = AcousticWaveformAnalyzer(sample_rate=req.sample_rate)
        bridge = GeometricWaveformBridge(sample_rate=req.sample_rate)
        
        if req.audio_base64:
            raw_bytes = base64.b64decode(req.audio_base64)
            sr, samples = analyzer.load_audio(raw_bytes)
        else:
            # Synthetic 440Hz test tone if no audio payload
            sr = req.sample_rate
            t = np.linspace(0, 1.0, sr, endpoint=False)
            samples = (0.5 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)
            
        analytic = analyzer.compute_analytic_signal(samples, sample_rate=sr)
        stft = analyzer.compute_stft(samples, sample_rate=sr)
        blades = bridge.project_audio_to_blades(stft, analytic)
        
        return {
            "status": "SUCCESS",
            "sample_rate": sr,
            "duration_sec": round(len(samples) / sr, 3),
            "instantaneous_f0_mean_hz": round(float(np.mean(analytic.instantaneous_freq)), 2),
            "spectral_centroid_mean_hz": round(float(np.mean(stft.spectral_centroid)), 2),
            "cl16_4_blades": blades
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/waveforms/transform-image")
def transform_image(req: ImageTransformRequest):
    try:
        cross_modal = CrossModalTransformer()
        img_trans = ImageWavefieldTransformer()
        
        if req.image_base64:
            raw_bytes = base64.b64decode(req.image_base64)
            img_mat = img_trans.load_image_matrix(raw_bytes)
        else:
            # Synthetic test matrix
            y, x = np.mgrid[:128, :128]
            img_mat = 0.5 * (1.0 + np.sin(x / 8.0) * np.cos(y / 8.0))
            
        spatial = img_trans.image_to_spatial_wavefield(img_mat)
        wav_bytes = cross_modal.image_to_wav_bytes(img_mat, duration_sec=req.duration_sec)
        wav_b64 = base64.b64encode(wav_bytes).decode("ascii")
        
        return {
            "status": "SUCCESS",
            "spatial_entropy": round(spatial.spatial_entropy, 4),
            "resolution": list(spatial.resolution),
            "sonified_wav_base64_length": len(wav_b64),
            "sonified_wav_base64": wav_b64[:200] + "..."  # preview
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/waveforms/cross-modal-resonate")
def cross_modal_resonate(req: ResonanceRequest):
    try:
        bridge = GeometricWaveformBridge()
        analyzer = AcousticWaveformAnalyzer()
        img_trans = ImageWavefieldTransformer()
        
        if req.audio_base64:
            _, audio_samples = analyzer.load_audio(base64.b64decode(req.audio_base64))
        else:
            t = np.linspace(0, 1.0, 22050, endpoint=False)
            audio_samples = (0.5 * np.sin(2 * np.pi * 330.0 * t)).astype(np.float32)
            
        if req.image_base64:
            img_mat = img_trans.load_image_matrix(base64.b64decode(req.image_base64))
        else:
            img_mat = np.ones((128, 128), dtype=np.float32) * 0.5
            
        res = bridge.compute_multimodal_resonance(audio_samples, img_mat)
        return {
            "status": "SUCCESS",
            "nci": res.nci,
            "cpc": res.cpc,
            "faf": res.faf,
            "cl16_4_blades": res.blade_channels,
            "adversarial_flag": res.adversarial_anomaly
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
