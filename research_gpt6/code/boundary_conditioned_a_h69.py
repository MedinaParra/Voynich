#!/usr/bin/env python3
import argparse, hashlib, json, random, re
from collections import defaultdict
from pathlib import Path
SEED=20261007
BLOBS={'A':'2a4533ab9bdfa85db9bad602d590978953055df1','B':'7f491b574b65e5fba6b553e57372c3fa50e10fec'}
def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def toks(x):
 x=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',x).replace('?',' ')
 return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',x)
def typ(pos):
 m=re.search(r'([PLCR])(?:[A-Za-z0-9]*)',pos); return m.group(1) if m else None
def parse(raw):
 pages={}; lab={}; p=defaultdict(list)
 for line in raw.splitlines():
  h=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
  if h:
   d=dict(re.findall(r'\$([A-Z])=([^\s>]+)',h.group(2))); pages[h.group(1)]=(d.get('L','?'),d.get('H','?')); continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m.group(1): continue
  locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]; cur,hand=pages.get(fol,('?','?')); ts=toks(text)
  if re.search(r'(L[A-Za-z]?)',pos) and len(ts)==1 and '?' not in text:
   lab[locus]=(fol,ts[0],cur,hand); continue
  if typ(pos)=='P':
   for t in ts:
    if len(t)>=5: p[(fol,cur,hand,len(t),t[:2],t[-1])].append(t)
 return lab,p
def build(la,pa,lb,pb):
 eligible=[]
 for locus in sorted(set(la)&set(lb)):
  a,b=la[locus],lb[locus]
  if a[1:]!=b[1:] or len(a[1])<5: continue
  fol,t,cur,hand=a; key=(fol,cur,hand,len(t),t[:2],t[-1])
  if pa.get(key) and pb.get(key): eligible.append((locus,fol,t,key))
 ra=random.Random(SEED); rb=random.Random(SEED); A=[]; B=[]
 for locus,fol,t,key in eligible:
  ca=sorted(pa[key]); cb=sorted(pb[key]); A.append((fol,t,ca[ra.randrange(len(ca))])); B.append((fol,t,cb[rb.randrange(len(cb))]))
 return A,B
def fa(t):
 b=t[2:-1]; return b.count('a')/len(b)
def test(pairs,n,seed):
 N=len(pairs); fols=len(set(x[0] for x in pairs))
 if N<50 or fols<8:return {'status':'BLOCKED','pairs':N,'folios':fols,'permutations_completed':0,'reason':'sample threshold not met'}
 d=[fa(l)-fa(c) for _,l,c in pairs]; obs=sum(d)/N; rng=random.Random(seed); null=[]
 for _ in range(n): null.append(sum((x if rng.randrange(2) else -x) for x in d)/N)
 p=(1+sum(x>=obs for x in null))/(1+len(null)); return {'pairs':N,'folios':fols,'mean_diff_a':obs,'null_mean':sum(null)/len(null),'p_one_sided':p,'permutations_completed':len(null),'status':'PASS' if obs>0 and p<=.05 and len(null)==999 else 'FAIL'}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source-a',type=Path,required=True); ap.add_argument('--source-b',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args(); ba=a.source_a.read_bytes(); bb=a.source_b.read_bytes(); out={'classification':'H69_BOUNDARY_CONDITIONED_A_NOT_TRANSLATION','source_a_blob':blob_sha(ba),'source_b_blob':blob_sha(bb),'seed_a':SEED,'seed_b':SEED+1}
 if out['source_a_blob']!=BLOBS['A'] or out['source_b_blob']!=BLOBS['B']: out.update(status='BLOCKED',reason='blob mismatch')
 else:
  la,pa=parse(ba.decode()); lb,pb=parse(bb.decode()); A,B=build(la,pa,lb,pb); out['source_a']=test(A,a.permutations,SEED); out['source_b']=test(B,a.permutations,SEED+1); out['common_pairs']=len(A); out['common_folios']=len(set(x[0] for x in A)); out['status']='BLOCKED' if 'BLOCKED' in (out['source_a']['status'],out['source_b']['status']) else ('PASS' if out['source_a']['status']=='PASS' and out['source_b']['status']=='PASS' else 'FAIL')
 out.update(language_identification='NOT_RUN',semantic_identification='NOT_RUN',translation='NOT_RUN',decipherment='NOT_RUN'); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
