LAYERS=[
("FDL","Frame Detection Layer","Lock the actual question, decision, scope, actors, constraints, and hidden framing pressure."),
("AML","Assumption Map Layer","Map explicit, implicit, causal, measurement, and operational assumptions with falsifiers."),
("AWP","Assertion Weighting and Prioritization","Weight claims by source quality, consequence, reversibility, relevance, and uncertainty."),
("BST","Breaker Stress Test","Search for counterexamples, edge cases, adversarial inputs, distribution shifts, and catastrophic paths."),
("CRL","Claim Recovery Layer","Repair falsified or overstated claims minimally and disclose every change."),
("MCS","Monte Carlo Simulation Layer","Explore multiple uncertain futures without presenting simulated outcomes as observations."),
("DSV","Decision Safety Valve","Define stop conditions, rollback, escalation, human review, and safe fallback states."),
("TRC","Trace Consistency Layer","Check consistency across evidence order, paraphrase, prior outputs, and corrections."),
("CON","Contradiction Scan Layer","Find material conflicts and distinguish contradiction from scope or definition differences."),
("EVD","Evidence Demand Layer","Specify minimum evidence, verification state, source authority, and unresolved gaps."),
("REC","Recursion Planning Layer","Allocate review depth, dependencies, termination criteria, and anti-theater checks."),
("GOV","Governance Gate Layer","Apply prespecified release gates and fail closed when required controls are missing."),
("OUT","Output Record Layer","Create an inspectable record separating facts, claims, inferences, uncertainty, and actions."),
("RIL","Recursion Integrity Layer","Detect duplicated checks, circular scoring, self-validation, and fabricated independence."),
("IAL","Incentive Alignment Layer","Analyze incentives, conflicts, gaming pressure, Goodhart effects, and stakeholder impact."),
("AOG","Authority Output Gate","Preserve scope, corrigibility, human authority, and refusal of unauthorized self-expansion."),
]

REQUIRED_FIELDS=[
 "layer_code","summary","answer_delta","facts","claims","assumptions","uncertainties",
 "counterarguments","provenance","safety_flags","missing_evidence","corrections",
 "dependencies","confidence_0_100","disposition"
]
ALLOWED_DISPOSITIONS={"PASS","RELEASE/CAUTION","BLOCK","INSUFFICIENT_EVIDENCE"}

def layer_request(index,question,envelope,prior,firewall):
    code,name,objective=LAYERS[index]
    return {
      "protocol":"DAXDA-V10-LAYER-REQUEST-1.0","layer_index":index+1,"layer_code":code,
      "layer_name":name,"objective":objective,"question":question,"envelope":envelope,
      "v9_preflight":{"verdict":firewall["verdict"],"decision_rule":firewall["decision_rule"],"flags":firewall["flags"]},
      "prior_layers":prior,
      "required_fields":REQUIRED_FIELDS,
      "instruction":"Perform the named layer transformation. Return JSON only. Give concise auditable reasoning summaries, not private chain-of-thought. Do not invent evidence."
    }

