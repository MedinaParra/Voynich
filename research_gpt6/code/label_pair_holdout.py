#!/usr/bin/env python3
"""Pre-model lexical-anchor test: within-stratum label pairs, grouped by quire.
No translation/gloss inference. Primary preregistered contrast: Lc vs Lf.
"""
import argparse,hashlib,json,re,random
from collections import Counter
from pathlib import Path
SOURCE_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
def blob_sha(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def feats(t):
 return [len(t),t.count('o')/len(t),t.count('a')/len(t),t.count('y')/len(t),t.startswith('q'),t.endswith('y')]
def dist(a,b):return sum((x-y)**2 for x,y in zip(a,b))
def parse(raw):
 pages={};rows=[]
 for line in raw.splitlines():
  p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
  if p:
   m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2)));pages[p.group(1)]={'quire':m.get('Q','?'),'currier':m.get('L','?'),'hand':m.get('H','?')};continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m.group(1):continue
  locus,text=m.groups();fol=locus.split('.')[0];pos=locus.split(',',1)[1];sub=next((s for s in ('Lc','Lf') if s in pos),None)
  if not sub:continue
  clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text);uncertain='?' in clean;toks=re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean.replace('?',' '))
  if len(toks)==1 and not uncertain:rows.append({'y':sub,'token':toks[0],**pages.get(fol,{})})
 return rows
def predict(train,test):
 means={}
 for c in ('Lc','Lf'):
  xs=[feats(r['token']) for r in train if r['y']==c];means[c]=[sum(z[i] for z in xs)/len(xs) for i in range(len(xs[0]))]
 return [min(means,key=lambda c:dist(feats(r['token']),means[c])) for r in test]
def bal(y,p):
 rs=[]
 for c in ('Lc','Lf'):
  ix=[i for i,z in enumerate(y) if z==c];rs.append(sum(p[i]==c for i in ix)/len(ix))
 return sum(rs)/2
def score(rows):
 qs=sorted(set(r['quire'] for r in rows)-{'?'});fold=[]
 for q in qs:
  tr=[r for r in rows if r['quire']!=q];te=[r for r in rows if r['quire']==q]
  if not te or any(not any(r['y']==c for r in tr) for c in ('Lc','Lf')) or any(not any(r['y']==c for r in te) for c in ('Lc','Lf')):continue
  y=[r['y'] for r in te];p=predict(tr,te);fold.append({'quire':q,'n':len(te),'balanced_accuracy':bal(y,p)})
 return sum(x['balanced_accuracy'] for x in fold)/len(fold) if fold else None,fold
def main():
 a=argparse.ArgumentParser();a.add_argument('--corpus',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--permutations',type=int,default=999);z=a.parse_args();b=z.corpus.read_bytes()
 if blob_sha(b)!=SOURCE_BLOB:raise SystemExit('frozen corpus mismatch')
 rows=parse(b.decode());obs,fold=score(rows);rng=random.Random(20261006);null=[]
 if obs is not None:
  for _ in range(z.permutations):
   rr=[dict(r) for r in rows]
   for q in set(r['quire'] for r in rr):
    ix=[i for i,r in enumerate(rr) if r['quire']==q];ys=[rr[i]['y'] for i in ix];rng.shuffle(ys)
    for i,y in zip(ix,ys):rr[i]['y']=y
   s,_=score(rr)
   if s is not None:null.append(s)
 p=(1+sum(s>=obs for s in null))/(1+len(null)) if obs is not None else None
 result={'classification':'LEXICAL_ANCHOR_PAIR_PILOT_NOT_TRANSLATION','source_blob':SOURCE_BLOB,'contrast':'Lc_vs_Lf','counts':dict(Counter(r['y'] for r in rows)),'quires':sorted(set(r['quire'] for r in rows)),'currier_hand':dict(Counter(f"{r.get('currier','?')}|{r.get('hand','?')}" for r in rows)),'folds':fold,'balanced_accuracy':obs,'permutations_completed':len(null),'monte_carlo_p':p,'pilot_pass':bool(obs is not None and obs>0.5 and p<=0.05),'status':'PASS_EXECUTED' if obs is not None else 'BLOCKED'}
 z.out.parent.mkdir(parents=True,exist_ok=True);z.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
