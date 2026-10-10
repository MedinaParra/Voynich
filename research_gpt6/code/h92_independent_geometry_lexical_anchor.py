#!/usr/bin/env python3
"""H92 preregistered independent geometry -> label-length replication.

Recomputes the frozen H91 Stage-B family before lexical opening, verifies the
9-folio/153-pair gate, then resolves only token lengths. Raw token strings are
never written to output.
"""
import argparse, hashlib, json, math, os, unicodedata
from pathlib import Path
import numpy as np
from h91b_stage_a_inventory import API, EXCLUDED, JITTER_OFFSETS, blind_label_boxes, frozen_objects, get_bytes
from h91_stage_b_pairing_gate import greedy_pairs
from h76_visual_object_extraction_admissibility import run_page

EXPECTED_FOLIOS=9
EXPECTED_PAIRS=153
MIN_STABILITY=.80
N_PERM=9999
ALPHA=.01


def sha256(b): return hashlib.sha256(b).hexdigest()

def loocv_mae(X,y):
    A=np.column_stack([np.ones(len(y)),X])
    beta=np.linalg.lstsq(A,y,rcond=None)[0]
    pred=A@beta; resid=y-pred
    h=np.einsum('ij,jk,ik->i',A,np.linalg.pinv(A.T@A),A)
    den=1.0-h
    if np.any(np.abs(den)<1e-12): raise ValueError('LOOCV leverage degeneracy')
    return float(np.mean(np.abs(resid/den)))

def strat_perm_test(X,y,groups,seed):
    obs=loocv_mae(X,y); rng=np.random.default_rng(seed); null=np.empty(N_PERM)
    uniq=sorted(set(groups)); inds={g:np.where(groups==g)[0] for g in uniq}
    for k in range(N_PERM):
        yp=y.copy()
        for g in uniq:
            ix=inds[g]; yp[ix]=y[ix][rng.permutation(len(ix))]
        null[k]=loocv_mae(X,yp)
    return {'observed_mae':obs,'null_median':float(np.median(null)),'p':float((1+np.sum(null<=obs))/(N_PERM+1))}

def derange_indices(n,rng):
    if n<2: raise ValueError('folio has one eligible pair; scramble control impossible')
    base=np.arange(n)
    while True:
        p=rng.permutation(n)
        if np.all(p!=base): return p

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    runner_sha=sha256(Path(__file__).read_bytes())
    listing=json.loads(get_bytes(API)); files=sorted((x for x in listing if x.get('type')=='file' and x['name'].endswith('.json')),key=lambda x:x['name'])
    frozen=[]; source_hashes={}; stage_a_count=0; blocked=[]
    for item in files:
        page=item['name'][:-5]
        if page in EXCLUDED: continue
        try:
            raw=get_bytes(item['download_url']); p=Path('/tmp')/item['name']; p.write_bytes(raw)
            r=run_page(page,p); objects=frozen_objects(r)
            if len(objects)<15: continue
            stage_a_count+=1; labels=blind_label_boxes(raw)
            base=greedy_pairs(objects,labels); jm=[greedy_pairs(objects,labels,float(dx),float(dy)) for dx,dy in JITTER_OFFSETS]
            stable=[(oid,lid) for oid,lid in sorted(base.items()) if all(m.get(oid)==lid for m in jm)]
            frac=len(stable)/len(base) if base else 0.0
            if len(base)>=15 and frac>=MIN_STABILITY:
                frozen.append((page,raw,r,objects,stable,frac,item.get('sha')))
                source_hashes[page]={'coord_blob_sha':item.get('sha'),'coord_sha256':sha256(raw),'image_sha256':r.get('image_sha256')}
        except Exception as e: blocked.append({'page':page,'error':f'{type(e).__name__}: {e}'})
    pair_n=sum(len(z[4]) for z in frozen)
    gate_ok=(not blocked and stage_a_count==168 and len(frozen)==EXPECTED_FOLIOS and pair_n==EXPECTED_PAIRS)
    if not gate_ok:
        out={'status':'BLOCKED' if blocked else 'FAIL','reason':'H91 frozen-family reproduction gate failed','stage_a_candidate_count':stage_a_count,'admissible_folio_count':len(frozen),'stable_pair_count':pair_n,'blocked':blocked,'runner_sha256':runner_sha}
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2)); return

    rows=[]
    for page,raw,r,objects,stable,frac,blobsha in frozen:
        vocab,boxes=json.loads(raw); om={o['object_id']:o for o in objects}
        for oid,lid in stable:
            token=unicodedata.normalize('NFC',vocab[int(boxes[lid][0])][0]).strip()
            if not token: raise ValueError(f'empty token at {page}:{lid}')
            rows.append({'page':page,'object_id':oid,'label_ordinal':int(lid),'centroid':[float(x) for x in om[oid]['centroid']],'token_length':len(token)})
    # Geometry normalized independently within each folio exactly as preregistered.
    feats=np.empty((len(rows),5),float); groups=np.array([r['page'] for r in rows],object); y=np.array([r['token_length'] for r in rows],float)
    for page in sorted(set(groups)):
        ix=np.where(groups==page)[0]; xy=np.array([rows[i]['centroid'] for i in ix],float); spans=xy.max(0)-xy.min(0)
        if np.any(spans==0):
            out={'status':'BLOCKED','reason':f'degenerate x/y span in {page}'}; a.out.write_text(json.dumps(out,indent=2)+'\n'); return
        nxy=(xy-xy.min(0))/spans; c=nxy.mean(0); d=nxy-c; rad=np.sqrt((d*d).sum(1)); mr=rad.max()
        if mr==0:
            out={'status':'BLOCKED','reason':f'zero maximum radius in {page}'}; a.out.write_text(json.dumps(out,indent=2)+'\n'); return
        rad/=mr; th=np.arctan2(d[:,1],d[:,0]); feats[ix]=np.column_stack([nxy[:,0],nxy[:,1],rad,np.sin(th),np.cos(th)])
    primary=strat_perm_test(feats,y,groups,20261010)
    ablation=strat_perm_test(feats[:,:2],y,groups,20261010)
    rng=np.random.default_rng(92090); ys=y.copy()
    try:
        for page in sorted(set(groups)):
            ix=np.where(groups==page)[0]; ys[ix]=y[ix][derange_indices(len(ix),rng)]
    except ValueError as e:
        out={'status':'BLOCKED','reason':str(e)}; a.out.write_text(json.dumps(out,indent=2)+'\n'); return
    scramble=strat_perm_test(feats,ys,groups,92091)
    primary_pass=primary['observed_mae']<primary['null_median'] and primary['p']<=ALPHA
    scramble_fp=scramble['observed_mae']<scramble['null_median'] and scramble['p']<=ALPHA
    status='PASS' if primary_pass and not scramble_fp else 'FAIL'
    counts={p:int(np.sum(groups==p)) for p in sorted(set(groups))}
    audit=[{'page':r['page'],'object_id':r['object_id'],'label_ordinal':r['label_ordinal'],'token_length':r['token_length']} for r in rows]
    out={'experiment':'H92 independent geometry-label-length replication','status':status,'executing_commit_sha':os.environ.get('GITHUB_SHA','UNKNOWN'),'runner_sha256':runner_sha,'h91_reproduction':{'stage_a_candidates':stage_a_count,'admissible_folios':len(frozen),'stable_pairs':pair_n,'folio_ids':sorted(set(groups)),'pair_counts':counts},'source_hashes':source_hashes,'seeds':{'primary':20261010,'scramble_derangement':92090,'scramble_test':92091},'n_permutations':N_PERM,'alpha':ALPHA,'primary_length':primary,'pair_scramble_control':scramble,'xy_ablation':ablation,'primary_pass':primary_pass,'scramble_false_positive':scramble_fp,'pair_audit_numeric_only':audit,'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN','interpretation_ceiling':'Association with label length only; no semantic, language, plaintext, translation, or decipherment claim.'}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':status,'n_folios':len(frozen),'n_pairs':pair_n,'primary':primary,'scramble':scramble,'xy_ablation':ablation},indent=2,sort_keys=True))
if __name__=='__main__': main()
