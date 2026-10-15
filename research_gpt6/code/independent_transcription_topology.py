#!/usr/bin/env python3
import argparse,json,math,random,re,hashlib
from collections import Counter,defaultdict
from pathlib import Path
import topology_from_text as h1
import topology_crossview_h2 as h2

SEED=20261007
REPL_GIT_BLOB='7f491b574b65e5fba6b553e57372c3fa50e10fec'

def git_blob_sha(b):
 return hashlib.sha1((f'blob {len(b)}\0').encode()+b).hexdigest()

def addnorm(c,prefix,d):
 n=sum(c.values()) or 1
 for k,v in c.items(): d[prefix+str(k)]=v/n

def toks(line): return re.findall(r'[a-z]{2,}',line.lower())

def vector_r(p):
 lines=[toks(x) for x in p['lines']]; lines=[x for x in lines if x]
 d={}
 addnorm(Counter(min(len(x),20) for x in lines),'ntok:',d)
 addnorm(Counter(min(len(x[0]),15) for x in lines),'firstlen:',d)
 addnorm(Counter(min(len(x[-1]),15) for x in lines),'lastlen:',d)
 addnorm(Counter(min(sum(len(t) for t in x)//10,12) for x in lines),'charbin:',d)
 allc=Counter(t for x in lines for t in x)
 if lines:
  types=set(allc); d['repeat_type_fraction']=sum(allc[t]>1 for t in types)/len(types) if types else 0
  d['first_repeat']=sum(allc[x[0]]>1 for x in lines)/len(lines)
  d['last_repeat']=sum(allc[x[-1]]>1 for x in lines)/len(lines)
 else: d['repeat_type_fraction']=d['first_repeat']=d['last_repeat']=0
 return d

def cosine(a,b):
 dot=sum(v*b.get(k,0) for k,v in a.items()); aa=sum(v*v for v in a.values()); bb=sum(v*v for v in b.values())
 return 1-dot/math.sqrt(aa*bb) if aa and bb else 1.0

def mean_dist(edges,dist): return sum(dist[h2.edge(a,b)] for a,b in edges)/len(edges)

def matched_null(obs,groups,pages,available,rng,target):
 out=set(); items=list(obs); tries=0
 while len(out)<target and tries<target*500:
  u,v=rng.choice(items)
  pool=[x for x in groups[h1.strata(pages[v])] if x in available and x!=u and h2.edge(u,x) not in obs]
  if pool: out.add(h2.edge(u,rng.choice(pool)))
  tries+=1
 return out if len(out)==target else None

def random_null(available,rng,target):
 av=list(available); out=set(); tries=0
 while len(out)<target and tries<target*500:
  a,b=rng.sample(av,2); out.add(h2.edge(a,b)); tries+=1
 return out if len(out)==target else None

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--discovery',type=Path,required=True); ap.add_argument('--replication',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args()
 db=a.discovery.read_bytes(); rb=a.replication.read_bytes()
 if h1.blob_sha(db)!=h1.SOURCE_BLOB: raise SystemExit('frozen discovery corpus mismatch')
 if git_blob_sha(rb)!=REPL_GIT_BLOB: raise SystemExit('frozen replication Git blob mismatch')
 pages=h1.parse(db.decode()); fs=sorted(pages,key=h1.folio_num)
 rp=h1.parse(rb.decode(errors='replace'))
 prep={}
 for fam in ('A','B'):
  vec={f:h1.vector(pages[f],fam) for f in fs}; groups,cand,dist,ranked=h1.prepare(fs,pages,vec); prep[fam]=(groups,cand,dist)
 _,ea=h2.build_edges(fs,prep['A'][1],prep['A'][2]); _,eb=h2.build_edges(fs,prep['B'][1],prep['B'][2]); consensus=ea & eb
 available=set(fs)&set(rp); obs={e for e in consensus if e[0] in available and e[1] in available}
 out={'classification':'INDEPENDENT_TRANSCRIPTION_TOPOLOGY_NOT_TRANSLATION','discovery_blob':h1.SOURCE_BLOB,'replication_git_blob':REPL_GIT_BLOB,'discovery_eligible_folios':len(fs),'aligned_eligible_folios':len(available),'frozen_consensus_edges':len(consensus),'surviving_consensus_edges':len(obs),'permutations_requested':a.permutations}
 if len(available)<150:
  out.update(status='BLOCKED',reason='fewer than 150 aligned eligible folios')
 elif len(obs)<60:
  out.update(status='BLOCKED',reason='fewer than 60 surviving frozen consensus edges')
 else:
  vr={f:vector_r(rp[f]) for f in available}; av=sorted(available); dist={h2.edge(f,g):cosine(vr[f],vr[g]) for i,f in enumerate(av) for g in av[i+1:]}
  observed=mean_dist(obs,dist); groups=defaultdict(list)
  for f in fs: groups[h1.strata(pages[f])].append(f)
  rng=random.Random(SEED); null=[]; neg=[]; blocked=False
  for _ in range(a.permutations):
   ne=matched_null(obs,groups,pages,available,rng,len(obs)); re=random_null(available,rng,len(obs))
   if ne is None or re is None: blocked=True; break
   null.append(mean_dist(ne,dist)); neg.append(mean_dist(re,dist))
  if blocked or len(null)!=a.permutations:
   out.update(status='BLOCKED',permutations_completed=len(null),reason='null generation incomplete')
  else:
   nm=sum(null)/len(null); ng=sum(neg)/len(neg); p=(1+sum(x<=observed for x in null))/(1+len(null)); status='PASS' if observed<nm and p<=.05 else 'FAIL'
   out.update(status=status,observed_replication_distance=observed,matched_null_mean_distance=nm,negative_control_mean_distance=ng,monte_carlo_p=p,permutations_completed=len(null),negative_control_permutations_completed=len(neg))
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
