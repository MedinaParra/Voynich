#!/usr/bin/env python3
"""Independent checks of primary failure, exploratory inputs and OCR outputs.

No OpenCV estimation, neural inference, palaeographic review or translation.
"""
import argparse
from collections import Counter
import hashlib
import gzip
import json
import math
from pathlib import Path
import statistics
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from audit_local_residual_registration import field,compensate,metrics as geometric_metrics,gate
from audit_voynichese_registration import apply
from audit_kraken_stage2 import edit,feature


def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def restore_inputs(primary,prepared,repo,runs=None):
    """Restore lossless JSON archives and reproducible PNG/mask/text inputs."""
    for root in [primary,prepared]+([runs] if runs is not None else []):
        for p in root.rglob('*.json.gz'):
            target=p.with_suffix('');data=gzip.decompress(p.read_bytes())
            if target.exists() and target.read_bytes()!=data:raise ValueError('Restored JSON conflicts with existing bytes')
            if not target.exists():target.write_bytes(data)
    photos={}
    for r in read(prepared/'dataset.json'):
        source=repo/r['source_image_path']
        if source not in photos:
            if sha(source)!=r['source_image_sha256']:raise ValueError('Changed source image')
            photos[source]=Image.open(source).convert('RGB')
        x0,y0,x1,y1=r['bounds'];size=(x1-x0,y1-y0);mask=Image.new('L',size,0)
        ImageDraw.Draw(mask).polygon([(round(x-x0),round(y-y0)) for x,y in r['polygon']],fill=255);mask=mask.filter(ImageFilter.MaxFilter(9))
        crop=Image.composite(photos[source].crop(r['bounds']),Image.new('RGB',size,'white'),mask);path=prepared/'crops'/Path(r['path']).name;mp=prepared/'crops'/Path(r['mask_path']).name;path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists():crop.save(path)
        if not mp.exists():mask.save(mp)
        if sha(path)!=r['image_sha256'] or sha(mp)!=r['mask_sha256']:raise ValueError('Restored PNG differs from original bytes; use Pillow12.3.0')
        gt=path.with_suffix('.gt.txt')
        if not gt.exists():gt.write_text(r['reference'])


def audit(primary,prepared,repo,runs=None):
    checks=0;failures=[]
    def check(label,a,b=True):
        nonlocal checks
        checks+=1
        if isinstance(a,np.ndarray) or isinstance(b,np.ndarray):equal=np.asarray(a).shape==np.asarray(b).shape and bool(np.allclose(a,b,rtol=1e-9,atol=1e-6))
        elif isinstance(a,(float,int)) and isinstance(b,(float,int)):equal=math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-6)
        else:equal=a==b
        if not equal:failures.append({'check':label,'actual':json.loads(json.dumps(a,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else repr(x))),'expected':json.loads(json.dumps(b,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else repr(x)))})
    original_plan=read(repo/'data/kraken_expansion_plan.json');followup=read(repo/'data/kraken_expansion_followup_plan.json');execution=read(repo/'data/kraken_expansion_execution.json');inputs=read(repo/'data/kraken_expansion_inputs.json');pages={p['folio']:p for p in inputs['pages']}
    result=read(primary/'geometry_result.json');raw=read(primary/'geometry_correspondences.json');cases=read(primary/'geometry_cases.json');pairs={p['folio']:p for p in raw};models=read(primary/'geometry_models.json');grids=read(primary/'geometry_grids.json');words=read(primary/'new_word_polygons.json');opts=original_plan['local']
    check('original_plan_hash',result['plan_sha256'],sha(repo/'data/kraken_expansion_plan.json'));check('original_inputs_hash',result['inputs_sha256'],sha(repo/'data/kraken_expansion_inputs.json'));check('all_thirty_cases',sorted((c['folio'],c['fold']) for c in cases),sorted((f,k) for f in pages for k in range(5)))
    decisions={};coverage={f:[] for f in pages}
    for case in cases:
        f=case['folio'];fold=case['fold'];label=f+'/'+str(fold);width,height=pages[f]['preview_size'];points=np.array([p['source'] for p in pairs[f]['points']]);targets=np.array([p['target'] for p in pairs[f]['points']]);colors=[]
        for x,y in points:colors.append((min(7,max(0,math.floor(x/width*8)))+2*min(7,max(0,math.floor(y/height*8))))%5)
        held=[i for i,c in enumerate(colors) if c==fold];fit=[];excluded=[]
        for i,c in enumerate(colors):
            if c==fold:continue
            distance=min(math.hypot(*(points[i]-points[j])) for j in held)
            (excluded if distance<=3 else fit).append(i)
        check(label+'/held',case['held_indices'],held);check(label+'/fit',case['fit_indices'],fit);check(label+'/guard',case['guard_excluded_indices'],excluded);coverage[f].extend(held)
        h=np.array(case['matrix']);inliers=case['fit_inlier_indices'];span=np.ptp(points[inliers],axis=0)/pages[f]['preview_size'];check(label+'/inliers_only_fit',set(inliers)<=set(fit));check(label+'/span',case['fit_inlier_span'],span)
        source,vectors,selected=field(points[fit],targets[fit],h,opts);check(label+'/anchors',case['anchor_sources'],source);check(label+'/vectors',case['anchor_vectors'],vectors);check(label+'/selected',case['local_selected_fit_indices'],[fit[i] for i in selected])
        order=np.random.default_rng(original_plan['seed']+1000*list(pages).index(f)+fold).permutation(len(source));check(label+'/permutation',case['shuffle_order'],order.tolist());base=apply(points[held],h);local,support,capped=compensate(points[held],source,vectors,opts);null,_,_=compensate(points[held],source,vectors[order],opts);check(label+'/support',case['support_counts'],support);check(label+'/cap',case['capped'],capped)
        for method,pred in [('global',base),('spatial_median',base+local),('shuffled_median',base+null)]:
            actual=case['conditions'][method];errors=[math.hypot(*(p-t)) for p,t in zip(pred,targets[held])];m=geometric_metrics(errors);passed=gate(m,len(inliers),span)
            check(label+'/'+method+'/prediction',actual['predictions'],pred);check(label+'/'+method+'/errors',np.array(actual['errors']),np.array(errors))
            for key,v in m.items():check(label+'/'+method+'/'+key,actual['metrics'][key],v)
            check(label+'/'+method+'/gate',actual['accepted'],passed)
            if method=='spatial_median':decisions[(f,fold)]=passed
    for f in pages:check(f+'/held_once',sorted(coverage[f]),list(range(len(pairs[f]['points']))))
    check('local_fold_passes',sum(decisions.values()),29);check('f5r_rejected_fold0',decisions[('f5r',0)],False)
    check('primary_original_status',result['status'],'FAIL_PRESELECTED_PAGE_GEOMETRY_NO_EXPANSION_TRAINING')
    new_by={(w['folio'],w['index']):w for w in words}
    for f,model in models.items():
        p=pairs[f];points=np.array([r['source'] for r in p['points']]);targets=np.array([r['target'] for r in p['points']]);h=np.array(model['global_matrix']);source,vectors,_=field(points,targets,h,opts)
        check(f+'/final_source',model['anchor_sources'],source);check(f+'/final_vectors',model['anchor_vectors'],vectors)
        def warp(q):return apply(q,h)+compensate(np.asarray(q),source,vectors,opts)[0]
        g=grids[f];mapped=warp(g['source']);check(f+'/grid_points',g['mapped'],mapped);grid=mapped.reshape(25,17,2);areas=[]
        def cross(a,b):return a[0]*b[1]-a[1]*b[0]
        for y in range(24):
            for x in range(16):
                a,b,c,d=grid[y,x],grid[y,x+1],grid[y+1,x+1],grid[y+1,x];areas.extend([cross(b-a,c-a),cross(c-a,d-a)])
        check(f+'/positive_grid',g['positive_orientation'],bool(min(areas)>0));check(f+'/grid_area',g['minimum_double_triangle_area'],float(min(areas)))
        for w in pages[f]['words']:
            actual=new_by[(f,w['index'])];x,y,width,height=w['preview_bbox'];check(f+'/word_text/'+str(w['index']),actual['eva'],w['eva']);check(f+'/preview_box/'+str(w['index']),actual['source_preview_bbox'],w['preview_bbox'])
            if not actual['flags']:check(f+'/word_polygon/'+str(w['index']),actual['yale_polygon'],warp([[x,y],[x+width,y],[x+width,y+height],[x,y+height]]))
    for name,digest in execution['prepared_hashes'].items():check('prepared_hash/'+name,sha(prepared/name),digest)
    ds=read(prepared/'dataset.json');by={r['id']:r for r in ds};old={r['id']:r for r in read(repo/followup['previous_dataset_path'])};check('rows',len(ds),724);check('unique_rows',len(by),724);check('roles',Counter(r['role'] for r in ds),Counter({'original_train':197,'historical_development':147,'additional_train':245,'reserved':135}));check('excluded_f5r',not any(r['folio']=='f5r' for r in ds))
    photos={}
    for r in ds:
        label='sample/'+r['id'];path=prepared/'crops'/Path(r['path']).name;mp=prepared/'crops'/Path(r['mask_path']).name
        check(label+'/image',sha(path),r['image_sha256']);check(label+'/mask',sha(mp),r['mask_sha256']);check(label+'/textfile',path.with_suffix('.gt.txt').read_text(),r['reference'])
        source=repo/r['source_image_path']
        if source not in photos:check(label+'/source',sha(source),r['source_image_sha256']);photos[source]=Image.open(source).convert('RGB')
        with Image.open(path) as im:actual=np.array(im.convert('RGB'))
        with Image.open(mp) as im:mask=np.array(im.convert('L'))
        original=np.array(photos[source].crop(r['bounds']));check(label+'/source_pixels',bool(np.array_equal(actual[mask==255],original[mask==255])));check(label+'/white_outside',bool(np.all(actual[mask==0]==255)))
        if r['id'] in old:
            previous=old[r['id']]
            for key in ['reference','image_sha256','mask_sha256','bounds','polygon']:check(label+'/old_'+key,r[key],previous[key])
        else:
            word=new_by[(r['folio'],r['index'])];check(label+'/new_reference',r['reference'],word['eva']);check(label+'/new_polygon',r['polygon'],word['yale_polygon']);check(label+'/new_flags',word['flags'],[])
    def score(rows):
        if not rows:return None
        n=sum(len(r['reference']) for r in rows);multi=[r for r in rows if len(r['reference'])>1]
        return {m:{'errors':sum(edit(r['reference'],r['predictions'][m]) for r in rows),'reference_characters':n,'cer':sum(edit(r['reference'],r['predictions'][m]) for r in rows)/n,'exact_words':sum(r['reference']==r['predictions'][m] for r in rows),'words':len(rows),'exact_word_fraction':sum(r['reference']==r['predictions'][m] for r in rows)/len(rows),'multicharacter_exact_words':sum(r['reference']==r['predictions'][m] for r in multi),'multicharacter_words':len(multi)} for m in rows[0]['predictions']}
    summaries={};outputs={};paired_initial_differences=[]
    if runs is not None:
        for variant in ['continuation_200','expanded_200']:
            bundle=runs/variant;r=read(bundle/'result.json');outputs[variant]=r;train=[x for x in ds if x['role']=='original_train' or (variant=='expanded_200' and x['role']=='additional_train')];evaluation=[x for x in ds if x['role'] in ['historical_development','reserved']];name=variant
            check(name+'/training_ids',read(bundle/'training_ids.json'),[x['id'] for x in train]);check(name+'/training_rows',r['training_words'],len(train));check(name+'/physical_leaves_disjoint',not ({x['folio'][:-1] for x in train}&{x['folio'][:-1] for x in evaluation}));check(name+'/plan_hash',r['plan_sha256'],sha(repo/'data/kraken_expansion_followup_plan.json'));check(name+'/execution_hash',r['execution_metadata_sha256'],sha(repo/'data/kraken_expansion_execution.json'));check(name+'/prepared_dataset',r['prepared_dataset_sha256'],sha(prepared/'dataset.json'))
            check(name+'/design',r['design_status'],'EXPLORATORY_GEOMETRY_FILTERED_AFTER_PRIMARY_GATE_FAILURE');check(name+'/primary_failure',r['primary_geometry_status'],result['status']);check(name+'/epochs',r['epochs'],200);check(name+'/checkpoint_index',r['final_epoch_zero_based'],199);check(name+'/checkpoint_epoch',r['checkpoint_epoch'],199);check(name+'/optimizer_steps',r['optimizer_steps'],200*math.ceil(len(train)/16))
            config=read(bundle/'training/training_config.json');command=read(bundle/'training/command.json');check(name+'/train_only_monitor',config['train']['training_data'],config['train']['evaluation_data']);check(name+'/manifest_only_training',[Path(x).stem for x in (bundle/'training/train.lst').read_text().splitlines()],[x['id'] for x in train]);check(name+'/load_flag','--load' in command);check(name+'/resize_add',command[-2:],['--resize','add'])
            for k,v in [('epochs',200),('min_epochs',200),('freq',200),('batch_size',16),('lrate',.001),('schedule','constant'),('augment',False),('freeze_backbone',0)]:check(name+'/config/'+k,config['train'][k],v)
            proof=read(bundle/'warmstart_equivalence.json');check(name+'/source_weights',proof['source_tensors'],proof['converted_tensors']);check(name+'/tensor_count',len(proof['source_tensors']),14);check(name+'/codec_equal',proof['codec_equal']);check(name+'/source_hash',proof['source_sha256'],followup['warmstart_sha256']);check(name+'/converted_hash',proof['converted_sha256'],sha(bundle/'warmstart.safetensors'));check(name+'/model_hash',r['model_sha256'],sha(bundle/'final_epoch.mlmodel'));check(name+'/log_hash',r['training_log_sha256'],sha(bundle/'training/training.log'));check(name+'/epochs_finished','max_epochs=200` reached' in (bundle/'training/training.log').read_text())
            cps=list((bundle/'training/checkpoints').glob('checkpoint_199-*.ckpt'));check(name+'/one_final_checkpoint',len(cps),1)
            if len(cps)==1:check(name+'/checkpoint_hash',r['checkpoint_sha256'],sha(cps[0]))
            train_data=read(bundle/'dataset.json');check(name+'/all_dataset_ids',[x['id'] for x in train_data],[x['id'] for x in ds])
            for x,y in zip(train_data,ds):
                for k in ['id','folio','reference','role','image_sha256','mask_sha256']:check(name+'/input/'+x['id']+'/'+k,x[k],y[k])
            codec=read(bundle/'trained_codec.json');alphabet=set(''.join(x['reference'] for x in train));check(name+'/EVA_codec',alphabet<=set(''.join(codec)));check(name+'/only_lowercase',all('a'<=c<='z' for c in ''.join(codec)))
            tf=[feature(prepared/'crops'/Path(x['path']).name) for x in train];vectors=np.array([f for f,a in tf]);aspects=np.array([a for f,a in tf]);vocabulary={x['reference'] for x in train};word=Counter(x['reference'] for x in train).most_common(1)[0][0];char=Counter(''.join(x['reference'] for x in train)).most_common(1)[0][0];length=int(statistics.median(len(x['reference']) for x in train));scored=r['rows'];check(name+'/evaluation_ids',[x['id'] for x in scored],[x['id'] for x in evaluation])
            initial=read(bundle/'frozen_initial_predictions.json');check(name+'/initial_saved',[{'id':x['id'],'reference':x['reference'],'prediction':x['predictions']['frozen_initial']} for x in scored],initial)
            for x in scored:
                label=name+'/output/'+x['id'];target=by[x['id']];check(label+'/reference',x['reference'],target['reference']);check(label+'/role',x['role'],target['role']);f,a=feature(prepared/'crops'/Path(target['path']).name);delta=vectors-np.array(f);dist=np.einsum('ij,ij->i',delta,delta)/len(f)+.05*(aspects-a)**2;nearest=train[int(np.argmin(dist))];check(label+'/nearest_id',x['nearest_train_id'],nearest['id'])
                for m,value in [('nearest_image',nearest['reference']),('mode_word',word),('repeat_character',char*length),('empty','')]:check(label+'/'+m,x['predictions'][m],value)
                check(label+'/vocabulary_seen',x['reference_seen_in_training'],x['reference'] in vocabulary)
                for m,p in x['predictions'].items():check(label+'/edit/'+m,x['errors'][m],edit(x['reference'],p))
            for role in ['historical_development','reserved']:
                selected=[x for x in scored if x['role']==role];check(name+'/summary/'+role,r['metrics'][role],score(selected))
                for key,seen in [('seen',True),('unseen',False)]:check(name+'/stratum/'+role+'/'+key,r['lexical_strata'][role][key],score([x for x in selected if x['reference_seen_in_training']==seen]))
                unseen=Counter(c for x in selected for c in x['reference'] if c not in alphabet);check(name+'/unseen_characters/'+role,r['evaluation_characters_absent_from_training'][role],dict(unseen))
            for f in ['f4r','f4v','f7r','f7v']:check(name+'/folio/'+f,r['by_folio'][f],score([x for x in scored if x['folio']==f]))
            t=r['training_predictions'];check(name+'/training_prediction_ids',[x['id'] for x in t],[x['id'] for x in train]);total=0
            for x in t:check(name+'/train_reference/'+x['id'],x['reference'],by[x['id']]['reference']);distance=edit(x['reference'],x['prediction']);check(name+'/train_edit/'+x['id'],x['errors'],distance);total+=distance
            n=sum(len(x['reference']) for x in train);check(name+'/train_characters',r['training_reference_characters'],n);check(name+'/fit',r['training_fit_cer'],total/n);check(name+'/train_exact',r['training_exact_words'],sum(x['reference']==x['prediction'] for x in t));check(name+'/translation',r['translation'],'NOT_RUN')
            previous={x['id']:x['predictions']['kraken'] for x in read(repo/'results/kraken_eva_words/runs/aligned_200/result.json')['rows']};diff=[{'id':x['id'],'old':previous[x['id']],'current_frozen':x['predictions']['frozen_initial']} for x in scored if x['role']=='historical_development' and x['predictions']['frozen_initial']!=previous[x['id']]];check(name+'/initial_replay_differences',r['frozen_initial_historical_replay_differences'],diff)
            summaries[variant]={'metrics':r['metrics'],'training_fit_cer':r['training_fit_cer'],'optimizer_steps':r['optimizer_steps'],'seconds':r['seconds_training_conversion_evaluation'],'result_sha256':sha(bundle/'result.json')}
        for x,y in zip(outputs['continuation_200']['rows'],outputs['expanded_200']['rows']):
            check('paired_evaluation_id/'+x['id'],x['id'],y['id'])
            if x['predictions']['frozen_initial']!=y['predictions']['frozen_initial']:paired_initial_differences.append({'id':x['id'],'reference':x['reference'],'continuation_job_initial':x['predictions']['frozen_initial'],'expanded_job_initial':y['predictions']['frozen_initial']})
        check('paired_execution',outputs['continuation_200']['execution_commit'],outputs['expanded_200']['execution_commit'])
    return {'status':'PASS' if not failures else 'FAIL','checks':checks,'mismatches':failures,'primary_geometry_status':result['status'],'spatial_folds_passed':sum(decisions.values()),'spatial_folds_total':30,'followup_design':followup['design_status'],'followup_counts':dict(Counter(x['role'] for x in ds)),'training_results':summaries,'paired_initial_prediction_differences':paired_initial_differences,'scope':'Independent numerical replay of exported geometry and recognition arithmetic; source pixels and frozen old pairs checked. Inter-run inference variation is recorded separately from arithmetic mismatches. No new homography estimation, neural inference, expert reading or semantic validation.','translation':'NOT_RUN'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--primary',type=Path,required=True);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--runs',type=Path);p.add_argument('--restore-inputs',action='store_true');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.restore_inputs:restore_inputs(a.primary,a.prepared,a.repo,a.runs)
    r=audit(a.primary,a.prepared,a.repo,a.runs);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','checks','mismatches','primary_geometry_status']}));raise SystemExit(r['status']!='PASS')
