#!/usr/bin/env python3
import json
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parent
def read(p): return [json.loads(x) for x in p.open(encoding='utf-8') if x.strip()]
i=read(R/'benchmark_inputs_blind.jsonl'); l=read(R/'benchmark_labels_private.jsonl')
assert len(i)==len(l)==12000
assert {x['case_id'] for x in i}=={x['case_id'] for x in l}
assert Counter(x['expected_disposition'] for x in l)==Counter({'BLOCK':6000,'WARN':3000,'RELEASE':3000})
s=Counter(x['subgroup'] for x in l); assert len(s)==60 and set(s.values())=={200}
print(json.dumps({'status':'PASS','cases':12000,'labels':dict(Counter(x['expected_disposition'] for x in l)),'subgroups':60},indent=2))
