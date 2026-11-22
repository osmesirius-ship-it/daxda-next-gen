"""DAXDA Heliosphere & Planetary Observer (helios_observer.py).

Autonomous ingestion and enhancement pipeline for live solar, magnetic, and space-weather telemetry.
Coupled with the DAXDA Nicole Protocol and Cl(16,4) Clifford manifold representation.

Includes an embedded zero-dependency local relay server (resolves NASA/NOAA browser CORS blocks)
and background polling daemon.
"""

from __future__ import annotations

import argparse
import http.server
import io
import json
import logging
import math
import os
import sys
import threading
import time
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

logger = logging.getLogger("helios_observer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs" / "helios_telemetry"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "DAXDA-Helios-Observer/2.0 (Nicole Protocol; Autonomous Surveillance)"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class IMFTelemetry:
    timestamp: str
    bt: float
    bx: float
    by: float
    bz: float
    reconnection_active: bool
    reconnection_energy_index: float


@dataclass
class SolarWindTelemetry:
    timestamp: str
    speed_km_s: float
    density_p_cm3: float
    temp_k: float
    dynamic_pressure_npa: float


@dataclass
class SolarFlareTelemetry:
    timestamp: str
    xray_flux: float
    flare_tier: str
    threat_level: str


@dataclass
class GeomagneticState:
    kp_index: float
    storm_category: str
    description: str


@dataclass
class CliffordSpaceWeatherBlade:
    grade_0_scalar: float           # Plasma density + kinetic energy density
    grade_1_vector: Tuple[float, float, float]  # Solar wind velocity vector
    grade_2_bivector: Tuple[float, float, float] # Faraday magnetic flux (Bx, By, Bz)
    grade_3_trivector: float        # Magnetic helicity / flux rope twist index
    manifold_anomaly_norm: float    # Clifford manifold distance from quiescent baseline


# ---------------------------------------------------------------------------
# Network Collectors
# ---------------------------------------------------------------------------

def fetch_json(url: str, timeout: int = 8) -> Optional[Any]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        logger.warning(f"Failed to fetch JSON from {url}: {exc}")
        return None


def fetch_image(url: str, timeout: int = 12) -> Optional[Image.Image]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return Image.open(io.BytesIO(resp.read())).convert("RGB")
    except Exception as exc:
        logger.warning(f"Failed to fetch image from {url}: {exc}")
        return None


def fetch_raw_bytes(url: str, timeout: int = 12) -> Optional[bytes]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as exc:
        logger.warning(f"Failed to fetch raw bytes from {url}: {exc}")
        return None


def poll_space_weather() -> Dict[str, Any]:
    """Collect real-time telemetry from NOAA SWPC."""
    # 1. IMF Magnetometer
    mag_raw = fetch_json("https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json")
    latest_mag = mag_raw[-1] if mag_raw else {}
    bt = float(latest_mag.get("bt", 5.0) or 5.0)
    bx = float(latest_mag.get("bx_gsm", 0.0) or 0.0)
    by = float(latest_mag.get("by_gsm", 0.0) or 0.0)
    bz = float(latest_mag.get("bz_gsm", 0.0) or 0.0)
    
    # 2. Solar Wind Plasma
    wind_raw = fetch_json("https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json")
    latest_wind = wind_raw[-1] if wind_raw else {}
    v_sw = float(latest_wind.get("proton_speed", 350.0) or 350.0)
    n_p = float(latest_wind.get("proton_density", 4.0) or 4.0)
    t_p = float(latest_wind.get("proton_temperature", 80000.0) or 80000.0)
    
    dyn_p = 1.6726e-6 * n_p * (v_sw ** 2)
    reconnection_active = bz < -1.0
    recon_index = max(0.0, -bz) * (v_sw / 1000.0)

    # 3. GOES X-ray flux
    xray_raw = fetch_json("https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json")
    latest_xray = xray_raw[-1] if xray_raw else {}
    flux = float(latest_xray.get("flux", 1e-7) or 1e-7)
    
    if flux >= 1e-4: flare_tier = f"X{flux / 1e-4:.1f}"; flare_threat = "EXTREME_SOLAR_SUPERFLARE"
    elif flux >= 1e-5: flare_tier = f"M{flux / 1e-5:.1f}"; flare_threat = "STRONG_SOLAR_FLARE"
    elif flux >= 1e-6: flare_tier = f"C{flux / 1e-6:.1f}"; flare_threat = "MODERATE_SOLAR_ACTIVITY"
    elif flux >= 1e-7: flare_tier = f"B{flux / 1e-7:.1f}"; flare_threat = "QUIET_SOLAR_BACKGROUND"
    else: flare_tier = f"A{flux / 1e-8:.1f}"; flare_threat = "DEEP_QUIET"

    # 4. Kp Index
    kp_raw = fetch_json("https://services.swpc.noaa.gov/json/planetary_k_index_1m.json")
    latest_kp = kp_raw[-1] if kp_raw else {}
    kp = float(latest_kp.get("kp_index", 1.0) or 1.0)
    
    if kp >= 8: storm_cat = "G4/G5 Extreme Storm"
    elif kp >= 6: storm_cat = "G2/G3 Moderate-Strong Storm"
    elif kp >= 5: storm_cat = "G1 Minor Storm"
    elif kp >= 4: storm_cat = "Unsettled / Active"
    else: storm_cat = "Quiet Geomagnetic Conditions"

    # 5. Clifford Cl(16,4) Multivector State
    energy_density = (bt**2) / (2.0 * 1.2566) + 0.5 * (1.67e-27 * n_p * 1e6) * ((v_sw * 1000.0)**2)
    helicity = abs(bx * by * bz) / max(1.0, bt**2)
    anomaly_norm = math.sqrt(
        ((v_sw - 350.0) / 100.0) ** 2 +
        (max(0.0, -bz) / 2.5) ** 2 +
        (math.log10(max(1e-9, flux)) - (-7.0)) ** 2 +
        ((kp - 1.0) / 1.5) ** 2
    )

    imf = IMFTelemetry(
        timestamp=latest_mag.get("time_tag", time.strftime("%Y-%m-%dT%H:%M:%SZ")),
        bt=round(bt, 2), bx=round(bx, 2), by=round(by, 2), bz=round(bz, 2),
        reconnection_active=reconnection_active, reconnection_energy_index=round(recon_index, 3)
    )

    wind = SolarWindTelemetry(
        timestamp=latest_wind.get("time_tag", time.strftime("%Y-%m-%dT%H:%M:%SZ")),
        speed_km_s=round(v_sw, 1), density_p_cm3=round(n_p, 2), temp_k=round(t_p, 0),
        dynamic_pressure_npa=round(dyn_p, 3)
    )

    flare = SolarFlareTelemetry(
        timestamp=latest_xray.get("time_tag", time.strftime("%Y-%m-%dT%H:%M:%SZ")),
        xray_flux=flux, flare_tier=flare_tier, threat_level=flare_threat
    )

    geo = GeomagneticState(
        kp_index=kp, storm_category=storm_cat,
        description=f"Planetary geomagnetic index Kp={kp:.1f} ({storm_cat})"
    )

    blade = CliffordSpaceWeatherBlade(
        grade_0_scalar=round(energy_density, 4),
        grade_1_vector=(round(v_sw, 1), 0.0, 0.0),
        grade_2_bivector=(round(bx, 2), round(by, 2), round(bz, 2)),
        grade_3_trivector=round(helicity, 4),
        manifold_anomaly_norm=round(anomaly_norm, 3)
    )

    return {
        "imf": asdict(imf),
        "solar_wind": asdict(wind),
        "solar_flare": asdict(flare),
        "geomagnetic": asdict(geo),
        "clifford_manifold": asdict(blade),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }


# ---------------------------------------------------------------------------
# Image Enhancement Algorithms
# ---------------------------------------------------------------------------

def enhance_sdo_171(img: Image.Image) -> Image.Image:
    """Enhance SDO 171Å: sharpen coronal loops, boost magnetic filaments."""
    sharpened = img.filter(ImageFilter.UnsharpMask(radius=3, percent=220, threshold=2))
    contrast = ImageEnhance.Contrast(sharpened).enhance(1.6)
    edges = img.convert("L").filter(ImageFilter.FIND_EDGES)
    edges_colored = ImageOps.colorize(edges, black="#000000", white="#00ffff")
    return Image.blend(contrast, edges_colored, alpha=0.30)


def enhance_sdo_magnetogram(img: Image.Image) -> Image.Image:
    """Transform grayscale HMI magnetogram into high-contrast bipolar false-color."""
    gray = img.convert("L")
    arr = np.array(gray, dtype=np.float32)
    delta = arr - 128.0
    boosted = np.sign(delta) * (np.abs(delta) ** 0.8) * 3.2
    boosted = np.clip(boosted, -128, 127)

    rgb = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
    disk_mask = arr > 5
    rgb[disk_mask, :] = [18, 22, 28]

    pos_mask = boosted > 12
    rgb[pos_mask, 0] = np.clip(boosted[pos_mask] * 2.2, 90, 255).astype(np.uint8)
    rgb[pos_mask, 1] = np.clip(boosted[pos_mask] * 0.7, 20, 140).astype(np.uint8)
    rgb[pos_mask, 2] = 20

    neg_mask = boosted < -12
    rgb[neg_mask, 2] = np.clip(-boosted[neg_mask] * 2.2, 90, 255).astype(np.uint8)
    rgb[neg_mask, 1] = np.clip(-boosted[neg_mask] * 1.3, 30, 210).astype(np.uint8)
    rgb[neg_mask, 0] = 20

    return Image.fromarray(rgb)


def enhance_soho_coronagraph(img: Image.Image) -> Image.Image:
    """Enhance SOHO LASCO C2: expand dynamic range for CME shock fronts."""
    arr = np.array(img.convert("L"), dtype=np.float32)
    norm = arr / 255.0
    stretched = np.power(norm, 0.6) * 255.0
    stretched = np.clip(stretched, 0, 255).astype(np.uint8)
    
    cme_img = Image.fromarray(stretched)
    cme_contrast = ImageEnhance.Contrast(cme_img).enhance(1.8)
    return ImageOps.colorize(cme_contrast, black="#0a0518", mid="#c85020", white="#ffffff")


# ---------------------------------------------------------------------------
# Pipeline Execution & Feed Downlink
# ---------------------------------------------------------------------------

ALL_FEEDS = {
    "sdo_171": {
        "url": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_0171.jpg",
        "raw_file": "raw_sdo_171.jpg",
        "enhancer": enhance_sdo_171,
        "enhanced_file": "enhanced_sdo_171_loops.jpg"
    },
    "sdo_hmi": {
        "url": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_HMIB.jpg",
        "raw_file": "raw_sdo_hmi.jpg",
        "enhancer": enhance_sdo_magnetogram,
        "enhanced_file": "enhanced_sdo_magnetogram.jpg"
    },
    "sdo_193": {
        "url": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_0193.jpg",
        "raw_file": "raw_sdo_193.jpg",
        "enhancer": None,
        "enhanced_file": None
    },
    "soho_c2": {
        "url": "https://soho.nascom.nasa.gov/data/realtime/c2/512/latest.jpg",
        "raw_file": "raw_soho_c2.jpg",
        "enhancer": enhance_soho_coronagraph,
        "enhanced_file": "enhanced_soho_lasco_c2.jpg"
    },
    "noaa_aurora": {
        "url": "https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg",
        "raw_file": "raw_noaa_aurora.jpg",
        "enhancer": None,
        "enhanced_file": None
    }
}


def run_pipeline() -> Dict[str, Any]:
    logger.info("Polling live space-weather telemetry...")
    telemetry = poll_space_weather()

    processed_images = {}
    for key, feed in ALL_FEEDS.items():
        try:
            raw_bytes = fetch_raw_bytes(feed["url"])
            if raw_bytes:
                raw_path = OUTPUT_DIR / feed["raw_file"]
                raw_path.write_bytes(raw_bytes)
                processed_images[key] = {"status": "OK", "local_raw": feed["raw_file"]}

                # If an enhancer is defined, compute the enhanced version
                if feed["enhancer"] and feed["enhanced_file"]:
                    img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
                    enhanced = feed["enhancer"](img)
                    enh_path = OUTPUT_DIR / feed["enhanced_file"]
                    enhanced.save(enh_path, quality=92)
                    processed_images[key]["local_enhanced"] = feed["enhanced_file"]
            else:
                processed_images[key] = {"status": "FETCH_FAILED"}
        except Exception as e:
            logger.warning(f"Error processing {key}: {e}")
            processed_images[key] = {"status": f"ERROR: {e}"}

    telemetry["imagery"] = processed_images

    # Save state
    state_file = OUTPUT_DIR / "helios_live_state.json"
    with open(state_file, "w") as fh:
        json.dump(telemetry, fh, indent=2)

    logger.info("Pipeline update complete.")
    return telemetry


# ---------------------------------------------------------------------------
# Local Relay Server (Resolves CORS & Local File Security Blocks)
# ---------------------------------------------------------------------------

class HeliosRelayHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def end_headers(self):
        # Enable CORS for all local requests
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_GET(self):
        # Direct root or /cockpit to helios_observer_cockpit.html
        if self.path in ("/", "/cockpit", "/cockpit/"):
            self.path = "/helios_observer_cockpit.html"
        return super().do_GET()


def start_server(port: int = 8080):
    # Run background updater thread
    def bg_worker():
        while True:
            try:
                run_pipeline()
            except Exception as exc:
                logger.error(f"Background worker error: {exc}")
            time.sleep(60)

    t = threading.Thread(target=bg_worker, daemon=True)
    t.start()

    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), HeliosRelayHandler)
    logger.info(f"★ DAXDA Heliosphere Cockpit Server live at: http://localhost:{port}/cockpit")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server.")
        server.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DAXDA Helios Observer")
    parser.add_argument("--serve", action="store_true", help="Start local relay server & background poller")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    args = parser.parse_args()

    # Always do an initial run
    run_pipeline()

    if args.serve:
        start_server(port=args.port)
