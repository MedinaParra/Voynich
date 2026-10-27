#!/usr/bin/env python3
"""Recompute candidate v2 fields and geometry; no new detector or model fitting."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from audit_local_residual_registration import read,sha,field,compensate
from audit_voynichese_registration import apply


def audit(bundle,repo):
    plan_path=repo/'data/local_reference_v2_plan.json';plan=read(plan_path);result=read(bundle/'result.json')
    params=read(repo/plan['parameters_path']);cv=read(repo/plan['cv_result_path']);cases=read(repo/plan['cv_cases_path'])
    inputs=read(repo/params['inputs_path']);raw=read(repo/params['correspondences_path']);previous=read(repo/params['previous_result_path'])
    models=read(bundle/'models.json');grids=read(bundle/'orientation_grids.json');words=read(bundle/'word_polygons.json')
    old_f4r=read(repo/plan['f4r_model_path']);old_words=read(repo/'results/voynichese_local_registration/word_polygons.json')
    checks=0;errors=[]
    def check(label,actual,expected=True):
        nonlocal checks
        checks+=1
        if actual is None or expected is None:equal=actual is None and expected is None
        elif isinstance(actual,np.ndarray) or isinstance(expected,np.ndarray):equal=bool(np.allclose(actual,expected,atol=1e-6,rtol=1e-9))
        elif isinstance(actual,(int,float)) and isinstance(expected,(int,float)):equal=math.isclose(actual,expected,abs_tol=1e-6,rel_tol=1e-9)
        else:equal=actual==expected
        if not equal:errors.append({'check':label,'actual':actual.tolist() if isinstance(actual,np.ndarray) else actual,'expected':expected.tolist() if isinstance(expected,np.ndarray) else expected})
    check('builder_plan_hash',result['plan_sha256'],sha(plan_path))
    for prefix in ['method','parameters','cv_result','cv_cases','cv_audit','f4r_model']:
        check(prefix+'_hash',sha(repo/plan[prefix+'_path']),plan[prefix+'_sha256'])
    for prefix in ['inputs','correspondences','previous_result']:
        check(prefix+'_hash',sha(repo/params[prefix+'_path']),params[prefix+'_sha256'])
    check('cv_parameters_hash',cv['plan_sha256'],plan['parameters_sha256'])
    check('all_four_models',sorted(models),sorted(p['folio'] for p in inputs['pages']))
    expected_keys=[(p['folio'],w['index']) for p in inputs['pages'] for w in p['words']]
    check('word_keys',[(w['folio'],w['index']) for w in words],expected_keys);check('unique_keys',len(set(expected_keys)),345)
    by_word={(w['folio'],w['index']):w for w in words};page_counts={};all_geometry=True
    def cross(u,v):return u[0]*v[1]-u[1]*v[0]
    for page in inputs['pages']:
        f=page['folio'];cs=[c for c in cases if c['folio']==f]
        check(f+'/five_source_cases',sorted(c['fold'] for c in cs),list(range(5)))
        check(f+'/all_local_cases_pass',all(c['conditions']['spatial_median']['accepted'] for c in cs))
        pair=next(p for p in raw if p['source_folio']==f==p['target_folio'])
        a=np.array([p['source'] for p in pair['points']]);b=np.array([p['target'] for p in pair['points']]);model=models[f];h=np.array(model['global_matrix'])
        source,vectors,_=field(a,b,h,params['local'])
        check(f+'/anchor_sources',model['anchor_sources'],source);check(f+'/anchor_vectors',model['anchor_vectors'],vectors)
        calibration=np.array(previous['calibrations'][f]['matrix']);check(f+'/calibration',model['calibration_matrix'],calibration)
        check(f+'/model_reuse_flag',model['f4r_model_reused'],f=='f4r')
        if f=='f4r':
            check('f4r/reused_global_matrix',model['global_matrix'],np.array(old_f4r['global_matrix']))
            check('f4r/reused_sources',model['anchor_sources'],np.array(old_f4r['anchor_sources']))
            check('f4r/reused_vectors',model['anchor_vectors'],np.array(old_f4r['anchor_vectors']))
        def warp(q):return apply(q,h)+compensate(q,source,vectors,params['local'])[0]
        width,height=page['preview_size'];grid_source=np.array([[x,y] for y in np.linspace(0,height,25) for x in np.linspace(0,width,17)])
        mapped=warp(grid_source);grid=grids[f];check(f+'/grid_source',grid['source'],grid_source);check(f+'/grid_mapped',grid['mapped'],mapped)
        cells=mapped.reshape(25,17,2);areas=[]
        for y in range(24):
            for x in range(16):
                aa,bb,cc,dd=cells[y,x],cells[y,x+1],cells[y+1,x+1],cells[y+1,x]
                areas.extend([cross(bb-aa,cc-aa),cross(cc-aa,dd-aa)])
        positive=bool(min(areas)>0);all_geometry=all_geometry and positive
        check(f+'/grid_orientation',grid['positive_orientation'],positive);check(f+'/grid_area',grid['minimum_double_triangle_area'],float(min(areas)))
        check(f+'/yale_hash',sha(repo/page['yale_path']),page['yale_sha256'])
        with Image.open(repo/page['yale_path']) as im:size=im.size
        count=0
        for w in page['words']:
            label=f+'/'+str(w['index']);actual=by_word[(f,w['index'])];x,y,ww,hh=w['xml_bbox'];flags=[];expected=None
            if ww<=0:flags.append('source_nonpositive_width')
            if hh<=0:flags.append('source_nonpositive_height')
            if not flags:
                expected=warp(apply([[x,y],[x+ww,y],[x+ww,y+hh],[x,y+hh]],calibration))
                if min(cross(expected[(k+1)%4]-expected[k],expected[(k+2)%4]-expected[(k+1)%4]) for k in range(4))<=0:flags.append('nonpositive_or_nonconvex_polygon')
                if any(u<0 or v<0 or u>size[0] or v>size[1] for u,v in expected):flags.append('outside_yale_frame')
            if flags and not(f=='f3r' and w['index']==2 and flags==['source_nonpositive_width']):all_geometry=False
            for key,value in {'eva':w['eva'],'source_xml_bbox':w['xml_bbox'],'flags':flags,'reading_uncertainty_marker':'*' in w['eva'],'geometry_method':'global_homography_plus_spatial_median_v2'}.items():check(label+'/'+key,actual[key],value)
            check(label+'/polygon',actual['yale_polygon'],expected)
            count+=int(expected is not None and not flags)
            if f=='f4r':check(label+'/replayed_f4r_polygon',actual['yale_polygon'],np.array(old_words[w['index']]['yale_polygon']))
        page_counts[f]=count
        summary=next(p for p in result['pages'] if p['folio']==f)
        check(f+'/candidate_count',summary['candidate_polygons'],count);check(f+'/source_count',summary['source_words'],len(page['words']))
        check(f+'/correspondence_count',summary['full_fit_correspondences'],len(a));check(f+'/grid_summary',summary['grid_positive'],positive)
    candidates=sum(page_counts.values());check('candidate_total',result['candidate_word_polygons'],candidates)
    check('source_total',result['source_records'],len(words));check('expected_source_total',len(words),345)
    check('unique_source_total',result['unique_source_records'],len(by_word));check('new_validation_cases',result['new_validation_cases'],0)
    exclusions=[{'folio':w['folio'],'index':w['index'],'reason':w['flags'][0]} for w in words if w['yale_polygon'] is None]
    check('expected_exclusions',exclusions,plan['expected_exclusions']);check('zero_width_count',result['source_zero_width_exclusions'],sum('source_nonpositive_width' in w['flags'] for w in words))
    expected_status='CANDIDATE_REFERENCE_V2_GEOMETRY_CHECKED_NOT_EXPERT_VALIDATED' if all_geometry and candidates==344 and len(words)==345 and len(by_word)==345 else 'FAIL_UNIFORM_CANDIDATE_CONSTRUCTION'
    check('construction_status',result['status'],expected_status)
    return {'status':'PASS_UNIFORM_CANDIDATE_EXPORT_AUDIT' if not errors else 'FAIL','checks':checks,'mismatches':errors,
            'candidate_polygons_by_folio':page_counts,'source_records':len(words),'candidate_polygons':candidates,'exclusions':exclusions,
            'scope':'Frozen evidence, four local fields, grid orientation, original EVA/boxes, every candidate polygon and f4r replay recomputed. No new OpenCV fit or expert validation of image matches or readings.',
            'expert_review':'NOT_REVIEWED','new_ocr_training':'NOT_RUN','translation':'NOT_RUN'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=audit(args.bundle,args.repo);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=True))
    if result['mismatches']:raise SystemExit(1)
