#!/usr/bin/env python3
"""H94 preregistered initial-glyph -> visual-object anchor test."""
import argparse, hashlib, json, math, os, unicodedata
from collections import Counter
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from h91b_stage_a_inventory import API, EXCLUDED, JITTER_OFFSETS, blind_label_boxes, frozen_objects, get_bytes
from h91_stage_b_pairing_gate import greedy_pairs
from h76_visual_object_extraction_admissibility import run_page
EXPECTED_STAGE_A=168; EXPECTED_FOLIOS=9; EXPECTED_OBJECTS=153; MIN_STABILITY=.80
N_PERM=19999; ALPHA=.001; SEED=20261010; SCRAMBLE_SEED=94001; MIN_CLASS=10

def sha256(b): return hashlib.sha256(b).hexdigest()
def canon_hash(x): return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def build_classes(chars):
    c=Counter(chars); eligible={k for k,v in c.items() if v>=MIN_CLASS}
    y=np.array([x if x in eligible else 'OTHER' for x in chars],object)
    return y,{str(k):int(v) for k,v in sorted(Counter(y).items(),key=lambda z:str(z[0]))}
def lofo_score(X,y,groups):
    classes=sorted(set(y.tolist()),key=str); pred=np.empty(len(y),object)
    for g in sorted(set(groups)):
        te=np.where(groups==g)[0]; tr=np.where(groups!=g)[0]
        missing=set(y[te])-set(y[tr])
        if missing: raise ValueError(f'held-out target class absent from training fold {g}: {sorted(map(str,missing))}')
        mu=X[tr].mean(0); sd=X[tr].std(0,ddof=0); ztr=np.zeros_like(X[tr]); zte=np.zeros_like(X[te]); nz=sd!=0
        ztr[:,nz]=(X[tr][:,nz]-mu[nz])/sd[nz]; zte[:,nz]=(X[te][:,nz]-mu[nz])/sd[nz]
        m=LogisticRegression(penalty='l2',C=1.0,fit_intercept=True,max_iter=10000,solver='lbfgs',class_weight=None)
        m.fit(ztr,y[tr]); pred[te]=m.predict(zte)
    recalls=[]
    for c in classes:
        ix=y==c
        if not np.any(ix): raise ValueError(f'empty global class {c}')
        recalls.append(float(np.mean(pred[ix]==c)))
    return float(np.mean(recalls))
def perm_test(X,y,groups):
    obs=lofo_score(X,y,groups); rng=np.random.default_rng(SEED); null=np.empty(N_PERM,float)
    inds={g:np.where(groups==g)[0] for g in sorted(set(groups))}
    for k in range(N_PERM):
        yp=y.copy()
        for g,ix in inds.items(): yp[ix]=y[ix][rng.permutation(len(ix))]
        null[k]=lofo_score(X,yp,groups)
    return obs,float(np.median(null)),float((1+np.sum(null>=obs))/(N_PERM+1))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args(); runner_sha=sha256(Path(__file__).read_bytes())
    listing=json.loads(get_bytes(API)); files=sorted((x for x in listing if x.get('type')=='file' and x['name'].endswith('.json')),key=lambda x:x['name'])
    frozen=[]; stage_a=0; blocked=[]; source_hashes={}
    for item in files:
        page=item['name'][:-5]
        if page in EXCLUDED: continue
        try:
            raw=get_bytes(item['download_url']); p=Path('/tmp')/item['name']; p.write_bytes(raw); r=run_page(page,p); objects=frozen_objects(r)
            if len(objects)<15: continue
            stage_a+=1; labels=blind_label_boxes(raw); base=greedy_pairs(objects,labels); jitter=[greedy_pairs(objects,labels,float(dx),float(dy)) for dx,dy in JITTER_OFFSETS]
            stable=[(oid,lid) for oid,lid in sorted(base.items()) if all(m.get(oid)==lid for m in jitter)]; frac=len(stable)/len(base) if base else 0.0
            if len(base)>=15 and frac>=MIN_STABILITY:
                frozen.append((page,raw,objects,stable)); source_hashes[page]={'coord_blob_sha':item.get('sha'),'coord_sha256':sha256(raw),'image_sha256':r.get('image_sha256')}
        except Exception as e: blocked.append({'page':page,'error':f'{type(e).__name__}: {e}'})
    nobj=sum(len(z[3]) for z in frozen)
    if blocked or stage_a!=EXPECTED_STAGE_A or len(frozen)!=EXPECTED_FOLIOS or nobj!=EXPECTED_OBJECTS:
        out={'experiment':'H94','status':'BLOCKED','reason':'frozen H91 family reproduction failed','stage_a_candidates':stage_a,'admissible_folios':len(frozen),'stable_objects':nobj,'blocked':blocked,'runner_sha256':runner_sha}; a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2)); return
    rows=[]; tokens=[]
    for page,raw,objects,stable in frozen:
        vocab,boxes=json.loads(raw); om={o['object_id']:o for o in objects}
        xy=np.array([om[oid]['centroid'] for oid,lid in stable],float); spans=xy.max(0)-xy.min(0)
        if np.any(spans==0): raise ValueError(f'degenerate centroid span {page}')
        nxy=(xy-xy.min(0))/spans
        for j,(oid,lid) in enumerate(stable):
            o=om[oid]; bb=o['bbox']; w=float(bb[2]); h=float(bb[3]); tok=unicodedata.normalize('NFC',vocab[int(boxes[lid][0])][0]).strip()
            if not tok or o['area']<=0 or w<=0 or h<=0: raise ValueError(f'invalid provenance/geometry {page}:{oid}:{lid}')
            rows.append({'page':page,'object_id':oid,'label_ordinal':int(lid),'features_raw':[math.log(float(o['area'])),math.log(w/h),float(nxy[j,0]),float(nxy[j,1])]}); tokens.append(tok)
    X=np.array([r['features_raw'] for r in rows],float); groups=np.array([r['page'] for r in rows],object)
    pair_payload={'feature_definition':['log(area)','log(width/height)','x_norm','y_norm'],'normalization':'x/y min-max independently within each frozen folio, matching H92 convention','rows':rows}
    visual_hash=canon_hash(pair_payload); pair_hash=canon_hash([{'page':r['page'],'object_id':r['object_id'],'label_ordinal':r['label_ordinal']} for r in rows])
    first=[t[0] for t in tokens]; y,class_counts=build_classes(first); target_hash=canon_hash(y.tolist())
    try: observed,null_med,pval=perm_test(X,y,groups)
    except Exception as e:
        out={'experiment':'H94','status':'BLOCKED','reason':f'{type(e).__name__}: {e}','pair_sha256':pair_hash,'visual_feature_sha256':visual_hash,'class_counts':class_counts,'runner_sha256':runner_sha}; a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2)); return
    srng=np.random.default_rng(SCRAMBLE_SEED); ys=y.copy()
    for g in sorted(set(groups)):
        ix=np.where(groups==g)[0]; ys[ix]=y[ix][srng.permutation(len(ix))]
    try: scramble=lofo_score(X,ys,groups)
    except Exception as e: scramble=f'BLOCKED: {type(e).__name__}: {e}'
    last=[t[-1] for t in tokens]; yl,last_counts=build_classes(last)
    try: terminal=lofo_score(X,yl,groups)
    except Exception as e: terminal=f'BLOCKED: {type(e).__name__}: {e}'
    primary_pass=observed>null_med and pval<=ALPHA; status='PASS' if primary_pass else 'FAIL'; counts={g:int(np.sum(groups==g)) for g in sorted(set(groups))}
    out={'experiment':'H94 initial-glyph visual-object anchor','status':status,'executing_commit_sha':os.environ.get('GITHUB_SHA','UNKNOWN'),'runner_sha256':runner_sha,'h91_reproduction':{'stage_a_candidates':stage_a,'admissible_folios':len(frozen),'stable_objects':nobj,'per_folio_counts':counts},'source_hashes':source_hashes,'pair_sha256':pair_hash,'visual_feature_sha256':visual_hash,'target_sha256':target_hash,'class_counts':class_counts,'n_permutations':N_PERM,'seed':SEED,'alpha':ALPHA,'primary':{'observed_macro_balanced_recall':observed,'null_median_macro_balanced_recall':null_med,'p':pval,'pass':primary_pass},'controls':{'pairing_scramble_seed':SCRAMBLE_SEED,'pairing_scramble_macro_balanced_recall':scramble,'terminal_character_class_counts':last_counts,'terminal_character_macro_balanced_recall':terminal},'token_strings_written_to_artifact':False,'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN','interpretation_ceiling':'Initial transcription character prediction from coarse geometry only; no semantic, language, plaintext, translation, or decipherment claim.'}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':status,'objects':nobj,'class_counts':class_counts,'observed':observed,'null_median':null_med,'p':pval,'scramble':scramble,'terminal':terminal},indent=2,sort_keys=True))
if __name__=='__main__': main()
