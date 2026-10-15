#!/usr/bin/env python3
"""H98 cross-transcription label-object lexical-anchor closure.

Reuses H92's frozen H91 visual family and geometry, but resolves label ordinal
lengths from the frozen GC v101 IVTFF source. Raw GC/IT token strings are never
written to output. Any ordinal-resolution mismatch blocks the experiment.
"""
import argparse, hashlib, json, os, re, unicodedata
from pathlib import Path
import numpy as np
from h91b_stage_a_inventory import API, EXCLUDED, JITTER_OFFSETS, blind_label_boxes, frozen_objects, get_bytes
from h91_stage_b_pairing_gate import greedy_pairs
from h76_visual_object_extraction_admissibility import run_page
from h92_independent_geometry_lexical_anchor import loocv_mae, strat_perm_test, derange_indices

EXPECTED_GC='b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f'
EXPECTED_FOLIOS=9; EXPECTED_PAIRS=153; MIN_STABILITY=.80; ALPHA=.01

def sha256(b): return hashlib.sha256(b).hexdigest()

def clean_tokens(payload):
    s=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;', ' ', payload)
    out=[]
    for p in re.split(r'[.\s]+',s):
        p=p.strip()
        if not p or '?' in p: continue
        runs=re.findall(r'[A-Za-z0-9]+',p)
        if len(runs)==1 and runs[0]: out.append(unicodedata.normalize('NFC',runs[0]))
    return out

def gc_label_tokens(data):
    """Return GC label-like single-token records in stable IVTFF line order per folio.

    The H91 label ordinal is a visual label-box ordinal. We require an exact
    one-to-one count match between H91 blind label boxes and GC label records;
    otherwise ordinal transfer is not identified and H98 is BLOCKED.
    """
    d={}
    for line in data.decode('utf-8','strict').splitlines():
        m=re.match(r'^<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)$',line)
        if not m: continue
        fol,num,locator,payload=m.groups(); loc=re.sub(r'^[@+*=]','',locator.strip())
        # IVTFF label locators used by the frozen IT/GC family begin with L.
        if not loc.startswith('L'): continue
        toks=clean_tokens(payload)
        if len(toks)==1: d.setdefault(fol,[]).append(toks[0])
    return d

def write_blocked(a,runner,reason,**kw):
    out={'experiment':'H98 cross-transcription label-object lexical-anchor closure','status':'BLOCKED','reason':reason,'runner_sha256':runner,'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN'}; out.update(kw)
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--gc',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    runner=sha256(Path(__file__).read_bytes()); gcd=a.gc.read_bytes(); gch=sha256(gcd)
    if gch!=EXPECTED_GC: return write_blocked(a,runner,'frozen GC v101 source hash mismatch',gc_sha256=gch,expected_gc_sha256=EXPECTED_GC)
    gc=gc_label_tokens(gcd)
    listing=json.loads(get_bytes(API)); files=sorted((x for x in listing if x.get('type')=='file' and x['name'].endswith('.json')),key=lambda x:x['name'])
    frozen=[]; blocked=[]; stage_a=0
    for item in files:
        page=item['name'][:-5]
        if page in EXCLUDED: continue
        try:
            raw=get_bytes(item['download_url']); p=Path('/tmp')/item['name']; p.write_bytes(raw); r=run_page(page,p); objects=frozen_objects(r)
            if len(objects)<15: continue
            stage_a+=1; labels=blind_label_boxes(raw); base=greedy_pairs(objects,labels); jm=[greedy_pairs(objects,labels,float(dx),float(dy)) for dx,dy in JITTER_OFFSETS]
            stable=[(oid,lid) for oid,lid in sorted(base.items()) if all(m.get(oid)==lid for m in jm)]; frac=len(stable)/len(base) if base else 0
            if len(base)>=15 and frac>=MIN_STABILITY: frozen.append((page,raw,objects,stable,labels))
        except Exception as e: blocked.append({'page':page,'error':f'{type(e).__name__}: {e}'})
    n=sum(len(z[3]) for z in frozen)
    if blocked or stage_a!=168 or len(frozen)!=EXPECTED_FOLIOS or n!=EXPECTED_PAIRS:
        return write_blocked(a,runner,'H91 frozen-family reproduction gate failed',stage_a_candidate_count=stage_a,admissible_folio_count=len(frozen),stable_pair_count=n,blocked=blocked)
    rows=[]; disagreements=0; coverage_errors=[]
    for page,raw,objects,stable,labels in frozen:
        vocab,boxes=json.loads(raw); om={o['object_id']:o for o in objects}; gt=gc.get(page,[])
        # Strict transfer gate: no heuristic remapping after lexical opening.
        if len(gt)!=len(labels): coverage_errors.append({'page':page,'h91_label_boxes':len(labels),'gc_label_records':len(gt)}); continue
        for oid,lid in stable:
            i=int(lid)
            if i<0 or i>=len(gt): coverage_errors.append({'page':page,'label_ordinal':i,'gc_label_records':len(gt)}); continue
            it=unicodedata.normalize('NFC',vocab[int(boxes[i][0])][0]).strip(); gl=gt[i]
            if not it or not gl: coverage_errors.append({'page':page,'label_ordinal':i,'error':'empty token'}); continue
            if len(it)!=len(gl): disagreements+=1
            rows.append({'page':page,'object_id':oid,'label_ordinal':i,'centroid':[float(x) for x in om[oid]['centroid']],'gc_length':len(gl),'it_length':len(it)})
    if coverage_errors or len(rows)!=EXPECTED_PAIRS:
        return write_blocked(a,runner,'GC v101 ordinal coverage gate failed',resolved_pairs=len(rows),expected_pairs=EXPECTED_PAIRS,coverage_errors=coverage_errors,gc_sha256=gch)
    groups=np.array([r['page'] for r in rows],object); y=np.array([r['gc_length'] for r in rows],float); feats=np.empty((len(rows),5),float)
    for page in sorted(set(groups)):
        ix=np.where(groups==page)[0]; xy=np.array([rows[i]['centroid'] for i in ix],float); spans=xy.max(0)-xy.min(0)
        if np.any(spans==0): return write_blocked(a,runner,f'degenerate x/y span in {page}')
        nxy=(xy-xy.min(0))/spans; c=nxy.mean(0); d=nxy-c; rad=np.sqrt((d*d).sum(1)); mr=rad.max()
        if mr==0: return write_blocked(a,runner,f'zero maximum radius in {page}')
        rad/=mr; th=np.arctan2(d[:,1],d[:,0]); feats[ix]=np.column_stack([nxy[:,0],nxy[:,1],rad,np.sin(th),np.cos(th)])
    primary=strat_perm_test(feats,y,groups,20261011)
    rng=np.random.default_rng(98090); ys=y.copy()
    for page in sorted(set(groups)):
        ix=np.where(groups==page)[0]; ys[ix]=y[ix][derange_indices(len(ix),rng)]
    scramble=strat_perm_test(feats,ys,groups,98091)
    pp=primary['observed_mae']<primary['null_median'] and primary['p']<=ALPHA; sf=scramble['observed_mae']<scramble['null_median'] and scramble['p']<=ALPHA
    status='PASS' if pp and not sf else 'FAIL'
    geom_payload=[{'page':r['page'],'object_id':r['object_id'],'label_ordinal':r['label_ordinal'],'centroid':r['centroid']} for r in rows]
    out={'experiment':'H98 cross-transcription label-object lexical-anchor closure','status':status,'executing_commit_sha':os.environ.get('GITHUB_SHA','UNKNOWN'),'runner_sha256':runner,'gc_sha256':gch,'resolved_pairs':len(rows),'folio_ids':sorted(set(groups)),'geometry_pair_sha256':sha256(json.dumps(geom_payload,sort_keys=True,separators=(',',':')).encode()),'seeds':{'primary':20261011,'scramble_derangement':98090,'scramble_test':98091},'n_permutations':9999,'alpha':ALPHA,'primary_length':primary,'pair_scramble_control':scramble,'primary_pass':pp,'scramble_false_positive':sf,'length_disagreement_count_it_vs_gc':disagreements,'pair_audit_numeric_only':[{'page':r['page'],'object_id':r['object_id'],'label_ordinal':r['label_ordinal'],'gc_length':r['gc_length'],'it_length':r['it_length']} for r in rows],'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN','interpretation_ceiling':'Cross-transcription geometry-to-label-length association only; no semantic, language, plaintext, translation, or decipherment claim.'}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':status,'resolved_pairs':len(rows),'primary':primary,'scramble':scramble,'length_disagreement_count':disagreements},indent=2,sort_keys=True))
if __name__=='__main__': main()
