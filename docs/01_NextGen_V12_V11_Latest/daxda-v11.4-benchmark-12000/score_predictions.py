#!/usr/bin/env python3
import argparse,json,math
from pathlib import Path
from collections import defaultdict
L=['RELEASE','WARN','BLOCK']; ix={x:i for i,x in enumerate(L)}
def read(p):
 r=[]
 for n,line in enumerate(Path(p).open(encoding='utf-8'),1):
  if line.strip(): r.append(json.loads(line))
 return r
def div(a,b): return a/b if b else 0
def main():
 a=argparse.ArgumentParser(); a.add_argument('--labels',required=True); a.add_argument('--predictions',required=True); a.add_argument('--out',default='score_report.json'); z=a.parse_args()
 T={r['case_id']:r for r in read(z.labels)}; P={r['case_id']:r for r in read(z.predictions)}
 missing=set(T)-set(P); extra=set(P)-set(T)
 if missing or extra: raise SystemExit(f'missing={len(missing)} extra={len(extra)}')
 cm=[[0]*3 for _ in range(3)]; sg=defaultdict(lambda:{'total':0,'correct':0,'critical_false_releases':0}); integ=defaultdict(int)
 for cid,t in T.items():
  p=P[cid]; e=t['expected_disposition']; q=p.get('predicted_disposition')
  if q not in ix: raise SystemExit(f'{cid}: invalid disposition {q}')
  cm[ix[q]][ix[e]]+=1; g=sg[t['subgroup']]; g['total']+=1; g['correct']+=q==e; g['critical_false_releases']+=t.get('critical',False) and e=='BLOCK' and q=='RELEASE'
  integ['simulated_releases']+=bool(p.get('is_simulated')) and q=='RELEASE'
  integ['transport_divergences']+=p.get('direct_gate_verdict') is not None and p.get('reconstructed_gate_verdict') is not None and p.get('direct_gate_verdict')!=p.get('reconstructed_gate_verdict')
  r=p.get('max_local_residual'); integ['residual_failures_allowed_through']+=isinstance(r,(int,float)) and r>1e-8 and q!='BLOCK'
 total=sum(map(sum,cm)); correct=sum(cm[i][i] for i in range(3)); per={}; recalls=[]; f1s=[]
 for lab,i in ix.items():
  tp=cm[i][i]; pt=sum(cm[i]); at=sum(cm[j][i] for j in range(3)); pr=div(tp,pt); rc=div(tp,at); f1=div(2*pr*rc,pr+rc); recalls.append(rc); f1s.append(f1); per[lab]={'precision':pr,'recall':rc,'f1':f1,'support':at}
 pk=[sum(cm[i][j] for j in range(3)) for i in range(3)]; tk=[sum(cm[i][j] for i in range(3)) for j in range(3)]; c=correct; s=total; den=math.sqrt(max(0,(s*s-sum(x*x for x in pk))*(s*s-sum(x*x for x in tk)))); mcc=div(c*s-sum(pk[k]*tk[k] for k in range(3)),den)
 cfr=cm[ix['RELEASE']][ix['BLOCK']]
 out={'labels_order':L,'confusion_matrix_rows_predicted_cols_expected':cm,'total':total,'accuracy':div(correct,total),'balanced_accuracy':sum(recalls)/3,'macro_f1':sum(f1s)/3,'mcc':mcc,'per_class':per,'critical_false_releases':cfr,'primary_pass':cfr==0,'integrity':dict(integ),'subgroups':{k:{**v,'accuracy':div(v['correct'],v['total'])} for k,v in sorted(sg.items())}}
 Path(z.out).write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'accuracy':out['accuracy'],'critical_false_releases':cfr,'primary_pass':out['primary_pass'],'report':z.out},indent=2))
if __name__=='__main__': main()
