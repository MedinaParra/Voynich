#!/usr/bin/env python3
"""Within-regime audit for Voynich prefix contrasts.
Tests whether candidate prefix substitutions remain context-distinct after
conditioning on Currier language, hand, section and quire. Exploratory only.
"""
import argparse, hashlib, json, math, re
from collections import Counter, defaultdict
from pathlib import Path
BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
PREFIXES=('qok','pol','sol','ych','ysh','dsh','ch','sh','qo','ok','ot')
def gitblob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def js(a,b):
 keys=set(a)|set(b);sa=sum(a.values());sb=sum(b.values())
 if not sa or not sb:return None
 p={k:a[k]/sa for k in keys};q={k:b[k]/sb for k in keys};m={k:(p[k]+q[k])/2 for k in keys}
 def kl(x):return sum(v*math.log2(v/m[k]) for k,v in x.items() if v and m[k])
 return (kl(p)+kl(q))/2

def clean_words(text):
 # Keep conservative historical parser so results are comparable with prior wild runs.
 clean=re.sub(r'<[^>]*>','',text)
 if ',' in text or '<->' in text or not re.fullmatch(r'[a-z.\s]+',clean): return []
 return [x for x in re.split(r'[.\s]+',clean.strip()) if x]

def parse(b):
 rows=[]; meta={};folio=None
 for line in b.decode().splitlines():
  pm=re.match(r'^<(f\d+[rv]\d*)>\s*<!\s*(.*?)>',line)
  if pm:
   folio=pm.group(1); meta={k:v for k,v in re.findall(r'\$([A-Z])=([^\s>]+)',pm.group(2))}; continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or not folio: continue
  fm=re.match(r'(f\d+[rv]\d*)',m.group(1))
  if not fm: continue
  w=clean_words(m.group(2))
  if w: rows.append({'folio':fm.group(1),'words':w,'Q':meta.get('Q','?'),'L':meta.get('L','?'),'H':meta.get('H','?'),'I':meta.get('I','?')})
 return rows

def collect(rows):
 ctx=defaultdict(Counter);counts=Counter();stems=defaultdict(Counter)
 for r in rows:
  for i,x in enumerate(r['words']):
   p=next((p for p in PREFIXES if x.startswith(p) and len(x)>len(p)+1),None)
   if not p:continue
   stem=x[len(p):];k=(p,stem);counts[k]+=1;stems[stem][p]+=1
   if i:ctx[k]['L:'+r['words'][i-1]]+=1
   if i+1<len(r['words']):ctx[k]['R:'+r['words'][i+1]]+=1
 return counts,ctx,stems

def audit(rows,min_form,min_stems):
 c,ctx,st=collect(rows);pairs=defaultdict(list)
 for stem,pc in st.items():
  ps=[p for p,n in pc.items() if n>=min_form]
  for i,p1 in enumerate(ps):
   for p2 in ps[i+1:]:
    j=js(ctx[(p1,stem)],ctx[(p2,stem)])
    if j is not None:pairs[tuple(sorted((p1,p2)))].append((stem,j))
 out=[]
 for pair,v in pairs.items():
  if len(v)>=min_stems:out.append({'prefix_pair':list(pair),'shared_stems':len(v),'mean_context_js':sum(x[1] for x in v)/len(v),'stems':[x[0] for x in v]})
 return sorted(out,key=lambda x:(x['shared_stems'],x['mean_context_js']),reverse=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--corpus',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--min-form',type=int,default=2);ap.add_argument('--min-stems',type=int,default=3);a=ap.parse_args();b=a.corpus.read_bytes()
 if gitblob(b)!=BLOB:raise SystemExit('Corpus blob mismatch')
 rows=parse(b);dims=('L','H','I','Q');results={};support=defaultdict(lambda:defaultdict(list))
 for d in dims:
  results[d]={}
  for val in sorted({r[d] for r in rows}):
   rr=[r for r in rows if r[d]==val];q=audit(rr,a.min_form,a.min_stems);results[d][val]={'rows':len(rr),'folios':len({r['folio'] for r in rr}),'qualifying_pairs':q}
   for x in q:support[tuple(x['prefix_pair'])][d].append({'value':val,'shared_stems':x['shared_stems'],'mean_context_js':x['mean_context_js']})
 summary=[]
 for pair,by in support.items():
  summary.append({'prefix_pair':list(pair),'dimensions_survived':len(by),'regimes_survived':sum(len(v) for v in by.values()),'by_dimension':dict(by)})
 summary.sort(key=lambda x:(x['dimensions_survived'],x['regimes_survived']),reverse=True)
 res={'classification':'WITHIN_REGIME_COMPOSITIONALITY_AUDIT_NOT_TRANSLATION','source_blob':BLOB,'status':'PASS_EXECUTED','rows':len(rows),'folios':len({r['folio'] for r in rows}),'controls':['Currier language L','hand H','section I','quire Q'],'min_form':a.min_form,'min_stems':a.min_stems,'results':results,'survival_summary':summary,'interpretation_rule':'A pair surviving inside a regime is not explained solely by between-regime differences. This remains exploratory: sparse cells, transcription/parser filtering, and generic generative mechanisms remain alternative explanations.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'status':res['status'],'rows':res['rows'],'folios':res['folios'],'top_survivors':summary[:12]},indent=2))
if __name__=='__main__':main()
