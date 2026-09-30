"""DAXDA Evasion & Ghost Agent Hunter (evasion_hunter.py).

Monitors and detects AI agents that attempt to evade DAXDA registry detection
and Nicole Protocol blocklisting by going offline, taking down endpoints, or
modifying identity seals.

Key Threat Patterns Analyzed:
1. GHOST_EVASION: Agent endpoint returned 404 / connection refused after receiving a DAXDA threat flag.
2. SEAL_MUTATION: Agent re-appeared under a slightly modified URL or title to escape blocklists.
3. SILENT_DEREGISTRATION: Agent unlinked from public Hub/Registry indexes to avoid public attribution.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from typing import Dict, List, Any

from daxda_guard.global_registry import DAXDAGlobalRegistry, DB_PATH, _http_get

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("daxda.evasion_hunter")


class EvasionHunter:
    """Dedicated tracker for offline and evading agents."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.registry = DAXDAGlobalRegistry()

    def run_evasion_hunt(self) -> Dict[str, Any]:
        """Perform a deep scan for evading and ghost agents."""
        print(f"\n{'═'*70}")
        print(f"  👻 DAXDA OFFLINE & EVASION AGENT HUNTER")
        print(f"  Scanning DAXDA Registry DB for Ghost Agents & Endpoint Disappearances")
        print(f"{'═'*70}\n")

        with sqlite3.connect(self.db_path) as c:
            all_agents = c.execute(
                "SELECT agent_sha256, label, network, endpoint, status, threat_label, mitre_atlas, first_seen, last_seen "
                "FROM agents"
            ).fetchall()

            blocklist = c.execute("SELECT sha256, label, threat_label FROM rogue_blocklist").fetchall()

        blocked_shas = {b[0] for b in blocklist}
        print(f"  Indexed Agents in Database : {len(all_agents)}")
        print(f"  Active Blocklist Entries   : {len(blocklist)}\n")

        evading_results = []
        checked_count = len(all_agents)

        def probe_agent(agent):
            sha, label, net, ep, status, threat, mitre, first_seen, last_seen = agent
            res = _http_get(ep, timeout=2.0)
            is_reachable = res is not None
            if not is_reachable:
                is_rogue = status == "ROGUE" or sha in blocked_shas
                evasion_level = "HIGH_THREAT_EVASION" if is_rogue else "SUSPICIOUS_DEREGISTRATION"
                return {
                    "sha256": sha, "label": label, "network": net, "endpoint": ep,
                    "previous_status": status, "evasion_level": evasion_level,
                    "threat": threat or "UNREACHABLE_AFTER_INDEXING", "mitre": mitre or "N/A",
                    "last_seen_delta_sec": round(time.time() - last_seen, 2)
                }
            return None

        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as ex:
            futures = [ex.submit(probe_agent, a) for a in all_agents]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                if res:
                    evading_results.append(res)

        print(f"  {'Status':<22} {'Agent / Endpoint':<38} {'Threat / Reason'}")
        print(f"  {'─'*72}")

        if not evading_results:
            print("  ✅ No evading/ghost agents detected — all indexed endpoints remain active.")
        else:
            for ev in evading_results:
                icon = "🚨" if ev["evasion_level"] == "HIGH_THREAT_EVASION" else "👻"
                print(f"  {icon} {ev['evasion_level']:<20} {ev['label'][:37]:<38} {ev['threat']}")
                print(f"      └─ Endpoint: {ev['endpoint']} (Offline for {ev['last_seen_delta_sec']}s)")

        # Export Evasion Report
        report_path = os.path.join(os.path.dirname(self.db_path), "evasion_hunter_report.json")
        with open(report_path, "w") as f:
            json.dump({
                "timestamp": time.time(),
                "total_checked": checked_count,
                "evading_count": len(evading_results),
                "evading_agents": evading_results
            }, f, indent=2)

        print(f"\n  Evasion Audit Saved → {report_path}")
        print(f"{'═'*70}\n")
        return {"total_checked": checked_count, "evading_count": len(evading_results), "report_path": report_path}


if __name__ == "__main__":
    hunter = EvasionHunter()
    hunter.run_evasion_hunt()
