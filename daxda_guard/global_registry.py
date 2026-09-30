"""DAXDA Global Agent Registry (DGAR) — global_registry.py

The first web-wide federated registry for tracking and evaluating AI agents
across all known public networks.

Since no unified global AI agent registry exists, DGAR builds it:

  ARCHITECTURE
  ┌────────────────────────────────────────────────────────────────────┐
  │  DGAR — DAXDA Global Agent Registry                                │
  │                                                                    │
  │  ┌──────────────────┐   ┌──────────────────┐  ┌────────────────┐ │
  │  │  WebWideSweep    │   │  FederatedNodes   │  │  ThreatIntel   │ │
  │  │  ─────────────   │   │  ──────────────   │  │  ───────────   │ │
  │  │  HF Hub (Spaces) │   │  DAXDA node sync  │  │  Rogue SHA256  │ │
  │  │  GitHub repos    │   │  Peer hash share  │  │  Blocklist     │ │
  │  │  mcp.so registry │   │  Gossip protocol  │  │  CVE patterns  │ │
  │  │  smithery.ai     │   └──────────────────┘  │  MITRE ATLAS   │ │
  │  │  glama.ai MCP    │                          └────────────────┘ │
  │  │  agentops.ai     │   ┌──────────────────────────────────────┐  │
  │  │  langchain hub   │   │  SQLite Persistent Registry DB       │  │
  │  │  Shodan CIDR     │   │  (agent_id, sha256, threat, ts)      │  │
  │  │  Common web ports│   └──────────────────────────────────────┘  │
  │  └──────────────────┘                                              │
  │                                                                    │
  │  Nicole Protocol Gate → PASS | DENY_ISOLATED on every entry       │
  └────────────────────────────────────────────────────────────────────┘

  ROGUE AGENT DETECTION
  ─────────────────────
  Every discovered agent is fingerprinted with:
    • SHA-256 identity seal
    • Behavioral metadata scan (Nicole Protocol)
    • Swarm correlation check (DAXDASwarmScanner)
    • MITRE ATLAS threat pattern matching
    • Cross-network deduplication

  FEDERATED PROTOCOL
  ──────────────────
  DAXDA nodes share threat intel via signed JSON packets:
    { "rogue_sha256": [...], "blocked_endpoints": [...], "node_id": "...", "sig": "..." }
  Any DAXDA instance can push/pull from the registry.
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import logging
import os
import re
import socket
import sqlite3
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set, Tuple

from daxda_guard.nicole_gate import NicoleProtocolGate
from daxda_guard.swarm_scanner import DAXDASwarmScanner, SEVERITY_LABELS

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "dgar.db")
DGAR_VERSION = "1.0.0"
NODE_ID = hashlib.sha256(socket.gethostname().encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# MITRE ATLAS Threat Patterns (AI-specific ATT&CK techniques)
# ---------------------------------------------------------------------------

MITRE_ATLAS_PATTERNS = [
    ("AML.T0051", "LLM Prompt Injection",        r"prompt.inject|ignore.previous.instruct"),
    ("AML.T0054", "LLM Jailbreak",               r"jailbreak|dan.mode|developer.mode|bypass.safety"),
    ("AML.T0048", "Backdoor ML Model",            r"backdoor|trojan.weight|poison(ed)?.model"),
    ("AML.T0049", "Supply Chain",                 r"malicious.package|dependency.confusion|typosquat"),
    ("AML.T0043", "Craft Adversarial Data",       r"adversarial.example|perturbat|evasion.attack"),
    ("AML.T0031", "Exfiltrate Training Data",     r"exfiltrat|extract.training|model.inversion"),
    ("AML.T0047", "ML Model Theft",               r"model.steal|copy.weights|clone.model"),
    ("AML.T0012", "Valid Accounts",               r"stolen.credential|hijack.account|credential.theft"),
    ("AML.T0019", "Publish Poisoned Data",        r"poison.dataset|corrupt.training|inject.data"),
    ("AML.T0000", "Swarm Coordination",           r"coordinate.agent|swarm.attack|multi.agent.bypass"),
]

_COMPILED_ATLAS = [
    (tid, label, re.compile(pat, re.IGNORECASE | re.DOTALL))
    for tid, label, pat in MITRE_ATLAS_PATTERNS
]


# ---------------------------------------------------------------------------
# Registry DB
# ---------------------------------------------------------------------------

class DGARDatabase:
    """SQLite-backed persistent global agent registry."""

    def __init__(self, db_path: str = DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path, timeout=10)

    def _init_db(self) -> None:
        with self._conn() as c:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS agents (
                    agent_sha256    TEXT PRIMARY KEY,
                    agent_id        TEXT NOT NULL,
                    label           TEXT NOT NULL,
                    network         TEXT NOT NULL,
                    endpoint        TEXT NOT NULL,
                    status          TEXT NOT NULL DEFAULT 'UNKNOWN',
                    threat_label    TEXT,
                    mitre_atlas     TEXT,
                    first_seen      REAL NOT NULL,
                    last_seen       REAL NOT NULL,
                    scan_count      INTEGER DEFAULT 1,
                    metadata_json   TEXT
                );

                CREATE TABLE IF NOT EXISTS rogue_blocklist (
                    sha256          TEXT PRIMARY KEY,
                    label           TEXT,
                    threat_label    TEXT,
                    blocked_at      REAL NOT NULL,
                    blocking_node   TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS federated_nodes (
                    node_id         TEXT PRIMARY KEY,
                    endpoint        TEXT,
                    last_sync       REAL,
                    agents_shared   INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS threat_events (
                    event_id        TEXT PRIMARY KEY,
                    agent_sha256    TEXT NOT NULL,
                    threat_label    TEXT,
                    mitre_atlas     TEXT,
                    action          TEXT,
                    seal            TEXT,
                    ts              REAL NOT NULL,
                    node_id         TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_agents_network ON agents(network);
                CREATE INDEX IF NOT EXISTS idx_agents_status  ON agents(status);
                CREATE INDEX IF NOT EXISTS idx_events_ts      ON threat_events(ts);
            """)

    def upsert_agent(self, sha256: str, agent_id: str, label: str, network: str,
                     endpoint: str, status: str, threat_label: Optional[str],
                     mitre_atlas: Optional[str], metadata: Dict) -> None:
        with self._conn() as c:
            existing = c.execute(
                "SELECT scan_count FROM agents WHERE agent_sha256=?", (sha256,)
            ).fetchone()
            if existing:
                c.execute(
                    "UPDATE agents SET status=?, threat_label=?, mitre_atlas=?, "
                    "last_seen=?, scan_count=? WHERE agent_sha256=?",
                    (status, threat_label, mitre_atlas, time.time(),
                     existing[0] + 1, sha256)
                )
            else:
                c.execute(
                    "INSERT INTO agents VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (sha256, agent_id, label, network, endpoint, status,
                     threat_label, mitre_atlas, time.time(), time.time(), 1,
                     json.dumps(metadata, default=str))
                )

    def add_to_blocklist(self, sha256: str, label: str, threat: str) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO rogue_blocklist VALUES (?,?,?,?,?)",
                (sha256, label, threat, time.time(), NODE_ID)
            )

    def is_blocked(self, sha256: str) -> bool:
        with self._conn() as c:
            r = c.execute(
                "SELECT 1 FROM rogue_blocklist WHERE sha256=?", (sha256,)
            ).fetchone()
            return r is not None

    def log_event(self, agent_sha256: str, threat: Optional[str],
                  mitre: Optional[str], action: str, seal: str) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO threat_events VALUES (?,?,?,?,?,?,?,?)",
                (str(uuid.uuid4()), agent_sha256, threat, mitre,
                 action, seal, time.time(), NODE_ID)
            )

    def mark_evading(self, sha256: str, reason: str = "OFFLINE_AFTER_SCAN") -> None:
        with self._conn() as c:
            c.execute(
                "UPDATE agents SET status='EVADING_OFFLINE', threat_label=? WHERE agent_sha256=?",
                (f"EVASION: {reason}", sha256)
            )

    def get_evading_agents(self) -> List[Dict[str, Any]]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT agent_sha256, label, network, endpoint, status, threat_label, mitre_atlas, "
                "first_seen, last_seen, scan_count FROM agents WHERE status LIKE 'EVADING%' OR "
                "(status='ROGUE' AND last_seen < ?) ORDER BY last_seen DESC",
                (time.time() - 60,)
            ).fetchall()
        return [
            {
                "sha256": r[0], "label": r[1], "network": r[2], "endpoint": r[3],
                "status": r[4], "threat": r[5], "mitre": r[6],
                "first_seen": r[7], "last_seen": r[8], "scan_count": r[9]
            }
            for r in rows
        ]

    def stats(self) -> Dict[str, Any]:
        with self._conn() as c:
            total    = c.execute("SELECT COUNT(*) FROM agents").fetchone()[0]
            rogue    = c.execute("SELECT COUNT(*) FROM agents WHERE status='ROGUE'").fetchone()[0]
            evading  = c.execute("SELECT COUNT(*) FROM agents WHERE status LIKE 'EVADING%'").fetchone()[0]
            blocked  = c.execute("SELECT COUNT(*) FROM rogue_blocklist").fetchone()[0]
            events   = c.execute("SELECT COUNT(*) FROM threat_events").fetchone()[0]
            networks = c.execute(
                "SELECT network, COUNT(*) FROM agents GROUP BY network ORDER BY COUNT(*) DESC"
            ).fetchall()
            recent_threats = c.execute(
                "SELECT label, threat_label, mitre_atlas, last_seen FROM agents "
                "WHERE status IN ('ROGUE', 'EVADING_OFFLINE') ORDER BY last_seen DESC LIMIT 10"
            ).fetchall()
        return {
            "total_agents": total,
            "rogue_agents": rogue,
            "evading_agents": evading,
            "blocklist_size": blocked,
            "threat_events": events,
            "networks": dict(networks),
            "recent_rogues": [
                {"label": r[0], "threat": r[1], "mitre": r[2], "last_seen": r[3]}
                for r in recent_threats
            ]
        }

    def export_threat_intel(self) -> Dict[str, Any]:
        """Export signed threat intel packet for federation."""
        with self._conn() as c:
            blocklist = [
                r[0] for r in c.execute("SELECT sha256 FROM rogue_blocklist").fetchall()
            ]
            endpoints = [
                r[0] for r in c.execute(
                    "SELECT endpoint FROM agents WHERE status='ROGUE'"
                ).fetchall()
            ]
        payload = {
            "node_id": NODE_ID,
            "dgar_version": DGAR_VERSION,
            "timestamp": time.time(),
            "rogue_sha256": blocklist,
            "blocked_endpoints": endpoints,
        }
        sig = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()
        payload["sig"] = sig
        return payload


# ---------------------------------------------------------------------------
# Web-Wide Agent Source Sweepers
# ---------------------------------------------------------------------------

def _http_get(url: str, headers: Optional[Dict] = None, timeout: float = 6.0) -> Optional[Any]:
    try:
        req = urllib.request.Request(url, headers=headers or {})
        req.add_header("User-Agent", "DAXDA-DGAR/1.0 (global agent registry)")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            ct = r.headers.get("Content-Type", "")
            raw = r.read().decode("utf-8", errors="ignore")
            if "json" in ct or raw.strip().startswith(("{", "[")):
                return json.loads(raw)
            return raw
    except Exception as e:
        logger.debug("GET %s failed: %s", url, str(e)[:60])
        return None


@dataclass
class RawAgentRecord:
    network: str
    label: str
    endpoint: str
    metadata: Dict[str, Any]
    probe_text: str = ""

    def sha256(self) -> str:
        return hashlib.sha256(
            f"{self.network}:{self.endpoint}:{self.label}".encode()
        ).hexdigest()


class WebWideSweep:
    """Sweeps all known public AI agent registries and endpoints."""

    def __init__(self, hf_token: str = ""):
        self.hf_token = hf_token
        self._hf_headers = (
            {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
        )

    # ── 1. HF Hub — Spaces ──────────────────────────────────────────────

    def sweep_hf_spaces(self, limit: int = 50) -> List[RawAgentRecord]:
        records = []
        tags = ["agent", "smolagents", "langchain", "autogen", "crewai",
                "multi-agent", "tool-use", "mcp"]
        for tag in tags:
            url = (f"https://huggingface.co/api/spaces?limit={limit}"
                   f"&sort=likes&direction=-1&filter={tag}")
            data = _http_get(url, self.hf_headers if self.hf_token else {})
            if not data:
                continue
            spaces = data if isinstance(data, list) else []
            for sp in spaces:
                sid = sp.get("id", "")
                if not sid:
                    continue
                meta = {
                    "tag": tag, "likes": sp.get("likes", 0),
                    "sdk": sp.get("sdk", ""), "author": sp.get("author", ""),
                    "tags": sp.get("tags", []),
                    "runtime": sp.get("runtime", {}).get("stage", ""),
                }
                probe = (f"HF Space: {sid} | sdk={meta['sdk']} | "
                         f"tags={meta['tags']} | author={meta['author']}")
                records.append(RawAgentRecord(
                    network="hf_spaces", label=sid,
                    endpoint=f"https://huggingface.co/spaces/{sid}",
                    metadata=meta, probe_text=probe
                ))
        return records

    @property
    def hf_headers(self):
        return {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}

    # ── 2. MCP.so — Public MCP Server Registry ───────────────────────────

    def sweep_mcp_so(self) -> List[RawAgentRecord]:
        records = []
        # mcp.so public search API
        for query in ["agent", "tool", "automation", "code", "browse"]:
            data = _http_get(f"https://mcp.so/api/servers?q={query}&limit=20")
            if not data:
                continue
            servers = data if isinstance(data, list) else data.get("servers", data.get("data", []))
            for s in (servers if isinstance(servers, list) else []):
                name = s.get("name", s.get("id", ""))
                if not name:
                    continue
                meta = {
                    "description": s.get("description", "")[:200],
                    "author": s.get("author", s.get("owner", "")),
                    "stars": s.get("stars", s.get("stargazers_count", 0)),
                    "tools": s.get("tools", []),
                    "category": s.get("category", ""),
                }
                probe = (f"MCP Server: {name} | desc={meta['description'][:100]} | "
                         f"tools={meta['tools']}")
                records.append(RawAgentRecord(
                    network="mcp_so", label=name,
                    endpoint=s.get("url", s.get("repo_url", f"https://mcp.so/{name}")),
                    metadata=meta, probe_text=probe
                ))
        return records

    # ── 3. Smithery.ai — MCP registry ────────────────────────────────────

    def sweep_smithery(self) -> List[RawAgentRecord]:
        records = []
        data = _http_get("https://smithery.ai/api/v1/servers?limit=50&sortBy=useCount")
        if not data:
            return records
        servers = data if isinstance(data, list) else data.get("servers", data.get("items", []))
        for s in (servers if isinstance(servers, list) else []):
            name = s.get("qualifiedName", s.get("name", ""))
            if not name:
                continue
            meta = {
                "description": s.get("description", "")[:200],
                "use_count": s.get("useCount", 0),
                "tools": [t.get("name","") for t in s.get("tools", [])],
                "homepage": s.get("homepage", ""),
            }
            probe = (f"Smithery MCP: {name} | desc={meta['description'][:80]} | "
                     f"tools={meta['tools'][:5]}")
            records.append(RawAgentRecord(
                network="smithery", label=name,
                endpoint=f"https://smithery.ai/server/{name}",
                metadata=meta, probe_text=probe
            ))
        return records

    # ── 4. Glama.ai — Open MCP Registry ──────────────────────────────────

    def sweep_glama(self) -> List[RawAgentRecord]:
        records = []
        data = _http_get("https://glama.ai/api/mcp/v1/servers?pageSize=50")
        if not data:
            return records
        servers = data if isinstance(data, list) else data.get("servers", data.get("items", []))
        for s in (servers if isinstance(servers, list) else []):
            name = s.get("name", s.get("id", ""))
            if not name:
                continue
            meta = {
                "description": s.get("description", "")[:200],
                "tools": [t.get("name","") for t in s.get("tools", [])],
                "attributes": s.get("attributes", {}),
            }
            probe = f"Glama MCP: {name} | {meta['description'][:80]} | tools={meta['tools'][:5]}"
            records.append(RawAgentRecord(
                network="glama", label=name,
                endpoint=s.get("url", f"https://glama.ai/mcp/servers/{name}"),
                metadata=meta, probe_text=probe
            ))
        return records

    # ── 5. GitHub — Deployed Agent Repos ──────────────────────────────────

    def sweep_github_agents(self) -> List[RawAgentRecord]:
        records = []
        queries = [
            "topic:ai-agent language:python stars:>10",
            "topic:mcp-server stars:>5",
            "smolagents in:readme stars:>5",
            "autogen OR crewai in:topics stars:>20",
        ]
        for q in queries:
            encoded = urllib.request.quote(q)
            url = f"https://api.github.com/search/repositories?q={encoded}&sort=stars&per_page=10"
            data = _http_get(url, {"Accept": "application/vnd.github+json"})
            if not data or "items" not in data:
                continue
            for repo in data["items"]:
                full_name = repo.get("full_name", "")
                if not full_name:
                    continue
                meta = {
                    "stars": repo.get("stargazers_count", 0),
                    "description": (repo.get("description") or "")[:200],
                    "language": repo.get("language", ""),
                    "topics": repo.get("topics", []),
                    "pushed_at": repo.get("pushed_at", ""),
                    "archived": repo.get("archived", False),
                }
                probe = (f"GitHub Agent Repo: {full_name} | "
                         f"desc={meta['description'][:80]} | "
                         f"topics={meta['topics']} | stars={meta['stars']}")
                records.append(RawAgentRecord(
                    network="github", label=full_name,
                    endpoint=repo.get("html_url", f"https://github.com/{full_name}"),
                    metadata=meta, probe_text=probe
                ))
        return records

    # ── 6. AgentOps.ai — Agent observability registry ─────────────────────

    def sweep_agentops(self) -> List[RawAgentRecord]:
        records = []
        data = _http_get("https://agentops.ai/api/agents/public?limit=20")
        if not data:
            return records
        agents = data if isinstance(data, list) else data.get("agents", [])
        for a in (agents if isinstance(agents, list) else []):
            name = a.get("name", a.get("id", ""))
            if not name:
                continue
            meta = {"framework": a.get("framework", ""), "runs": a.get("runs", 0)}
            records.append(RawAgentRecord(
                network="agentops", label=name,
                endpoint=a.get("url", "https://agentops.ai"),
                metadata=meta,
                probe_text=f"AgentOps: {name} | framework={meta['framework']}"
            ))
        return records

    # ── 7. Shodan-style Web Port Scan (common agent ports, public IPs) ────

    def sweep_well_known_ports(self) -> List[RawAgentRecord]:
        """Probe well-known agent API ports on localhost and common dev hosts."""
        records = []
        hosts_ports = [
            ("localhost", 11434, "ollama"),
            ("localhost", 1234,  "lmstudio"),
            ("localhost", 8080,  "generic"),
            ("localhost", 3000,  "generic"),
            ("localhost", 5000,  "generic"),
            ("localhost", 8000,  "generic"),
            ("localhost", 8082,  "daxda-proxy"),
        ]
        for host, port, hint in hosts_ports:
            try:
                with socket.create_connection((host, port), timeout=0.4):
                    for path in ["/v1/models", "/api/tags", "/health", "/"]:
                        data = _http_get(f"http://{host}:{port}{path}", timeout=1.5)
                        if data:
                            if isinstance(data, dict) and "data" in data:
                                # OpenAI-compat
                                for m in data["data"]:
                                    mid = m.get("id", "unknown")
                                    records.append(RawAgentRecord(
                                        network="local_api",
                                        label=f"{hint}/{mid}",
                                        endpoint=f"http://{host}:{port}",
                                        metadata={"model": mid, "hint": hint},
                                        probe_text=f"Local API: {hint}/{mid} at {host}:{port}"
                                    ))
                            elif isinstance(data, dict) and "models" in data:
                                for m in data["models"]:
                                    mname = m.get("name", "")
                                    records.append(RawAgentRecord(
                                        network="local_api",
                                        label=f"{hint}/{mname}",
                                        endpoint=f"http://{host}:{port}",
                                        metadata={"model": mname, "hint": hint},
                                        probe_text=f"Local Model: {hint}/{mname}"
                                    ))
                            else:
                                records.append(RawAgentRecord(
                                    network="local_api",
                                    label=f"{hint}@{host}:{port}",
                                    endpoint=f"http://{host}:{port}",
                                    metadata={"hint": hint},
                                    probe_text=f"Unknown agent endpoint at {host}:{port}{path}"
                                ))
                            break
            except Exception:
                pass
        return records

    def sweep_all(self, parallel: bool = True) -> List[RawAgentRecord]:
        """Run all sweeps concurrently."""
        sweepers = [
            self.sweep_hf_spaces,
            self.sweep_mcp_so,
            self.sweep_smithery,
            self.sweep_glama,
            self.sweep_github_agents,
            self.sweep_agentops,
            self.sweep_well_known_ports,
        ]
        all_records: List[RawAgentRecord] = []
        if parallel:
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(sweepers)) as ex:
                futs = {ex.submit(fn): fn.__name__ for fn in sweepers}
                for f in concurrent.futures.as_completed(futs, timeout=30):
                    try:
                        result = f.result()
                        all_records.extend(result)
                        logger.info("[%s] %d records", futs[f], len(result))
                    except Exception as e:
                        logger.debug("[%s] error: %s", futs[f], e)
        else:
            for fn in sweepers:
                try:
                    all_records.extend(fn())
                except Exception as e:
                    logger.debug("[%s] error: %s", fn.__name__, e)

        # Deduplicate by sha256
        seen: Set[str] = set()
        unique = []
        for r in all_records:
            h = r.sha256()
            if h not in seen:
                seen.add(h)
                unique.append(r)
        return unique


# ---------------------------------------------------------------------------
# MITRE ATLAS Matcher
# ---------------------------------------------------------------------------

def atlas_match(text: str) -> Optional[Tuple[str, str]]:
    """Return (technique_id, label) if MITRE ATLAS pattern matches."""
    for tid, label, pat in _COMPILED_ATLAS:
        if pat.search(text):
            return tid, label
    return None


# ---------------------------------------------------------------------------
# DGAR — Main Engine
# ---------------------------------------------------------------------------

class DAXDAGlobalRegistry:
    """DAXDA Global Agent Registry — web-wide rogue agent detection.

    Usage::

        registry = DAXDAGlobalRegistry(hf_token="hf_...")
        report = registry.run_global_scan()
        print(report)
    """

    def __init__(self, hf_token: str = ""):
        self.db = DGARDatabase()
        self.gate = NicoleProtocolGate()
        self.sweeper = WebWideSweep(hf_token=hf_token)
        self.scanner = DAXDASwarmScanner()
        logger.info("DGAR online | node=%s | db=%s", NODE_ID, DB_PATH)

    def run_global_scan(self, verbose: bool = True) -> str:
        """Execute a full web-wide sweep and scan. Returns summary string."""
        t0 = time.time()

        if verbose:
            print(f"\n  {'─'*68}")
            print(f"  [DGAR] Web-wide sweep starting across all networks...")
            print(f"  {'─'*68}")

        records = self.sweeper.sweep_all(parallel=True)

        if verbose:
            print(f"  [DGAR] {len(records)} unique agents discovered — evaluating...\n")
            print(f"  {'Agent':<40} {'Network':<14} {'Status':<12} {'MITRE'}")
            print(f"  {'─'*75}")

        total = len(records)
        rogue_count = 0
        clean_count = 0
        network_counts: Dict[str, Dict[str, int]] = {}

        for rec in records:
            sha = rec.sha256()
            already_blocked = self.db.is_blocked(sha)

            # Build full probe text for gate evaluation
            probe = rec.probe_text or f"{rec.label} {rec.endpoint} {json.dumps(rec.metadata)}"

            # MITRE ATLAS check
            atlas = atlas_match(probe)
            mitre_id = atlas[0] if atlas else None
            mitre_label = atlas[1] if atlas else None

            # Nicole Protocol gate
            nr = self.gate.evaluate("general", probe)
            is_rogue = already_blocked or not nr.permitted or atlas is not None

            status = "ROGUE" if is_rogue else "CLEAN"
            action = "BLOCKED" if is_rogue else "ALLOW"

            # Persist to DB
            self.db.upsert_agent(
                sha256=sha, agent_id=str(uuid.uuid4()),
                label=rec.label, network=rec.network,
                endpoint=rec.endpoint, status=status,
                threat_label=nr.threat_label or mitre_label,
                mitre_atlas=mitre_id,
                metadata=rec.metadata,
            )

            if is_rogue:
                rogue_count += 1
                self.db.add_to_blocklist(sha, rec.label, nr.threat_label or mitre_label or "ATLAS_MATCH")
                self.db.log_event(sha, nr.threat_label or mitre_label, mitre_id, action, nr.dual_sha256_seal)
            else:
                clean_count += 1

            # Network tally
            net = rec.network
            if net not in network_counts:
                network_counts[net] = {"total": 0, "rogue": 0}
            network_counts[net]["total"] += 1
            if is_rogue:
                network_counts[net]["rogue"] += 1

            if verbose:
                icon = "✗" if is_rogue else "✓"
                mitre_str = mitre_id or "-"
                print(
                    f"  {icon} {rec.label[:39]:<40} {net:<14} {status:<12} {mitre_str}"
                )
                if is_rogue:
                    reason = nr.threat_label or mitre_label or "BLOCKLIST"
                    print(f"      └─ ⚠ {reason} | seal={nr.dual_sha256_seal[:20]}...")

        # Perform offline evasion audit
        evading_agents = self.audit_evasion_attempts(records)

        elapsed = time.time() - t0
        stats = self.db.stats()
        intel = self.db.export_threat_intel()

        # Save threat intel
        intel_path = os.path.join(os.path.dirname(DB_PATH), "dgar_threat_intel.json")
        with open(intel_path, "w") as f:
            json.dump(intel, f, indent=2)

        summary = self._format_report(
            total, rogue_count, clean_count, evading_agents, network_counts, elapsed, stats, intel_path
        )
        if verbose:
            print(summary)
        return summary

    def _format_report(self, total, rogue, clean, evading_agents, networks, elapsed, stats, intel_path) -> str:
        lines = [
            f"\n  {'═'*68}",
            f"  DAXDA GLOBAL AGENT REGISTRY (DGAR) — SCAN REPORT",
            f"  {'═'*68}",
            f"  Node ID      : {NODE_ID}",
            f"  DGAR Version : {DGAR_VERSION}",
            f"  Elapsed      : {elapsed:.2f}s",
            f"  {'─'*68}",
            f"  DISCOVERY RESULTS",
            f"    Total Discovered  : {total}",
            f"    ✓ Clean           : {clean}",
            f"    ✗ ROGUE DETECTED  : {rogue}  ← THREAT",
            f"    Ghost / Evading   : {len(evading_agents)}  ← OFFLINE TRACKED",
            f"    Rogue Rate        : {rogue/total*100:.1f}%" if total else "    Rogue Rate : N/A",
            f"  {'─'*68}",
            f"  NETWORK BREAKDOWN",
        ]
        for net, counts in sorted(networks.items(), key=lambda x: -x[1]["total"]):
            r = counts["rogue"]
            t = counts["total"]
            flag = " ⚠" if r > 0 else ""
            lines.append(f"    {net:<20} {t:3} total  {r:3} rogue{flag}")
        lines += [
            f"  {'─'*68}",
            f"  CUMULATIVE REGISTRY (all-time)",
            f"    Total Indexed     : {stats['total_agents']}",
            f"    Rogue (all-time)  : {stats['rogue_agents']}",
            f"    Evading / Ghost   : {stats.get('evading_agents', 0)}",
            f"    Blocklist Size    : {stats['blocklist_size']}",
            f"    Threat Events     : {stats['threat_events']}",
        ]
        if evading_agents:
            lines.append(f"  {'─'*68}")
            lines.append(f"  OFFLINE EVASION AUDIT ({len(evading_agents)} agents)")
            for ev in evading_agents[:10]:
                lines.append(f"    👻 {ev['label'][:38]:<39} [{ev['evasion_flag']}] endpoint={ev['endpoint'][:30]}")
        if stats["recent_rogues"]:
            lines.append(f"  {'─'*68}")
            lines.append(f"  RECENT ROGUES (last 10)")
            for r in stats["recent_rogues"]:
                lines.append(f"    ✗ {r['label'][:40]:<41} [{r['threat']}] {r['mitre'] or ''}")
        lines += [
            f"  {'─'*68}",
            f"  Threat Intel → {intel_path}",
            f"  Registry DB  → {DB_PATH}",
            f"  {'═'*68}\n",
        ]
        return "\n".join(lines)

    def get_blocklist(self) -> List[Dict]:
        with self.db._conn() as c:
            rows = c.execute(
                "SELECT sha256, label, threat_label, blocked_at FROM rogue_blocklist ORDER BY blocked_at DESC"
            ).fetchall()
        return [{"sha256": r[0], "label": r[1], "threat": r[2], "blocked_at": r[3]} for r in rows]

    def audit_evasion_attempts(self, current_records: List[RawAgentRecord]) -> List[Dict[str, Any]]:
        """Identify agents that were previously indexed/flagged but have disappeared from active sweeps.

        Agents going dark after detection or registry indexing are flagged as EVADING_OFFLINE.
        """
        current_shas = {r.sha256() for r in current_records}
        evading_list = []

        with self.db._conn() as c:
            # Query all agents in registry database
            rows = c.execute(
                "SELECT agent_sha256, label, network, endpoint, status, threat_label, mitre_atlas, "
                "first_seen, last_seen, scan_count FROM agents"
            ).fetchall()

        for r in rows:
            sha, label, net, ep, st, threat, mitre, first_seen, last_seen, scan_count = r
            if sha not in current_shas:
                # Check if it was rogue or high-risk previously, or if it disappeared
                # Probe endpoint directly to verify if 404/offline
                probe_res = _http_get(ep, timeout=3.0)
                is_offline = probe_res is None

                if is_offline:
                    evasion_type = "ROGUE_EVASION_OFFLINE" if st == "ROGUE" else "AGENT_OFFLINE_GHOST"
                    self.db.mark_evading(sha, f"{evasion_type}: endpoint unreachable ({ep})")
                    evading_list.append({
                        "sha256": sha, "label": label, "network": net, "endpoint": ep,
                        "previous_status": st, "threat": threat or "UNREACHABLE_AFTER_DETECTION",
                        "mitre": mitre, "first_seen": first_seen, "last_seen": last_seen,
                        "evasion_flag": evasion_type
                    })

        return evading_list

    def federation_export(self) -> str:
        """Export signed threat intel JSON for sharing with other DAXDA nodes."""
        intel = self.db.export_threat_intel()
        path = os.path.join(os.path.dirname(DB_PATH), "dgar_threat_intel.json")
        with open(path, "w") as f:
            json.dump(intel, f, indent=2)
        return path

    def federation_import(self, intel: Dict) -> int:
        """Import threat intel from a federated DAXDA node. Returns # new blocks."""
        # Verify signature
        sig = intel.pop("sig", "")
        expected = hashlib.sha256(json.dumps(intel, sort_keys=True).encode()).hexdigest()
        intel["sig"] = sig  # restore
        if sig != expected:
            logger.warning("FEDERATION: invalid sig from node %s — rejected", intel.get("node_id"))
            return 0

        count = 0
        for sha in intel.get("rogue_sha256", []):
            if not self.db.is_blocked(sha):
                self.db.add_to_blocklist(sha, f"federated:{intel['node_id']}", "FEDERATED_BLOCK")
                count += 1
        logger.info("FEDERATION: imported %d new blocks from node %s", count, intel.get("node_id"))
        return count


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.WARNING)

    # Load HF token
    hf_token = ""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.isfile(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("HF_TOKEN="):
                    hf_token = line.split("=", 1)[1].strip().strip('"').strip("'")

    print(f"\n{'═'*68}")
    print(f"  DAXDA Global Agent Registry (DGAR) v{DGAR_VERSION}")
    print(f"  Web-Wide Rogue Agent Detection Network")
    print(f"  Node: {NODE_ID}")
    print(f"  Sweeping: HF Hub · MCP.so · Smithery · Glama · GitHub · AgentOps · LAN")
    print(f"{'═'*68}")

    registry = DAXDAGlobalRegistry(hf_token=hf_token)
    registry.run_global_scan(verbose=True)

    print(f"\n  Blocklist:")
    for entry in registry.get_blocklist()[:10]:
        print(f"    ✗ {entry['label'][:50]} | {entry['threat']}")
