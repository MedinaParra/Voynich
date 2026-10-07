#!/usr/bin/env python3
import argparse,hashlib,json,random,re
from collections import defaultdict
from pathlib import Path
PRIMARY_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'; INDEPENDENT_BLOB='7f491b574b65e5fba6b553e57372c3fa50e10fec'
PRIMARY_SEED=20261013; INDEPENDENT_SEED=20261014

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def clean_tokens(text):
 clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text)
 return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean)
def q(t): return int(t.startswith('q'))

def parse(raw):
 pages={}; ini=defaultdict(list); internal=defaultdict(list)
 for line in raw.splitlines():
  p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
  if p:
   m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2))); pages[p.group(1)]={'quire':m.get('Q','?'),'currier':m.get('L','?'),'hand':m.get('H','?')}; continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m.group(1): continue
  locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]
  if '?' in text or re.search(r'(L[A-Za-z]?)',pos): continue
  toks=clean_tokens(text)
  if not toks: continue
  meta=pages.get(fol,{'quire':'?','currier':'?','hand':'?'})
  t=toks[0]; ini[(fol,meta['currier'],meta['hand'],len(t))].append(t)
  for t in toks[1:]: internal[(fol,meta['currier'],meta['hand'],len(t))].append(t)
 return pages,ini,internal

def make_specs(pages,ini,internal):
 ss=[]; counts=defaultdict(int)
 for key,I in ini.items():
  N=internal.get(key,[])
  if not N: continue
  qu=pages.get(key[0],{}).get('quire','?'); counts[qu]+=len(I)
  qi=sum(map(q,I)); qn=sum(map(q,N)); nI=len(I); nN=len(N)
  ss.append({'quire':qu,'nI':nI,'nN':nN,'nT':nI+nN,'qI':qi,'qN':qn,'qT':qi+qn})
 return ss,counts

def D(ss):
 n=sum(s['nI'] for s in ss)
 return sum(s['qI']-s['nI']*s['qT']/s['nT'] for s in ss)/n if n else 0.0

def perm_D(ss,rng):
 n=sum(s['nI'] for s in ss); r=0.0
 for s in ss:
  picks=rng.sample(range(s['nT']),s['nI']); pq=sum(i<s['qT'] for i in picks); r+=pq-s['nI']*s['qT']/s['nT']
 return r/n

def run_one(path,blob,seed,perms):
 b=path.read_bytes(); got=blob_sha(b)
 if got!=blob: raise SystemExit(f'frozen corpus mismatch: {got}')
 pages,ini,internal=parse(b.decode()); ss,counts=make_specs(pages,ini,internal)
 eq=sorted(x for x,n in counts.items() if x!='?' and n>=20); es=[s for s in ss if s['quire'] in eq]; ni=sum(s['nI'] for s in es); nn=sum(s['nN'] for s in es)
 out={'source_blob':got,'evaluable_quires':eq,'quire_initial_counts':dict(sorted(counts.items())),'included_exact_strata':len(es),'included_initial_instances':ni,'included_internal_instances':nn,'seed':seed,'permutations_requested':perms}
 if ni<200 or len(es)<50 or len(eq)<4:
  out.update(status='BLOCKED',reason='frozen support gate not met',permutations_completed=0); return out
 obs=D(es); perq={x:D([s for s in es if s['quire']==x]) for x in eq}; pos=sum(v>0 for v in perq.values()); rng=random.Random(seed); null=[perm_D(es,rng) for _ in range(perms)]; p=(1+sum(abs(v)>=abs(obs) for v in null))/(1+len(null))
 out.update(status='POSITIVE' if len(null)==999 and obs>=0.05 and p<=0.01 and pos>=3 else 'NEGATIVE',observed_D_pos=obs,per_quire_D_pos=perq,quires_positive=pos,raw_initial_q_prevalence=sum(s['qI'] for s in es)/ni,raw_internal_q_prevalence=sum(s['qN'] for s in es)/nn,null_mean_D_pos=sum(null)/len(null),null_max_abs_D_pos=max(abs(v) for v in null),monte_carlo_p_two_sided=p,permutations_completed=len(null)); return out

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--primary',type=Path,required=True); ap.add_argument('--independent',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args()
 p=run_one(a.primary,PRIMARY_BLOB,PRIMARY_SEED,a.permutations); i=run_one(a.independent,INDEPENDENT_BLOB,INDEPENDENT_SEED,a.permutations)
 status='BLOCKED' if 'BLOCKED' in (p['status'],i['status']) else ('PASS_REPLICATED_Q_LINE_INITIAL_ENRICHMENT' if p['status']=='POSITIVE' and i['status']=='POSITIVE' else 'FAIL')
 out={'classification':'H71_RUNNING_Q_LINE_POSITION_NOT_SEMANTIC','status':status,'primary':p,'independent':i}; a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
