#!/usr/bin/env python3
import argparse,hashlib,json,random,re
from collections import defaultdict
from pathlib import Path
PRIMARY_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'; INDEPENDENT_BLOB='7f491b574b65e5fba6b553e57372c3fa50e10fec'
PRIMARY_SEED=20261011; INDEPENDENT_SEED=20261012

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def clean_tokens(text):
 clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text)
 return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean)
def starts_q(t): return int(t.startswith('q'))

def parse(raw):
 pages={}; labels=defaultdict(list); initial=defaultdict(list); cand=0
 for line in raw.splitlines():
  p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
  if p:
   m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2))); pages[p.group(1)]={'quire':m.get('Q','?'),'currier':m.get('L','?'),'hand':m.get('H','?')}; continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m.group(1): continue
  locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]
  if '?' in text: continue
  toks=clean_tokens(text); meta=pages.get(fol,{'quire':'?','currier':'?','hand':'?'})
  is_label=bool(re.search(r'(L[A-Za-z]?)',pos))
  if is_label and len(toks)==1:
   cand+=1; t=toks[0]; labels[(fol,meta['currier'],meta['hand'],len(t))].append(t)
  elif not is_label and toks:
   t=toks[0]; initial[(fol,meta['currier'],meta['hand'],len(t))].append(t)
 return pages,labels,initial,cand

def specs_for(pages,labels,initial):
 specs=[]; counts=defaultdict(int); excluded=0
 for key,labs in labels.items():
  runs=initial.get(key,[])
  if not runs: excluded+=len(labs); continue
  q=pages.get(key[0],{}).get('quire','?'); counts[q]+=len(labs)
  ql=sum(map(starts_q,labs)); qr=sum(map(starts_q,runs)); nL=len(labs); nR=len(runs)
  specs.append({'quire':q,'nL':nL,'nR':nR,'nT':nL+nR,'qL':ql,'qR':qr,'qT':ql+qr})
 return specs,counts,excluded

def D(ss):
 n=sum(s['nL'] for s in ss)
 return sum(s['qL']-s['nL']*s['qT']/s['nT'] for s in ss)/n if n else 0.0

def perm_D(ss,rng):
 n=sum(s['nL'] for s in ss); r=0.0
 for s in ss:
  ix=rng.sample(range(s['nT']),s['nL']); pq=sum(i<s['qT'] for i in ix); r+=pq-s['nL']*s['qT']/s['nT']
 return r/n

def run_one(path,blob,seed,perms):
 b=path.read_bytes(); got=blob_sha(b)
 if got!=blob: raise SystemExit(f'frozen corpus mismatch: {got}')
 pages,labels,initial,cand=parse(b.decode()); specs,counts,excluded=specs_for(pages,labels,initial)
 eq=sorted(q for q,n in counts.items() if q!='?' and n>=8); es=[s for s in specs if s['quire'] in eq]
 nl=sum(s['nL'] for s in es); nr=sum(s['nR'] for s in es)
 out={'source_blob':got,'candidate_labels':cand,'excluded_labels_no_line_initial_stratum':excluded,'quire_label_counts':dict(sorted(counts.items())),'evaluable_quires':eq,'included_exact_strata':len(es),'included_label_instances':nl,'included_line_initial_instances':nr,'seed':seed,'permutations_requested':perms}
 if nl<50 or len(eq)<4 or len(es)<20:
  out.update(status='BLOCKED',reason='frozen support gate not met',permutations_completed=0); return out
 obs=D(es); perq={q:D([s for s in es if s['quire']==q]) for q in eq}; neg=sum(v<0 for v in perq.values())
 rng=random.Random(seed); null=[perm_D(es,rng) for _ in range(perms)]; p=(1+sum(abs(x)>=abs(obs) for x in null))/(1+len(null))
 out.update(status='POSITIVE' if len(null)==999 and obs<=-0.05 and p<=0.01 and neg>=3 else 'NEGATIVE',observed_conditional_D=obs,per_quire_conditional_D=perq,quires_negative=neg,raw_label_q_prevalence=sum(s['qL'] for s in es)/nl,raw_line_initial_q_prevalence=sum(s['qR'] for s in es)/nr,null_mean_D=sum(null)/len(null),null_max_abs_D=max(abs(x) for x in null),monte_carlo_p_two_sided=p,permutations_completed=len(null))
 return out

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--primary',type=Path,required=True); ap.add_argument('--independent',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args()
 p=run_one(a.primary,PRIMARY_BLOB,PRIMARY_SEED,a.permutations); i=run_one(a.independent,INDEPENDENT_BLOB,INDEPENDENT_SEED,a.permutations)
 status='BLOCKED' if 'BLOCKED' in (p['status'],i['status']) else ('PASS_LINE_INITIAL_Q_DEPLETION' if p['status']=='POSITIVE' and i['status']=='POSITIVE' else 'FAIL')
 out={'classification':'H70_Q_INITIAL_LINE_INITIAL_CONTROL_NOT_SEMANTIC','status':status,'primary':p,'independent':i}; a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
