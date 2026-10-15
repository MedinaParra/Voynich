#!/usr/bin/env python3
import argparse,csv,hashlib,json,math,unicodedata
from pathlib import Path
import numpy as np

STAR_SHA256='e7cb7787118aa71f440fbf544da5b327a6afd8eba8b2989d6e5ca71d40629d04'
YALE_BLOB_SHA1='12c4230fdefc8c566e9bdb3626fc6009c70a7533'
MAPPING=[50,38,37,43,31,36,48,53,54,41,32,55,56,46,34,39,59,51,52,40,44,58,57,35,45,47,49,42,33]

def sha256(b): return hashlib.sha256(b).hexdigest()
def blobsha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def loocv_mae(X,y):
    p=[]
    for i in range(len(y)):
        keep=np.arange(len(y))!=i
        A=np.column_stack([np.ones(keep.sum()),X[keep]])
        beta=np.linalg.lstsq(A,y[keep],rcond=None)[0]
        p.append(float(np.r_[1.0,X[i]]@beta))
    return float(np.mean(np.abs(np.asarray(p)-y)))
def perm_test(X,y,seed):
    obs=loocv_mae(X,y); rng=np.random.default_rng(seed); null=np.empty(9999)
    for k in range(9999): null[k]=loocv_mae(X,y[rng.permutation(len(y))])
    return {'observed_mae':obs,'null_median':float(np.median(null)),'p':float((1+np.sum(null<=obs))/10000)}
def derangement(n,seed):
    rng=np.random.default_rng(seed)
    while True:
        p=rng.permutation(n)
        if np.all(p!=np.arange(n)): return p

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--stars',required=True); ap.add_argument('--yale',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    sb=Path(a.stars).read_bytes(); yb=Path(a.yale).read_bytes()
    checks={'star_sha256':sha256(sb),'star_sha256_matches':sha256(sb)==STAR_SHA256,'yale_blob_sha1':blobsha(yb),'yale_blob_sha1_matches':blobsha(yb)==YALE_BLOB_SHA1}
    stars=[]
    for r in csv.DictReader(sb.decode().splitlines()):
        if r.get('page')=='f68r1': stars.append((int(r['star_id']),float(r['x']),float(r['y'])))
    stars.sort(); checks['star_inventory_29']=len(stars)==29 and [r[0] for r in stars]==list(range(1,30))
    try:
        raw=json.loads(yb.decode()); vocab,boxes=raw
        toks=[]
        for occ in MAPPING:
            row=boxes[occ]; token=vocab[int(row[0])][0]
            token=unicodedata.normalize('NFC',token).strip()
            if not token: raise ValueError('empty token')
            toks.append(token)
        checks['mapping_29_unique']=len(toks)==29 and len(set(MAPPING))==29
    except Exception as e:
        Path(a.out).write_text(json.dumps({'status':'BLOCKED','reason':str(e),'checks':checks},indent=2)); return
    if not all(checks.values()):
        Path(a.out).write_text(json.dumps({'status':'BLOCKED','reason':'source/inventory gate failed','checks':checks},indent=2)); return
    xy=np.array([[r[1],r[2]] for r in stars],float); mins=xy.min(0); spans=xy.max(0)-mins
    if np.any(spans==0):
        Path(a.out).write_text(json.dumps({'status':'BLOCKED','reason':'degenerate geometry','checks':checks},indent=2)); return
    nxy=(xy-mins)/spans; c=nxy.mean(0); d=nxy-c; rad=np.sqrt((d*d).sum(1)); rad/=rad.max(); th=np.arctan2(d[:,1],d[:,0])
    X=np.column_stack([nxy[:,0],nxy[:,1],rad,np.sin(th),np.cos(th)])
    lengths=np.array([len(t) for t in toks],float)
    primary=perm_test(X,lengths,20261007)
    abl=perm_test(X[:,:2],lengths,20261007)
    dp=derangement(29,90090); scramble=perm_test(X,lengths[dp],90091)
    primary_pass=primary['observed_mae']<primary['null_median'] and primary['p']<=.01
    scramble_false_positive=scramble['observed_mae']<scramble['null_median'] and scramble['p']<=.01
    # Categorical endpoints require class-size gates. H90 preregistration names sklearn logistic regression;
    # avoid silently substituting an implementation. Execute only if gates pass and sklearn is available.
    secondary={}
    endpoints={'first_character':[t[0] for t in toks],'last_character':[t[-1] for t in toks],'adjacent_equality':[any(x==y for x,y in zip(t,t[1:])) for t in toks]}
    from collections import Counter
    for name,v in endpoints.items():
        cnt=Counter(v); gate=(min(cnt.values())>=3 if name!='adjacent_equality' else len(cnt)==2 and min(cnt.values())>=5)
        secondary[name]={'status':'NOT_RUN' if not gate else 'BLOCKED','class_counts':{str(k):v for k,v in cnt.items()},'reason':'preregistered class-size gate not met' if not gate else 'categorical implementation intentionally not substituted in this runner'}
    # Mandatory controls are complete; secondary BLOCKED cannot rescue or invalidate primary decision because preregistration makes them secondary.
    status='FAIL' if (not primary_pass or scramble_false_positive) else 'PASS'
    out={'status':status,'checks':checks,'n':29,'primary_length':primary,'pair_scramble_control':scramble,'xy_ablation':abl,'secondary':secondary,'token_lengths':[int(x) for x in lengths], 'interpretation_ceiling':'No semantics, language, plaintext, translation, or decipherment tested.'}
    Path(a.out).write_text(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
