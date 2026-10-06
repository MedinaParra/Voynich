#!/usr/bin/env python3
"""Test whether recurring EVA affixes have stable positional roles. No translation claims."""
import argparse,hashlib,json,re,math
from collections import Counter,defaultdict
from pathlib import Path
BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def js(p,q):
 keys=set(p)|set(q); sp=sum(p.values()) or 1;sq=sum(q.values()) or 1
 P={k:p[k]/sp for k in keys};Q={k:q[k]/sq for k in keys};M={k:(P[k]+Q[k])/2 for k in keys}
 def kl(a,m):return sum(v*math.log2(v/m[k]) for k,v in a.items() if v and m[k])
 return (kl(P,M)+kl(Q,M))/2
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--corpus',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--min',type=int,default=25);a=ap.parse_args();b=a.corpus.read_bytes()
 if blob(b)!=BLOB:raise SystemExit('Corpus blob mismatch')
 pref=defaultdict(Counter);suff=defaultdict(Counter);examples=defaultdict(list);tot=Counter()
 for line in b.decode().splitlines():
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m:continue
  locus,text=m.groups();clean=re.sub(r'<[^>]*>','',text)
  if ',' in text or '<->' in text or not re.fullmatch(r'[a-z.\s]+',clean):continue
  w=[x for x in re.split(r'[.\s]+',clean.strip()) if x]
  for i,x in enumerate(w):
   pos='initial' if i==0 else ('final' if i==len(w)-1 else 'medial')
   for n in (1,2,3):
    if len(x)>n:
     P='P:'+x[:n];S='S:'+x[-n:];pref[P][pos]+=1;suff[S][pos]+=1;tot[P]+=1;tot[S]+=1
     if len(examples[P])<8:examples[P].append([x,locus,pos])
     if len(examples[S])<8:examples[S].append([x,locus,pos])
 allc=Counter()
 for d in list(pref.values())+list(suff.values()):allc.update(d)
 rows=[]
 for k,d in {**pref,**suff}.items():
  if tot[k]<a.min:continue
  n=sum(d.values());dist={z:d[z]/n for z in ['initial','medial','final']};rows.append({'morpheme':k,'n':n,'position_distribution':dist,'js_from_global':js(d,allc),'examples':examples[k]})
 rows.sort(key=lambda r:(r['js_from_global'],r['n']),reverse=True)
 res={'classification':'MORPHEME_POSITIONAL_ROLE_AUDIT_NOT_TRANSLATION','source_blob':BLOB,'global_position_counts':dict(allc),'candidate_morphemes':rows,'interpretation_rule':'High divergence means positional specialization only; it is not a semantic gloss.','status':'PASS_EXECUTED'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'tested':len(rows),'top':rows[:12]},indent=2))
if __name__=='__main__':main()
