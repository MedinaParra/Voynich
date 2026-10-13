#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re
from collections import defaultdict
from pathlib import Path
SEED=20261007
BLOBS={'A':'2a4533ab9bdfa85db9bad602d590978953055df1','B':'7f491b574b65e5fba6b553e57372c3fa50e10fec'}

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def clean_tokens(x):
 x=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',x).replace('?',' ')
 return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',x)
def gtype(pos):
 m=re.search(r'([PLCR])(?:[A-Za-z0-9]*)',pos); return m.group(1) if m else None

def parse(raw):
 pages={}; labels={}; running=defaultdict(list)
 for line in raw.splitlines():
  p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
  if p:
   m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2))); pages[p.group(1)]=(m.get('L','?'),m.get('H','?')); continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m.group(1): continue
  locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]; cur,hand=pages.get(fol,('?','?')); toks=clean_tokens(text)
  if re.search(r'(L[A-Za-z]?)',pos) and len(toks)==1 and '?' not in text:
   labels[locus]=(fol,toks[0],cur,hand); continue
  if gtype(pos)=='P':
   for t in toks: running[(fol,cur,hand,len(t))].append(t)
 return labels,running

def build(la,ra,lb,rb):
 common=[]
 for locus in sorted(set(la)&set(lb)):
  a,b=la[locus],lb[locus]
  if a[1:]!=b[1:]: continue
  fol,t,cur,hand=a; ka=(fol,cur,hand,len(t)); kb=(fol,cur,hand,len(t))
  if not ra.get(ka) or not rb.get(kb): continue
  common.append((locus,fol,t,cur,hand,ka,kb))
 rnga=random.Random(SEED); rngb=random.Random(SEED); pa=[]; pb=[]
 for locus,fol,t,cur,hand,ka,kb in common:
  ca,cb=ra[ka],rb[kb]
  pa.append((fol,t,ca[rnga.randrange(len(ca))]))
  pb.append((fol,t,cb[rngb.randrange(len(cb))]))
 return pa,pb

def body(t): return t[2:-1]
def fs(t):
 b=body(t); return (b.count('o')/len(b), b.count('a')/len(b))
def tstat(ds):
 n=len(ds); mu=sum(ds)/n
 if n<2:return 0.0
 v=sum((x-mu)**2 for x in ds)/(n-1)
 if v==0:return 0.0 if mu==0 else (1e12 if mu>0 else -1e12)
 return mu/(math.sqrt(v)/math.sqrt(n))

def eval_source(pairs,nperm,seed):
 pairs=[p for p in pairs if len(p[1])>=5 and len(p[2])>=5]
 fols=len(set(p[0] for p in pairs)); n=len(pairs)
 if n<100 or fols<8:return {'status':'BLOCKED','retained_pairs':n,'represented_folios':fols,'permutations_completed':0,'reason':'sample threshold not met'}
 diffs=[[],[]]
 for _,l,c in pairs:
  fl,fc=fs(l),fs(c)
  for j in range(2): diffs[j].append(fl[j]-fc[j])
 obs_mean=[sum(d)/n for d in diffs]; obs_t=[tstat(d) for d in diffs]
 rng=random.Random(seed); maxnull=[]
 for _ in range(nperm):
  signs=[1 if rng.randrange(2) else -1 for _ in range(n)]
  ts=[]
  for j in range(2): ts.append(abs(tstat([diffs[j][i]*signs[i] for i in range(n)])))
  maxnull.append(max(ts))
 pf=[(1+sum(x>=abs(obs_t[j]) for x in maxnull))/(1+len(maxnull)) for j in range(2)]
 return {'retained_pairs':n,'represented_folios':fols,'mean_diff_o':obs_mean[0],'mean_diff_a':obs_mean[1],'t_o':obs_t[0],'t_a':obs_t[1],'p_fwer_o':pf[0],'p_fwer_a':pf[1],'permutations_completed':len(maxnull),'status':'VALID'}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source-a',type=Path,required=True); ap.add_argument('--source-b',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args()
 ba,bb=a.source_a.read_bytes(),a.source_b.read_bytes(); out={'classification':'H68_INTERNAL_OA_NOT_TRANSLATION','source_a_blob':blob_sha(ba),'source_b_blob':blob_sha(bb),'seed':SEED,'permutations_requested_each_source':a.permutations}
 if out['source_a_blob']!=BLOBS['A'] or out['source_b_blob']!=BLOBS['B']:
  out.update(status='BLOCKED',reason='blob mismatch'); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); return
 la,ra=parse(ba.decode()); lb,rb=parse(bb.decode()); pa,pb=build(la,ra,lb,rb); A=eval_source(pa,a.permutations,SEED); B=eval_source(pb,a.permutations,SEED+1); out['source_a']=A; out['source_b']=B
 if A.get('status')=='BLOCKED' or B.get('status')=='BLOCKED': out['status']='BLOCKED'
 else:
  reps=[]
  if A['mean_diff_o']>0 and B['mean_diff_o']>0 and A['p_fwer_o']<=.05 and B['p_fwer_o']<=.05: reps.append('residual_frac_o')
  if A['mean_diff_a']>0 and B['mean_diff_a']>0 and A['p_fwer_a']<=.05 and B['p_fwer_a']<=.05: reps.append('residual_frac_a')
  out['replicated_components']=reps; out['status']='PASS' if reps else 'FAIL'
 out.update(language_identification='NOT_RUN',semantic_identification='NOT_RUN',translation='NOT_RUN',decipherment='NOT_RUN'); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
