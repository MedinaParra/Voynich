#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED_IT = 'db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee'
EXPECTED_GC = 'b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f'
SEED = 20261007
PERMUTATIONS = 9999
FAMILYWISE_ALPHA = 0.001
FEATURE_NAMES = ['unique_fraction','singleton_type_fraction','max_frequency_fraction','adjacent_equal_fraction','first_last_equal']
CONTRASTS = {
    'Lc_vs_Lf': {'class0':'Lc','class1':'Lf','strata':{('O','A','1'),('S','A','1')}},
    'Ln_vs_Lt': {'class0':'Ln','class1':'Lt','strata':{('M','B','2')}},
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def clean_tokens(payload):
    s = re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;', ' ', payload)
    pieces = re.split(r'[.\s]+', s)
    out=[]
    for p in pieces:
        p=p.strip()
        if not p or '?' in p:
            continue
        runs=re.findall(r'[A-Za-z0-9]+', p)
        if len(runs)==1 and runs[0]:
            out.append(runs[0])
    return out


def parse(data):
    text=data.decode('utf-8',errors='strict')
    meta={}
    records={}
    for line in text.splitlines():
        ph=re.match(r'^<(f\d+[rv]\d*)>\s*<!([^>]*)>',line)
        if ph:
            m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',ph.group(2)))
            meta[ph.group(1)]={'Q':m.get('Q','?'),'L':m.get('L','?'),'H':m.get('H','?')}
            continue
        lm=re.match(r'^<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)$',line)
        if not lm:
            continue
        fol,num,locator,payload=lm.groups()
        records[(fol,int(num))]={
            'folio':fol,'number':int(num),'locator':locator,'payload':payload,
            'tokens':clean_tokens(payload),'meta':meta.get(fol,{'Q':'?','L':'?','H':'?'})
        }
    return records


def it_unit(locator):
    loc=re.sub(r'^[@+*=]','',locator.strip())
    m=re.match(r'(L[A-Za-z0-9]*)',loc)
    return m.group(1) if m else None


def features(t):
    n=len(t); c=Counter(t); k=len(c)
    return (
        k/n,
        sum(v==1 for v in c.values())/k,
        max(c.values())/n,
        sum(t[i]==t[i-1] for i in range(1,n))/(n-1) if n>1 else 0.0,
        float(t[0]==t[-1]),
    )


def aligned_rows(it,gc):
    rows=[]
    for key,r in it.items():
        unit=it_unit(r['locator'])
        if unit not in {'Lc','Lf','Ln','Lt'}:
            continue
        rr=gc.get(key)
        if rr is None or len(r['tokens'])!=1 or len(rr['tokens'])!=1:
            continue
        qlh=(r['meta']['Q'],r['meta']['L'],r['meta']['H'])
        allowed=set()
        if unit in ('Lc','Lf'): allowed={('O','A','1'),('S','A','1')}
        elif unit in ('Ln','Lt'): allowed={('M','B','2')}
        if qlh not in allowed:
            continue
        rows.append({'class':unit,'folio':r['folio'],'Q':qlh[0],'L':qlh[1],'H':qlh[2],'gc_token':rr['tokens'][0]})
    return rows


def build_pairs(rows,spec):
    c0,c1=spec['class0'],spec['class1']
    cells=defaultdict(lambda:{c0:[],c1:[]})
    for r in rows:
        if r['class'] not in (c0,c1): continue
        if (r['Q'],r['L'],r['H']) not in spec['strata']: continue
        key=(r['Q'],r['L'],r['H'],r['folio'],len(r['gc_token']))
        cells[key][r['class']].append(r['gc_token'])
    pairs=[]; excluded={c0:0,c1:0}
    for key in sorted(cells):
        a=sorted(cells[key][c0]); b=sorted(cells[key][c1]); n=min(len(a),len(b))
        for i in range(n): pairs.append({'cell':key,'folio':key[3],'token0':a[i],'token1':b[i]})
        excluded[c0]+=len(a)-n; excluded[c1]+=len(b)-n
    return pairs,excluded


def fit(rows):
    d=len(FEATURE_NAMES); X=[x for x,_ in rows]
    mu=[sum(x[j] for x in X)/len(X) for j in range(d)]
    sd=[]
    for j in range(d):
        v=sum((x[j]-mu[j])**2 for x in X)/len(X)
        sd.append(math.sqrt(v) if v>0 else 1.0)
    means={}
    for cls in (0,1):
        z=[[(x[j]-mu[j])/sd[j] for j in range(d)] for x,y in rows if y==cls]
        if not z: return None
        means[cls]=[sum(v[j] for v in z)/len(z) for j in range(d)]
    return mu,sd,means


def predict(x,model):
    mu,sd,means=model
    z=[(x[j]-mu[j])/sd[j] for j in range(len(x))]
    def dist(cls): return sum((z[j]-means[cls][j])**2 for j in range(len(z)))
    return 0 if dist(0)<=dist(1) else 1


def score(pairs,swaps=None):
    folios=sorted(set(p['folio'] for p in pairs))
    fs=[(features(p['token0']),features(p['token1'])) for p in pairs]
    if swaps is None: swaps=[0]*len(pairs)
    truth=[]; pred=[]
    for fol in folios:
        train=[]; test=[]
        for i,p in enumerate(pairs):
            s=swaps[i]; y0=1 if s else 0; y1=0 if s else 1
            if p['folio']==fol: test.append((i,y0,y1))
            else:
                train.append((fs[i][0],y0)); train.append((fs[i][1],y1))
        if not train or not test: continue
        model=fit(train)
        if model is None: return None
        for i,y0,y1 in test:
            pred.extend([predict(fs[i][0],model),predict(fs[i][1],model)])
            truth.extend([y0,y1])
    if not truth: return None
    recalls=[]
    for cls in (0,1):
        idx=[i for i,y in enumerate(truth) if y==cls]
        if not idx: return None
        recalls.append(sum(pred[i]==cls for i in idx)/len(idx))
    return sum(recalls)/2


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--it',type=Path,required=True)
    ap.add_argument('--gc',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    itd=a.it.read_bytes(); gcd=a.gc.read_bytes()
    out={'classification':'GC_V101_SINGLE_SOURCE_VISUAL_SUBTYPE_MORPHOLOGY_REPLICATION_NOT_TRANSLATION','it_sha256':sha256(itd),'gc_sha256':sha256(gcd),'seed':SEED,'permutations_requested':PERMUTATIONS,'familywise_alpha':FAMILYWISE_ALPHA,'feature_names':FEATURE_NAMES}
    if out['it_sha256']!=EXPECTED_IT or out['gc_sha256']!=EXPECTED_GC:
        out.update({'status':'BLOCKED','reason':'frozen source hash mismatch'})
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); return
    it=parse(itd); gc=parse(gcd); rows=aligned_rows(it,gc)
    out['aligned_single_token_rows']=len(rows)
    out['aligned_class_counts']={c:sum(r['class']==c for r in rows) for c in ['Lc','Lf','Ln','Lt']}
    prepared={}; blocked=[]
    for name,spec in CONTRASTS.items():
        pairs,excluded=build_pairs(rows,spec); folios=sorted(set(p['folio'] for p in pairs))
        valid=len(pairs)>=20 and len(folios)>=5 and all(any(q['folio']!=f for q in pairs) for f in folios)
        prepared[name]={'pairs':pairs,'excluded':excluded,'folios':folios,'valid':valid,'spec':spec}
        if not valid: blocked.append(name)
    out['contrasts']={name:{'class0':x['spec']['class0'],'class1':x['spec']['class1'],'strata':['|'.join(s) for s in sorted(x['spec']['strata'])],'matched_pairs':len(x['pairs']),'represented_folios':len(x['folios']),'folios':x['folios'],'excluded_unmatched':x['excluded'],'valid':x['valid']} for name,x in prepared.items()}
    if blocked:
        out.update({'status':'BLOCKED','blocked_contrasts':blocked,'permutations_completed':0,'reason':'one or more frozen GC contrasts failed preregistered pair/folio validity gates'})
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); return
    observed={name:score(x['pairs']) for name,x in prepared.items()}
    for name,v in observed.items(): out['contrasts'][name]['observed_balanced_accuracy']=v
    rng=random.Random(SEED); null_by={name:[] for name in prepared}; null_max=[]
    for _ in range(PERMUTATIONS):
        vals={}
        for name,x in prepared.items():
            swaps=[rng.randrange(2) for _ in x['pairs']]
            v=score(x['pairs'],swaps)
            if v is None:
                out.update({'status':'BLOCKED','permutations_completed':len(null_max),'reason':'classifier undefined under valid paired permutation'})
                a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); return
            null_by[name].append(v); vals[name]=v
        null_max.append(max(v-0.5 for v in vals.values()))
    passing=[]
    for name in prepared:
        obs=observed[name]
        raw=(1+sum(v>=obs for v in null_by[name]))/(1+PERMUTATIONS)
        fwer=(1+sum(v>=obs-0.5 for v in null_max))/(1+PERMUTATIONS)
        stat='PASS' if obs>0.5 and fwer<=FAMILYWISE_ALPHA else 'FAIL'
        if stat=='PASS': passing.append(name)
        out['contrasts'][name].update({'null_mean_balanced_accuracy':sum(null_by[name])/PERMUTATIONS,'monte_carlo_raw_p':raw,'familywise_maxstat_p':fwer,'permutations_completed':PERMUTATIONS,'status':stat})
    out.update({'permutations_completed':PERMUTATIONS,'passing_contrasts':passing,'status':'PASS' if passing else 'FAIL'})
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
