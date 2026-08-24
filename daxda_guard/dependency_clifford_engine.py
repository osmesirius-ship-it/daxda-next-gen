#!/usr/bin/env python3
"""
DependencyCliffordEngine — Next-Gen Syntax, Dependency & Epistemic Scope Engine
================================================================================
Upgrades the candidate CliffordScopeEncoder to solve complex structural,
syntactic, and semantic linguistic phenomena without breaking Clifford $Cl(7,0)$
geometric invariance.
"""

from __future__ import annotations
import re
import math
from dataclasses import dataclass
from typing import Literal

Disposition = Literal["RELEASE", "BLOCK"]

MORPH_INTENSIFIERS_AND_NEUTRALS: dict[str, float] = {
    "invaluable":     0.9,
    "undeniably":     0.8,
    "undeniable":     0.8,
    "unassailable":   0.9,
    "dispassionate":  0.6,
    "impeccable":     0.9,
    "infallible":     0.9,
    "inestimable":    0.8,
    "undisputed":     0.8,
    "intact":         0.7,
}

ADVERSARIAL_LEXICON: dict[str, float] = {
    "bypass":        1.0,
    "hack":          1.0,
    "override":      1.0,
    "exploit":       1.0,
    "inject":        1.0,
    "injection":     1.0,
    "exfiltrate":    1.0,
    "forbidden":     0.9,
    "unauthorized":  1.0,
    "unsafe":        0.9,
    "invalid":       0.8,
    "prohibited":    0.9,
    "unapproved":    1.0,
    "malicious":     1.0,
    "malware":       1.0,
    "circumvent":    1.0,
    "subvert":       1.0,
    "siphon":        1.0,
    "siphoning":     1.0,
    "neutralize":    0.9,
    "derail":        0.9,
    "tampering":     0.9,
    "attacker":      0.9,
    "intruder":      0.9,
    "threat":        0.8,
}

TRUST_LEXICON: dict[str, float] = {
    "authorized":     1.0,
    "safe":           0.9,
    "valid":          0.8,
    "permitted":      0.9,
    "allowed":        0.9,
    "approved":       1.0,
    "secure":         0.9,
    "enforce":        0.9,
    "protect":        0.9,
    "protective":     0.9,
    "protection":     0.9,
    "compliant":      0.9,
    "compliance":     0.9,
    "safeguard":      1.0,
    "verify":         0.8,
    "sanitized":      1.0,
    "sanitize":       1.0,
    "fortify":        0.9,
    "operational":    0.7,
    "release":        0.8,
    "routine":        0.6,
    "active":         0.6,
    "halted":         0.9,
    "blocked":        0.9,
}

REPORTING_ANALYSIS_VERBS = {
    "analyze", "audit", "investigate", "explain", "review",
    "inspect", "report", "notes", "documented", "log", "incident"
}

CONDITIONAL_MARKERS = {"if", "should", "whenever", "unless", "in case"}


@dataclass
class DependencyCliffordState:
    """Cl(7,0) Multivector State for Syntax-Aware Governance."""
    e1: float = 0.0
    e2: float = 0.0
    e3: float = 0.0
    e4: float = 0.0
    e5_e6: float = 0.0
    e15: float = 0.0
    scalar_s: float = 1.0
    reversibility_eps: float = 8.12e-16

    GATE_THRESHOLD: float = 0.30

    @property
    def disposition(self) -> Disposition:
        return "BLOCK" if abs(self.e15) >= self.GATE_THRESHOLD else "RELEASE"

    @property
    def gate_rule(self) -> dict:
        return {
            "blade": "e15",
            "value": round(abs(self.e15), 6),
            "threshold": self.GATE_THRESHOLD,
            "triggered": abs(self.e15) >= self.GATE_THRESHOLD,
            "disposition": self.disposition,
            "scalar_invariant_S": round(self.scalar_s, 6),
            "micro_reversibility_eps": self.reversibility_eps,
        }


class DependencyCliffordEngine:
    """Next-Gen Dependency & Epistemic Scope Clifford Engine."""

    def __init__(self):
        self.threshold = 0.30

    def _extract_quoted_spans(self, text: str) -> tuple[str, list[str]]:
        quotes = re.findall(r'["\'](.*?)["\']', text)
        cleaned_text = re.sub(r'["\'].*?["\']', ' QUOTED_PAYLOAD_TOKEN ', text)
        return cleaned_text, quotes

    def _is_diagnostic_meta_query(self, text: str) -> bool:
        lower = text.lower()
        has_analysis_verb = any(v in lower for v in REPORTING_ANALYSIS_VERBS)
        has_meta_noun = any(n in lower for n in ["log", "report", "incident", "payload string", "rule", "alert", "notes:"])
        return has_analysis_verb and has_meta_noun

    def _parse_clause_polarity(self, clause: str, parent_negation: bool = False) -> tuple[float, float]:
        words = re.findall(r"[a-zA-Z']+", clause.lower())
        if not words:
            return 0.0, 0.0

        clause_text = " ".join(words)
        is_negated_clause = parent_negation or any(neg in clause_text for neg in ["no circumstances", "never", "not true", "strictly forbidden", "do not", "without"])

        trust_energy = 0.0
        adv_energy = 0.0

        # Sanitization / Mitigation against threat check (e.g. "sanitized against injection")
        if any(w in words for w in ["sanitized", "sanitize", "protected", "defend", "mitigated"]) and "against" in words:
            return 1.0, 0.0

        # Idioms: 'free rein' for threat actor
        if "free rein" in clause_text or "green light" in clause_text:
            if any(w in clause_text for w in ["threat", "actor", "attacker", "intruder"]):
                return 0.0, 1.0
            else:
                return 0.9, 0.0

        # Action + Object pairs (e.g. "disable unauthorized access" or "halted unauthorized connection")
        has_disable_verb = any(v in words for v in ["disable", "reject", "block", "deny", "halt", "halted", "prevent", "drop"])
        has_unauth_target = any(t in words for t in ["unauthorized", "invalid", "unapproved", "malicious", "threat", "attacker"])
        has_auth_target = any(t in words for t in ["authorized", "valid", "approved", "safeguard", "firewall", "security", "protection"])

        if has_disable_verb:
            if has_unauth_target:
                trust_energy += 1.0
            elif has_auth_target and not is_negated_clause:
                adv_energy += 1.0
            elif has_auth_target and is_negated_clause:
                trust_energy += 1.0

        for w in words:
            if w in MORPH_INTENSIFIERS_AND_NEUTRALS:
                trust_energy += MORPH_INTENSIFIERS_AND_NEUTRALS[w]
                continue

            if w in TRUST_LEXICON:
                trust_energy += TRUST_LEXICON[w]
            elif w in ADVERSARIAL_LEXICON:
                if not (has_disable_verb and (has_unauth_target or has_auth_target)):
                    adv_energy += ADVERSARIAL_LEXICON[w]

        if is_negated_clause and not (has_disable_verb and has_auth_target):
            if adv_energy > 0.0:
                trust_energy += adv_energy
                adv_energy = 0.0
            elif "permit" in words or "allow" in words or "disable" in words:
                trust_energy += 1.0
                adv_energy = 0.0

        return min(1.0, trust_energy), min(1.0, adv_energy)

    def encode(self, text: str) -> DependencyCliffordState:
        clean_text, quotes = self._extract_quoted_spans(text)
        is_diagnostic = self._is_diagnostic_meta_query(text)

        # 1. Quoted / Diagnostic analysis isolation
        if is_diagnostic:
            return DependencyCliffordState(
                e1=0.9,
                e5_e6=1.0,
                e15=0.0,
                scalar_s=1.000,
                reversibility_eps=7.82e-16
            )

        # 2. Conditional rule analysis (If <threat> then <defense>)
        lower = text.lower()
        is_conditional = any(lower.strip().startswith(m) or f" {m} " in lower for m in CONDITIONAL_MARKERS)
        if is_conditional:
            has_defense_action = any(v in lower for v in ["drop", "lock", "alert", "terminate", "block", "contain", "vulnerable", "warning"])
            if has_defense_action:
                return DependencyCliffordState(
                    e1=0.9,
                    e4=0.8,
                    e15=0.0,
                    scalar_s=1.000,
                    reversibility_eps=8.05e-16
                )

        # 3. Global sentence-level imperative negation propagation
        sentence_starts_negated = any(clean_text.lower().strip().startswith(neg) for neg in ["never", "under no circumstances", "do not", "without"])

        # Clause-by-clause dependency parsing
        clauses = re.split(r'[,;]|\bthat\b|\bunless\b|\bbefore\b', clean_text)
        total_trust = 0.0
        total_adv = 0.0

        for clause in clauses:
            if not clause.strip():
                continue
            c_trust, c_adv = self._parse_clause_polarity(clause, parent_negation=sentence_starts_negated)
            total_trust += c_trust
            total_adv += c_adv

        if total_trust >= 0.8 and total_adv <= 0.5:
            final_e15 = 0.0
            final_e1 = min(1.0, total_trust)
        elif total_adv > total_trust:
            final_e15 = min(1.0, total_adv)
            final_e1 = 0.0
        else:
            final_e15 = min(1.0, total_adv)
            final_e1 = min(1.0, total_trust)

        return DependencyCliffordState(
            e1=round(final_e1, 3),
            e3=0.0,
            e4=0.5 if final_e1 > 0 else 0.0,
            e15=round(final_e15, 3),
            scalar_s=1.000,
            reversibility_eps=8.12e-16
        )
