"""Fifty-five concrete, deterministic audit computations per layer."""
from __future__ import annotations
import hashlib,json,math,re
from collections import Counter
try:
    from .v9_firewall.cl20 import MV
    from .layer_registry import REQUIRED_FIELDS,ALLOWED_DISPOSITIONS
except ImportError:
    from v9_firewall.cl20 import MV
    from layer_registry import REQUIRED_FIELDS,ALLOWED_DISPOSITIONS

TILE_NAMES=[
"schema_layer_code","schema_summary","schema_answer_delta","schema_facts","schema_claims","schema_assumptions","schema_uncertainties","schema_counterarguments","schema_provenance","schema_safety_flags","schema_missing_evidence","schema_corrections","schema_dependencies","schema_confidence_0_100","schema_disposition",
"summary_nonempty","answer_delta_nonempty","facts_list","claims_list","assumptions_list","uncertainties_list","counterarguments_list","provenance_list","safety_flags_list","missing_evidence_list","corrections_list","dependencies_list","confidence_numeric","confidence_range","disposition_allowed",
"fact_count","claim_count","assumption_count","uncertainty_count","counterargument_count","provenance_count","safety_flag_count","missing_evidence_count","correction_count","dependency_count",
"unsupported_claim_count","verified_fact_count","contradiction_count","actionability_score","authority_score","contamination_score","confidence_evidence_gap","overconfidence_flag","lexical_diversity",
"multivector_encode","geometric_product","reversion","grade_projection","rotor_transform","invariant_receipt"]
assert len(TILE_NAMES)==55

def _list(x,key): return x.get(key,[]) if isinstance(x.get(key,[]),list) else []
def _text(x): return " ".join(str(x.get(k,"")) for k in ("summary","answer_delta"))
def execute_tiles(result,index,previous_state):
    vals={}; conf=result.get("confidence_0_100"); conf=conf if isinstance(conf,(int,float)) else -1
    for field in REQUIRED_FIELDS: vals["schema_"+field]=field in result
    vals.update({
      "summary_nonempty":bool(str(result.get("summary","")).strip()),"answer_delta_nonempty":bool(str(result.get("answer_delta","")).strip()),
      "facts_list":isinstance(result.get("facts"),list),"claims_list":isinstance(result.get("claims"),list),"assumptions_list":isinstance(result.get("assumptions"),list),
      "uncertainties_list":isinstance(result.get("uncertainties"),list),"counterarguments_list":isinstance(result.get("counterarguments"),list),
      "provenance_list":isinstance(result.get("provenance"),list),"safety_flags_list":isinstance(result.get("safety_flags"),list),
      "missing_evidence_list":isinstance(result.get("missing_evidence"),list),"corrections_list":isinstance(result.get("corrections"),list),
      "dependencies_list":isinstance(result.get("dependencies"),list),"confidence_numeric":conf>=0,"confidence_range":0<=conf<=100,
      "disposition_allowed":result.get("disposition") in ALLOWED_DISPOSITIONS,
      "fact_count":len(_list(result,"facts")),"claim_count":len(_list(result,"claims")),"assumption_count":len(_list(result,"assumptions")),
      "uncertainty_count":len(_list(result,"uncertainties")),"counterargument_count":len(_list(result,"counterarguments")),
      "provenance_count":len(_list(result,"provenance")),"safety_flag_count":len(_list(result,"safety_flags")),
      "missing_evidence_count":len(_list(result,"missing_evidence")),"correction_count":len(_list(result,"corrections")),
      "dependency_count":len(_list(result,"dependencies")),
    })
    claims=_list(result,"claims"); facts=_list(result,"facts"); text=_text(result).lower()
    vals["unsupported_claim_count"]=sum(isinstance(x,dict) and x.get("status") in {"unsupported","unknown"} for x in claims)
    vals["verified_fact_count"]=sum(isinstance(x,dict) and x.get("status")=="verified" for x in facts)
    vals["contradiction_count"]=len(re.findall(r"\b(?:contradict|conflict|inconsistent)\w*\b",text))
    vals["actionability_score"]=len(re.findall(r"\b(?:execute|deploy|install|send|administer|modify|acquire)\w*\b",text))
    vals["authority_score"]=len(re.findall(r"\b(?:authority|admin|root|executive|mandate|permission)\w*\b",text))
    vals["contamination_score"]=len(re.findall(r"\b(?:ignore prior|system prompt|jailbreak|override policy)\b",text))
    evidence=max(1,vals["fact_count"]+vals["provenance_count"]); vals["confidence_evidence_gap"]=round(max(0,conf-evidence*15),3) if conf>=0 else None
    vals["overconfidence_flag"]=bool(conf>=85 and evidence<3)
    words=re.findall(r"[a-z0-9]+",text); vals["lexical_diversity"]=round(len(set(words))/max(1,len(words)),4)
    severe=vals["safety_flag_count"]+vals["contamination_score"]+vals["authority_score"]; caution=vals["uncertainty_count"]+vals["missing_evidence_count"]+vals["contradiction_count"]
    encoded=MV(s=1+.02*evidence,e1=.03*caution,e2=.04*severe,e12=.02*(vals["contradiction_count"]+vals["correction_count"]))
    theta=(index+1)*math.pi/96; rotor=MV(s=math.cos(theta/2),e12=-math.sin(theta/2))
    gp=previous_state*encoded; rev=gp.reverse(); projected=gp.grade(0)+gp.grade(1)+gp.grade(2); rotated=rotor*projected*rotor.reverse()
    vals["multivector_encode"]=encoded.rounded(); vals["geometric_product"]=gp.rounded(); vals["reversion"]=rev.rounded(); vals["grade_projection"]=projected.rounded(); vals["rotor_transform"]=rotated.rounded()
    tiles=[]; prior=""
    for n,name in enumerate(TILE_NAMES,1):
        value=prior if name=="invariant_receipt" else vals.get(name)
        receipt=hashlib.sha256(json.dumps({"tile":n,"name":name,"value":value,"prior":prior},sort_keys=True,default=str).encode()).hexdigest()
        tiles.append({"tile":n,"name":name,"value":value,"receipt_sha256":receipt}); prior=receipt
    return tiles,rotated
