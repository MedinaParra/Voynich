#!/usr/bin/env python3
"""Construct a versioned candidate catalog from an already evaluated method."""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from local_residual_registration import sha, save, project, fit_global, anchors, corrections, positive_grid


def build(args):
    plan=json.loads(args.plan.read_text());args.out.mkdir(parents=True,exist_ok=True)
    def pinned(path,digest):
        p=args.repo/path
        if sha(p)!=digest:raise ValueError('Frozen input changed: '+path)
        return p
    method=pinned(plan['method_path'],plan['method_sha256'])
    params=json.loads(pinned(plan['parameters_path'],plan['parameters_sha256']).read_text())
    result=json.loads(pinned(plan['cv_result_path'],plan['cv_result_sha256']).read_text())
    cases=json.loads(pinned(plan['cv_cases_path'],plan['cv_cases_sha256']).read_text())
    audit=json.loads(pinned(plan['cv_audit_path'],plan['cv_audit_sha256']).read_text())
    old_f4r=json.loads(pinned(plan['f4r_model_path'],plan['f4r_model_sha256']).read_text())
    if audit['mismatches'] or not audit['status'].startswith('PASS_'):raise ValueError('Prior export audit did not pass')
    for f in ['f3r','f3v','f4r','f4v']:
        cs=[c for c in cases if c['folio']==f]
        if len(cs)!=5 or sorted(c['fold'] for c in cs)!=list(range(5)) or not all(c['conditions']['spatial_median']['accepted'] for c in cs):
            raise ValueError('Not all fixed spatial cases passed: '+f)
    raw=json.loads(pinned(params['correspondences_path'],params['correspondences_sha256']).read_text())
    inputs=json.loads(pinned(params['inputs_path'],params['inputs_sha256']).read_text())
    previous=json.loads(pinned(params['previous_result_path'],params['previous_result_sha256']).read_text())
    if result['plan_sha256']!=plan['parameters_sha256']:raise ValueError('CV parameter hash mismatch')
    for p,v in [('opencv-python-headless','4.12.0.88'),('numpy','2.2.6'),('pillow','12.3.0')]:
        if importlib.metadata.version(p)!=v:raise ValueError('Changed environment: '+p)
    opts=params['local'];models={};grids={};words=[];page_summaries=[];all_geometry=True
    for page in inputs['pages']:
        f=page['folio'];pair=next(p for p in raw if p['source_folio']==f==p['target_folio'])
        a=np.array([p['source'] for p in pair['points']]);b=np.array([p['target'] for p in pair['points']])
        if f=='f4r':h=np.array(old_f4r['global_matrix']);reused=True
        else:h,_=fit_global(a,b,params['seed']+10000);reused=False
        if h is None:raise ValueError('No final homography: '+f)
        source,vectors,_=anchors(a,b,h,opts)
        if reused and (not np.allclose(source,old_f4r['anchor_sources'],atol=1e-8,rtol=1e-10) or not np.allclose(vectors,old_f4r['anchor_vectors'],atol=1e-8,rtol=1e-10)):
            raise ValueError('Reused f4r field does not replay')
        def warp(q):return project(q,h)+corrections(q,source,vectors,opts)[0]
        width,height=page['preview_size'];shape=[17,25]
        grid_source=np.array([[x,y] for y in np.linspace(0,height,25) for x in np.linspace(0,width,17)])
        mapped=warp(grid_source);positive,area=positive_grid(mapped,shape);all_geometry=all_geometry and positive
        grids[f]={'source':grid_source.tolist(),'mapped':mapped.tolist(),'shape':shape,'positive_orientation':positive,'minimum_double_triangle_area':area}
        calibration=np.array(previous['calibrations'][f]['matrix'])
        models[f]={'global_matrix':h.tolist(),'anchor_sources':source.tolist(),'anchor_vectors':vectors.tolist(),
                   'calibration_matrix':calibration.tolist(),'f4r_model_reused':reused,
                   'fit_uses_all_correspondences_after_evaluation':True}
        target=pinned(page['yale_path'],page['yale_sha256'])
        with Image.open(target) as src:im=src.convert('RGB')
        start=len(words)
        for w in page['words']:
            x,y,ww,hh=w['xml_bbox'];polygon=None;flags=[]
            if ww<=0:flags.append('source_nonpositive_width')
            if hh<=0:flags.append('source_nonpositive_height')
            if not flags:
                polygon=warp(project([[x,y],[x+ww,y],[x+ww,y+hh],[x,y+hh]],calibration))
                crosses=[]
                for k in range(4):
                    u=polygon[(k+1)%4]-polygon[k];v=polygon[(k+2)%4]-polygon[(k+1)%4];crosses.append(u[0]*v[1]-u[1]*v[0])
                if min(crosses)<=0:flags.append('nonpositive_or_nonconvex_polygon')
                if any(u<0 or v<0 or u>im.width or v>im.height for u,v in polygon):flags.append('outside_yale_frame')
            expected_exclusion=f=='f3r' and w['index']==2 and flags==['source_nonpositive_width']
            if flags and not expected_exclusion:all_geometry=False
            words.append({'folio':f,'index':w['index'],'eva':w['eva'],'source_xml_bbox':w['xml_bbox'],
                          'yale_polygon':None if polygon is None else polygon.tolist(),'flags':flags,
                          'reading_uncertainty_marker':'*' in w['eva'],'reading_status':'SOURCE_EVA_NOT_EXPERT_REVIEWED',
                          'geometry_method':'global_homography_plus_spatial_median_v2'})
        subset=words[start:];draw=ImageDraw.Draw(im)
        for w in subset:
            if w['yale_polygon'] is None:continue
            p=[tuple(v) for v in w['yale_polygon']];draw.line(p+[p[0]],fill='#009970',width=2);draw.text(p[0],str(w['index']),fill='#003fbb')
        overview=im.copy();overview.thumbnail((1100,1600));(args.out/'overlays').mkdir(exist_ok=True)
        overview.save(args.out/'overlays'/(f+'.jpg'),quality=92)
        polygons=[w['yale_polygon'] for w in subset[:12] if w['yale_polygon'] is not None]
        pts=np.array(polygons).reshape(-1,2)
        im.crop((max(0,int(pts[:,0].min())-15),max(0,int(pts[:,1].min())-20),min(im.width,int(pts[:,0].max())+15),min(im.height,int(pts[:,1].max())+35))).save(args.out/'overlays'/(f+'_detail.jpg'),quality=92)
        page_summaries.append({'folio':f,'source_words':len(subset),'candidate_polygons':sum(w['yale_polygon'] is not None and not w['flags'] for w in subset),
                               'grid_positive':positive,'full_fit_correspondences':len(a),'model_reused':reused})
    candidates=sum(w['yale_polygon'] is not None and not w['flags'] for w in words)
    unique=len({(w['folio'],w['index']) for w in words});accepted=bool(all_geometry and candidates==344 and len(words)==345 and unique==345)
    result={'date':plan['date'],'status':'CANDIDATE_REFERENCE_V2_GEOMETRY_CHECKED_NOT_EXPERT_VALIDATED' if accepted else 'FAIL_UNIFORM_CANDIDATE_CONSTRUCTION',
            'plan_sha256':sha(args.plan),'source_cv_run':result['run_id'],'source_cv_result_sha256':plan['cv_result_sha256'],
            'source_cv_cases_sha256':plan['cv_cases_sha256'],'method_sha256':sha(method),'pages':page_summaries,
            'source_records':len(words),'unique_source_records':unique,'candidate_word_polygons':candidates,'source_zero_width_exclusions':1,
            'new_full_homography_fits':3,'previous_f4r_model_reused':True,'old_reference_files_modified':False,
            'new_validation_cases':0,'source_case_gates_required':20,'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA'),
            'environment':{k:importlib.metadata.version(k) for k in ['opencv-python-headless','numpy','pillow']},
            'scope':plan['scope'],'expert_review':'NOT_REVIEWED','new_ocr_training':'NOT_RUN','translation':'NOT_RUN'}
    save(args.out/'models.json',models);save(args.out/'orientation_grids.json',grids);save(args.out/'word_polygons.json',words);save(args.out/'result.json',result)
    print('UNIFORM_REFERENCE_RESULT='+json.dumps(result,ensure_ascii=True),flush=True)
    if not accepted:raise SystemExit(2)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    build(p.parse_args())
