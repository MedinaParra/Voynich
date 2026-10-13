#!/usr/bin/env python3
import argparse,json,random
from collections import defaultdict
from pathlib import Path
import topology_from_text as h1
import topology_crossview_h2 as h2
import topology_linegrammar_h3 as h3
SEED=20261006

def edge(a,b): return h2.edge(a,b)
def candidates(qfs,pages):
 return {f:[g for g in qfs if g!=f and h1.strata(pages[g])==h1.strata(pages[f])] for f in qfs}
def distances(qfs,vec):
 return {(f,g):h1.cosine(vec[f],vec[g]) for f in qfs for g in qfs if f!=g}
def build(qfs,cand,dist):
 out=set()
 for f in qfs:
  if cand[f]: out.add(edge(f,min(cand[f],key=lambda g:dist[(f,g)])))
 return out
def md(edges,dc): return sum(dc[edge(a,b)] for a,b in edges)/len(edges)
def random_edges(qfs,cand,rng,n):
 possible=set(edge(f,g) for f in qfs for g in cand[f])
 if len(possible)<n:return None
 return set(rng.sample(sorted(possible),n))
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args(); b=a.corpus.read_bytes()
 if h1.blob_sha(b)!=h1.SOURCE_BLOB: raise SystemExit('frozen corpus mismatch')
 pages=h1.parse(b.decode()); fs=sorted(pages,key=h1.folio_num); byq=defaultdict(list)
 for f in fs: byq[pages[f]['quire']].append(f)
 va={f:h1.vector(pages[f],'A') for f in fs}; vb={f:h1.vector(pages[f],'B') for f in fs}; vc={f:h3.vector_c(pages[f]) for f in fs}
 folds=[]; supported=[]
 for q,qfs in sorted(byq.items(),key=lambda z:str(z[0])):
  rec={'quire':q,'eligible_folios':len(qfs)}
  if len(qfs)<8: rec.update(status='EXCLUDED',reason='fewer than 8 eligible folios'); folds.append(rec); continue
  cand=candidates(qfs,pages); valid=sum(bool(cand[f]) for f in qfs); rec['valid_candidate_folios']=valid
  if valid<8: rec.update(status='EXCLUDED',reason='fewer than 8 folios with frozen-confound candidate'); folds.append(rec); continue
  da=distances(qfs,va); db=distances(qfs,vb); ea=build(qfs,cand,da); eb=build(qfs,cand,db); cons=ea&eb; rec['consensus_edges']=len(cons)
  if len(cons)<3: rec.update(status='UNSUPPORTED',reason='fewer than 3 consensus edges'); folds.append(rec); continue
  dc={edge(f,g):h3.cosine(vc[f],vc[g]) for i,f in enumerate(qfs) for g in qfs[i+1:]}; rec['observed_family_c_mean_distance']=md(cons,dc); rec['status']='SUPPORTED'; folds.append(rec); supported.append((q,qfs,cand,cons,dc,rec))
 out={'classification':'HOLISTIC_TOPOLOGY_LOQO_H4_NOT_TRANSLATION','source_blob':h1.SOURCE_BLOB,'eligible_folios':len(fs),'permutations_requested':a.permutations,'folds':folds,'evaluable_quires':sum(r.get('status')!='EXCLUDED' for r in folds),'supported_quires':len(supported),'pooled_consensus_edges':sum(len(x[3]) for x in supported)}
 if len(supported)<3 or out['pooled_consensus_edges']<30:
  out.update(status='BLOCKED',reason='insufficient supported quires or pooled consensus edges',permutations_completed=0)
 else:
  obs=sum(sum(x[4][edge(a,b)] for a,b in x[3]) for x in supported)/out['pooled_consensus_edges']; rng=random.Random(SEED); null=[]; blocked=False
  for _ in range(a.permutations):
   vals=[]
   for q,qfs,cand,cons,dc,rec in supported:
    ne=random_edges(qfs,cand,rng,len(cons))
    if ne is None: blocked=True; break
    vals.extend(dc[e] for e in ne)
   if blocked: break
   null.append(sum(vals)/len(vals))
  if blocked or len(null)!=a.permutations: out.update(status='BLOCKED',reason='matched within-quire null generation incomplete',permutations_completed=len(null))
  else:
   nm=sum(null)/len(null); p=(1+sum(x<=obs for x in null))/(1+len(null)); out.update(status='PASS' if p<=.05 and obs<nm else 'FAIL',observed_aggregate_family_c_distance=obs,null_mean_distance=nm,monte_carlo_p=p,permutations_completed=len(null))
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
