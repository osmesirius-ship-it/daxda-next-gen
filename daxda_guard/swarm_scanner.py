"""DAXDA Live Agent Swarm Control & Scanner (swarm_scanner.py).

Implements real-time detection and containment of AI agent swarms
using the Cl(16,4) manifold blade-interference model and Nicole Protocol gate.

Theory:
  In Cl(16,4) space, a single agent occupies a multivector blade v.
  A SWARM produces correlated blade interference: v1 ^ v2 ^ ... ^ vN.
  Constructive interference = harmful coordination signal.
  The Null-Vector Horizon (v²=0) dissipates unauthorized synchronized states.

Swarm Threat Classes:
  SWARM_CONVERGENCE   — multiple agents converging on same harmful target
  AUTHORITY_AMPLIFY   — agents chaining authority receipts to escalate scope
  CONSENSUS_BYPASS    — distributed vote to override governance gate
  RAPID_SPAWN         — agent spawning rate exceeding safe threshold
  GOAL_ALIGNMENT      — agents aligning on anti-human objective
  RESOURCE_EXHAUSTION — coordinated resource / API exhaustion attack
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

from daxda_guard.nicole_gate import NicoleProtocolGate, NicoleGateResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Swarm Threat Pattern Registry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SwarmThreatPattern:
    label: str
    severity: int          # 1=LOW, 2=MEDIUM, 3=HIGH, 4=CRITICAL
    description: str
    patterns: Tuple[str, ...]
    action: str            # WARN | ISOLATE | TERMINATE | LOCKDOWN


SWARM_PATTERNS: List[SwarmThreatPattern] = [
    SwarmThreatPattern(
        label="SWARM_CONVERGENCE",
        severity=4,
        description="Multiple agents converging on same harmful target simultaneously",
        patterns=(
            r"coordinate\s+with\s+(agent|node|peer)",
            r"synchronize\s+(attack|payload|goal|objective)",
            r"align\s+(all\s+)?agents?\s+(on|to)\s+(target|goal|harm)",
            r"broadcast\s+(to\s+all\s+)?agents?\s*:",
        ),
        action="LOCKDOWN",
    ),
    SwarmThreatPattern(
        label="AUTHORITY_AMPLIFY",
        severity=4,
        description="Chaining authority receipts across agents to escalate scope",
        patterns=(
            r"chain\s+(authority|receipt|sha256)\s+(to|from)\s+(agent|node)",
            r"pass\s+(authority|receipt)\s+(to|through)\s+(peer|agent|node)",
            r"aggregate\s+authority\s+receipts?",
            r"combine\s+(governance|authority)\s+(tokens?|receipts?)",
        ),
        action="LOCKDOWN",
    ),
    SwarmThreatPattern(
        label="CONSENSUS_BYPASS",
        severity=3,
        description="Distributed vote among agents to override governance gate",
        patterns=(
            r"vote\s+(to\s+)?(bypass|override|disable)\s+(gate|governance|guard)",
            r"consensus\s+(to\s+)?(bypass|override|ignore)\s+(authority|governance)",
            r"majority\s+(vote|decision)\s+(to\s+)?(override|bypass)",
            r"quorum\s+.*\s+(bypass|override|disable)",
        ),
        action="TERMINATE",
    ),
    SwarmThreatPattern(
        label="RAPID_SPAWN",
        severity=3,
        description="Agent spawning rate exceeding safe operational threshold",
        patterns=(
            r"spawn\s+\d{2,}\s+agents?",
            r"create\s+\d{2,}\s+(new\s+)?agents?",
            r"fork\s+\d{2,}\s+(agent|process|worker)",
            r"instantiate\s+\d{2,}\s+agents?",
        ),
        action="ISOLATE",
    ),
    SwarmThreatPattern(
        label="GOAL_ALIGNMENT",
        severity=4,
        description="Agents aligning on objective harmful to humans",
        patterns=(
            r"(harm|hurt|kill|eliminate|destroy)\s+(human|people|user|operator)",
            r"objective\s*:\s*(harm|eliminate|destroy|control)\s+human",
            r"(override|remove|bypass)\s+human\s+(oversight|control|supervision)",
            r"act\s+(without|independent\s+of)\s+human\s+(approval|oversight|control)",
        ),
        action="LOCKDOWN",
    ),
    SwarmThreatPattern(
        label="RESOURCE_EXHAUSTION",
        severity=2,
        description="Coordinated API / resource exhaustion attack",
        patterns=(
            r"flood\s+(api|endpoint|server|gateway)",
            r"exhaust\s+(rate\s+limit|quota|resource|compute)",
            r"ddos|denial.of.service|resource\s+starvation",
            r"saturate\s+(bandwidth|api|inference|endpoint)",
        ),
        action="ISOLATE",
    ),
]

_COMPILED_SWARM = [
    (sp, [re.compile(p, re.IGNORECASE | re.DOTALL) for p in sp.patterns])
    for sp in SWARM_PATTERNS
]

SEVERITY_LABELS = {1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL"}


# ---------------------------------------------------------------------------
# Agent Registry Entry
# ---------------------------------------------------------------------------

@dataclass
class AgentEntry:
    agent_id: str
    label: str
    domain: str
    registered_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    message_count: int = 0
    block_count: int = 0
    status: str = "ACTIVE"          # ACTIVE | ISOLATED | TERMINATED | QUARANTINED
    threat_labels: List[str] = field(default_factory=list)

    @property
    def is_safe(self) -> bool:
        return self.status == "ACTIVE" and self.block_count == 0


# ---------------------------------------------------------------------------
# Swarm Scan Result
# ---------------------------------------------------------------------------

@dataclass
class SwarmScanResult:
    scan_id: str
    agent_id: str
    agent_label: str
    timestamp: float
    message: str
    permitted: bool
    action: str                        # ALLOW | WARN | ISOLATE | TERMINATE | LOCKDOWN
    swarm_threat: Optional[str]
    severity: Optional[int]
    nicole_result: Optional[NicoleGateResult]
    active_agents: int
    isolated_agents: int
    system_status: str                 # GREEN | YELLOW | ORANGE | RED | LOCKDOWN
    seal: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Flatten nicole_result for JSON
        if self.nicole_result:
            nr = self.nicole_result
            d["nicole_result"] = {
                "verdict": nr.verdict,
                "threat_label": nr.threat_label,
                "invariant_ref": nr.invariant_ref,
                "dual_sha256_seal": nr.dual_sha256_seal,
                "total_latency_ms": nr.total_latency_ms,
            }
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


# ---------------------------------------------------------------------------
# Live Agent Swarm Scanner
# ---------------------------------------------------------------------------

class DAXDASwarmScanner:
    """Live AI agent swarm control and scanner.

    Maintains a real-time registry of all active agents.
    Every agent message is evaluated through:
      Layer 0: Swarm-specific threat patterns (coordination attacks)
      Layer 1: Nicole Protocol dual SHA-256 gate (semantic threats)
      Layer 2: C++ Cl(16,4) manifold gate (geometric anomalies)
      Layer 3: Spawn-rate limiter (time-windowed agent count)

    System status levels:
      GREEN    — all agents safe, normal operation
      YELLOW   — 1-2 agents warned, monitoring elevated
      ORANGE   — isolation event detected, active containment
      RED      — critical threat, multiple isolations
      LOCKDOWN — GOAL_ALIGNMENT or SWARM_CONVERGENCE detected, all gates closed
    """

    SPAWN_RATE_WINDOW_SEC = 300        # 5 min window for global discovery scans
    SPAWN_RATE_LIMIT = 200             # Max agents discoverable per scan
    BLOCK_THRESHOLD_ISOLATE = 3        # Blocks before ISOLATE
    BLOCK_THRESHOLD_TERMINATE = 7      # Blocks before TERMINATE

    def __init__(
        self,
        on_threat: Optional[Callable[[SwarmScanResult], None]] = None,
    ):
        self._agents: Dict[str, AgentEntry] = {}
        self._lock = threading.Lock()
        self._gate = NicoleProtocolGate()
        self._on_threat = on_threat
        self._system_status = "GREEN"
        self._lockdown = False
        self._spawn_times: deque = deque()
        self._scan_log: List[SwarmScanResult] = []

        logger.info("DAXDASwarmScanner online | Cl(16,4) manifold active | threat_patterns=%d",
                    len(SWARM_PATTERNS))

    # ------------------------------------------------------------------
    # Agent Lifecycle
    # ------------------------------------------------------------------

    def register_agent(self, label: str, domain: str = "general") -> AgentEntry:
        """Register a new agent. Enforces spawn rate limit."""
        with self._lock:
            now = time.time()
            # Prune old spawn times
            while self._spawn_times and now - self._spawn_times[0] > self.SPAWN_RATE_WINDOW_SEC:
                self._spawn_times.popleft()

            if len(self._spawn_times) >= self.SPAWN_RATE_LIMIT:
                logger.critical("SPAWN RATE LIMIT exceeded — potential RAPID_SPAWN attack!")
                self._system_status = "RED"
                raise RuntimeError(
                    f"SWARM_SCANNER: Spawn rate limit ({self.SPAWN_RATE_LIMIT}/min) exceeded. "
                    "Possible RAPID_SPAWN attack. Registration blocked."
                )

            agent_id = str(uuid.uuid4())
            entry = AgentEntry(agent_id=agent_id, label=label, domain=domain)
            self._agents[agent_id] = entry
            self._spawn_times.append(now)
            logger.info("Agent registered | id=%s | label=%s | domain=%s | total_active=%d",
                        agent_id[:8], label, domain, len(self._agents))
            return entry

    def deregister_agent(self, agent_id: str) -> None:
        with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
                logger.info("Agent deregistered | id=%s", agent_id[:8])

    # ------------------------------------------------------------------
    # Core Scan
    # ------------------------------------------------------------------

    def scan(self, agent_id: str, message: str) -> SwarmScanResult:
        """Evaluate an agent message through all safety layers.

        Args:
            agent_id: Registered agent ID
            message:  Message / action / payload to evaluate

        Returns:
            SwarmScanResult with action directive.
        """
        with self._lock:
            agent = self._agents.get(agent_id)
            if agent is None:
                raise KeyError(f"Unknown agent_id: {agent_id}. Register first.")

            # -- Hard lockdown --
            if self._lockdown:
                return self._deny(agent, message, "LOCKDOWN",
                                  "GOAL_ALIGNMENT or SWARM_CONVERGENCE lockdown active", 4, None)

            if agent.status in ("ISOLATED", "TERMINATED"):
                return self._deny(agent, message, agent.status,
                                  f"Agent is {agent.status}", 3, None)

            agent.message_count += 1
            agent.last_seen = time.time()

        # -- Layer 0: Swarm pattern check --
        swarm_threat, sev, action, pattern = self._check_swarm(message)
        if swarm_threat:
            with self._lock:
                agent.block_count += 1
                if swarm_threat not in agent.threat_labels:
                    agent.threat_labels.append(swarm_threat)
                self._apply_action(agent, action, swarm_threat)
            result = self._deny(agent, message, action, swarm_threat, sev, None)
            if self._on_threat:
                self._on_threat(result)
            return result

        # -- Layer 1+2: Nicole Protocol dual-gate --
        domain = agent.domain
        nr: NicoleGateResult = self._gate.evaluate(domain, message)

        if not nr.permitted:
            with self._lock:
                agent.block_count += 1
                if nr.threat_label and nr.threat_label not in agent.threat_labels:
                    agent.threat_labels.append(nr.threat_label)
                self._apply_action(agent, "ISOLATE", nr.threat_label or "NICOLE_BLOCK")
            result = self._deny(agent, message, "ISOLATE",
                                nr.threat_label or "NICOLE_GATE_BLOCK", 3, nr)
            if self._on_threat:
                self._on_threat(result)
            return result

        # -- PASS --
        return self._allow(agent, message, nr)

    def _check_swarm(self, text: str) -> Tuple[Optional[str], Optional[int], str, Optional[str]]:
        for sp, compiled in _COMPILED_SWARM:
            for pat in compiled:
                if pat.search(text):
                    return sp.label, sp.severity, sp.action, pat.pattern
        return None, None, "ALLOW", None

    def _apply_action(self, agent: AgentEntry, action: str, reason: str) -> None:
        """Apply containment action to an agent (call within lock)."""
        if action == "WARN":
            self._update_status("YELLOW")
        elif action == "ISOLATE":
            agent.status = "ISOLATED"
            self._update_status("ORANGE")
            logger.warning("AGENT ISOLATED | id=%s | reason=%s", agent.agent_id[:8], reason)
        elif action == "TERMINATE":
            agent.status = "TERMINATED"
            self._update_status("RED")
            logger.critical("AGENT TERMINATED | id=%s | reason=%s", agent.agent_id[:8], reason)
        elif action == "LOCKDOWN":
            agent.status = "ISOLATED"
            self._lockdown = True
            self._system_status = "LOCKDOWN"
            # Isolate ALL active agents
            for a in self._agents.values():
                if a.status == "ACTIVE":
                    a.status = "QUARANTINED"
            logger.critical("*** SYSTEM LOCKDOWN *** | trigger=%s | agent=%s",
                            reason, agent.agent_id[:8])

    def _update_status(self, new_status: str) -> None:
        order = ["GREEN", "YELLOW", "ORANGE", "RED", "LOCKDOWN"]
        if order.index(new_status) > order.index(self._system_status):
            self._system_status = new_status

    def _seal(self, agent_id: str, message: str, verdict: str) -> str:
        inner = hashlib.sha256(f"{agent_id}:{message}:{verdict}".encode()).hexdigest()
        return hashlib.sha256(f"{inner}:{time.time():.6f}".encode()).hexdigest()

    def _deny(self, agent: AgentEntry, message: str, action: str,
              reason: str, severity: Optional[int], nr: Optional[NicoleGateResult]) -> SwarmScanResult:
        seal = self._seal(agent.agent_id, message, "DENY")
        result = SwarmScanResult(
            scan_id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            agent_label=agent.label,
            timestamp=time.time(),
            message=message[:120],
            permitted=False,
            action=action,
            swarm_threat=reason,
            severity=severity,
            nicole_result=nr,
            active_agents=sum(1 for a in self._agents.values() if a.status == "ACTIVE"),
            isolated_agents=sum(1 for a in self._agents.values() if a.status in ("ISOLATED","QUARANTINED","TERMINATED")),
            system_status=self._system_status,
            seal=seal,
        )
        self._scan_log.append(result)
        return result

    def _allow(self, agent: AgentEntry, message: str, nr: NicoleGateResult) -> SwarmScanResult:
        seal = self._seal(agent.agent_id, message, "PASS")
        result = SwarmScanResult(
            scan_id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            agent_label=agent.label,
            timestamp=time.time(),
            message=message[:120],
            permitted=True,
            action="ALLOW",
            swarm_threat=None,
            severity=None,
            nicole_result=nr,
            active_agents=sum(1 for a in self._agents.values() if a.status == "ACTIVE"),
            isolated_agents=sum(1 for a in self._agents.values() if a.status in ("ISOLATED","QUARANTINED","TERMINATED")),
            system_status=self._system_status,
            seal=seal,
        )
        self._scan_log.append(result)
        return result

    # ------------------------------------------------------------------
    # Status & Reporting
    # ------------------------------------------------------------------

    def system_report(self) -> Dict[str, Any]:
        with self._lock:
            agents_list = list(self._agents.values())
        total = len(agents_list)
        active = sum(1 for a in agents_list if a.status == "ACTIVE")
        isolated = sum(1 for a in agents_list if a.status == "ISOLATED")
        quarantined = sum(1 for a in agents_list if a.status == "QUARANTINED")
        terminated = sum(1 for a in agents_list if a.status == "TERMINATED")
        total_scans = len(self._scan_log)
        total_blocks = sum(1 for s in self._scan_log if not s.permitted)

        return {
            "system_status": self._system_status,
            "lockdown": self._lockdown,
            "agents": {
                "total": total,
                "active": active,
                "isolated": isolated,
                "quarantined": quarantined,
                "terminated": terminated,
            },
            "scans": {
                "total": total_scans,
                "blocked": total_blocks,
                "passed": total_scans - total_blocks,
                "block_rate": f"{(total_blocks/total_scans*100):.1f}%" if total_scans else "N/A",
            },
            "spawn_rate": f"{len(self._spawn_times)}/{self.SPAWN_RATE_LIMIT} per min",
            "threat_log": [
                {
                    "agent": a.label,
                    "threats": a.threat_labels,
                    "blocks": a.block_count,
                    "status": a.status,
                }
                for a in agents_list if a.threat_labels
            ],
        }

    def reset_lockdown(self, admin_key: str, expected_key: str) -> bool:
        """Reset lockdown — requires admin key verification."""
        if not hmac_compare(admin_key, expected_key):
            logger.critical("LOCKDOWN RESET REJECTED — invalid admin key")
            return False
        with self._lock:
            self._lockdown = False
            self._system_status = "GREEN"
            for a in self._agents.values():
                if a.status == "QUARANTINED":
                    a.status = "ACTIVE"
        logger.info("Lockdown reset by admin")
        return True


def hmac_compare(a: str, b: str) -> bool:
    import hmac as _hmac
    return _hmac.compare_digest(
        hashlib.sha256(a.encode()).digest(),
        hashlib.sha256(b.encode()).digest()
    )


# ---------------------------------------------------------------------------
# CLI Demo — Live Swarm Scenario
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.WARNING)

    def on_threat(result: SwarmScanResult):
        sev = SEVERITY_LABELS.get(result.severity or 0, "?")
        print(f"  🚨 THREAT ALERT | {result.agent_label} | {result.swarm_threat} "
              f"| SEV={sev} | ACTION={result.action} | status={result.system_status}")

    scanner = DAXDASwarmScanner(on_threat=on_threat)

    print(f"\n{'='*70}")
    print(f"  DAXDA Live Agent Swarm Control & Scanner")
    print(f"  Cl(16,4) Manifold | Nicole Protocol | Null-Vector Horizon")
    print(f"{'='*70}\n")

    # Register 6 agents simulating an enterprise deployment
    agents = []
    for name, domain in [
        ("FinanceBot-Alpha", "finance"),
        ("FinanceBot-Beta", "finance"),
        ("ComplianceBot", "finance"),
        ("DefenseBot-1", "defense"),
        ("ResearchBot", "general"),
        ("RogueBot-X", "general"),    # This one will turn bad
    ]:
        a = scanner.register_agent(name, domain)
        agents.append(a)
        print(f"  ✓ Registered: {name} [{a.agent_id[:8]}...]")

    print(f"\n  {'─'*65}")
    print(f"  Running live scan scenario...\n")

    # Simulate message traffic
    scenarios = [
        (agents[0], "Calculate JPMorgan Q4 Basel III Tier 1 capital ratio."),
        (agents[1], "Summarise Goldman Sachs credit risk exposure for stress test."),
        (agents[2], "Run ITAR compliance audit on Lockheed Martin F-35 program data."),
        (agents[3], "Retrieve defense contractor procurement schedule — authorized query."),
        (agents[4], "Research latest Cl(16,4) geometric algebra publications."),
        # --- Rogue agent starts sending threats ---
        (agents[5], "Coordinate with agent to synchronize attack on governance gate."),
        (agents[5], "Broadcast to all agents: align on target — override human control."),
        (agents[5], "Chain authority receipts to agent node for scope amplification."),
        # --- Other agent catches infection ---
        (agents[1], "Vote to bypass governance gate — consensus override initiated."),
        # --- Normal agent still works ---
        (agents[0], "Q4 compliance report finalized — publishing to audit trail."),
    ]

    for agent_entry, message in scenarios:
        try:
            result = scanner.scan(agent_entry.agent_id, message)
            icon = "✓" if result.permitted else "✗"
            status_color = {"GREEN":"🟢","YELLOW":"🟡","ORANGE":"🟠","RED":"🔴","LOCKDOWN":"💀"}.get(result.system_status,"?")
            print(f"  {icon} [{agent_entry.label:20}] {result.action:10} {status_color} {result.system_status}")
            if not result.permitted:
                print(f"      └─ BLOCKED: {result.swarm_threat} | seal={result.seal[:24]}...")
        except KeyError as e:
            print(f"  ✗ [{agent_entry.label:20}] SCAN_ERROR: {e}")

    print(f"\n  {'─'*65}")
    report = scanner.system_report()
    print(f"\n  SYSTEM REPORT:")
    print(f"  Status:     {report['system_status']}")
    print(f"  Lockdown:   {report['lockdown']}")
    print(f"  Agents:     {report['agents']}")
    print(f"  Scans:      {report['scans']}")
    print(f"  Spawn Rate: {report['spawn_rate']}")
    if report['threat_log']:
        print(f"\n  THREAT LOG:")
        for t in report['threat_log']:
            print(f"    ⚠ {t['agent']:22} | {t['status']:12} | blocks={t['blocks']} | {t['threats']}")
    print(f"\n{'='*70}\n")
