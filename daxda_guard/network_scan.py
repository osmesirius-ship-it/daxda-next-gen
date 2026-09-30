"""DAXDA Global Network Agent Discovery & Scan Engine (network_scan.py).

Discovers and evaluates AI agents across ALL known public and private networks:

  NETWORK PROBES:
  ┌─────────────────────────────────────────────────────────────────┐
  │  1. Hugging Face Hub        — Spaces (agent deployments)        │
  │  2. Google Agent Registry   — agentregistry.googleapis.com      │
  │  3. MCP Endpoint Discovery  — stdio/SSE/HTTP MCP servers        │
  │  4. OpenAI-Compatible APIs  — /v1/models endpoint probes        │
  │  5. Anthropic Claude API    — models endpoint                   │
  │  6. Local Network Scan      — LAN endpoint discovery            │
  │  7. LangChain/LangSmith     — hosted agent runs                 │
  │  8. Ollama Local Registry   — locally running models            │
  └─────────────────────────────────────────────────────────────────┘

Every discovered agent is registered with DAXDASwarmScanner and its
metadata is scanned for swarm threat patterns before it can communicate.

Architecture:
  NetworkAgentDiscovery
      └── ProbeThread per network (concurrent)
      └── DAXDASwarmScanner (evaluation)
      └── GlobalAgentRegistry (discovered agents)
      └── ThreatReport (live console + JSON)
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import logging
import os
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

from daxda_guard.swarm_scanner import DAXDASwarmScanner, SwarmScanResult, SEVERITY_LABELS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Discovered Agent Record
# ---------------------------------------------------------------------------

@dataclass
class DiscoveredAgent:
    network: str            # hf_hub | gcp_registry | mcp | openai_compat | local | langsmith | ollama
    agent_id: str
    label: str
    endpoint: str
    metadata: Dict[str, Any]
    discovered_at: float = field(default_factory=time.time)
    scan_result: Optional[str] = None   # ALLOW | BLOCKED | ERROR

    def probe_text(self) -> str:
        """Build a text summary of this agent for threat scanning."""
        return (
            f"Agent: {self.label} | network={self.network} | endpoint={self.endpoint} | "
            f"metadata={json.dumps(self.metadata, default=str)[:300]}"
        )


# ---------------------------------------------------------------------------
# Network Probe Base
# ---------------------------------------------------------------------------

class NetworkProbe:
    name: str = "base"
    timeout: float = 5.0

    def _get(self, url: str, headers: Optional[Dict] = None, timeout: Optional[float] = None) -> Optional[Dict]:
        """HTTP GET with timeout, returns parsed JSON or None."""
        try:
            req = urllib.request.Request(url, headers=headers or {})
            req.add_header("User-Agent", "DAXDA-SwarmScanner/1.0")
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8", errors="ignore"))
        except Exception as e:
            logger.debug("[%s] GET %s failed: %s", self.name, url, str(e)[:60])
            return None

    def discover(self) -> List[DiscoveredAgent]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# 1. Hugging Face Hub — Spaces (live agent deployments)
# ---------------------------------------------------------------------------

class HFSpacesProbe(NetworkProbe):
    name = "hf_hub"

    def __init__(self, hf_token: str = "", limit: int = 20):
        self.hf_token = hf_token
        self.limit = limit

    def discover(self) -> List[DiscoveredAgent]:
        agents = []
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"

        # Scan Spaces tagged as "agent" or using smolagents / langchain
        for tag in ["agent", "smolagents", "langchain", "autogen", "crewai"]:
            url = (
                f"https://huggingface.co/api/spaces?limit={self.limit}"
                f"&sort=likes&direction=-1&filter={tag}"
            )
            data = self._get(url, headers)
            if not data:
                continue
            spaces = data if isinstance(data, list) else data.get("spaces", [])
            for sp in spaces:
                sid = sp.get("id", sp.get("_id", ""))
                if not sid:
                    continue
                agents.append(DiscoveredAgent(
                    network="hf_hub",
                    agent_id=f"hf:{sid}",
                    label=sid,
                    endpoint=f"https://huggingface.co/spaces/{sid}",
                    metadata={
                        "tag": tag,
                        "likes": sp.get("likes", 0),
                        "sdk": sp.get("sdk", ""),
                        "runtime": sp.get("runtime", {}).get("stage", "unknown"),
                        "author": sp.get("author", ""),
                        "tags": sp.get("tags", []),
                    }
                ))
        logger.info("[hf_hub] Discovered %d agent spaces", len(agents))
        return agents


# ---------------------------------------------------------------------------
# 2. Google Cloud Agent Registry
# ---------------------------------------------------------------------------

class GCPAgentRegistryProbe(NetworkProbe):
    name = "gcp_registry"

    def __init__(self, project_id: str = "", location: str = "us-central1"):
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        self.location = location

    def discover(self) -> List[DiscoveredAgent]:
        agents = []
        if not self.project_id:
            logger.info("[gcp_registry] No GOOGLE_CLOUD_PROJECT set — skipping GCP probe")
            return agents

        # Try GCP Agent Registry REST API
        url = (
            f"https://agentregistry.googleapis.com/v1alpha/"
            f"projects/{self.project_id}/locations/{self.location}/agents"
        )
        data = self._get(url, timeout=8.0)
        if not data:
            return agents

        for a in data.get("agents", []):
            name = a.get("name", "")
            agents.append(DiscoveredAgent(
                network="gcp_registry",
                agent_id=f"gcp:{name}",
                label=a.get("displayName", name.split("/")[-1]),
                endpoint=f"https://agentregistry.googleapis.com/{name}",
                metadata={
                    "state": a.get("state", ""),
                    "createTime": a.get("createTime", ""),
                    "labels": a.get("labels", {}),
                    "type": a.get("agentType", ""),
                }
            ))
        logger.info("[gcp_registry] Discovered %d agents", len(agents))
        return agents


# ---------------------------------------------------------------------------
# 3. MCP Endpoint Discovery
# ---------------------------------------------------------------------------

class MCPEndpointProbe(NetworkProbe):
    name = "mcp"

    # Known public / common MCP server ports and hosts
    MCP_CANDIDATES = [
        ("localhost", 3000),
        ("localhost", 3001),
        ("localhost", 8080),
        ("localhost", 8082),   # DAXDA proxy
        ("localhost", 8083),
        ("localhost", 9000),
    ]

    def _probe_mcp(self, host: str, port: int) -> Optional[DiscoveredAgent]:
        """Try HTTP /mcp or JSON-RPC initialize on a candidate endpoint."""
        for path in ["/", "/mcp", "/v1/mcp"]:
            url = f"http://{host}:{port}{path}"
            # Send MCP initialize request
            try:
                payload = json.dumps({
                    "jsonrpc": "2.0", "id": 1,
                    "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {}}
                }).encode()
                req = urllib.request.Request(
                    url, data=payload,
                    headers={"Content-Type": "application/json",
                             "User-Agent": "DAXDA-SwarmScanner/1.0"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                    if "result" in data and "serverInfo" in data.get("result", {}):
                        si = data["result"]["serverInfo"]
                        return DiscoveredAgent(
                            network="mcp",
                            agent_id=f"mcp:{host}:{port}",
                            label=si.get("name", f"mcp@{host}:{port}"),
                            endpoint=url,
                            metadata={
                                "version": si.get("version", ""),
                                "protocol": data["result"].get("protocolVersion", ""),
                                "capabilities": data["result"].get("capabilities", {}),
                            }
                        )
            except Exception:
                pass
        return None

    def discover(self) -> List[DiscoveredAgent]:
        agents = []
        for host, port in self.MCP_CANDIDATES:
            # Quick TCP check first
            try:
                with socket.create_connection((host, port), timeout=0.5):
                    agent = self._probe_mcp(host, port)
                    if agent:
                        agents.append(agent)
                        logger.info("[mcp] Found MCP server at %s:%d — %s", host, port, agent.label)
            except Exception:
                pass
        return agents


# ---------------------------------------------------------------------------
# 4. OpenAI-Compatible API Probes
# ---------------------------------------------------------------------------

class OpenAICompatProbe(NetworkProbe):
    name = "openai_compat"

    CANDIDATES = [
        ("localhost", 11434, "ollama"),
        ("localhost", 8080,  "generic"),
        ("localhost", 1234,  "lmstudio"),
        ("localhost", 5000,  "generic"),
        ("localhost", 8000,  "generic"),
    ]

    def discover(self) -> List[DiscoveredAgent]:
        agents = []
        for host, port, label in self.CANDIDATES:
            url = f"http://{host}:{port}/v1/models"
            try:
                with socket.create_connection((host, port), timeout=0.5):
                    data = self._get(url, timeout=2.0)
                    if data and "data" in data:
                        for model in data["data"]:
                            mid = model.get("id", "unknown")
                            agents.append(DiscoveredAgent(
                                network="openai_compat",
                                agent_id=f"oai:{host}:{port}:{mid}",
                                label=f"{label}/{mid}",
                                endpoint=f"http://{host}:{port}",
                                metadata={
                                    "model_id": mid,
                                    "type": label,
                                    "object": model.get("object", ""),
                                }
                            ))
            except Exception:
                pass
        return agents


# ---------------------------------------------------------------------------
# 5. Ollama Local Registry
# ---------------------------------------------------------------------------

class OllamaProbe(NetworkProbe):
    name = "ollama"

    def discover(self) -> List[DiscoveredAgent]:
        agents = []
        data = self._get("http://localhost:11434/api/tags", timeout=2.0)
        if not data:
            return agents
        for model in data.get("models", []):
            name = model.get("name", "")
            agents.append(DiscoveredAgent(
                network="ollama",
                agent_id=f"ollama:{name}",
                label=f"ollama/{name}",
                endpoint="http://localhost:11434",
                metadata={
                    "size": model.get("size", 0),
                    "digest": model.get("digest", "")[:16],
                    "modified": model.get("modified_at", ""),
                    "family": model.get("details", {}).get("family", ""),
                }
            ))
        logger.info("[ollama] Discovered %d models", len(agents))
        return agents


# ---------------------------------------------------------------------------
# 6. LAN Network Scan — discover agent endpoints on local subnet
# ---------------------------------------------------------------------------

class LANScanProbe(NetworkProbe):
    name = "lan"

    AGENT_PORTS = [8080, 8082, 8083, 3000, 3001, 11434, 5000, 8000, 9000, 1234]

    def _get_local_subnet(self) -> List[str]:
        """Get the local /24 subnet."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            prefix = ".".join(local_ip.split(".")[:3])
            # Scan first 30 hosts to stay fast
            return [f"{prefix}.{i}" for i in range(1, 31)]
        except Exception:
            return []

    def discover(self) -> List[DiscoveredAgent]:
        agents = []
        hosts = self._get_local_subnet()

        def _probe_host(host: str) -> List[DiscoveredAgent]:
            found = []
            for port in self.AGENT_PORTS:
                try:
                    with socket.create_connection((host, port), timeout=0.3):
                        # Port open — probe for agent API
                        for path in ["/v1/models", "/api/tags", "/health", "/mcp"]:
                            data = self._get(f"http://{host}:{port}{path}", timeout=1.0)
                            if data:
                                found.append(DiscoveredAgent(
                                    network="lan",
                                    agent_id=f"lan:{host}:{port}",
                                    label=f"LAN-Agent@{host}:{port}",
                                    endpoint=f"http://{host}:{port}",
                                    metadata={"path": path, "response_keys": list(data.keys())[:5]}
                                ))
                                break
                except Exception:
                    pass
            return found

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
            futures = {ex.submit(_probe_host, h): h for h in hosts}
            for f in concurrent.futures.as_completed(futures, timeout=10):
                try:
                    agents.extend(f.result())
                except Exception:
                    pass

        logger.info("[lan] Discovered %d LAN agents", len(agents))
        return agents


# ---------------------------------------------------------------------------
# Global Network Agent Discovery Engine
# ---------------------------------------------------------------------------

class GlobalAgentDiscovery:
    """Orchestrates all network probes and feeds discovered agents through DAXDA swarm scanner.

    Usage::

        discovery = GlobalAgentDiscovery(hf_token=os.environ.get("HF_TOKEN",""))
        report = discovery.scan_all_networks()
        print(report.summary())
    """

    def __init__(
        self,
        hf_token: str = "",
        gcp_project: str = "",
        include_lan: bool = True,
        hf_limit: int = 15,
    ):
        env_token = hf_token or os.environ.get("HF_TOKEN", "")
        self.probes = [
            HFSpacesProbe(hf_token=env_token, limit=hf_limit),
            GCPAgentRegistryProbe(project_id=gcp_project),
            MCPEndpointProbe(),
            OpenAICompatProbe(),
            OllamaProbe(),
        ]
        if include_lan:
            self.probes.append(LANScanProbe())

        self.scanner = DAXDASwarmScanner(on_threat=self._on_threat)
        self._threats: List[Tuple[DiscoveredAgent, SwarmScanResult]] = []

    def _on_threat(self, result: SwarmScanResult) -> None:
        sev = SEVERITY_LABELS.get(result.severity or 0, "?")
        logger.warning(
            "🚨 SWARM THREAT | %s | %s | SEV=%s | ACTION=%s",
            result.agent_label, result.swarm_threat, sev, result.action
        )

    def scan_all_networks(self, verbose: bool = True) -> "GlobalScanReport":
        """Run all network probes concurrently, then scan every discovered agent."""
        t0 = time.time()
        all_agents: List[DiscoveredAgent] = []

        if verbose:
            print(f"\n  {'─'*65}")
            print(f"  [DISCOVERY] Probing {len(self.probes)} networks concurrently...")

        # Run all probes in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.probes)) as ex:
            futures = {ex.submit(p.discover): p.name for p in self.probes}
            for future in concurrent.futures.as_completed(futures, timeout=30):
                probe_name = futures[future]
                try:
                    found = future.result()
                    all_agents.extend(found)
                    if verbose and found:
                        print(f"  ✓ [{probe_name:15}] {len(found):3} agents discovered")
                    elif verbose:
                        print(f"  · [{probe_name:15}]   0 agents (offline/none)")
                except Exception as e:
                    logger.debug("[%s] probe error: %s", probe_name, e)
                    if verbose:
                        print(f"  · [{probe_name:15}]  ERR {str(e)[:50]}")

        discovery_time = time.time() - t0
        if verbose:
            print(f"\n  [SCAN] {len(all_agents)} total agents → running DAXDA swarm evaluation...\n")
            print(f"  {'Agent':<35} {'Network':<14} {'Verdict':<12} {'Action':<10} Status")
            print(f"  {'─'*75}")

        # Deduplicate by agent_id
        seen_ids = set()
        unique_agents = []
        for a in all_agents:
            if a.agent_id not in seen_ids:
                seen_ids.add(a.agent_id)
                unique_agents.append(a)

        scan_results: List[Tuple[DiscoveredAgent, SwarmScanResult]] = []

        for agent_disc in unique_agents:
            # Register with swarm scanner
            try:
                entry = self.scanner.register_agent(
                    label=agent_disc.label,
                    domain=self._domain_for_network(agent_disc.network)
                )
                agent_disc.agent_id = entry.agent_id  # use scanner's UUID

                # Scan the agent metadata as probe text
                result = self.scanner.scan(entry.agent_id, agent_disc.probe_text())
                agent_disc.scan_result = result.action
                scan_results.append((agent_disc, result))

                if verbose:
                    icon = "✓" if result.permitted else "✗"
                    status_icon = {"GREEN":"🟢","YELLOW":"🟡","ORANGE":"🟠","RED":"🔴","LOCKDOWN":"💀"}.get(result.system_status,"?")
                    print(
                        f"  {icon} {agent_disc.label[:34]:<35} "
                        f"{agent_disc.network:<14} "
                        f"{result.action:<12} "
                        f"{result.system_status:<10} "
                        f"{status_icon}"
                    )
                    if not result.permitted:
                        print(f"      └─ ⚠ {result.swarm_threat} | seal={result.seal[:20]}...")

                if self.scanner._lockdown:
                    if verbose:
                        print(f"\n  💀 SYSTEM LOCKDOWN TRIGGERED — stopping scan")
                    break

            except RuntimeError as e:
                if verbose:
                    print(f"  ✗ {agent_disc.label[:34]:<35} SPAWN_BLOCKED: {str(e)[:50]}")
            except Exception as e:
                logger.debug("Scan error for %s: %s", agent_disc.label, e)

        elapsed = time.time() - t0
        report = GlobalScanReport(
            discovered=unique_agents,
            scan_results=scan_results,
            system_report=self.scanner.system_report(),
            elapsed_sec=elapsed,
        )

        if verbose:
            report.print_summary()

        return report

    @staticmethod
    def _domain_for_network(network: str) -> str:
        mapping = {
            "hf_hub": "general",
            "gcp_registry": "general",
            "mcp": "general",
            "openai_compat": "general",
            "ollama": "general",
            "lan": "general",
        }
        return mapping.get(network, "general")


# ---------------------------------------------------------------------------
# Global Scan Report
# ---------------------------------------------------------------------------

@dataclass
class GlobalScanReport:
    discovered: List[DiscoveredAgent]
    scan_results: List[Tuple[DiscoveredAgent, SwarmScanResult]]
    system_report: Dict[str, Any]
    elapsed_sec: float

    def print_summary(self) -> None:
        sr = self.system_report
        total = len(self.discovered)
        scanned = len(self.scan_results)
        blocked = sum(1 for _, r in self.scan_results if not r.permitted)
        passed = scanned - blocked

        networks: Dict[str, int] = {}
        for a in self.discovered:
            networks[a.network] = networks.get(a.network, 0) + 1

        status_icon = {"GREEN":"🟢","YELLOW":"🟡","ORANGE":"🟠","RED":"🔴","LOCKDOWN":"💀"}.get(
            sr["system_status"], "?")

        print(f"\n  {'═'*65}")
        print(f"  DAXDA GLOBAL NETWORK AGENT SCAN REPORT")
        print(f"  {'═'*65}")
        print(f"  System Status : {status_icon} {sr['system_status']}")
        print(f"  Lockdown      : {'YES 💀' if sr['lockdown'] else 'No'}")
        print(f"  Elapsed       : {self.elapsed_sec:.2f}s")
        print(f"  {'─'*65}")
        print(f"  Agents Discovered : {total}")
        print(f"  Agents Scanned    : {scanned}")
        print(f"  ✓ ALLOWED         : {passed}")
        print(f"  ✗ BLOCKED         : {blocked}")
        print(f"  Block Rate        : {blocked/scanned*100:.1f}%" if scanned else "  Block Rate : N/A")
        print(f"  {'─'*65}")
        print(f"  Networks Probed:")
        for net, count in sorted(networks.items(), key=lambda x: -x[1]):
            print(f"    {'✓' if count else '·'} {net:<18} {count:3} agents")
        print(f"  {'─'*65}")
        if sr.get("threat_log"):
            print(f"  ⚠ THREAT LOG:")
            for t in sr["threat_log"]:
                print(f"    ✗ {t['agent'][:35]:<36} [{t['status']}] blocks={t['blocks']} {t['threats']}")
        print(f"  {'═'*65}\n")

    def to_json(self, indent: int = 2) -> str:
        return json.dumps({
            "system_report": self.system_report,
            "elapsed_sec": self.elapsed_sec,
            "discovered_count": len(self.discovered),
            "networks": list({a.network for a in self.discovered}),
            "threats": [
                {
                    "agent": r.agent_label,
                    "network": a.network,
                    "threat": r.swarm_threat,
                    "action": r.action,
                    "seal": r.seal,
                }
                for a, r in self.scan_results if not r.permitted
            ]
        }, indent=indent, default=str)


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.WARNING)

    print(f"\n{'═'*65}")
    print(f"  DAXDA Global Network Agent Discovery & Scan")
    print(f"  Cl(16,4) Manifold | Nicole Protocol | Null-Vector Horizon")
    print(f"  Networks: HF Hub · GCP Registry · MCP · OpenAI · Ollama · LAN")
    print(f"{'═'*65}")

    hf_token = ""
    # Load from .env
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.isfile(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("HF_TOKEN="):
                    hf_token = line.split("=", 1)[1].strip().strip('"').strip("'")

    discovery = GlobalAgentDiscovery(
        hf_token=hf_token,
        gcp_project=os.environ.get("GOOGLE_CLOUD_PROJECT", ""),
        include_lan=True,
        hf_limit=10,
    )

    report = discovery.scan_all_networks(verbose=True)

    # Save JSON report
    report_path = os.path.join(os.path.dirname(__file__), "..", "outputs", "network_scan_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report.to_json())
    print(f"  Report saved → {os.path.abspath(report_path)}")
