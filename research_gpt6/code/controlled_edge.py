"""Exploratory grouped prediction with fixed, coarsened controls; not decipherment."""
import argparse,hashlib,json,math,random,re
from collections import Counter,defaultdict
from pathlib import Path
from boundary_dependence import parse,SOURCE_BLOB
SEED=20261006

def records(raw):
    rows,_,_=parse(raw,'join'); original={}
    for line in raw.splitlines():
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if m: original[m[1]]=m[2]
    out=[]
    for row in rows:
        text=original.get(row['locus'],'')
        # Exclude uncertain commas, drawing gaps, alternatives and illegible signs.
        clean=re.sub(r'<[^>]*>','',text)
        if ',' in text or '<->' in text or not re.fullmatch(r'[a-z.\s]+',clean): continue
        w=row['words'];n=len(w)
        leaf=re.sub(r'([rv]).*$','',row['folio'])
        for i in range(2,n-1):
            c=(row['quire'] or 'UNKNOWN',min(3,4*i//n),min(8,len(w[i-1])),min(8,len(w[i])),min(15,n))
            out.append((leaf,c,w[i-1][-1],w[i][0]))
    return out

def run(data):
    leaves=sorted({r[0] for r in data}); folds={l:i%5 for i,l in enumerate(leaves)}
    evaluated=[]
    for f in range(5):
        train=[r for r in data if folds[r[0]]!=f];test=[r for r in data if folds[r[0]]==f]
        base=Counter(r[3] for r in train);ctx=defaultdict(Counter);edge=defaultdict(Counter)
        for l,c,x,y in train: ctx[c][y]+=1;edge[c,x][y]+=1
        def gain(c,x,y):
            p=(base[y]+.5)/(sum(base.values())+13)
            cc=ctx[c];p0=(cc[y]+20*p)/(sum(cc.values())+20)
            ee=edge[c,x];p1=(ee[y]+20*p0)/(sum(ee.values())+20)
            return math.log2(p1/p0)
        for l,c,x,y in test:
            evaluated.append((l,c,x,y,{z:gain(c,z,y) for z in 'abcdefghijklmnopqrstuvwxyz'}))
    observed=[r[4][r[2]] for r in evaluated]
    groups=defaultdict(list)
    for i,r in enumerate(evaluated):groups[r[0],r[1]].append(i)
    rng=random.Random(SEED);null=[];changed=[]
    for _ in range(199):
        total=0;changes=0
        for ids in groups.values():
            xs=[evaluated[i][2] for i in ids];rng.shuffle(xs)
            for i,x in zip(ids,xs):total+=evaluated[i][4][x];changes+=x!=evaluated[i][2]
        null.append(total/len(data));changed.append(changes/len(data))
    per=defaultdict(list)
    for r,g in zip(evaluated,observed):per[r[0]].append(g)
    vals=list(per.values());boot=[]
    for _ in range(999):
        draws=[rng.choice(vals) for v in vals];boot.append(sum(map(sum,draws))/sum(map(len,draws)))
    boot.sort();mean=sum(observed)/len(data)
    return {'pairs':len(data),'leaves':len(leaves),'gain_bits_per_pair':mean,'leaf_bootstrap_95':[boot[24],boot[974]],'test_feature_permutation_p':(1+sum(v>=mean for v in null))/200,'permutation_mean':sum(null)/len(null),'mean_changed_final_fraction':sum(changed)/len(changed),'pairs_in_exchangeable_cells':sum(len(ids) for ids in groups.values() if len({evaluated[i][2] for i in ids})>1),'fold_assignment':folds,'per_leaf':{l:{'pairs':len(gs),'gain':sum(gs)/len(gs)} for l,gs in per.items()}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--corpus',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();b=a.corpus.read_bytes()
    assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==SOURCE_BLOB
    r={'classification':'EXPLORATORY_CONDITIONAL_PREDICTION_NOT_TRANSLATION','seed':SEED,'source_sha256':hashlib.sha256(b).hexdigest(),'controls':['quire','position quartile','previous length capped 8','next length capped 8','line group count capped 15'],'smoothing':20,'permutations':199,'limitations':['Previously explored corpus; not independent confirmatory study.','Coarsened controls, not exact conditional independence.','No Currier, hand or alternative grapheme representation control.','Permutation shuffles held-out final features within leaf and control cells; models are not refitted.','Leaf bootstrap does not resample training or account for all quire dependence.'],'results':run(records(b.decode()))}
    a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r['results'].items() if k not in ['per_leaf','fold_assignment']},indent=2))
if __name__=='__main__':main()
