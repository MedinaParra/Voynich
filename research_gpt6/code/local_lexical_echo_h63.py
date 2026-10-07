#!/usr/bin/env python3
import argparse,hashlib,json,math,random,re
from collections import defaultdict,Counter
from pathlib import Path
PRIMARY_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
INDEPENDENT_BLOB='7f491b574b65e5fba6b553e57372c3fa50e10fec'
SEED=20261007

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def clean_tokens(text):
 clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text).replace('?',' ')
 return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean)
def parse(raw):
 pages={}; labels=defaultdict(list); running=defaultdict(list)
 for line in raw.splitlines():
  p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
  if p:
   m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2)))
   pages[p.group(1)]={'quire':m.get('Q','?'),'currier':m.get('L','?'),'hand':m.get('H','?')}
   continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m.group(1): continue
  locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]
  toks=clean_tokens(text); lm=re.search(r'(L[A-Za-z]?)',pos)
  if lm and len(toks)==1 and '?' not in text:
   labels[fol].append(toks[0]); continue
  if not lm:
   running[fol].extend(toks)
 return pages,labels,running

def core(t): return t[1:-1] if len(t)>=4 else None

def weights_from_sets(sets_by_folio):
 folios=[f for f,s in sets_by_folio.items() if s]; n=len(folios); df=Counter()
 for f in folios:
  for x in sets_by_folio[f]: df[x]+=1
 return {x:1.0+math.log((n+1)/(d+1)) for x,d in df.items()},n

def weighted_echo(source_set,target_set,w):
 den=sum(w.get(x,1.0) for x in source_set)
 if den<=0:return 0.0
 return sum(w.get(x,1.0) for x in source_set if x in target_set)/den

def mean(xs): return sum(xs)/len(xs) if xs else 0.0

def run_one(path,expected_blob,permutations):
 b=path.read_bytes(); got=blob_sha(b)
 if got!=expected_blob: raise SystemExit(f'frozen corpus mismatch: expected {expected_blob}, got {got}')
 pages,labels,running=parse(b.decode())
 lcore={f:set(filter(None,(core(t) for t in ts))) for f,ts in labels.items()}
 rcore={f:set(filter(None,(core(t) for t in ts))) for f,ts in running.items()}
 lfull={f:set(ts) for f,ts in labels.items()}; rfull={f:set(ts) for f,ts in running.items()}
 cw,nrun=weights_from_sets(rcore); fw,_=weights_from_sets(rfull)
 eligible=[]; controls={}
 for f in sorted(pages):
  if len(lcore.get(f,set()))<2 or not rcore.get(f): continue
  m=pages[f]
  cc=[g for g in sorted(pages) if g!=f and rcore.get(g) and pages[g]['quire']==m['quire'] and pages[g]['currier']==m['currier'] and pages[g]['hand']==m['hand']]
  if len(cc)>=2:
   eligible.append(f); controls[f]=cc
 quires=sorted(set(pages[f]['quire'] for f in eligible if pages[f]['quire']!='?'))
 out={'source_blob':got,'parsed_folios':len(pages),'running_core_folios':nrun,'label_folios':sum(bool(v) for v in labels.values()),'evaluable_source_folios':len(eligible),'represented_quires':quires,'permutations_requested':permutations}
 if len(eligible)<20 or len(quires)<4:
  out.update(status='BLOCKED',permutations_completed=0,reason='preregistered source-folio/quire support threshold not met'); return out
 def ecore(f,g): return weighted_echo(lcore[f],rcore.get(g,set()),cw)
 deltas=[]; own=[]; ctrl=[]; byq=defaultdict(list)
 for f in eligible:
  o=ecore(f,f); c=mean([ecore(f,g) for g in controls[f]]); d=o-c
  own.append(o); ctrl.append(c); deltas.append(d); byq[pages[f]['quire']].append(d)
 obs=mean(deltas); med=sorted(deltas)[len(deltas)//2] if len(deltas)%2 else mean(sorted(deltas)[len(deltas)//2-1:len(deltas)//2+1])
 frac=sum(d>0 for d in deltas)/len(deltas)
 rng=random.Random(SEED); null=[]
 for _ in range(permutations):
  ds=[]
  for f in eligible:
   cand=[f]+controls[f]; j=rng.randrange(len(cand)); pseudo=cand[j]; others=cand[:j]+cand[j+1:]
   ds.append(ecore(f,pseudo)-mean([ecore(f,g) for g in others]))
  null.append(mean(ds))
 pval=(1+sum(x>=obs for x in null))/(1+len(null))
 status='PASS_LOCAL_LEXICAL_ECHO' if len(null)==999 and obs>0 and pval<=0.01 and frac>0.55 else 'FAIL'
 # Non-gating exact-full-token diagnostic, using same source folios and target pools.
 def efull(f,g): return weighted_echo(lfull.get(f,set()),rfull.get(g,set()),fw)
 fd=[]
 for f in eligible:
  fd.append(efull(f,f)-mean([efull(f,g) for g in controls[f]]))
 out.update(status=status,mean_own_folio_echo=mean(own),mean_matched_control_echo=mean(ctrl),observed_mean_delta=obs,median_delta=med,fraction_folios_positive_delta=frac,per_quire_mean_delta={q:mean(v) for q,v in sorted(byq.items())},null_mean_delta=mean(null),null_max_delta=max(null),monte_carlo_p=pval,permutations_completed=len(null),full_token_diagnostic_mean_delta=mean(fd))
 return out

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--primary',type=Path,required=True); ap.add_argument('--independent',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args()
 p=run_one(a.primary,PRIMARY_BLOB,a.permutations); i=run_one(a.independent,INDEPENDENT_BLOB,a.permutations)
 status='PASS_REPLICATED_LOCAL_LEXICAL_ECHO' if p.get('status')=='PASS_LOCAL_LEXICAL_ECHO' and i.get('status')=='PASS_LOCAL_LEXICAL_ECHO' else ('BLOCKED' if 'BLOCKED' in (p.get('status'),i.get('status')) else 'FAIL')
 out={'classification':'H63_LOCAL_LEXICAL_ECHO_NOT_TRANSLATION','seed':SEED,'status':status,'primary':p,'independent':i}
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
