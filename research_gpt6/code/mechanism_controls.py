#!/usr/bin/env python3
"""Exploratory held-out generative controls, not a decipherment."""
import argparse,base64,hashlib,json,math,random,re,statistics,sys
from collections import Counter,defaultdict
from pathlib import Path
from boundary_dependence import parse,mi,entropy,SOURCE_BLOB
from contextual_link import samples

def edit_one(a,b):
    if abs(len(a)-len(b))>1:return False
    if len(a)==len(b):return sum(x!=y for x,y in zip(a,b))<=1
    if len(a)>len(b):a,b=b,a
    i=j=miss=0
    while i<len(a) and j<len(b):
        if a[i]==b[j]:i+=1;j+=1
        else:miss+=1;j+=1
        if miss>1:return False
    return True

def metrics(runs,rng,shuffles=19):
    pairs=[(a,b) for w in runs for a,b in zip(w,w[1:])]
    edge=mi((a[-1],b[0]) for a,b in pairs)
    null=[]
    for _ in range(shuffles):
        shuffled=[]
        for row in runs:
            row=row[:];rng.shuffle(row);shuffled.append(row)
        null.append(mi((a[-1],b[0]) for w in shuffled for a,b in zip(w,w[1:])))
    chars=Counter((a,b) for row in runs for w in row for a,b in zip(w,w[1:]))
    left=Counter()
    for (a,b),c in chars.items():left[a]+=c
    n=sum(chars.values())
    hc=-sum(c/n*math.log2(c/left[a]) for (a,b),c in chars.items())
    words=[w for row in runs for w in row]
    return {'edge_mi':edge,'edge_excess':edge-statistics.mean(null),'internal_h1':hc,
            'repeat_rate':sum(a==b for a,b in pairs)/len(pairs),
            'edit_le1_rate':sum(edit_one(a,b) for a,b in pairs)/len(pairs),
            'mean_length':statistics.mean(map(len,words))}

def build(rows):
    byband=defaultdict(Counter); byfirst=defaultdict(Counter); links=defaultdict(Counter)
    for row in rows:
        w=row['words']
        for i,word in enumerate(w):
            b=min(3,4*i//len(w));byband[b][word]+=1;byfirst[b,word[0]][word]+=1
            if i:links[b,w[i-1][-1]][word[0]]+=1
    return byband,byfirst,links

def choose(c,rng):return rng.choices(list(c),weights=list(c.values()),k=1)[0]

def generate(model,lengths,kind,rng):
    bands,firsts,links=model;out=[]
    for n in lengths:
        row=[]
        for i in range(n):
            b=min(3,4*i//n)
            if kind=='copy15' and row and rng.random()<.15:word=row[-1]
            elif kind=='linked' and row:
                base=Counter()
                for w,c in bands[b].items():base[w[0]]+=c
                total=sum(base.values());counts=links[b,row[-1][-1]]
                initial=choose({a:counts[a]+20*c/total for a,c in base.items()},rng)
                word=choose(firsts[b,initial],rng)
            else:word=choose(bands[b],rng)
            row.append(word)
        out.append(row)
    return out

def windows(tokens,lengths,rng):
    n=sum(lengths);assert len(tokens)>=n,(len(tokens),n)
    start=rng.randrange(len(tokens)-n+1);stream=tokens[start:start+n];out=[];i=0
    for length in lengths:out.append(stream[i:i+length]);i+=length
    return out

def latin(bundle):
    groups=defaultdict(list);provenance=[]
    for f in bundle['files']:
        raw=base64.b64decode(f['base64']);blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert blob==f['sha']
        text=raw.decode(); lines=[x for i,x in enumerate(text.splitlines()) if i>0 and not x.isupper()]
        tokens=re.findall('[a-z]+','\n'.join(lines).lower())
        groups[f['path'].split('/')[0]].extend(tokens)
        provenance.append({'path':f['path'],'blob':blob,'sha256':hashlib.sha256(raw).hexdigest(),'tokens':len(tokens)})
    return groups,provenance

def summarize(draws,observed):
    out={}
    for key in observed:
        vals=sorted(d[key] for d in draws);lo,hi=vals[1],vals[-2]
        out[key]={'median':statistics.median(vals),'simulation_interval':[lo,hi],'observed_in_interval':lo<=observed[key]<=hi}
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--corpus',type=Path,required=True);ap.add_argument('--latin',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    raw=args.corpus.read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert blob==SOURCE_BLOB
    bundle=json.loads(args.latin.read_text());lt,prov=latin(bundle);rng=random.Random(20261006)
    out={'classification':'EXPLORATORY_MECHANISM_CONTROLS_NOT_TRANSLATION','python':sys.version.split()[0],'source_blob':blob,'latin_commit':bundle['commit'],'latin_provenance':prov,'draws':50,'shuffle_draws_per_sample':19,'seed':20261006,'results':{}}
    for mode in ('split','join'):
        rows,_,_=parse(raw.decode(),mode)
        leaves=sorted(set(re.sub(r'([rv]).*$','',r['folio']) for r in rows));testleaves={l for i,l in enumerate(leaves) if i%5==0}
        tr=[r for r in rows if re.sub(r'([rv]).*$','',r['folio']) not in testleaves];te=[r for r in rows if re.sub(r'([rv]).*$','',r['folio']) in testleaves]
        runs=[r['words'] for r in te];lengths=list(map(len,runs));obs=metrics(runs,rng);model=build(tr);tests={}
        for kind in ('independent','linked','copy15','latin_apicius','latin_caesar'):
            draws=[]
            for _ in range(50):
                sim=windows(lt[kind.removeprefix('latin_')],lengths,rng) if kind.startswith('latin_') else generate(model,lengths,kind,rng)
                draws.append(metrics(sim,rng))
            tests[kind]=summarize(draws,obs)
            print(mode,kind,json.dumps(tests[kind]),flush=True)
        rotation=str.maketrans('abcdefghijklmnopqrstuvwxyz','hijklmnopqrstuvwxyzabcdefg')
        check=windows(lt['caesar'],lengths,rng)
        before=metrics(check,random.Random(1));after=metrics([[w.translate(rotation) for w in r] for r in check],random.Random(1))
        assert all(abs(before[k]-after[k])<1e-10 for k in before)
        out['results'][mode]={'test_leaf_groups':len(testleaves),'test_runs':len(runs),'tokens':sum(lengths),'pairs':sum(n-1 for n in lengths),'observed':obs,'controls':tests,'monoalphabetic_invariance_pass':True}
    args.out.write_text(json.dumps(out,indent=2)+'\n');print('saved',args.out)
if __name__=='__main__':main()
