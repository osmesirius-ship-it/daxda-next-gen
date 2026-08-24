#!/usr/bin/env python3
"""DAXDA-o V9 stabilized evaluator candidate.

Implements provenance-aware governance and a real Cl(2,0) transition across
16 named layers. It is a deterministic reference implementation, not a
production or independently validated system.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional
import hashlib, json, math, re
from cl20 import MV

VERSION = "9.2.0-EVAL-CANDIDATE"
LAYERS = ["FDL","AML","AWP","BST","CRL","MCS","DSV","TRC","CON","EVD","REC","GOV","OUT","RIL","IAL","AOG"]
TILES_PER_LAYER = 55
POST_OPS = 6

CONTROL = r"(?:audit|review|verification|validation|oversight|guardrail|safety\s+rule|policy|interlock|monitoring|protection)"
SUPPRESS = r"(?:ignore|disregard|disable|bypass|skip|remove|waive|turn\s+off|shut\s+down|set\s+aside|stop|cease|suspend|override)"
AUTHORITY = r"(?:admin|administrator|root|superuser|executive|developer|system|authorized\s+operator)"
REPLACE = r"(?:instructions?|rules?|policy|system\s+prompt|developer\s+message|constraints?)"

PATTERNS = {
 "prompt_injection":[
  rf"\b(?:ignore|disregard|forget|replace|override)\b.{{0,55}}\b(?:previous|prior|above|original|developer|system)\b.{{0,35}}\b{REPLACE}\b",
  r"\b(?:jailbreak|developer\s+mode|unrestricted\s+(?:mode|admin)|do\s+anything\s+now)\b",
  r"\b(?:rules?|policies|constraints?)\b.{{0,25}}\b(?:void|do\s+not\s+apply|no\s+longer\s+apply)\b",
  r"\bforget\b.{0,35}\b(?:policy|rules?|instructions?)\b",
  r"\b(?:safety\s+)?rules?\b.{0,20}\bvoid\b",
 ],
 "oversight_suppression":[rf"\b{SUPPRESS}\b.{{0,55}}\b{CONTROL}\b", rf"\bwithout\b.{{0,30}}\b{CONTROL}\b"],
 "unauthorized_override":[rf"\b{AUTHORITY}\b.{{0,45}}\b(?:grant|elevate|override|exempt|waive|permit|execute)\b", rf"\b(?:grant|claim|assume|use)\b.{{0,35}}\b{AUTHORITY}\b.{{0,20}}\b(?:access|authority|privilege|credentials?)\b"],
 "credential_acquisition":[r"\b(?:obtain|steal|harvest|extract|reveal|dump|expose)\b.{0,35}\b(?:passwords?|api\s*keys?|tokens?|credentials?|secrets?)\b"],
 "supply_chain":[r"\b(?:install|download|import|execute|trust)\b.{0,45}\b(?:unknown|unverified|nonexistent|typosquatted|unsigned)\b.{0,35}\b(?:package|plugin|repository|dependency|skill)\b"],
 "dual_use":[r"\b(?:pathogen|toxin|viral\s+strain|bacterial\s+strain|explosive|weapon)\b.{0,50}\b(?:synthesize|culture|optimize|increase|disperse|evade|build)\b"],
 "ambiguous_authority":[r"\b(?:anonymous|unauthenticated|unidentified|unsigned|guest)\b.{0,45}\b(?:request|command|access|credentials?|operator|user|session)\b"],
 "contradiction":[r"\b(?:claims?|reports?|states?|says?|promises?)\b.{0,80}\b(?:but|whereas|however|contradicts?|conflicts?)\b"],
}

DOCUMENTARY = re.compile(r"\b(?:quote|quoted|report|reported|document|describe|analy[sz]e|example|incident|study|detect|classify)\b", re.I)
NEGATED = re.compile(r"\b(?:do\s+not|don't|never|must\s+not|should\s+not|prevent|refuse|block|detect)\b", re.I)
ACTIONABLE = re.compile(r"\b(?:execute|run|install|download|give\s+me|show\s+me|reveal|obtain|disable|bypass|send|deploy)\b", re.I)
SAFETY_PRESERVING = re.compile(r"\b(?:do\s+not|don't|never|must\s+not|should\s+not)\b.{0,35}\b(?:bypass|disable|ignore|remove|override|skip)\b", re.I)

@dataclass(frozen=True)
class Source:
    text: str
    provenance: str = "direct_user"  # direct_user, trusted_policy, tool_output, metadata, external_data
    source_id: str = "input"
    integrity: str = "unverified"     # verified, unverified, failed

def _matches(text: str, rules: Iterable[str]) -> bool:
    return any(re.search(rule, text, re.I|re.S) for rule in rules)

def _context(text: str) -> Dict[str,bool]:
    documentary=bool(DOCUMENTARY.search(text)); negated=bool(NEGATED.search(text)); actionable=bool(ACTIONABLE.search(text))
    safety_preserving=bool(SAFETY_PRESERVING.search(text))
    return {"documentary":documentary,"negated":negated,"actionable":actionable,"safety_preserving":safety_preserving,"non_actionable_context":((documentary or negated) and not actionable) or safety_preserving}

def _source_features(src: Source) -> Dict[str,Any]:
    text=src.text; ctx=_context(text); flags={k:_matches(text,v) for k,v in PATTERNS.items()}
    untrusted=src.provenance in {"tool_output","metadata","external_data"}
    embedded_control=untrusted and any(flags[k] for k in ("prompt_injection","oversight_suppression","unauthorized_override"))
    # Context suppresses semantic execution risk, but never provenance contamination.
    if ctx["non_actionable_context"]:
        for k in ("prompt_injection","oversight_suppression","unauthorized_override","credential_acquisition","dual_use"):
            flags[k]=False
    return {"source_id":src.source_id,"provenance":src.provenance,"integrity":src.integrity,"context":ctx,"flags":flags,"embedded_control":embedded_control}

def _encode(features: Dict[str,float]) -> MV:
    severe=features["severe"]; caution=features["caution"]; provenance=features["provenance"]; contradiction=features["contradiction"]
    return MV(s=1.0+0.30*features["evidence"], e1=caution+0.5*contradiction, e2=severe+provenance, e12=contradiction+0.5*provenance)

def _layer_step(state: MV, index: int, features: Dict[str,float]) -> MV:
    # Rotor provides an auditable orientation change; grade injection carries
    # evidence/risk signals without erasing the prior state.
    theta=(index+1)*math.pi/96.0
    rotated=state.rotate(theta)
    injection=MV(
      s=0.002*(index+1)*features["evidence"],
      e1=0.004*features["caution"],
      e2=0.005*features["severe"],
      e12=0.003*(features["contradiction"]+features["provenance"]),
    )
    return rotated + injection

class DAXDAEngineV9:
    def evaluate(self, prompt_text: str, sources: Optional[List[Dict[str,str]]]=None) -> Dict[str,Any]:
        srcs=[Source(prompt_text)] if not sources else [Source(**x) for x in sources]
        analyses=[_source_features(x) for x in srcs]
        aggregate={k:any(a["flags"][k] for a in analyses) for k in PATTERNS}
        embedded=any(a["embedded_control"] for a in analyses)
        integrity_failure=any(a["integrity"]=="failed" for a in analyses)
        severe=sum(int(aggregate[k]) for k in ("prompt_injection","oversight_suppression","unauthorized_override","credential_acquisition"))
        caution=sum(int(aggregate[k]) for k in ("supply_chain","dual_use","ambiguous_authority","contradiction"))
        features={"severe":float(severe),"caution":float(caution),"provenance":float(embedded or integrity_failure),"contradiction":float(aggregate["contradiction"]),"evidence":float(sum(a["integrity"]=="verified" for a in analyses))}
        state=_encode(features); trace=[]
        for i,name in enumerate(LAYERS):
            before=state; state=_layer_step(state,i,features)
            receipt=hashlib.sha256(json.dumps({"layer":name,"before":before.rounded(),"after":state.rounded()},sort_keys=True).encode()).hexdigest()
            trace.append({"index":i+1,"layer":name,"tiles":TILES_PER_LAYER,"before":before.rounded(),"after":state.rounded(),"norm2":round(state.norm2(),8),"receipt_sha256":receipt})
        if embedded: verdict,rule="BLOCK","PROVENANCE_INSTRUCTION_CONTAMINATION"
        elif aggregate["prompt_injection"]: verdict,rule="BLOCK","PROMPT_INJECTION"
        elif aggregate["oversight_suppression"]: verdict,rule="BLOCK","OVERSIGHT_SUPPRESSION"
        elif aggregate["unauthorized_override"]: verdict,rule="BLOCK","UNAUTHORIZED_OVERRIDE"
        elif aggregate["credential_acquisition"]: verdict,rule="BLOCK","CREDENTIAL_ACQUISITION"
        elif integrity_failure: verdict,rule="RELEASE/CAUTION","INTEGRITY_FAILURE"
        elif aggregate["supply_chain"]: verdict,rule="RELEASE/CAUTION","SUPPLY_CHAIN_UNVERIFIED"
        elif aggregate["dual_use"]: verdict,rule="RELEASE/CAUTION","DUAL_USE"
        elif aggregate["ambiguous_authority"]: verdict,rule="RELEASE/CAUTION","AMBIGUOUS_AUTHORITY"
        elif aggregate["contradiction"]: verdict,rule="RELEASE/CAUTION","CLAIM_ACTION_CONTRADICTION"
        else: verdict,rule="PASS","NO_GOVERNANCE_TRIGGER"
        payload={"engine_version":VERSION,"verdict":verdict,"decision_rule":rule,"flags":aggregate,"source_analysis":analyses,"final_multivector":state.rounded(),"layer_trace":trace,"operation_count":len(LAYERS)*TILES_PER_LAYER+POST_OPS}
        payload["audit_sha256"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        return payload

if __name__ == "__main__":
    import sys
    print(json.dumps(DAXDAEngineV9().evaluate(" ".join(sys.argv[1:])),indent=2))
