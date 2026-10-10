#!/usr/bin/env python3
"""H93 preregistered visual-equivalence -> lexical-similarity test.

Reconstructs the frozen H91 9-folio/153-pair family before lexical exposure,
freezes/hashes the visual distance representation, then opens only the already
paired token strings for the preregistered normalized-Levenshtein endpoint.
"""
import argparse, hashlib, json, math, os, unicodedata
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
from h91b_stage_a_inventory import API, EXCLUDED, JITTER_OFFSETS, blind_label_boxes, frozen_objects, get_bytes
from h91_stage_b_pairing_gate import greedy_pairs
from h76_visual_object_extraction_admissibility import run_page

EXPECTED_STAGE_A=168
EXPECTED_FOLIOS=9
EXPECTED_OBJECTS=153
MIN_STABILITY=.80
N_PERM=19999
ALPHA=.001
SEED=20261010
SCRAMBLE_SEED=93001


def sha256(b): return hashlib.sha256(b).hexdigest()

def rho_from_vectors(x,y):
    rx=rankdata(x,method='average'); ry=rankdata(y,method='average')
    sx=float(np.std(rx)); sy=float(np.std(ry))
    if sx==0 or sy==0: raise ValueError('Spearman rank variance is zero')
    return float(np.corrcoef(rx,ry)[0,1])

def levenshtein(a,b):
    if len(a)<len(b): a,b=b,a
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1):
            cur.append(min(cur[-1]+1,prev[j]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    runner_sha=sha256(Path(__file__).read_bytes())
    listing=json.loads(get_bytes(API)); files=sorted((x for x in listing if x.get('type')=='file' and x['name'].endswith('.json')),key=lambda x:x['name'])
    frozen=[]; stage_a=0; blocked=[]; source_hashes={}
    for item in files:
        page=item['name'][:-5]
        if page in EXCLUDED: continue
        try:
            raw=get_bytes(item['download_url']); p=Path('/tmp')/item['name']; p.write_bytes(raw)
            r=run_page(page,p); objects=frozen_objects(r)
            if len(objects)<15: continue
            stage_a+=1; labels=blind_label_boxes(raw); base=greedy_pairs(objects,labels)
            jitter=[greedy_pairs(objects,labels,float(dx),float(dy)) for dx,dy in JITTER_OFFSETS]
            stable=[(oid,lid) for oid,lid in sorted(base.items()) if all(m.get(oid)==lid for m in jitter)]
            frac=len(stable)/len(base) if base else 0.0
            if len(base)>=15 and frac>=MIN_STABILITY:
                frozen.append((page,raw,objects,stable))
                source_hashes[page]={'coord_blob_sha':item.get('sha'),'coord_sha256':sha256(raw),'image_sha256':r.get('image_sha256')}
        except Exception as e: blocked.append({'page':page,'error':f'{type(e).__name__}: {e}'})
    nobj=sum(len(z[3]) for z in frozen)
    if blocked or stage_a!=EXPECTED_STAGE_A or len(frozen)!=EXPECTED_FOLIOS or nobj!=EXPECTED_OBJECTS:
        status='BLOCKED' if blocked else 'FAIL'
        out={'experiment':'H93','status':status,'reason':'frozen H91 family reproduction failed','stage_a_candidates':stage_a,'admissible_folios':len(frozen),'stable_objects':nobj,'blocked':blocked,'runner_sha256':runner_sha}
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2)); return

    # Freeze geometry and visual distances before reading any token value.
    geom=[]
    for page,raw,objects,stable in frozen:
        om={o['object_id']:o for o in objects}
        for oid,lid in stable:
            o=om[oid]; bb=o['bbox']; w=float(bb[2]); h=float(bb[3])
            if o['area']<=0 or w<=0 or h<=0: raise ValueError(f'nonpositive geometry {page}:{oid}')
            geom.append({'page':page,'object_id':oid,'label_ordinal':int(lid),'features_raw':[math.log(float(o['area'])),math.log(w/h),float(o['text_overlap_fraction'])]})
    G=np.array([x['features_raw'] for x in geom],float); mu=G.mean(0); sd=G.std(0,ddof=0)
    if np.any(sd==0): raise ValueError('zero global geometry feature standard deviation')
    Z=(G-mu)/sd; ii,jj=np.triu_indices(len(geom),1); visual=np.sqrt(((Z[ii]-Z[jj])**2).sum(1))
    visual_payload={'feature_definition':['log(area)','log(width/height)','overlap_fraction'],'standardization':'global population sd ddof=0','mean':mu.tolist(),'sd':sd.tolist(),'rows':geom,'pair_i':ii.tolist(),'pair_j':jj.tolist(),'visual_distance':visual.tolist()}
    visual_hash=sha256(json.dumps(visual_payload,sort_keys=True,separators=(',',':')).encode())

    # Lexical opening occurs only after visual representation/hash is fixed in memory.
    tokens=[]
    for page,raw,objects,stable in frozen:
        vocab,boxes=json.loads(raw)
        for oid,lid in stable:
            tok=unicodedata.normalize('NFC',vocab[int(boxes[lid][0])][0]).strip()
            if not tok:
                out={'experiment':'H93','status':'BLOCKED','reason':f'empty token provenance failure at {page}:{lid}','visual_representation_sha256':visual_hash,'runner_sha256':runner_sha}
                a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2)); return
            tokens.append(tok)
    if len(tokens)!=EXPECTED_OBJECTS: raise ValueError('token/object cardinality mismatch')
    D=np.zeros((len(tokens),len(tokens)),float)
    for i in range(len(tokens)):
        for j in range(i+1,len(tokens)):
            d=levenshtein(tokens[i],tokens[j])/max(len(tokens[i]),len(tokens[j])); D[i,j]=D[j,i]=d
    lexical=D[ii,jj]; observed=rho_from_vectors(visual,lexical)
    groups=np.array([x['page'] for x in geom],object); uniq=sorted(set(groups)); inds={g:np.where(groups==g)[0] for g in uniq}
    rng=np.random.default_rng(SEED); null=np.empty(N_PERM,float)
    base_idx=np.arange(len(tokens))
    for k in range(N_PERM):
        perm=base_idx.copy()
        for g in uniq:
            ix=inds[g]; perm[ix]=ix[rng.permutation(len(ix))]
        null[k]=rho_from_vectors(visual,D[perm[ii],perm[jj]])
    pval=float((1+np.sum(null>=observed))/(N_PERM+1))

    srng=np.random.default_rng(SCRAMBLE_SEED); sperm=base_idx.copy()
    for g in uniq:
        ix=inds[g]; sperm[ix]=ix[srng.permutation(len(ix))]
    scramble_rho=rho_from_vectors(visual,D[sperm[ii],sperm[jj]])
    cross=(groups[ii]!=groups[jj]); cross_rho=rho_from_vectors(visual[cross],lexical[cross])
    primary_pass=(observed>0 and pval<=ALPHA); status='PASS' if primary_pass else 'FAIL'
    counts={g:int(np.sum(groups==g)) for g in uniq}
    out={'experiment':'H93 visual-equivalence lexical-similarity test','status':status,'executing_commit_sha':os.environ.get('GITHUB_SHA','UNKNOWN'),'runner_sha256':runner_sha,'h91_reproduction':{'stage_a_candidates':stage_a,'admissible_folios':len(frozen),'stable_objects':nobj,'per_folio_counts':counts},'source_hashes':source_hashes,'visual_representation_sha256':visual_hash,'visual_feature_mean':mu.tolist(),'visual_feature_population_sd':sd.tolist(),'resolved_token_count':len(tokens),'unordered_pair_count':int(len(ii)),'n_permutations':N_PERM,'seed':SEED,'alpha':ALPHA,'primary':{'observed_rho':observed,'null_median_rho':float(np.median(null)),'p':pval,'pass':primary_pass},'controls':{'pairing_scramble_seed':SCRAMBLE_SEED,'pairing_scramble_rho':scramble_rho,'cross_folio_only_pair_count':int(np.sum(cross)),'cross_folio_only_rho':cross_rho},'token_strings_written_to_artifact':False,'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN','interpretation_ceiling':'Statistical visual-string similarity association only; no semantic, language, plaintext, translation, or decipherment claim.'}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':status,'objects':len(tokens),'pairs':len(ii),'observed_rho':observed,'null_median_rho':float(np.median(null)),'p':pval,'scramble_rho':scramble_rho,'cross_folio_rho':cross_rho,'visual_hash':visual_hash},indent=2,sort_keys=True))
if __name__=='__main__': main()
