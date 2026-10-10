#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED_BLOB = '4201d762a4bd6e9014e0e796d72dd5c3efb597da'
EXPECTED_SHA256 = 'db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee'
SEED = 20261007
PERMUTATIONS = 9999
FAMILYWISE_ALPHA = 0.001
FEATURE_NAMES = ['unique_fraction','singleton_type_fraction','max_frequency_fraction','adjacent_equal_fraction','first_last_equal']
CONTRASTS = {
    'Lc_vs_Lf': {'class0':'Lc','class1':'Lf','strata':{('O','A','1'),('S','A','1')}},
    'Ln_vs_Lt': {'class0':'Ln','class1':'Lt','strata':{('M','B','2')}},
}


def git_blob_sha1(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def known_tokens(text):
    cleaned = re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;', ' ', text).replace('?', ' ')
    return re.findall(r'(?<![A-Za-z])[A-Za-z]{2,}(?![A-Za-z])', cleaned.lower())


def locator_unit(locator):
    loc = re.sub(r'^[@+*=]', '', locator.strip())
    m = re.match(r'(L[A-Za-z0-9]*)', loc)
    return m.group(1) if m else None


def token_features(t):
    n = len(t)
    c = Counter(t)
    k = len(c)
    return (
        k/n,
        sum(v == 1 for v in c.values())/k,
        max(c.values())/n,
        sum(t[i] == t[i-1] for i in range(1,n))/(n-1),
        float(t[0] == t[-1]),
    )


def parse(data):
    text = data.decode('utf-8', errors='strict')
    page_meta = {}
    rows = []
    for line in text.splitlines():
        ph = re.match(r'^<([^>.,]+)>\s*<!([^>]*)>', line)
        if ph:
            m = dict(re.findall(r'\$([A-Z])=([^\s>]+)', ph.group(2)))
            page_meta[ph.group(1)] = {'Q':m.get('Q','?'),'L':m.get('L','?'),'H':m.get('H','?')}
            continue
        mm = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not mm or ',' not in mm.group(1):
            continue
        locus,payload = mm.groups()
        folio = locus.split('.')[0]
        unit = locator_unit(locus.split(',',1)[1])
        if unit not in {'Lc','Lf','Ln','Lt'}:
            continue
        meta = page_meta.get(folio, {'Q':'?','L':'?','H':'?'})
        for tok in known_tokens(payload):
            rows.append({'class':unit,'folio':folio,'Q':meta['Q'],'L':meta['L'],'H':meta['H'],'token':tok})
    return rows


def build_pairs(rows, spec):
    c0,c1 = spec['class0'],spec['class1']
    cells = defaultdict(lambda: {c0:[],c1:[]})
    for r in rows:
        if r['class'] not in (c0,c1):
            continue
        if (r['Q'],r['L'],r['H']) not in spec['strata']:
            continue
        key = (r['Q'],r['L'],r['H'],r['folio'],len(r['token']))
        cells[key][r['class']].append(r['token'])
    pairs=[]
    excluded={c0:0,c1:0}
    for key in sorted(cells):
        a=sorted(cells[key][c0]); b=sorted(cells[key][c1])
        n=min(len(a),len(b))
        for i in range(n):
            pairs.append({'cell':key,'folio':key[3],'token0':a[i],'token1':b[i]})
        excluded[c0]+=len(a)-n; excluded[c1]+=len(b)-n
    return pairs,excluded


def fit(rows):
    # rows: [(feature_tuple,label),...]
    d=len(FEATURE_NAMES)
    X=[x for x,_ in rows]
    mu=[sum(x[j] for x in X)/len(X) for j in range(d)]
    sd=[]
    for j in range(d):
        v=sum((x[j]-mu[j])**2 for x in X)/len(X)
        sd.append(math.sqrt(v) if v>0 else 1.0)
    means={}
    for cls in (0,1):
        z=[[(x[j]-mu[j])/sd[j] for j in range(d)] for x,y in rows if y==cls]
        if not z:
            return None
        means[cls]=[sum(v[j] for v in z)/len(z) for j in range(d)]
    return mu,sd,means


def predict(x,model):
    mu,sd,means=model
    z=[(x[j]-mu[j])/sd[j] for j in range(len(x))]
    def d2(cls): return sum((z[j]-means[cls][j])**2 for j in range(len(z)))
    return 0 if d2(0)<=d2(1) else 1


def score_pairs(pairs, swaps=None):
    folios=sorted(set(p['folio'] for p in pairs))
    truths=[]; preds=[]
    feats=[(token_features(p['token0']),token_features(p['token1'])) for p in pairs]
    if swaps is None: swaps=[0]*len(pairs)
    for fol in folios:
        train=[]
        test_indices=[]
        for i,p in enumerate(pairs):
            s=swaps[i]
            y0=1 if s else 0
            y1=0 if s else 1
            if p['folio']==fol:
                test_indices.append((i,y0,y1))
            else:
                train.append((feats[i][0],y0)); train.append((feats[i][1],y1))
        if not train or not test_indices:
            continue
        model=fit(train)
        if model is None:
            return None
        for i,y0,y1 in test_indices:
            preds.extend([predict(feats[i][0],model),predict(feats[i][1],model)])
            truths.extend([y0,y1])
    if not truths:
        return None
    rec=[]
    for cls in (0,1):
        idx=[i for i,y in enumerate(truths) if y==cls]
        rec.append(sum(preds[i]==cls for i in idx)/len(idx))
    return sum(rec)/2


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    data=a.source.read_bytes()
    blob=git_blob_sha1(data); sha=hashlib.sha256(data).hexdigest()
    out={'classification':'DOCUMENTARY_STRATIFIED_VISUAL_SUBTYPE_MORPHOLOGY_SCREEN_NOT_TRANSLATION','git_blob_sha1':blob,'sha256':sha,'seed':SEED,'permutations_requested':PERMUTATIONS,'familywise_alpha':FAMILYWISE_ALPHA,'feature_names':FEATURE_NAMES}
    if blob!=EXPECTED_BLOB or sha!=EXPECTED_SHA256:
        out.update({'status':'BLOCKED','reason':'frozen source hash mismatch'})
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); return
    rows=parse(data)
    prepared={}
    blocked=[]
    for name,spec in CONTRASTS.items():
        pairs,excluded=build_pairs(rows,spec)
        folios=sorted(set(p['folio'] for p in pairs))
        valid=len(pairs)>=20 and len(folios)>=5 and all(any(q['folio']!=f for q in pairs) for f in folios)
        prepared[name]={'pairs':pairs,'excluded':excluded,'folios':folios,'valid':valid,'spec':spec}
        if not valid: blocked.append(name)
    out['contrasts']={name:{
        'class0':x['spec']['class0'],'class1':x['spec']['class1'],
        'strata':['|'.join(s) for s in sorted(x['spec']['strata'])],
        'matched_pairs':len(x['pairs']),'represented_folios':len(x['folios']),
        'folios':x['folios'],'excluded_unmatched':x['excluded'],'valid':x['valid']
    } for name,x in prepared.items()}
    if blocked:
        out.update({'status':'BLOCKED','blocked_contrasts':blocked,'permutations_completed':0,'reason':'one or more frozen contrasts failed preregistered pair/folio validity gates'})
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); return

    observed={}
    for name,x in prepared.items():
        observed[name]=score_pairs(x['pairs'])
        out['contrasts'][name]['observed_balanced_accuracy']=observed[name]

    rng=random.Random(SEED)
    null_by={name:[] for name in prepared}
    null_max=[]
    for _ in range(PERMUTATIONS):
        vals={}
        for name,x in prepared.items():
            swaps=[rng.randrange(2) for _ in x['pairs']]
            v=score_pairs(x['pairs'],swaps)
            if v is None:
                out.update({'status':'BLOCKED','permutations_completed':len(null_max),'reason':'classifier became undefined under valid paired permutation'})
                a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); return
            null_by[name].append(v); vals[name]=v
        null_max.append(max(v-0.5 for v in vals.values()))

    passing=[]
    for name in prepared:
        obs=observed[name]
        raw_p=(1+sum(v>=obs for v in null_by[name]))/(1+PERMUTATIONS)
        fwer_p=(1+sum(v >= obs-0.5 for v in null_max))/(1+PERMUTATIONS)
        out['contrasts'][name].update({
            'null_mean_balanced_accuracy':sum(null_by[name])/PERMUTATIONS,
            'monte_carlo_raw_p':raw_p,
            'familywise_maxstat_p':fwer_p,
            'permutations_completed':PERMUTATIONS,
            'status':'PASS' if obs>0.5 and fwer_p<=FAMILYWISE_ALPHA else 'FAIL'
        })
        if obs>0.5 and fwer_p<=FAMILYWISE_ALPHA: passing.append(name)
    out.update({'permutations_completed':PERMUTATIONS,'passing_contrasts':passing,'status':'PASS' if passing else 'FAIL'})
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
