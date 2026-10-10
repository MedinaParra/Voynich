#!/usr/bin/env python3
import argparse,json,random,statistics
from pathlib import Path
import topology_from_text as h1
SEED=20261006

def edge(a,b): return tuple(sorted((a,b)))
def build_edges(fs,cand,dist):
 directed=[]
 for f in fs:
  if cand[f]: directed.append((f,min(cand[f],key=lambda g:dist[(f,g)])))
 return directed,set(edge(a,b) for a,b in directed)
def graph_stats(fs,edges):
 adj={f:set() for f in fs}
 for a,b in edges: adj[a].add(b); adj[b].add(a)
 seen=set(); comps=[]
 for f in fs:
  if f in seen: continue
  stack=[f]; seen.add(f); n=0
  while stack:
   x=stack.pop(); n+=1
   for y in adj[x]:
    if y not in seen: seen.add(y); stack.append(y)
  comps.append(n)
 deg=[len(adj[f]) for f in fs]
 return {'components':len(comps),'largest_component':max(comps) if comps else 0,'degree_min':min(deg) if deg else 0,'degree_mean':sum(deg)/len(deg) if deg else 0,'degree_max':max(deg) if deg else 0}
def validate(edges,vdist,physical):
 ds=[vdist[(a,b)] if (a,b) in vdist else vdist[(b,a)] for a,b in edges]
 overlap=sum(1 for e in edges if e in physical)/len(edges) if edges else 0
 return {'unique_edges':len(edges),'mean_validation_distance':sum(ds)/len(ds),'median_validation_distance':statistics.median(ds),'physical_neighbor_fraction':overlap}
def null_edges(fs,cand,rng):
 return set(edge(f,rng.choice(cand[f])) for f in fs if cand[f])
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args(); b=a.corpus.read_bytes()
 if h1.blob_sha(b)!=h1.SOURCE_BLOB: raise SystemExit('frozen corpus mismatch')
 pages=h1.parse(b.decode()); fs=sorted(pages,key=h1.folio_num); truth=h1.neighbors(fs,pages); physical=set()
 for f,ns in truth.items():
  for g in ns: physical.add(edge(f,g))
 prep={}
 for fam in ('A','B'):
  vec={f:h1.vector(pages[f],fam) for f in fs}; groups,cand,dist,ranked=h1.prepare(fs,pages,vec); prep[fam]=(cand,dist)
 out={'classification':'HOLISTIC_TOPOLOGY_CROSSVIEW_H2_NOT_TRANSLATION','source_blob':h1.SOURCE_BLOB,'eligible_folios':len(fs),'permutations_requested':a.permutations,'tests':{}}
 passes=[]; blocked=False
 for idx,(disc,val) in enumerate((('A','B'),('B','A'))):
  cand,ddist=prep[disc]; vdist=prep[val][1]; directed,edges=build_edges(fs,cand,ddist); key=f'{disc}_to_{val}'
  if len(edges)<50:
   out['tests'][key]={'status':'BLOCKED','unique_edges':len(edges)}; blocked=True; continue
  obs=validate(edges,vdist,physical); obs.update(graph_stats(fs,edges)); obs['directed_selections']=len(directed)
  rng=random.Random(SEED+idx); null=[]
  for _ in range(a.permutations):
   ne=null_edges(fs,cand,rng); null.append(validate(ne,vdist,physical)['mean_validation_distance'])
  p=(1+sum(x<=obs['mean_validation_distance'] for x in null))/(1+len(null))
  nm=sum(null)/len(null); status='PASS' if p<=.05 and obs['mean_validation_distance']<nm else 'FAIL'; passes.append(status=='PASS')
  out['tests'][key]={'status':status,'observed':obs,'null_mean_validation_distance':nm,'permutations_completed':len(null),'monte_carlo_p':p}
 out['status']='BLOCKED' if blocked else ('PASS' if len(passes)==2 and all(passes) else 'FAIL')
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
