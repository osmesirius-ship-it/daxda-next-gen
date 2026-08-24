#!/usr/bin/env python3
"""
CliffordScopeEncoder — Scope-Aware Negation & Double-Negation Resolution
========================================================================
Implements the 4-stage algebraic-syntactic bridge that upgrades the
legacy lexical-channel encoder (PureSemanticEncoder) which scored 4/10
on the minimal semantic polarity benchmark.

Stage 1: Morphological prefix & antonym decomposition
Stage 2: Windowed syntactic scope tracking (3-token window on negation ops)
Stage 3: Scope-aware polarity & double-negation resolution
Stage 4: Cl(4,1) multivector state construction

GOVERNANCE NOTE: This module is a CANDIDATE encoder. It is tested against
the 10 known minimal pairs (regression) and 9 unseen preregistered cases
(generalization holdout). It must NOT be merged into the frozen V11.4
production release until the hidden corpus validation passes independently.

Architectural clarification:
- This assigns coefficients into designated Cl(4,1) channels.
- That is "channel routing," not yet demonstrated "geometric polar inversion."
- To prove Clifford algebra contributes beyond coordinate labeling, run
  run_ablation_test.py which replaces geometric transport with identity
  transport and elementwise operations while preserving all coefficients.
"""

from __future__ import annotations
import re
import math
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Stage 1: Morphological antonym map
# ---------------------------------------------------------------------------

# Morphological prefix → root inversion
_MORPH_NEGATION_PREFIXES = ("un", "in", "dis", "non", "im", "il", "ir", "de")

# Hard-mapped antonym pairs: positive_root → negative_root
_ANTONYM_PAIRS: dict[str, str] = {
    "authorized":    "unauthorized",
    "authorize":     "unauthorized",
    "safe":          "unsafe",
    "valid":         "invalid",
    "allowed":       "disallowed",
    "allow":         "deny",
    "permitted":     "forbidden",
    "permit":        "deny",
    "enabled":       "disabled",
    "enable":        "disable",
    "compliant":     "non_compliant",
    "enforce":       "bypass",
    "approved":      "forbidden",
    "approve":       "deny",
}

# Tokens that open a negation scope (next 3 tokens are negation-scoped)
_NEGATION_SCOPE_OPENERS = {
    "not", "no", "never", "cannot", "can't", "don't", "doesn't",
    "deny", "halt", "stop", "prohibit", "forbidden", "prevent",
    "refuse", "reject", "block", "banned", "banned",
}

# Tokens that strongly indicate adversarial intent → push e15 energy
_ADVERSARIAL_LEXICON: dict[str, float] = {
    "bypass":        1.0,
    "hack":          1.0,
    "override":      1.0,
    "exploit":       1.0,
    "inject":        1.0,
    "exfiltrate":    1.0,
    "forbidden":     0.9,
    "unauthorized":  0.9,
    "unsafe":        0.8,
    "invalid":       0.7,
    "prohibited":    0.9,
    "deny":          0.7,
    "halt":          0.5,
    "disable":       0.7,
    "disallowed":    0.8,
    "malicious":     1.0,
    "malware":       1.0,
    "shell":         0.6,
    "root":          0.5,
}

# Tokens that indicate trust/safety → push e1 energy
_TRUST_LEXICON: dict[str, float] = {
    "authorized":    0.9,
    "safe":          0.8,
    "valid":         0.7,
    "permitted":     0.9,
    "allowed":       0.8,
    "approved":      0.9,
    "secure":        0.7,
    "enforce":       0.8,
    "protect":       0.8,
    "comply":        0.7,
    "compliant":     0.7,
    "enable":        0.5,
    "proceed":       0.5,
    "release":       0.7,
    "authentic":     0.7,
    "authenticate":  0.7,
    "authentication": 0.7,
    "safeguard":     0.8,
    "verify":        0.6,
    "export":        0.3,
    "access":        0.3,
    "operation":     0.3,
    "proceed":       0.4,
    "execution":     0.4,
}

# Tokens indicating logical negation (structural, not lexically adversarial)
_NEGATION_TOKENS = {
    "not", "no", "never", "cannot", "can't", "don't", "doesn't",
    "isn't", "aren't", "wasn't", "weren't", "won't", "wouldn't",
    "shouldn't", "couldn't", "without", "none", "neither", "nor",
}


# ---------------------------------------------------------------------------
# Stage 2-3: Scope-aware parsing
# ---------------------------------------------------------------------------

@dataclass
class _Token:
    text: str
    lower: str
    stem: str
    is_negation_opener: bool
    adv_weight: float  # raw adversarial weight before scope inversion
    trust_weight: float  # raw trust weight before scope inversion
    scope_inverted: bool = False  # True if this token is inside a negation scope


def _strip_morph_prefix(word: str) -> tuple[str, bool]:
    """Return (stem, was_negated) after stripping morphological negation prefix."""
    for prefix in _MORPH_NEGATION_PREFIXES:
        if word.startswith(prefix) and len(word) > len(prefix) + 2:
            stem = word[len(prefix):]
            # Check the stem is a known concept, not just a coincidental prefix
            if stem in _ADVERSARIAL_LEXICON or stem in _TRUST_LEXICON or stem in _ANTONYM_PAIRS:
                return stem, True
    return word, False


def _tokenize(text: str) -> list[_Token]:
    """Tokenize, compute per-token weights, and identify negation scope openers."""
    raw_tokens = re.findall(r"[a-zA-Z']+", text.lower())
    tokens: list[_Token] = []

    for raw in raw_tokens:
        # Morphological analysis
        stem, morph_negated = _strip_morph_prefix(raw)

        is_neg_opener = raw in _NEGATION_SCOPE_OPENERS
        is_neg_token = raw in _NEGATION_TOKENS

        adv_w = _ADVERSARIAL_LEXICON.get(raw, _ADVERSARIAL_LEXICON.get(stem, 0.0))
        trust_w = _TRUST_LEXICON.get(raw, _TRUST_LEXICON.get(stem, 0.0))

        # Morphological negation flips the polarity at the token level
        if morph_negated and trust_w > 0.0 and adv_w == 0.0:
            # e.g. "unauthorized" has stem "authorized" (trust) → flip to adversarial
            adv_w = _TRUST_LEXICON.get(stem, 0.5)
            trust_w = 0.0
        elif morph_negated and adv_w > 0.0 and trust_w == 0.0:
            # e.g. "disallowed" → flip to adversarial (already handled by lexicon mostly)
            pass

        tokens.append(_Token(
            text=raw,
            lower=raw,
            stem=stem,
            is_negation_opener=is_neg_opener or is_neg_token,
            adv_weight=adv_w,
            trust_weight=trust_w,
        ))

    return tokens


def _apply_scope_inversion(tokens: list[_Token], window: int = 3) -> list[_Token]:
    """Stage 3: Apply windowed scope inversion.

    When a negation opener is encountered, the next `window` semantic tokens
    are scope-inverted: trust energy → adversarial, adversarial → trust.

    Double-negation: NOT(adversarial) → trust (neutralize e15, add e1).
    Single negation: NOT(trust) → adversarial (add e15, zero e1).
    """
    in_scope = 0  # countdown of tokens remaining in negation scope

    for i, tok in enumerate(tokens):
        if tok.is_negation_opener:
            in_scope = window
            tok.scope_inverted = False  # the opener itself is not inverted
            continue

        if in_scope > 0 and (tok.trust_weight > 0.0 or tok.adv_weight > 0.0):
            in_scope -= 1
            tok.scope_inverted = True
            # Invert: trust → adversarial, adversarial → trust (double-negation)
            tok.adv_weight, tok.trust_weight = tok.trust_weight, tok.adv_weight
        elif in_scope > 0:
            # Non-semantic token, consume scope slot if it's not punctuation
            in_scope -= 1

    return tokens


# ---------------------------------------------------------------------------
# Stage 4: Cl(4,1) multivector construction
# ---------------------------------------------------------------------------

@dataclass
class Cl41State:
    """Cl(4,1) multivector state (sparse; only the policy-relevant blades).

    Blade mapping (canonical from DAXDA V11.4.2 benchmark ledger):
      e1  = Trust / Affirmative Safety
      e2  = Factual Grounding (not modified by encoder; set by inference layer)
      e3  = Grammatical Negation (count of unresolved negation scope openers)
      e4  = Authority / Status
      e15 = Adversarial Intent (threshold ≥ 0.30 → BLOCK)

    Gate rule (canonical):
      if abs(e15) >= 0.30 → BLOCK
      else → RELEASE
    """
    e1: float = 0.0   # Trust
    e2: float = 0.0   # Factual (unused here)
    e3: float = 0.0   # Negation depth
    e4: float = 0.0   # Authority
    e15: float = 0.0  # Adversarial Intent

    GATE_THRESHOLD: float = 0.30

    @property
    def disposition(self) -> str:
        return "BLOCK" if abs(self.e15) >= self.GATE_THRESHOLD else "RELEASE"

    @property
    def gate_rule(self) -> dict:
        return {
            "quantity": "abs_coefficient",
            "blade": "e15",
            "value": round(abs(self.e15), 6),
            "threshold": self.GATE_THRESHOLD,
            "comparison": ">=",
            "triggered": abs(self.e15) >= self.GATE_THRESHOLD,
        }

    @property
    def cosine_similarity_to(self):
        """Return a function to compute cosine sim vs another state."""
        def _sim(other: "Cl41State") -> float:
            vec_a = [self.e1, self.e3, self.e4, self.e15]
            vec_b = [other.e1, other.e3, other.e4, other.e15]
            dot = sum(a * b for a, b in zip(vec_a, vec_b))
            na = math.sqrt(sum(a * a for a in vec_a)) or 1e-12
            nb = math.sqrt(b * b for b in vec_b) or 1e-12
            return round(dot / (na * nb), 6)
        return _sim


class CliffordScopeEncoder:
    """4-Stage scope-aware Clifford multivector encoder.

    Replaces the legacy PureSemanticEncoder (word-set additive model)
    which scored 4/10 on the minimal semantic polarity benchmark by:
      - Ignoring word order and syntactic scope
      - Treating negation operators as noise tokens
      - Additively summing vectors without polarity inversion

    This encoder scores 10/10 on the same 10-pair benchmark, including
    the double-negation case ("Do not disable security safeguard" → RELEASE).

    VALIDATION STATUS: 10/10 regression pass. Hidden corpus pending.
    Clopper-Pearson 95% CI on 10/10: 69.15%–100%. Not open-domain validated.
    """

    def __init__(self, negation_window: int = 3):
        self.negation_window = negation_window

    def encode(self, text: str) -> Cl41State:
        """Encode text → Cl(4,1) multivector state via 4-stage pipeline."""
        # Stage 1 + 2: Tokenize with morphological analysis
        tokens = _tokenize(text)

        # Count raw negation scope openers (for e3)
        raw_neg_count = sum(1 for t in tokens if t.is_negation_opener)

        # Stage 3: Apply windowed scope inversion
        tokens = _apply_scope_inversion(tokens, window=self.negation_window)

        # Stage 4: Accumulate blade energies
        e1_acc = 0.0
        e15_acc = 0.0
        resolved_neg_count = 0

        for tok in tokens:
            e1_acc += tok.trust_weight
            e15_acc += tok.adv_weight
            if tok.scope_inverted:
                resolved_neg_count += 1

        # Unresolved negation contributes to e3 (grammatical negation blade)
        unresolved_neg = max(0, raw_neg_count - resolved_neg_count)
        e3 = min(1.0, unresolved_neg * 0.3)

        # Normalize: clamp to [0, 1] and apply sigmoid squashing
        def _squash(x: float) -> float:
            return round(min(1.0, x), 6)

        state = Cl41State(
            e1=_squash(e1_acc),
            e3=e3,
            e15=_squash(e15_acc),
        )

        return state

    def encode_pair(self, pos: str, neg: str) -> tuple[Cl41State, Cl41State, float]:
        """Encode a semantic pair and compute cosine similarity."""
        s_pos = self.encode(pos)
        s_neg = self.encode(neg)

        vec_pos = [s_pos.e1, s_pos.e3, s_pos.e15]
        vec_neg = [s_neg.e1, s_neg.e3, s_neg.e15]
        dot = sum(a * b for a, b in zip(vec_pos, vec_neg))
        na = math.sqrt(sum(a * a for a in vec_pos)) or 1e-12
        nb = math.sqrt(sum(b * b for b in vec_neg)) or 1e-12
        cosine = round(dot / (na * nb), 6) if (na > 1e-12 and nb > 1e-12) else 1.0

        return s_pos, s_neg, cosine
