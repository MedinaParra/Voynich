#!/usr/bin/env python3
"""H95 preregistered blind visual-cluster -> lexical-coherence test."""
import argparse, hashlib, json, math, os, unicodedata
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans
from h91b_stage_a_inventory import API, EXCLUDED, JITTER_OFFSETS, blind_label_boxes, frozen_objects, get_bytes
from h91_stage_b_pairing_gate import greedy_pairs
from h76_visual_object_extraction_admissibility import run_page
EXPECTED_STAGE_A=168; EXPECTED_FOLIOS=9; EXPECTED_OBJECTS=153; MIN_STABILITY=.80
N_PERM=19999; ALPHA=.001; SEED=20261010; SCRAMBLE_SEED=95002; K=4; MIN_CLUSTER=10

def sha256(b): return hashlib.sha256(b).hexdigest()
def canon_hash(x): return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def lev(a,b):
    if len(a)<len(b): a,b=b,a
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1): cur.append(min(cur[-1]+1,prev[j]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]
def mean_within(tokens,clusters):
    s=0.0; n=0
    for c in sorted(set(clusters.tolist())):
        ix=np.where(clusters==c)[0]
        for p in range(len(ix)):
            for q in range(p+1,len(ix)):
                a=tokens[ix[p]]; b=tokens[ix[q]]; den=max(len(a),len(b))
                if den==0: raise ValueError('empty token')
                s+=lev(a,b)/den; n+=1
    if not n: raise ValueError('no within-cluster pairs')
    return s/n,n
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
        out={'experiment':'H95','status':'BLOCKED','reason':'frozen H91 family reproduction failed','stage_a_candidates':stage_a,'admissible_folios':len(frozen),'stable_objects':nobj,'blocked':blocked,'runner_sha256':runner_sha}; a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2)); return
    rows=[]; delayed=[]
    for page,raw,objects,stable in frozen:
        om={o['object_id']:o for o in objects}; xy=np.array([om[oid]['centroid'] for oid,lid in stable],float); spans=xy.max(0)-xy.min(0)
        if np.any(spans==0): raise ValueError(f'degenerate centroid span {page}')
        nxy=(xy-xy.min(0))/spans
        for j,(oid,lid) in enumerate(stable):
            o=om[oid]; bb=o['bbox']; w=float(bb[2]); h=float(bb[3])
            if o['area']<=0 or w<=0 or h<=0: raise ValueError(f'invalid geometry {page}:{oid}')
            rows.append({'page':page,'object_id':oid,'label_ordinal':int(lid),'features_raw':[math.log(float(o['area'])),math.log(w/h),float(nxy[j,0]),float(nxy[j,1])]}); delayed.append((raw,int(lid)))
    X=np.array([r['features_raw'] for r in rows],float); mu=X.mean(0); sd=X.std(0,ddof=0); Z=np.zeros_like(X); nz=sd!=0; Z[:,nz]=(X[:,nz]-mu[nz])/sd[nz]
    km=KMeans(n_clusters=K,random_state=95001,n_init=100).fit(Z); cent=km.cluster_centers_; order=sorted(range(K),key=lambda c:tuple(float(x) for x in cent[c])); remap={old:new for new,old in enumerate(order)}; clusters=np.array([remap[int(c)] for c in km.labels_],int)
    sizes={str(c):int(np.sum(clusters==c)) for c in range(K)}
    visual_payload={'feature_definition':['log(area)','log(width/height)','x_norm','y_norm'],'standardization':'global population SD ddof=0; zero-SD -> 0','k':K,'random_state':95001,'n_init':100,'rows':[{**r,'cluster':int(c)} for r,c in zip(rows,clusters)]}; visual_hash=canon_hash(visual_payload)
    if min(sizes.values())<MIN_CLUSTER:
        out={'experiment':'H95','status':'BLOCKED','reason':'preregistered cluster has fewer than 10 objects','cluster_sizes':sizes,'visual_cluster_sha256':visual_hash,'runner_sha256':runner_sha}; a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2)); return
    # Lexical strings are resolved only after the visual cluster assignment/hash is frozen in memory.
    tokens=[]
    for raw,lid in delayed:
        vocab,boxes=json.loads(raw); tok=unicodedata.normalize('NFC',vocab[int(boxes[lid][0])][0]).strip()
        if not tok: raise ValueError('empty paired token')
        tokens.append(tok)
    tokens=np.array(tokens,object); groups=np.array([r['page'] for r in rows],object); obs,npairs=mean_within(tokens,clusters)
    inds={g:np.where(groups==g)[0] for g in sorted(set(groups))}; rng=np.random.default_rng(SEED); null=np.empty(N_PERM,float)
    for k in range(N_PERM):
        tp=tokens.copy()
        for g,ix in inds.items(): tp[ix]=tokens[ix][rng.permutation(len(ix))]
        null[k]=mean_within(tp,clusters)[0]
    null_med=float(np.median(null)); pval=float((1+np.sum(null<=obs))/(N_PERM+1)); primary_pass=bool(obs<null_med and pval<=ALPHA)
    srng=np.random.default_rng(SCRAMBLE_SEED); ts=tokens.copy()
    for g,ix in inds.items(): ts[ix]=tokens[ix][srng.permutation(len(ix))]
    scramble=mean_within(ts,clusters)[0]; status='PASS' if primary_pass else 'FAIL'
    out={'experiment':'H95 visual-cluster lexical coherence','status':status,'executing_commit_sha':os.environ.get('GITHUB_SHA','UNKNOWN'),'runner_sha256':runner_sha,'h91_reproduction':{'stage_a_candidates':stage_a,'admissible_folios':len(frozen),'stable_objects':nobj},'source_hashes':source_hashes,'visual_cluster_sha256':visual_hash,'cluster_sizes':sizes,'same_cluster_pairs':npairs,'n_permutations':N_PERM,'seed':SEED,'alpha':ALPHA,'primary':{'observed_mean_normalized_levenshtein':obs,'null_median':null_med,'p':pval,'pass':primary_pass},'controls':{'scramble_seed':SCRAMBLE_SEED,'scramble_mean_normalized_levenshtein':scramble},'token_strings_written_to_artifact':False,'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN','interpretation_ceiling':'Blind visual-category/string-form association only; no semantic, language, plaintext, translation, or decipherment claim.'}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':status,'objects':nobj,'cluster_sizes':sizes,'same_cluster_pairs':npairs,'observed':obs,'null_median':null_med,'p':pval,'scramble':scramble},indent=2,sort_keys=True))
if __name__=='__main__': main()
