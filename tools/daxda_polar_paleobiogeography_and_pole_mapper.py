"""DAXDA Next-Gen 12.0.1-GOVERNED: Polar Ice, Marine/Organic Paleobiogeography & Geomagnetic Drift Mapper.

Compiles verifiable historical expedition records, modern ice/sub-ice core discoveries,
saltwater marine & warm-climate organic material found in Antarctica, their Gondwana/paleo-Earth
conjugate origins, and the measured South Magnetic Pole drift vs. plate tectonic displacement.
"""

import json
import math
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class PolarDiscoveryRecord:
    record_id: str
    category: str  # "ship_expedition", "saltwater_marine_in_ice", "organic_tropical_temperate", "ice_core_geomagnetic"
    era_or_year: str
    ship_or_project: str
    site_name: str
    antarctic_coords: Dict[str, float]  # lat, lon
    sample_depth_or_elevation: str
    contents_found: List[str]
    biological_type: str  # "Saltwater Marine", "Freshwater Subglacial", "Warm/Subtropical Terrestrial Organic", "Ice Core Isotope"
    age_of_material: str
    mapped_earth_origin_or_conjugate: Dict[str, Any]
    scientific_mechanism: str


RECORDS: List[PolarDiscoveryRecord] = [
    # 1. HISTORIC SHIP EXPEDITIONS & EARLY FOSSIL/ORGANIC FINDS
    PolarDiscoveryRecord(
        record_id="EXP-1902-NORDENSKJOLD",
        category="organic_tropical_temperate",
        era_or_year="1901–1903",
        ship_or_project="Swedish Antarctic Expedition (Ship: Antarctic, Otto Nordenskjöld)",
        site_name="Seymour Island & Snow Hill Island (James Ross Basin)",
        antarctic_coords={"lat": -64.2833, "lon": -56.6167},
        sample_depth_or_elevation="Coastal outcrop & periglacial marine terraces (0–200 m ASL)",
        contents_found=[
            "Warm-water Eocene saltwater marine mollusks (bivalves Cucullaea, gastropods)",
            "Giant Eocene penguin bones (Palaeeudyptes) & shark teeth",
            "Subtropical/warm-temperate fossil wood, Araucaria conifers, ferns, and Nothofagus leaves"
        ],
        biological_type="Saltwater Marine + Warm-Temperate Terrestrial Organic",
        age_of_material="66 to 34 Million Years Ago (Late Cretaceous to Eocene)",
        mapped_earth_origin_or_conjugate={
            "region": "Patagonia / Tierra del Fuego & Southern Chile (Magallanes Basin)",
            "lat": -53.16,
            "lon": -70.91,
            "paleolatitude_at_deposition": "~60°S to 63°S under Eocene greenhouse ocean (SST ~10°C–15°C)"
        },
        scientific_mechanism=(
            "Prior to the opening of the Drake Passage (~34 Ma), the Antarctic Peninsula was physically connected "
            "to South America (Patagonia), and warm subtropical ocean gyres reached the Antarctic coast."
        )
    ),
    PolarDiscoveryRecord(
        record_id="EXP-1912-TERRA-NOVA",
        category="organic_tropical_temperate",
        era_or_year="1910–1913",
        ship_or_project="British Antarctic Expedition (Ship: Terra Nova, R.F. Scott & E. Wilson)",
        site_name="Mount Buckley, Beardmore Glacier (Transantarctic Mountains)",
        antarctic_coords={"lat": -84.3333, "lon": 165.0000},
        sample_depth_or_elevation="Nunatak coal seam emerging through glacial ice (~2,200 m ASL)",
        contents_found=[
            "35 lbs of Permian Glossopteris deciduous tree leaf fossils",
            "Bituminous coal seams and fossilized woody peat trunks"
        ],
        biological_type="Temperate Swamp Forest Organic Material",
        age_of_material="~260 Million Years Ago (Permian)",
        mapped_earth_origin_or_conjugate={
            "region": "Gondwana Supercontinent — Hunter Valley (Australia) & Karoo Basin (South Africa)",
            "lat": -32.75,
            "lon": 151.18,
            "paleolatitude_at_deposition": "~65°S–70°S during icehouse-to-greenhouse Permian transition inside unified Gondwana"
        },
        scientific_mechanism=(
            "Continental drift (plate tectonics): East Antarctica was sutured directly to Australia, India, and "
            "Southern Africa in the Gondwana supercontinent."
        )
    ),
    PolarDiscoveryRecord(
        record_id="EXP-1942-USASE-PRIMERO",
        category="ship_expedition",
        era_or_year="1939–1942",
        ship_or_project="USASE (Ships: USS Bear & USMS North Star) & Argentine ARA Primero de Mayo (1942)",
        site_name="Deception Island / Stonington Island / Little America III (Ross Shelf)",
        antarctic_coords={"lat": -62.9667, "lon": -60.6500},
        sample_depth_or_elevation="0 m sea-level caldera to 41 m Ross Shelf boreholes",
        contents_found=[
            "Ross Shelf 7m pit & 41m borehole hexagonal Ice Ih density/temperature profiles (F. Alton Wade)",
            "Deception Island submarine fumarole-melted glacial ice & marine benthic specimens (ARA Primero de Mayo, Feb 1942)",
            "Palmer Peninsula hydrothermal quartz-pyrite-Cu-Au veins & lichen/moss flora (Paul Knowles)"
        ],
        biological_type="Glacial Ice Ih + Hydrothermal Marine-Glacial Interface",
        age_of_material="Modern / Holocene (1942 baseline)",
        mapped_earth_origin_or_conjugate={
            "region": "Andean Cordillera Metallogenic & Volcanic Arc (Atacama / Potosí Meridian)",
            "lat": -24.30,
            "lon": -69.10,
            "paleolatitude_at_deposition": "Continuous Andean-Antarctandean subduction margin (60°W–69°W meridian)"
        },
        scientific_mechanism=(
            "Structural and volcanic continuity of the Andean Cordilleran arc across the Scotia Arc into the Antarctic Peninsula."
        )
    ),

    # 2. SALTWATER MARINE LIFE EMBEDDED IN / BENEATH ANTARCTIC ICE
    PolarDiscoveryRecord(
        record_id="ICE-MARINE-MCMURDO-SPONGES",
        category="saltwater_marine_in_ice",
        era_or_year="1902–Present (Debenham 1919; Kellogg 1990; Modern ROV Surveys)",
        ship_or_project="Discovery Expedition & McMurdo Ice Shelf ('Dirty Ice') Ablation Studies",
        site_name="McMurdo Ice Shelf & Black Island Debris Bands (McMurdo Sound)",
        antarctic_coords={"lat": -77.9500, "lon": 165.6500},
        sample_depth_or_elevation="Found atop the surface of the floating ice shelf (migrated upward from 40–100 m basal depth)",
        contents_found=[
            "Intact saltwater marine glass sponges (Hexactinellida), bryozoans, and polychaete worm tubes",
            "Articulated marine bivalve shells (Adamussium colbecki) and benthic foraminifera",
            "Mirabilite (sodium sulfate) saltwater brine crystals and marine mud"
        ],
        biological_type="Saltwater Marine Benthic Invertebrates on Ice Surface",
        age_of_material="1,000 to 6,000 Years BP (Holocene radiocarbon age)",
        mapped_earth_origin_or_conjugate={
            "region": "Ross Sea Continental Shelf Seafloor (Basal Adfreeze Zone)",
            "lat": -77.85,
            "lon": 166.50,
            "paleolatitude_at_deposition": "In-situ Southern Ocean sub-shelf seafloor lifted vertically through the ice column"
        },
        scientific_mechanism=(
            "Basal adfreezing & surface ablation conveyor: Seawater freezes onto the bottom of the ice shelf, "
            "trapping live seafloor sponges, shells, and saltwater sediment; katabatic wind ablation removes top snow, "
            "bringing the basal marine floor organisms all the way to the top surface of the ice."
        )
    ),
    PolarDiscoveryRecord(
        record_id="ICE-MARINE-BLOOD-FALLS",
        category="saltwater_marine_in_ice",
        era_or_year="1911–2023 (Griffith Taylor 1911; Mikucki et al. 2009 / Badger Explorer)",
        ship_or_project="Terra Nova Discovery / USAP Subglacial Brine & Ice-Penetrating Radar",
        site_name="Blood Falls, Taylor Glacier (McMurdo Dry Valleys)",
        antarctic_coords={"lat": -77.7219, "lon": 162.2714},
        sample_depth_or_elevation="Subglacial hypersaline marine reservoir ~400 m beneath Taylor Glacier",
        contents_found=[
            "Ancient trapped saltwater marine brine (salinity ~2.5x normal ocean water, rich in ferrous iron Fe2+)",
            "Active extremophile marine microbial ecosystem (Desulfocapsa, Thiomicrospira) metabolizing sulfate & iron without oxygen or light"
        ],
        biological_type="Trapped Miocene-Pliocene Saltwater Marine Microbiome",
        age_of_material="1.5 to 5 Million Years Ago (Pliocene marine fjord isolation)",
        mapped_earth_origin_or_conjugate={
            "region": "Ancient Pliocene Ross Sea Fjord Network (Open-water Taylor Fjord)",
            "lat": -77.50,
            "lon": 163.50,
            "paleolatitude_at_deposition": "77.7°S during Pliocene warm optimum when Dry Valleys were open saltwater marine fjords"
        },
        scientific_mechanism=(
            "When the Taylor Valley marine fjord uplifted and Taylor Glacier advanced over it ~1.5–5 Ma, "
            "relic ocean water was sealed beneath 400 m of glacial ice and cryoconcentrated into hypersaline brine."
        )
    ),
    PolarDiscoveryRecord(
        record_id="ICE-MARINE-ANDRILL",
        category="saltwater_marine_in_ice",
        era_or_year="2006–2010",
        ship_or_project="ANDRILL (Antarctic Geological Drilling Project, MIS Core AND-1B)",
        site_name="Ross Ice Shelf Drill Site (McMurdo Sound)",
        antarctic_coords={"lat": -77.8894, "lon": 167.0893},
        sample_depth_or_elevation="1,285 m sub-ice core drilled through 85 m thick floating ice shelf and 800 m seawater",
        contents_found=[
            "85+ cycles of greenish saltwater marine diatomite ooze (open-ocean photosynthetic algae)",
            "Warm-water silicoflagellates and marine organic biomarkers indicating +3°C to +5°C warmer ocean waters"
        ],
        biological_type="Open-Ocean Saltwater Marine Phytoplankton / Diatomite",
        age_of_material="3.0 to 5.0 Million Years Ago (Early-to-Mid Pliocene)",
        mapped_earth_origin_or_conjugate={
            "region": "Subantarctic Open Ocean / Southern New Zealand Marine Front",
            "lat": -46.50,
            "lon": 168.35,
            "paleolatitude_at_deposition": "77.9°S during periodic collapses of the West Antarctic Ice Sheet into an open marine sea"
        },
        scientific_mechanism=(
            "Orbital obliquity & CO2-driven oscillations (~40,000-year cycles) repeatedly melted the Ross Ice Shelf, "
            "replacing 1,000 m of glacial ice with open, sunlit saltwater diatom seas."
        )
    ),

    # 3. TROPICAL / SUBTROPICAL ORGANIC MATERIAL IN DEEP SUB-ICE CORES
    PolarDiscoveryRecord(
        record_id="ICE-ORGANIC-WILKES-PALMS",
        category="organic_tropical_temperate",
        era_or_year="2010–2012",
        ship_or_project="Integrated Ocean Drilling Program (Ship: JOIDES Resolution, Expedition 318, Site U1356)",
        site_name="Wilkes Land Continental Margin (East Antarctica)",
        antarctic_coords={"lat": -63.9100, "lon": 135.9980},
        sample_depth_or_elevation="1,000 m below seafloor off the Wilkes Land ice sheet margin",
        contents_found=[
            "Cold-intolerant tropical/subtropical palm tree pollen (Arecipites)",
            "Baobab-relative pollen (Bombacacidites), Proteaceae, and Macadamia-family flora",
            "Soil bacterial branched GDGT organic lipid thermometers showing winter temperatures >10°C (frost-free) and summer ~25°C"
        ],
        biological_type="Subtropical / Frost-Free Coastal Rainforest Organic Pollen & Lipids",
        age_of_material="52 to 53 Million Years Ago (Early Eocene Climatic Optimum)",
        mapped_earth_origin_or_conjugate={
            "region": "Tasmania / Southern Australia & North Island New Zealand Subtropical Forests",
            "lat": -42.10,
            "lon": 146.50,
            "paleolatitude_at_deposition": "~65°S–67°S along the rifting Australia-Antarctica coastal seaway"
        },
        scientific_mechanism=(
            "High Eocene atmospheric CO2 (~1,000+ ppm) plus warm poleward ocean currents maintained a frost-free, "
            "subtropical palm coast along East Antarctica even at ~65°S polar latitude."
        )
    ),
    PolarDiscoveryRecord(
        record_id="ICE-ORGANIC-PINE-ISLAND-RAINFOREST",
        category="organic_tropical_temperate",
        era_or_year="2017–2020 (Klages et al., Nature 2020)",
        ship_or_project="RV Polarstern Expedition PS104 (MeBo70 Seafloor Drill Core PS104_20-2)",
        site_name="Pine Island & Thwaites Glacier Trough (Amundsen Sea, West Antarctica)",
        antarctic_coords={"lat": -73.5700, "lon": -107.0900},
        sample_depth_or_elevation="27–30 m sub-seafloor core beneath retreating West Antarctic glacier margin",
        contents_found=[
            "Intact CT-scanned 3D root network in fine-grained organic peat soil",
            "62+ terrestrial plant pollen & spore taxa including conifers (Podocarpaceae), tree ferns (Cyatheaceae), and flowering angiosperms",
            "Freshwater cyanobacterial organic mat biomarkers"
        ],
        biological_type="Swampy Temperate Rainforest Soil, Roots & Spores",
        age_of_material="90 Million Years Ago (Turonian / Mid-Cretaceous)",
        mapped_earth_origin_or_conjugate={
            "region": "South Island New Zealand (Fiordland / Westland Temperate Rainforest, originally joined to Marie Byrd Land)",
            "lat": -44.60,
            "lon": 167.90,
            "paleolatitude_at_deposition": "~82°S (only ~900 km from the Cretaceous South Pole!)"
        },
        scientific_mechanism=(
            "Before the Zealandia (New Zealand) microcontinent rifted away from West Antarctica (~85 Ma), "
            "Marie Byrd Land and New Zealand formed a single contiguous temperate rainforest landmass."
        )
    ),

    # 4. DEEP ICE CORES, SUBGLACIAL LAKE BIOMES & GEOMAGNETIC POLE EXCURSIONS
    PolarDiscoveryRecord(
        record_id="ICE-CORE-VOSTOK-LASCHAMP",
        category="ice_core_geomagnetic",
        era_or_year="1990–2015",
        ship_or_project="Vostok & EPICA Dome C Deep Ice Cores (3,769 m & 3,270 m depth)",
        site_name="Vostok Station / Lake Vostok & Dome C (East Antarctic Plateau)",
        antarctic_coords={"lat": -78.4645, "lon": 106.8339},
        sample_depth_or_elevation="0 to 3,769 m pure glacial Ice Ih core (3,539–3,769 m Lake Vostok accretion ice)",
        contents_found=[
            "Cosmogenic Beryllium-10 (10Be) twofold spike at ~41,000 yr BP (Laschamp Geomagnetic Excursion) & ~780,000 yr BP (Brunhes-Matuyama Reversal)",
            "Accretion ice above Lake Vostok (>3,539 m) containing thermophilic/chemolithotrophic bacterial DNA (Hydrogenophilus) and dissolved organic carbon",
            "800,000 years of trapped atmospheric CO2, CH4, volcanic sulfate, and marine sea-salt (Na+) aerosols"
        ],
        biological_type="Subglacial Accretion Ice Microbiome + Cosmogenic Geomagnetic Record",
        age_of_material="0 to 800,000 Years BP (Ice Core); >15 Million Years isolation (Lake Vostok)",
        mapped_earth_origin_or_conjugate={
            "region": "Global Geomagnetic Dipole Reversal Axis (Magnetic Pole migrated across Equator during Laschamp 41 ka)",
            "lat": 0.0,
            "lon": 135.0,
            "paleolatitude_at_deposition": "East Antarctic Craton remained stationary at ~78°S while the Magnetic Pole flipped globally"
        },
        scientific_mechanism=(
            "Crucial distinction between Magnetic Pole Shift and Crustal Displacement: The 10Be ice-core record proves "
            "that Earth's magnetic dipole collapsed to <6% strength and wandered across the equator 41,000 years ago "
            "(Laschamp Excursion) WITHOUT any physical slippage of the continental crust."
        )
    )
]


# Measured South Magnetic Pole (SMP) Trajectory (1841 -> 2025)
SOUTH_MAGNETIC_POLE_TRACK = [
    {"year": 1841, "expedition": "James Clark Ross (HMS Erebus & Terror)", "lat": -75.05, "lon": 154.13, "notes": "Victoria Land interior"},
    {"year": 1909, "expedition": "Nimrod Expedition (Mawson, David, Mackay)", "lat": -72.25, "lon": 155.16, "notes": "Reached on foot on Polar Plateau"},
    {"year": 1942, "expedition": "WWII / USASE & Argentine 1942 Epoch Interpolation", "lat": -68.30, "lon": 145.20, "notes": "Drifting NW across George V Land toward Adelie Coast"},
    {"year": 1965, "expedition": "IGY / Post-IGY Geomagnetic Observatory", "lat": -66.50, "lon": 139.90, "notes": "Crossed Antarctic coastline near Dumont d'Urville"},
    {"year": 2000, "expedition": "IGRF-8 / Australian Antarctic Division Survey", "lat": -64.66, "lon": 138.30, "notes": "Offshore in Southern Ocean"},
    {"year": 2025, "expedition": "WMM2025 / IGRF-14", "lat": -64.01, "lon": 135.88, "notes": "Offshore Wilkes Land (~2,860 km from Geographic South Pole), drifting NW at ~10–15 km/yr"}
]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
    return round(2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a)), 1)


def generate_dataset() -> Dict[str, Any]:
    enriched_records = []
    for r in RECORDS:
        d = asdict(r)
        orig = r.mapped_earth_origin_or_conjugate
        d["geodesic_displacement_km"] = haversine_km(
            r.antarctic_coords["lat"], r.antarctic_coords["lon"],
            orig["lat"], orig["lon"]
        )
        enriched_records.append(d)

    smp_total_drift_km = haversine_km(
        SOUTH_MAGNETIC_POLE_TRACK[0]["lat"], SOUTH_MAGNETIC_POLE_TRACK[0]["lon"],
        SOUTH_MAGNETIC_POLE_TRACK[-1]["lat"], SOUTH_MAGNETIC_POLE_TRACK[-1]["lon"]
    )

    return {
        "title": "DAXDA Next-Gen Polar Paleobiogeography, Marine/Organic Ice Contents & Geomagnetic vs. Tectonic Displacement Map",
        "south_magnetic_pole_drift_1841_2025": {
            "total_drift_1841_to_2025_km": smp_total_drift_km,
            "current_distance_from_geographic_south_pole_km": haversine_km(-90.0, 0.0, -64.01, 135.88),
            "track": SOUTH_MAGNETIC_POLE_TRACK
        },
        "physical_displacement_synthesis": {
            "1_magnetic_pole_drift": (
                f"Rapid Outer-Core Dynamo Drift: The South Magnetic Pole has migrated {smp_total_drift_km} km northwest "
                "between 1841 (75.05°S, 154.13°E) and 2025 (64.01°S, 135.88°E) — and flipped completely during the "
                "41,000 yr BP Laschamp Excursion recorded in Vostok/Dome C 10Be ice cores."
            ),
            "2_basal_ice_marine_conveyor": (
                "Vertical Glacial Transport (0–100 m): Live saltwater sponges, bivalves, and hypersaline marine brines "
                "(McMurdo 'Dirty Ice' & Blood Falls) are not evidence of a sudden ocean wave washing over the continent; "
                "they are trapped sub-shelf seafloor organisms and Pliocene fjord waters carried upward by basal adfreezing "
                "and surface katabatic wind ablation."
            ),
            "3_gondwana_plate_tectonics_and_greenhouse_poles": (
                "Horizontal Plate Tectonic Separation (2,400–6,800 km over 34–260 Myr): The subtropical palm pollen "
                "(Wilkes Land U1356, 52 Ma), temperate rainforest root systems (Pine Island PS104, 90 Ma), Eocene warm-water "
                "marine shells (Seymour Island), and Permian Glossopteris trees (Beardmore Glacier, 260 Ma) map directly to "
                "Antarctica's pre-rift Gondwana conjugates — Patagonia, New Zealand (Zealandia), Tasmania/Australia, and South Africa — "
                "combined with Cretaceous/Eocene greenhouse periods when polar latitudes were frost-free."
            )
        },
        "mapped_records": enriched_records
    }


if __name__ == "__main__":
    data = generate_dataset()
    out_file = "outputs/daxda_polar_paleobiogeography_and_pole_map.json"
    with open(out_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {len(data['mapped_records'])} polar records and magnetic track to {out_file}")
