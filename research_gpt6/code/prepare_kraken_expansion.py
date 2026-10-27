#!/usr/bin/env python3
"""Gate preselected new pages geometrically, then prepare fixed EVA crops."""
import argparse
from collections import Counter
import importlib.metadata
import json
import os
from pathlib import Path
import time
import traceback
import cv2
import numpy as np
from PIL import Image
from register_voynichese_yale import match_images, overlay
from local_residual_registration import (sha,save,project,split_guarded,fit_global,anchors,corrections,measure,passes,positive_grid)
from kraken_eva_word_training import crop_word, sample_name


def prepare(a):
    started=time.perf_counter();plan=json.loads(a.plan.read_text());inputs=json.loads(a.inputs.read_text());a.out.mkdir(parents=True,exist_ok=True)
    if inputs['plan_sha256']!=sha(a.plan):raise ValueError('Acquired input plan mismatch')
    for k,v in [('opencv-python-headless','4.12.0.88'),('numpy','2.2.6'),('pillow','12.3.0')]:
        if importlib.metadata.version(k)!=v:raise ValueError('Changed geometry environment '+k)
    cv2.setNumThreads(2);detector=cv2.SIFT_create(nfeatures=plan['sift']['nfeatures'],contrastThreshold=plan['sift']['contrast_threshold'])
    fs={};ft={};images={};sizes={};pages=inputs['pages'];cases=[];pairs=[];models={};grids={};words=[];summaries=[]
    if [p['folio'] for p in pages]!=plan['additional_training_folios']+plan['reserved_folios']:raise ValueError('Preselected folios changed')
    for p in pages:
        f=p['folio']
        for key in ['json','preview','yale','xml']:
            if sha(a.repo/p[key+'_path'])!=p[key+'_sha256']:raise ValueError('Frozen input changed '+f+' '+key)
        with Image.open(a.repo/p['preview_path']) as im:preview=im.convert('RGB');sizes[f]=im.size
        with Image.open(a.repo/p['yale_path']) as im:images[f]=im.convert('RGB')
        fs[f]=detector.detectAndCompute(cv2.cvtColor(np.asarray(preview),cv2.COLOR_RGB2GRAY),None)
        ft[f]=detector.detectAndCompute(cv2.cvtColor(np.asarray(images[f]),cv2.COLOR_RGB2GRAY),None)
    for number,p in enumerate(pages):
        f=p['folio'];pair=match_images(fs[f],ft[f],sizes[f],{'ratio':plan['sift']['ratio'],'seed':plan['seed']})
        pairs.append({'folio':f,**pair})
        raw=pair.get('points',[]);points=np.array([r['source'] for r in raw]);targets=np.array([r['target'] for r in raw]);accepted=True
        for fold in range(5):
            case={'folio':f,'fold':fold,'conditions':{}}
            if len(raw)<12:case['failure']='Insufficient reciprocal matches';cases.append(case);accepted=False;continue
            fit,held,excluded=split_guarded(points,sizes[f],fold,plan['guard_source_pixels']);h,mask=fit_global(points[fit],targets[fit],plan['seed']+fold)
            case.update(fit_indices=fit.tolist(),held_indices=held.tolist(),guard_excluded_indices=excluded.tolist())
            if h is None or not len(held):case['failure']='No homography or held points';cases.append(case);accepted=False;continue
            inliers=fit[mask];span=np.ptp(points[inliers],axis=0)/sizes[f];source,vectors,selected=anchors(points[fit],targets[fit],h,plan['local'])
            order=np.random.default_rng(plan['seed']+1000*number+fold).permutation(len(source));base=project(points[held],h)
            local,support,capped=corrections(points[held],source,vectors,plan['local']);null,_,_=corrections(points[held],source,vectors[order],plan['local'])
            case.update(matrix=h.tolist(),fit_inlier_indices=inliers.tolist(),fit_inlier_span=span.tolist(),anchor_sources=source.tolist(),anchor_vectors=vectors.tolist(),local_selected_fit_indices=fit[selected].tolist(),shuffle_order=order.tolist(),support_counts=support,capped=capped)
            for name,pred in [('global',base),('spatial_median',base+local),('shuffled_median',base+null)]:
                errors,metrics=measure(pred,targets[held]);case['conditions'][name]={'predictions':pred.tolist(),'errors':errors.tolist(),'metrics':metrics,'accepted':passes(metrics,len(inliers),span)}
            accepted=accepted and case['conditions']['spatial_median']['accepted'];cases.append(case)
        page_words=[];positive=False
        if accepted:
            h,_=fit_global(points,targets,plan['seed']+10000)
            if h is None:accepted=False
            else:
                source,vectors,_=anchors(points,targets,h,plan['local'])
                def warp(q):return project(q,h)+corrections(q,source,vectors,plan['local'])[0]
                grid_source=np.array([[x,y] for y in np.linspace(0,sizes[f][1],25) for x in np.linspace(0,sizes[f][0],17)]);mapped=warp(grid_source);positive,area=positive_grid(mapped,[17,25]);accepted=accepted and positive
                models[f]={'global_matrix':h.tolist(),'anchor_sources':source.tolist(),'anchor_vectors':vectors.tolist(),'coordinates':'current preview directly, no XML-to-preview fit'}
                grids[f]={'source':grid_source.tolist(),'mapped':mapped.tolist(),'shape':[17,25],'positive_orientation':positive,'minimum_double_triangle_area':area}
                for w in p['words']:
                    x,y,width,height=w['preview_bbox'];flags=[];polygon=None;text=w['eva']
                    if width<=0 or height<=0:flags.append('source_nonpositive_size')
                    if x<0 or y<0 or x+width>sizes[f][0] or y+height>sizes[f][1]:flags.append('outside_preview_frame')
                    if not text or any(c<'a' or c>'z' for c in text):flags.append('uncertain_or_nonliteral_EVA')
                    if not flags:
                        polygon=warp([[x,y],[x+width,y],[x+width,y+height],[x,y+height]])
                        cross=[]
                        for j in range(4):
                            u=polygon[(j+1)%4]-polygon[j];v=polygon[(j+2)%4]-polygon[(j+1)%4];cross.append(u[0]*v[1]-u[1]*v[0])
                        if min(cross)<=0:flags.append('nonconvex_or_nonpositive')
                        if any(u<0 or v<0 or u>images[f].width or v>images[f].height for u,v in polygon):flags.append('outside_yale_frame')
                    page_words.append({'folio':f,'index':w['index'],'eva':text,'source_preview_bbox':w['preview_bbox'],'yale_polygon':None if polygon is None else polygon.tolist(),'flags':flags})
                accepted=accepted and sum(not w['flags'] for w in page_words)>=plan['minimum_accepted_words_per_folio']
        words.extend(page_words);summaries.append({'folio':f,'role':p['role'],'source_words':len(p['words']),'reciprocal_matches':len(raw),'accepted_folds':sum(c['conditions'].get('spatial_median',{}).get('accepted',False) for c in cases if c['folio']==f),'positive_grid':positive,'candidate_words':sum(not w['flags'] for w in page_words),'rejection_counts':dict(Counter(flag for w in page_words for flag in w['flags'])),'accepted':bool(accepted)})
        if page_words:
            overlay(images[f],page_words,a.out/'overlays'/(f+'.jpg'));overlay(images[f],page_words,a.out/'overlays'/(f+'_detail.jpg'),detail=True)
        print('GEOMETRY_PAGE='+json.dumps(summaries[-1]),flush=True)
        save(a.out/'geometry_cases.json',cases);save(a.out/'geometry_correspondences.json',pairs);save(a.out/'new_word_polygons.json',words)
    save(a.out/'geometry_models.json',models);save(a.out/'geometry_grids.json',grids)
    result={'status':'PASS_GEOMETRY_CANDIDATES_ONLY' if all(p['accepted'] for p in summaries) else 'FAIL_PRESELECTED_PAGE_GEOMETRY_NO_EXPANSION_TRAINING','pages':summaries,'plan_sha256':sha(a.plan),'inputs_sha256':sha(a.inputs),'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA'),'expert_review':'NOT_REVIEWED','translation':'NOT_RUN'}
    save(a.out/'geometry_result.json',result)
    if not all(p['accepted'] for p in summaries):raise ValueError('Fixed geometric expansion gate failed; no page substitution')
    old=json.loads((a.repo/plan['previous_dataset_path']).read_text());rows=[]
    def export(r,im):
        crop,mask,bounds=crop_word(im,r['polygon'],plan['padding_pixels']);name=r['id'];path=(a.out/'crops'/(name+'.png')).resolve();path.parent.mkdir(exist_ok=True);mask_path=path.with_name(name+'_mask.png');crop.save(path);mask.save(mask_path)
        old_hash=r.get('image_sha256');old_mask=r.get('mask_sha256')
        if old_hash and (sha(path)!=old_hash or sha(mask_path)!=old_mask or bounds!=r['bounds']):raise ValueError('Old sample pixels changed '+name)
        r.update(path=str(path),mask_path=str(mask_path),image_sha256=sha(path),mask_sha256=sha(mask_path),bounds=bounds,crop_size=list(crop.size),training_text=r['reference']);path.with_suffix('.gt.txt').write_text(r['reference']);rows.append(r)
    old_images={}
    for old_r in old:
        r=dict(old_r);r['role']='original_train' if r['role']=='train' else 'historical_development';f=r['folio']
        if f not in old_images:
            if sha(a.repo/r['source_image_path'])!=r['source_image_sha256']:raise ValueError('Old source photo changed')
            with Image.open(a.repo/r['source_image_path']) as im:old_images[f]=im.convert('RGB')
        export(r,old_images[f])
    by={p['folio']:p for p in pages}
    for w in words:
        if w['flags'] or w['yale_polygon'] is None:continue
        p=by[w['folio']];export({'id':sample_name(w['folio'],w['index']),'folio':w['folio'],'index':w['index'],'reference':w['eva'],'role':p['role'],'polygon':w['yale_polygon'],'source_image_path':p['yale_path'],'source_image_sha256':p['yale_sha256'],'reference_status':'CANDIDATE_EVA_NO_NEW_EXPERT_REVIEW'},images[w['folio']])
    if len({r['id'] for r in rows})!=len(rows):raise ValueError('Duplicate sample IDs')
    result.update(candidate_rows_by_role=dict(Counter(r['role'] for r in rows)),characters_by_role={role:sum(len(r['reference']) for r in rows if r['role']==role) for role in sorted({r['role'] for r in rows})},dataset_sha256=None,seconds=time.perf_counter()-started)
    save(a.out/'dataset.json',rows);result['dataset_sha256']=sha(a.out/'dataset.json');save(a.out/'geometry_result.json',result);print('EXPANSION_PREPARED='+json.dumps(result),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    try:prepare(a)
    except Exception as e:save(a.out/'failure.json',{'error':str(e),'traceback':traceback.format_exc(),'translation':'NOT_RUN'});raise
