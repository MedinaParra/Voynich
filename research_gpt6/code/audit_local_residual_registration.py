#!/usr/bin/env python3
"""Recompute exported guarded folds, residual fields and candidate geometry."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics

import numpy as np
from PIL import Image
from audit_voynichese_registration import apply


def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def metrics(errors):
    values = sorted(errors); position = .9*(len(values)-1); i = math.floor(position); fraction = position-i
    p90 = values[i] if i+1 == len(values) else values[i]*(1-fraction)+values[i+1]*fraction
    return {'points':len(values),'median':statistics.median(values),'p90':p90,'maximum':max(values),
            'within_5_fraction':sum(e<=5 for e in values)/len(values)}
def field(a,b,h,opts):
    residuals = b-apply(a,h); groups = defaultdict(list); selected = []
    for i,(point,vector) in enumerate(zip(a,residuals)):
        if math.hypot(*vector) <= opts['fit_residual_limit_yale_pixels']:
            key = tuple(np.rint(point/opts['source_group_grid_pixels']).astype(np.int64))
            groups[key].append((point,vector));selected.append(i)
    source = [];vectors = []
    for key in sorted(groups):
        values = groups[key]
        source.append([statistics.median(p[k] for p,v in values) for k in [0,1]])
        vectors.append([statistics.median(v[k] for p,v in values) for k in [0,1]])
    return np.array(source).reshape(-1,2),np.array(vectors).reshape(-1,2),selected
def compensate(query,source,vectors,opts):
    values=[];supports=[];capped=[]
    for point in query:
        candidates=sorted([(math.hypot(*(p-point)),i) for i,p in enumerate(source)])
        indices=[i for distance,i in candidates if distance<=opts['radius_source_pixels']][:opts['maximum_neighbors']]
        delta=[0.,0.]
        if len(indices)>=opts['minimum_groups']:
            delta=[statistics.median(vectors[i,k] for i in indices) for k in [0,1]]
        norm=math.hypot(*delta);limit=opts['correction_limit_yale_pixels'];cap=norm>limit
        if cap:delta=[v*limit/norm for v in delta]
        values.append(delta);supports.append(len(indices));capped.append(cap)
    return np.array(values),supports,capped
def gate(m,n,span):
    return bool(n>=50 and min(span)>=.5 and m['points']>=10 and m['median']<=2 and m['p90']<=5 and m['within_5_fraction']>=.8)


def audit(bundle,repo):
    plan_path=repo/'data/local_registration_plan.json';plan=read(plan_path);result=read(bundle/'result.json')
    raw=read(repo/plan['correspondences_path']);previous=read(repo/plan['previous_result_path']);inputs=read(repo/plan['inputs_path'])
    pairs={p['source_folio']:p for p in raw if p['correct_folio_pair']};pages={p['folio']:p for p in inputs['pages']}
    cases=read(bundle/'cases.json');checks=0;mismatches=[]
    def check(label,actual,expected=True):
        nonlocal checks
        checks+=1
        if isinstance(actual,np.ndarray) or isinstance(expected,np.ndarray):equal=bool(np.allclose(actual,expected,rtol=1e-9,atol=1e-6))
        elif isinstance(actual,(int,float)) and isinstance(expected,(int,float)):equal=math.isclose(actual,expected,rel_tol=1e-9,abs_tol=1e-6)
        else:equal=actual==expected
        if not equal:mismatches.append({'check':label,'actual':actual.tolist() if isinstance(actual,np.ndarray) else actual,'expected':expected.tolist() if isinstance(expected,np.ndarray) else expected})
    check('plan_hash',result['plan_sha256'],sha(plan_path))
    for p,h in [('correspondences_path','correspondences_sha256'),('previous_result_path','previous_result_sha256'),('inputs_path','inputs_sha256')]:
        check(p,sha(repo/plan[p]),plan[h])
    check('all_twenty_cases',sorted((c['folio'],c['fold']) for c in cases),sorted((f,k) for f in pages for k in range(5)))
    pools=defaultdict(list);held_coverage=defaultdict(list);opts=plan['local'];recomputed={}
    for c in cases:
        f=c['folio'];fold=c['fold'];label=f+'/'+str(fold);page_number=list(pairs).index(f)
        p=pairs[f];a=np.array([v['source'] for v in p['points']]);b=np.array([v['target'] for v in p['points']])
        width,height=pages[f]['preview_size'];colors=[]
        for x,y in a:
            col=min(7,max(0,math.floor(x/width*8)));row=min(7,max(0,math.floor(y/height*8)));colors.append((col+2*row)%5)
        held=[i for i,color in enumerate(colors) if color==fold];fit=[];excluded=[]
        for i,color in enumerate(colors):
            if color==fold:continue
            distance=min(math.hypot(*(a[i]-a[j])) for j in held)
            (excluded if distance<=plan['guard_source_pixels'] else fit).append(i)
        check(label+'/held_indices',c['held_indices'],held);check(label+'/fit_indices',c['fit_indices'],fit)
        check(label+'/guard_excluded',c['guard_excluded_indices'],excluded);held_coverage[f].extend(held)
        if 'matrix' not in c:
            check(label+'/failed_case_has_no_scores',c['conditions'],{});continue
        h=np.array(c['matrix']);inliers=c['fit_inlier_indices']
        check(label+'/inliers_subset_fit',set(inliers).issubset(fit));check(label+'/unique_inliers',len(set(inliers)),len(inliers))
        span=np.ptp(a[inliers],axis=0)/np.array(pages[f]['preview_size']);check(label+'/inlier_span',c['fit_inlier_span'],span)
        source,vectors,selected=field(a[fit],b[fit],h,opts)
        check(label+'/anchor_groups',c['local_anchor_groups'],len(source))
        check(label+'/selected_fit_indices',c['local_selected_fit_indices'],[fit[i] for i in selected])
        expected_order=np.random.default_rng(plan['seed']+1000*page_number+fold).permutation(len(source)).tolist()
        check(label+'/shuffle_order',c['shuffle_order'],expected_order)
        base=apply(a[held],h);local,support,capped=compensate(a[held],source,vectors,opts)
        shuffled,_,shuffled_capped=compensate(a[held],source,vectors[expected_order],opts)
        check(label+'/support',c['support_counts'],support);check(label+'/capped',c['capped'],capped)
        check(label+'/shuffled_capped',c['shuffled_capped'],shuffled_capped)
        for method,pred in [('global',base),('spatial_median',base+local),('shuffled_median',base+shuffled)]:
            out=c['conditions'][method];name=label+'/'+method
            check(name+'/predictions',out['predictions'],pred)
            errors=[math.hypot(*(u-v)) for u,v in zip(pred,b[held])]
            check(name+'/error_vector',np.array(out['errors']),np.array(errors));m=metrics(errors)
            for k,v in m.items():check(name+'/'+k,out['metrics'][k],v)
            check(name+'/gate',out['accepted'],gate(m,len(inliers),span));pools[(f,method)].extend(errors)
    for f,p in pairs.items():check(f+'/each_point_held_once',sorted(held_coverage[f]),list(range(len(p['points']))))
    for (f,method),errors in pools.items():
        m=metrics(errors);m['accepted_folds']=sum(c['conditions'][method]['accepted'] for c in cases if c['folio']==f)
        for k,v in m.items():check(f+'/'+method+'/pooled_'+k,result['pooled'][f][method][k],v)
        recomputed[f+'/'+method]=m
    f4r_cases=[c for c in cases if c['folio']=='f4r'];target=result['pooled']['f4r']
    cv=bool(len(f4r_cases)==5 and all(c.get('conditions',{}).get('spatial_median',{}).get('accepted',False) for c in f4r_cases)
            and target['spatial_median']['p90']<target['global']['p90'] and target['spatial_median']['p90']<target['shuffled_median']['p90'])
    check('cross_validation_decision',result['f4r_cross_validation_accepted'],cv)
    model=read(bundle/'final_model.json');grid=read(bundle/'orientation_grid.json');words=read(bundle/'word_polygons.json')
    final_valid=False
    if model is not None:
        check('final_model_requires_cv',cv)
        p=pairs['f4r'];a=np.array([v['source'] for v in p['points']]);b=np.array([v['target'] for v in p['points']]);h=np.array(model['global_matrix'])
        source,vectors,_=field(a,b,h,opts)
        check('final_anchor_sources',model['anchor_sources'],source);check('final_anchor_vectors',model['anchor_vectors'],vectors)
        calibration=np.array(previous['calibrations']['f4r']['matrix']);check('final_calibration',model['calibration_matrix'],calibration)
        def warp(q):return apply(q,h)+compensate(q,source,vectors,opts)[0]
        width,height=pages['f4r']['preview_size']
        grid_source=np.array([[x,y] for y in np.linspace(0,height,25) for x in np.linspace(0,width,17)])
        expected_grid=warp(grid_source);check('grid_source',grid['source'],grid_source);check('grid_mapping',grid['mapped'],expected_grid)
        points=expected_grid.reshape(25,17,2);areas=[]
        def cross(u,v):return u[0]*v[1]-u[1]*v[0]
        for y in range(24):
            for x in range(16):
                a,b,c,d=points[y,x],points[y,x+1],points[y+1,x+1],points[y+1,x]
                areas.extend([cross(b-a,c-a),cross(c-a,d-a)])
        orientation=min(areas)>0;check('grid_orientation',grid['positive_orientation'],bool(orientation))
        check('grid_minimum_area',grid['minimum_double_triangle_area'],float(min(areas)))
        with Image.open(repo/pages['f4r']['yale_path']) as im:size=im.size
        check('frozen_yale_image',sha(repo/pages['f4r']['yale_path']),pages['f4r']['yale_sha256'])
        source_words=pages['f4r']['words'];check('word_count',len(words),len(source_words));all_valid=True
        for actual,w in zip(words,source_words):
            label='word/'+str(w['index']);x,y,ww,hh=w['xml_bbox']
            expected=warp(apply([[x,y],[x+ww,y],[x+ww,y+hh],[x,y+hh]],calibration))
            for k,v in {'folio':'f4r','index':w['index'],'eva':w['eva'],'source_xml_bbox':w['xml_bbox']}.items():check(label+'/'+k,actual[k],v)
            flags=[]
            if min(cross(expected[(k+1)%4]-expected[k],expected[(k+2)%4]-expected[(k+1)%4]) for k in range(4))<=0:flags.append('nonpositive_or_nonconvex_polygon')
            if any(u<0 or v<0 or u>size[0] or v>size[1] for u,v in expected):flags.append('outside_yale_frame')
            all_valid=all_valid and not flags
            if result['f4r_final_geometry_accepted']:
                check(label+'/polygon',actual['yale_polygon'],expected);check(label+'/flags',actual['flags'],flags)
        final_valid=bool(cv and orientation and len(words)==64 and all_valid)
        check('model_acceptance',model['registration_accepted'],final_valid)
    else:
        check('no_final_model_no_candidates',result['new_candidate_word_polygons'],0)
    check('final_acceptance',result['f4r_final_geometry_accepted'],final_valid)
    check('new_candidate_count',result['new_candidate_word_polygons'],64 if final_valid else 0)
    check('previous_candidates_flag',result['previous_280_candidates_modified'],False)
    return {'status':'PASS_EXPORTED_SPATIAL_GEOMETRY_AUDIT' if not mismatches else 'FAIL','checks':checks,'mismatches':mismatches,
            'recomputed':recomputed,'f4r_final_geometry_accepted':final_valid,
            'scope':'Frozen data, all guarded partitions, every held-out prediction/error, shuffled controls, gates, final anchors, coarse grid and word geometry recomputed. Does not rerun OpenCV homography estimation or validate the detector correspondences or source readings independently.',
            'translation':'NOT_RUN'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=audit(args.bundle,args.repo);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=True))
    if result['mismatches']:raise SystemExit(1)
