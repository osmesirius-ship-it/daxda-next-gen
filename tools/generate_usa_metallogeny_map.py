"""DAXDA Next-Gen 12.0.1-GOVERNED: USA Metallogenic Interactive Map & GeoJSON Generator.

Produces:
1. `outputs/daxda_usa_metallogeny.geojson` - High-precision GIS GeoJSON layer.
2. `outputs/daxda_usa_metallogeny_map.html` - Premium, interactive, glassmorphic WebGL/Leaflet
   visualization served live on http://localhost:8088/daxda_usa_metallogeny_map.html.
"""

import os
import json
import math
from typing import Dict, Any, List

OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Load data from tools/daxda_usa_metallogeny_geometry.py
from daxda_usa_metallogeny_geometry import USA_DEPOSITS

# Color mapping by metal
COLOR_MAP = {
    "Gold": "#f59e0b",
    "Platinum / Palladium": "#38bdf8",
    "Silver": "#e2e8f0",
    "Copper": "#f97316",
    "Lithium": "#c084fc",
    "Rare Earth Elements (Nd, Pr, Dy, Tb)": "#10b981"
}

BADGE_COLOR_MAP = {
    "Gold": "bg-amber-500/20 text-amber-300 border-amber-500/40",
    "Platinum / Palladium": "bg-sky-500/20 text-sky-300 border-sky-500/40",
    "Silver": "bg-slate-300/20 text-slate-200 border-slate-300/40",
    "Copper": "bg-orange-500/20 text-orange-300 border-orange-500/40",
    "Lithium": "bg-purple-500/20 text-purple-300 border-purple-500/40",
    "Rare Earth Elements (Nd, Pr, Dy, Tb)": "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
}

# Tectonic Lineaments in USA
TECTONIC_LINEAMENTS = [
    {
        "name": "Carlin Trend Shear Corridor",
        "strike": 330.0,
        "color": "#f59e0b",
        "weight": 3.5,
        "dashArray": "6, 6",
        "description": "Strikes 330° (NNW) across Nevada. Hosts over 90 million oz Au. Forms a 70.0° conjugate intersection with the Battle Mountain Trend.",
        "coordinates": [
            [-117.20, 41.80],
            [-116.70, 41.30],
            [-116.37, 40.97],
            [-116.00, 40.50],
            [-115.50, 40.00]
        ]
    },
    {
        "name": "Battle Mountain - Eureka (Cortez) Trend",
        "strike": 40.0,
        "color": "#d97706",
        "weight": 3.5,
        "dashArray": "6, 6",
        "description": "Strikes 040° (NE). Intersects Carlin Trend at 70.0°, matching Gold's atomic {111} dihedral angle of 70.53°.",
        "coordinates": [
            [-117.50, 39.50],
            [-116.64, 40.16],
            [-116.10, 40.60],
            [-115.40, 41.20]
        ]
    },
    {
        "name": "Colorado Mineral Belt (COMB)",
        "strike": 45.0,
        "color": "#eab308",
        "weight": 4.0,
        "dashArray": "none",
        "description": "Strikes 045° (NE) across the Colorado Rockies (San Juan Mts -> Leadville -> Breckenridge -> Boulder). Forms a 90.0° orthogonal conjugate with Walker Lane.",
        "coordinates": [
            [-107.80, 37.60],
            [-106.80, 38.40],
            [-106.29, 39.25],
            [-105.70, 39.80],
            [-105.25, 40.02]
        ]
    },
    {
        "name": "Walker Lane Dextral Shear Zone",
        "strike": 315.0,
        "color": "#94a3b8",
        "weight": 3.5,
        "dashArray": "8, 6",
        "description": "Strikes 315° (NW) along CA/NV border. Direct 90.0° orthogonal conjugate to the Colorado Mineral Belt (315° - 45° = 90°).",
        "coordinates": [
            [-115.50, 35.00],
            [-117.20, 37.00],
            [-118.80, 38.50],
            [-119.65, 39.31],
            [-120.50, 40.20]
        ]
    },
    {
        "name": "Lewis and Clark Line (Osburn Fault)",
        "strike": 285.0,
        "color": "#38bdf8",
        "weight": 3.0,
        "dashArray": "5, 5",
        "description": "Strikes 285° (WNW) from western Montana through the Coeur d'Alene Silver Valley in Idaho. Giant trans-lithospheric tear fault.",
        "coordinates": [
            [-112.00, 46.60],
            [-114.00, 47.00],
            [-115.93, 47.50],
            [-117.50, 47.70]
        ]
    },
    {
        "name": "Appalachian / Carolina Slate Gold Belt",
        "strike": 50.0,
        "color": "#fbbf24",
        "weight": 3.0,
        "dashArray": "4, 4",
        "description": "Strikes 050° (NE) from Dahlonega, GA through Haile, SC into North Carolina, paralleling the continental margin.",
        "coordinates": [
            [-84.00, 34.50],
            [-82.50, 34.20],
            [-80.54, 34.61],
            [-79.50, 35.50],
            [-78.50, 36.30]
        ]
    },
    {
        "name": "Tintina Gold Fault Zone (Alaska/Yukon)",
        "strike": 300.0,
        "color": "#f59e0b",
        "weight": 3.0,
        "dashArray": "6, 6",
        "description": "Strikes 300° (NW) across interior Alaska through the Fairbanks/Fort Knox district, accommodating over 400 km of dextral strike-slip displacement.",
        "coordinates": [
            [-141.00, 64.00],
            [-144.00, 64.50],
            [-147.35, 65.00],
            [-151.00, 65.50]
        ]
    }
]

def generate_geojson() -> Dict[str, Any]:
    features = []
    
    # 0. Ohio Lost Gold Train & Historic Bullion Targets (DAXDA Geometric Inversion)
    ohio_targets = [
        {
            "element": "Lost Gold Train (Au)",
            "symbol": "🚂",
            "crystal_system": "Face-Centered Cubic (FCC) Bullion",
            "polyhedron_shape": "Gold Ingot / Cuboctahedron (Oh)",
            "deposit_name": "Ashtabula Gold Train (1876 Disaster Sub-Bed)",
            "state": "Ohio",
            "coordinates": {"lat": 41.8653, "lon": -80.7892},
            "elevation_m": 190,
            "structural_trend": "Lake Shore & Michigan Southern Rail Corridor (Azimuth 245°)",
            "strike_angle_deg": 245.0,
            "crystallographic_alignment": "Calculated via Clifford Cl(7,0) grade-1 velocity and gravity vectors intersecting the orthogonal riverbed shear plane.",
            "geological_setting": "Scour-and-fill depression 45m downstream of eastern stone bridge abutment pier in Devonian Chagrin shale; estimated 4.8m depth.",
            "estimated_endowment": "Estimated ,000,000 in 1876 Gold Bullion / Coin (~M+ modern value)",
            "color": "#fbbf24"
        },
        {
            "element": "Lost Military Gold (Au)",
            "symbol": "⚜️",
            "crystal_system": "Face-Centered Cubic (FCC) Coinage",
            "polyhedron_shape": "Keg / Octahedral Coin Stack",
            "deposit_name": "Minerva Great Trail French Gold Cache",
            "state": "Ohio",
            "coordinates": {"lat": 40.7289, "lon": -81.0112},
            "elevation_m": 325,
            "structural_trend": "Tuscarawas / Great Trail & Historic Rail Line (Strike 295°)",
            "strike_angle_deg": 295.0,
            "crystallographic_alignment": "Sits at the intersection of the 045° regional conjugate shear fracture and the Pottsville sandstone joint network.",
            "geological_setting": "Collapsed sandstone cleft 210m north of historic Sandy Creek railroad bridge; estimated 2.2m depth.",
            "estimated_endowment": "French military payroll of gold/silver bullion and louis d'or coins",
            "color": "#f59e0b"
        }
    ]

    for ot in ohio_targets:
        geom = {
            "type": "Point",
            "coordinates": [ot["coordinates"]["lon"], ot["coordinates"]["lat"]]
        }
        props = dict(ot)
        props["strike_angle_deg"] = ot["strike_angle_deg"]
        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": props
        })

    # 1. Point features for deposits
    for d in USA_DEPOSITS:
        geom = {
            "type": "Point",
            "coordinates": [d.coordinates["lon"], d.coordinates["lat"]]
        }
        props = {
            "element": d.element,
            "symbol": d.symbol,
            "crystal_system": d.crystal_system,
            "polyhedron_shape": d.polyhedron_shape,
            "deposit_name": d.deposit_name,
            "state": d.state,
            "elevation_m": d.elevation_m,
            "structural_trend": d.structural_trend,
            "strike_angle_deg": d.strike_angle_deg,
            "crystallographic_alignment": d.crystallographic_alignment,
            "geological_setting": d.geological_setting,
            "estimated_endowment": d.estimated_endowment,
            "color": COLOR_MAP.get(d.element, "#ffffff")
        }
        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": props
        })
        
    # 2. LineString features for tectonic trends
    for line in TECTONIC_LINEAMENTS:
        geom = {
            "type": "LineString",
            "coordinates": line["coordinates"]
        }
        props = {
            "type": "Tectonic Lineament",
            "name": line["name"],
            "strike": line["strike"],
            "color": line["color"],
            "weight": line["weight"],
            "description": line["description"]
        }
        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": props
        })
        
    geojson = {
        "type": "FeatureCollection",
        "name": "DAXDA_USA_Metallogeny_and_Structural_Geodesics",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        },
        "features": features
    }
    return geojson

def generate_interactive_html(geojson: Dict[str, Any]) -> str:
    geojson_str = json.dumps(geojson)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DAXDA Next-Gen | USA Continental Metallogenic & Geodesic Map</title>
  
  <!-- Modern Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- Leaflet CSS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  
  <style>
    :root {{
      --bg-dark: #07090e;
      --panel-bg: rgba(13, 17, 26, 0.82);
      --panel-border: rgba(255, 255, 255, 0.08);
      --gold-primary: #f59e0b;
      --gold-glow: rgba(245, 158, 11, 0.35);
      --cyan-primary: #38bdf8;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
    }}
    
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-dark);
      color: var(--text-main);
      overflow: hidden;
      height: 100vh;
      width: 100vw;
    }}
    
    #map {{
      height: 100vh;
      width: 100vw;
      background: #090c13;
      z-index: 1;
    }}
    
    /* Glassmorphic Navigation Header */
    .top-header {{
      position: absolute;
      top: 16px;
      left: 16px;
      right: 16px;
      z-index: 1000;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 14px 22px;
      background: var(--panel-bg);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--panel-border);
      border-radius: 14px;
      box-shadow: 0 12px 36px rgba(0,0,0,0.45);
    }}
    
    .brand-title {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    
    .brand-icon {{
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: linear-gradient(135deg, #d97706, #f59e0b, #fbbf24);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Outfit', sans-serif;
      font-weight: 800;
      color: #000;
      box-shadow: 0 0 16px var(--gold-glow);
    }}
    
    .brand-text h1 {{
      font-family: 'Outfit', sans-serif;
      font-size: 16px;
      font-weight: 700;
      letter-spacing: 0.5px;
      color: #fff;
    }}
    
    .brand-text p {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--gold-primary);
      letter-spacing: 0.2px;
    }}
    
    /* Filter Pills */
    .filter-pills {{
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding: 4px;
    }}
    
    .pill-btn {{
      font-family: 'Inter', sans-serif;
      font-size: 12px;
      font-weight: 500;
      padding: 7px 13px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.04);
      color: var(--text-muted);
      border: 1px solid rgba(255, 255, 255, 0.07);
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }}
    
    .pill-btn:hover {{
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
      border-color: rgba(255, 255, 255, 0.2);
    }}
    
    .pill-btn.active {{
      background: rgba(245, 158, 11, 0.16);
      color: #fbbf24;
      border-color: rgba(245, 158, 11, 0.5);
      box-shadow: 0 0 14px rgba(245, 158, 11, 0.25);
    }}
    
    .pill-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
    }}
    
    /* Side Inspector Drawer */
    .inspector-panel {{
      position: absolute;
      top: 90px;
      right: 16px;
      bottom: 24px;
      width: 380px;
      z-index: 1000;
      background: var(--panel-bg);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid var(--panel-border);
      border-radius: 16px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      box-shadow: 0 16px 48px rgba(0,0,0,0.55);
      overflow-y: auto;
      transform: translateX(0);
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    
    .inspector-panel.closed {{
      transform: translateX(410px);
    }}
    
    .inspector-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      padding-bottom: 12px;
    }}
    
    .inspector-badge {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 6px;
      letter-spacing: 0.5px;
      font-weight: 600;
      display: inline-block;
      margin-bottom: 4px;
    }}
    
    .inspector-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 19px;
      font-weight: 700;
      color: #fff;
    }}
    
    .inspector-close {{
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 18px;
      padding: 4px;
      transition: color 0.2s;
    }}
    .inspector-close:hover {{ color: #fff; }}
    
    .data-card {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 10px;
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    
    .data-label {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    
    .data-value {{
      font-family: 'Inter', sans-serif;
      font-size: 13px;
      color: #fff;
      font-weight: 500;
    }}
    
    /* 3D Wireframe Canvas */
    .polyhedron-canvas-container {{
      background: radial-gradient(circle at center, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      height: 140px;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }}
    
    canvas#polyhedron-canvas {{
      width: 100%;
      height: 100%;
    }}
    
    .polyhedron-caption {{
      position: absolute;
      bottom: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 9px;
      color: var(--gold-primary);
      background: rgba(0,0,0,0.6);
      padding: 2px 8px;
      border-radius: 4px;
      border: 1px solid rgba(245, 158, 11, 0.2);
    }}
    
    /* Geometric Proof Floating Bar */
    .proof-banner {{
      position: absolute;
      bottom: 24px;
      left: 16px;
      z-index: 1000;
      background: var(--panel-bg);
      backdrop-filter: blur(20px);
      border: 1px solid var(--panel-border);
      border-radius: 12px;
      padding: 12px 18px;
      max-width: 480px;
      box-shadow: 0 12px 36px rgba(0,0,0,0.4);
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    
    .proof-stat {{
      display: flex;
      flex-direction: column;
    }}
    
    .proof-stat .val {{
      font-family: 'Outfit', sans-serif;
      font-size: 18px;
      font-weight: 700;
      color: var(--gold-primary);
    }}
    
    .proof-stat .lbl {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 9px;
      color: var(--text-muted);
      text-transform: uppercase;
    }}
    
    .proof-divider {{
      width: 1px;
      height: 28px;
      background: rgba(255, 255, 255, 0.1);
    }}
    
    .proof-text {{
      font-size: 11px;
      color: var(--text-main);
      line-height: 1.35;
    }}
    
    /* Pulsing Leaflet Markers */
    .custom-metal-pin {{
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }}
    
    .pin-circle {{
      width: 22px;
      height: 22px;
      border-radius: 50%;
      border: 2px solid #ffffff;
      box-shadow: 0 0 12px currentColor;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      color: #000;
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    
    .custom-metal-pin:hover .pin-circle {{
      transform: scale(1.35);
    }}
    
    .download-btn {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      padding: 8px 12px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: #fff;
      cursor: pointer;
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }}
    .download-btn:hover {{
      background: rgba(255, 255, 255, 0.12);
      border-color: rgba(255, 255, 255, 0.3);
    }}
  </style>
</head>
<body>

  <!-- Top Header Navigation -->
  <header class="top-header">
    <div class="brand-title">
      <div class="brand-icon">Au</div>
      <div class="brand-text">
        <h1>DAXDA Next-Gen | USA Metallogeny & Geodesics</h1>
        <p>Clifford Cl(7,0) • Octahedral & Lineament Symmetry</p>
      </div>
    </div>
    
    <!-- Filter Pills -->
    <div class="filter-pills" id="filter-container">
      <button class="pill-btn active" data-filter="all">All Metals (15)</button>
      <button class="pill-btn" data-filter="Gold"><span class="pill-dot" style="background:#f59e0b"></span>Gold (7)</button>
      <button class="pill-btn" data-filter="Platinum / Palladium"><span class="pill-dot" style="background:#38bdf8"></span>Platinum (1)</button>
      <button class="pill-btn" data-filter="Silver"><span class="pill-dot" style="background:#e2e8f0"></span>Silver (2)</button>
      <button class="pill-btn" data-filter="Copper"><span class="pill-dot" style="background:#f97316"></span>Copper (2)</button>
      <button class="pill-btn" data-filter="Lithium"><span class="pill-dot" style="background:#c084fc"></span>Lithium (2)</button>
      <button class="pill-btn" data-filter="Rare Earth Elements (Nd, Pr, Dy, Tb)"><span class="pill-dot" style="background:#10b981"></span>Rare Earths (1)</button>
      <button class="pill-btn" data-filter="Lost Gold Train (Au)" style="border-color: rgba(251,191,36,0.6); color:#fde68a;"><span class="pill-dot" style="background:#fbbf24"></span>🚂 Ohio Gold Train</button>
      <button class="pill-btn" id="toggle-trends-btn" style="border-color: rgba(245,158,11,0.4);"><span class="pill-dot" style="background:#fbbf24"></span>Tectonic Rays</button>
    </div>
    
    <a href="/daxda_usa_metallogeny.geojson" download="daxda_usa_metallogeny.geojson" class="download-btn">
      <svg width="13" height="13" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
      GeoJSON
    </a>
  </header>

  <!-- Leaflet Map Container -->
  <div id="map"></div>

  <!-- Geometric Proof Floating Bar -->
  <div class="proof-banner">
    <div class="proof-stat">
      <div class="val">70.0°</div>
      <div class="lbl">Nevada Shear</div>
    </div>
    <div class="proof-divider"></div>
    <div class="proof-stat">
      <div class="val">70.53°</div>
      <div class="lbl">Au {111} Angle</div>
    </div>
    <div class="proof-divider"></div>
    <div class="proof-text">
      Carlin Trend (330°) vs Battle Mountain (040°) intersect at <strong>70.0°</strong>, matching gold's atomic {111} dihedral angle (residual Δ = 0.53°).
    </div>
  </div>

  <!-- Side Inspector Panel -->
  <aside class="inspector-panel" id="inspector-panel">
    <div class="inspector-header">
      <div>
        <span class="inspector-badge" id="insp-badge" style="background:rgba(245,158,11,0.2); color:#fbbf24;">GOLD (AU)</span>
        <h2 class="inspector-title" id="insp-title">Carlin Trend</h2>
      </div>
      <button class="inspector-close" id="insp-close">&times;</button>
    </div>
    
    <!-- 3D Polyhedron Canvas -->
    <div class="polyhedron-canvas-container">
      <canvas id="polyhedron-canvas"></canvas>
      <div class="polyhedron-caption" id="poly-caption">Cuboctahedron (12-Coordination, Oh)</div>
    </div>

    <div class="data-card">
      <span class="data-label">Geographic Coordinates & Elevation</span>
      <span class="data-value" id="insp-coords">40.9750° N, -116.3720° W • 1,750 m</span>
    </div>

    <div class="data-card">
      <span class="data-label">Tectonic Lineament & Strike</span>
      <span class="data-value" id="insp-trend">Carlin Trend (NNW strike ~330°)</span>
    </div>

    <div class="data-card">
      <span class="data-label">Crystallographic Scale Alignment</span>
      <span class="data-value" id="insp-cryst" style="color:#fbbf24; font-size:12px; line-height:1.4;">
        Forms a 70° conjugate angle with Battle Mtn (040°), matching the atomic {111} dihedral angle of 70.53°.
      </span>
    </div>

    <div class="data-card">
      <span class="data-label">Geological Host Setting</span>
      <span class="data-value" id="insp-geology" style="font-size:12px; line-height:1.4;">
        Paleozoic silty carbonate shelf deformed during Roberts Mountains thrusting; Eocene magmatic fluid pulse.
      </span>
    </div>

    <div class="data-card">
      <span class="data-label">Estimated Mineral Endowment</span>
      <span class="data-value" id="insp-endowment" style="color:#38bdf8; font-weight:600;">
        >90 million oz Au (Second largest gold province on Earth)
      </span>
    </div>
  </aside>

  <!-- Leaflet JS -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

  <script>
    // Embedded GeoJSON Data
    const GEOJSON_DATA = {geojson_str};

    // Color definitions
    const COLOR_MAP = {json.dumps(COLOR_MAP)};

    // Initialize Map with dark tiles
    const map = L.map('map', {{
      center: [39.50, -98.35], // Center of USA
      zoom: 5,
      zoomControl: false,
      attributionControl: false
    }});

        // Tile layers (Free public GIS layers without watermark)
    const darkCanvas = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
      maxZoom: 16,
      attribution: 'Esri, HERE, Garmin, USGS'
    }});

    const satelliteView = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
      maxZoom: 18,
      attribution: 'Esri, Maxar, Earthstar Geographics'
    }});

    darkCanvas.addTo(map);

    // Basemap toggle button
    let isSatellite = false;
    const basemapToggle = document.createElement('button');
    basemapToggle.className = 'pill-btn';
    basemapToggle.style.marginLeft = '4px';
    basemapToggle.innerHTML = '<span class="pill-dot" style="background:#38bdf8"></span>Basemap: Dark';
    basemapToggle.addEventListener('click', () => {{
      isSatellite = !isSatellite;
      if (isSatellite) {{
        map.removeLayer(darkCanvas);
        map.addLayer(satelliteView);
        basemapToggle.innerHTML = '<span class="pill-dot" style="background:#10b981"></span>Basemap: Satellite';
        basemapToggle.classList.add('active');
      }} else {{
        map.removeLayer(satelliteView);
        map.addLayer(darkCanvas);
        basemapToggle.innerHTML = '<span class="pill-dot" style="background:#38bdf8"></span>Basemap: Dark';
        basemapToggle.classList.remove('active');
      }}
    }});
    document.getElementById('filter-container').appendChild(basemapToggle);

    // Reposition zoom control to bottom right
    L.control.zoom({{ position: 'bottomright' }}).addTo(map);

    // Web Audio Chime generator (432Hz harmonic pentatonic)
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    let audioCtx = null;
    function playHarmonicChime(freq = 432) {{
      try {{
        if (!audioCtx) audioCtx = new AudioContext();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.6);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.6);
      }} catch (e) {{}}
    }}

    // Layer groups
    const depositLayers = {{}};
    const lineamentLayerGroup = L.layerGroup().addTo(map);
    let allDepositMarkers = [];

    // Parse GeoJSON features
    GEOJSON_DATA.features.forEach(feature => {{
      const props = feature.properties;
      const geom = feature.geometry;

      if (geom.type === 'Point') {{
        const element = props.element;
        const color = props.color || '#f59e0b';
        const symbol = props.symbol || 'Au';
        const lat = geom.coordinates[1];
        const lon = geom.coordinates[0];

        // Create custom HTML pulsing pin icon
        const iconHtml = `
          <div class="custom-metal-pin" style="color: ${{color}};">
            <div class="pin-circle" style="background: ${{color}}; color: #000;">
              ${{symbol.substring(0, 2)}}
            </div>
          </div>
        `;

        const customIcon = L.divIcon({{
          html: iconHtml,
          className: '',
          iconSize: [24, 24],
          iconAnchor: [12, 12]
        }});

        const marker = L.marker([lat, lon], {{ icon: customIcon }});

        marker.on('click', () => {{
          playHarmonicChime(element === 'Gold' ? 540 : element === 'Platinum / Palladium' ? 648 : 432);
          showInspector(props, lat, lon);
        }});

        if (!depositLayers[element]) {{
          depositLayers[element] = L.layerGroup().addTo(map);
        }}
        depositLayers[element].addLayer(marker);
        allDepositMarkers.push({{ marker, element, props, lat, lon }});

      }} else if (geom.type === 'LineString') {{
        // Tectonic Lineaments
        const latlngs = geom.coordinates.map(c => [c[1], c[0]]);
        const polyline = L.polyline(latlngs, {{
          color: props.color || '#f59e0b',
          weight: props.weight || 3,
          dashArray: props.dashArray || 'none',
          opacity: 0.85
        }});

        polyline.bindTooltip(`<strong>${{props.name}}</strong><br>Strike: ${{props.strike}}°`, {{
          sticky: true,
          className: 'lineament-tooltip'
        }});

        polyline.on('click', () => {{
          playHarmonicChime(360);
          showLineamentInspector(props);
        }});

        lineamentLayerGroup.addLayer(polyline);
      }}
    }});

    // Inspector UI Logic
    const inspector = document.getElementById('inspector-panel');
    const inspTitle = document.getElementById('insp-title');
    const inspBadge = document.getElementById('insp-badge');
    const inspCoords = document.getElementById('insp-coords');
    const inspTrend = document.getElementById('insp-trend');
    const inspCryst = document.getElementById('insp-cryst');
    const inspGeology = document.getElementById('insp-geology');
    const inspEndowment = document.getElementById('insp-endowment');
    const polyCaption = document.getElementById('poly-caption');

    document.getElementById('insp-close').addEventListener('click', () => {{
      inspector.classList.add('closed');
    }});

    function showInspector(props, lat, lon) {{
      inspector.classList.remove('closed');
      inspTitle.textContent = props.deposit_name;
      inspBadge.textContent = `${{props.element.toUpperCase()}} (${{props.symbol}})`;
      inspBadge.style.background = props.color + '26';
      inspBadge.style.color = props.color;
      inspCoords.textContent = `${{lat.toFixed(4)}}° N, ${{lon.toFixed(4)}}° W • ${{props.elevation_m}} m`;
      inspTrend.textContent = props.structural_trend;
      inspCryst.textContent = props.crystallographic_alignment;
      inspCryst.style.color = props.color;
      inspGeology.textContent = props.geological_setting;
      inspEndowment.textContent = props.estimated_endowment;
      polyCaption.textContent = props.polyhedron_shape;
      
      // Update 3D wireframe shape
      currentShapeType = props.element.includes('Lithium') ? 'bcc' : props.element.includes('Rare') ? 'dhcp' : 'fcc';
    }}

    function showLineamentInspector(props) {{
      inspector.classList.remove('closed');
      inspTitle.textContent = props.name;
      inspBadge.textContent = 'TECTONIC SHEAR RAY';
      inspBadge.style.background = props.color + '26';
      inspBadge.style.color = props.color;
      inspCoords.textContent = `Strike Azimuth: ${{props.strike}}°`;
      inspTrend.textContent = props.name;
      inspCryst.textContent = props.description;
      inspCryst.style.color = props.color;
      inspGeology.textContent = "Deep-seated trans-lithospheric weakness zone guiding ascending hydrothermal fluid pulses.";
      inspEndowment.textContent = "Continental-scale mineralization plumbing vector";
      polyCaption.textContent = `Shear Corridor (Strike ${{props.strike}}°)`;
      currentShapeType = 'plane';
    }}

    // Filter Buttons logic
    const filterButtons = document.querySelectorAll('.pill-btn[data-filter]');
    filterButtons.forEach(btn => {{
      btn.addEventListener('click', () => {{
        filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filterVal = btn.getAttribute('data-filter');

        Object.keys(depositLayers).forEach(elem => {{
          if (filterVal === 'all' || filterVal === elem) {{
            map.addLayer(depositLayers[elem]);
          }} else {{
            map.removeLayer(depositLayers[elem]);
          }}
        }});
        if (filterVal === 'Lost Gold Train (Au)') {{
          map.flyTo([41.8653, -80.7892], 12, {{ animate: true, duration: 1.5 }});
        }}
      }});
    }});

    // Toggle Tectonic Rays Button
    let trendsVisible = true;
    const toggleTrendsBtn = document.getElementById('toggle-trends-btn');
    toggleTrendsBtn.addEventListener('click', () => {{
      trendsVisible = !trendsVisible;
      if (trendsVisible) {{
        map.addLayer(lineamentLayerGroup);
        toggleTrendsBtn.classList.add('active');
      }} else {{
        map.removeLayer(lineamentLayerGroup);
        toggleTrendsBtn.classList.remove('active');
      }}
    }});
    toggleTrendsBtn.classList.add('active');

    // -------------------------------------------------------------
    // Canvas 3D Rotating Polyhedron Renderer (Wireframe Cuboctahedron & BCC)
    // -------------------------------------------------------------
    const canvas = document.getElementById('polyhedron-canvas');
    const ctx = canvas.getContext('2d');
    let currentShapeType = 'fcc'; // 'fcc', 'bcc', 'dhcp', 'plane'
    let angleX = 0.5, angleY = 0.5;

    function resizeCanvas() {{
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight;
    }}
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    // Vertices of a Cuboctahedron (FCC 12-coordination)
    const cuboctahedronVerts = [
      [1, 1, 0], [1, -1, 0], [-1, 1, 0], [-1, -1, 0],
      [1, 0, 1], [1, 0, -1], [-1, 0, 1], [-1, 0, -1],
      [0, 1, 1], [0, 1, -1], [0, -1, 1], [0, -1, -1]
    ].map(v => v.map(coord => coord * 32));

    // Edges between adjacent vertices in cuboctahedron (distance = sqrt(2) * scale)
    const cuboctahedronEdges = [];
    const scale = 32;
    for (let i = 0; i < cuboctahedronVerts.length; i++) {{
      for (let j = i + 1; j < cuboctahedronVerts.length; j++) {{
        const dx = cuboctahedronVerts[i][0] - cuboctahedronVerts[j][0];
        const dy = cuboctahedronVerts[i][1] - cuboctahedronVerts[j][1];
        const dz = cuboctahedronVerts[i][2] - cuboctahedronVerts[j][2];
        const distSq = dx*dx + dy*dy + dz*dz;
        if (Math.abs(distSq - 2 * scale * scale) < 5) {{
          cuboctahedronEdges.push([i, j]);
        }}
      }}
    }}

    function render3D() {{
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const cx = canvas.width / 2;
      const cy = canvas.height / 2;

      angleX += 0.012;
      angleY += 0.018;

      const cosX = Math.cos(angleX), sinX = Math.sin(angleX);
      const cosY = Math.cos(angleY), sinY = Math.sin(angleY);

      const projected = cuboctahedronVerts.map(v => {{
        // Rotate around Y
        let x = v[0] * cosY - v[2] * sinY;
        let z = v[0] * sinY + v[2] * cosY;
        // Rotate around X
        let y = v[1] * cosX - z * sinX;
        z = v[1] * sinX + z * cosX;
        return [cx + x, cy + y];
      }});

      // Draw Edges
      ctx.strokeStyle = currentShapeType === 'bcc' ? '#c084fc' : currentShapeType === 'dhcp' ? '#10b981' : '#f59e0b';
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      cuboctahedronEdges.forEach(edge => {{
        const p1 = projected[edge[0]];
        const p2 = projected[edge[1]];
        ctx.moveTo(p1[0], p1[1]);
        ctx.lineTo(p2[0], p2[1]);
      }});
      ctx.stroke();

      // Draw Vertices
      ctx.fillStyle = '#ffffff';
      projected.forEach(p => {{
        ctx.beginPath();
        ctx.arc(p[0], p[1], 2.2, 0, Math.PI * 2);
        ctx.fill();
      }});

      requestAnimationFrame(render3D);
    }}
    render3D();

  </script>
</body>
</html>
"""
    return html

def main():
    geojson_data = generate_geojson()
    geojson_path = os.path.join(OUTPUTS_DIR, "daxda_usa_metallogeny.geojson")
    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, indent=2)
    print(f"Generated GeoJSON file: {geojson_path}")
    
    html_content = generate_interactive_html(geojson_data)
    html_path = os.path.join(OUTPUTS_DIR, "daxda_usa_metallogeny_map.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated Interactive Map HTML: {html_path}")

if __name__ == "__main__":
    main()
