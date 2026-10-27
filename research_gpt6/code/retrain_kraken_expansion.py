#!/usr/bin/env python3
"""Compare continuation and expanded examples from one preserved EVA model."""
import argparse
from collections import Counter
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import time
import traceback
import numpy as np
from PIL import Image
from kraken_eva_word_training import sha,save,recognize,tensor_manifest
from kraken_row_tools import image_features,nearest_text,levenshtein


def select_rows(rows,variant):
    if variant not in ['continuation_200','expanded_200']:raise ValueError('Unknown variant')
    allowed={'original_train'} if variant=='continuation_200' else {'original_train','additional_train'}
    train=[r for r in rows if r['role'] in allowed];evaluation=[r for r in rows if r['role'] in {'historical_development','reserved'}]
    if len({r['id'] for r in rows})!=len(rows):raise ValueError('Duplicate dataset IDs')
    if len([r for r in rows if r['role']=='original_train'])!=197:raise ValueError('Changed original training set')
    if len([r for r in rows if r['role']=='historical_development'])!=147:raise ValueError('Changed historical development set')
    if {r['folio'] for r in evaluation}!={'f4r','f4v','f7r','f7v'}:raise ValueError('Changed evaluation folios')
    train_leaves={r['folio'][:-1] for r in train};eval_leaves={r['folio'][:-1] for r in evaluation}
    if train_leaves&eval_leaves:raise ValueError('Physical leaf leakage')
    expected={'f3'} if variant=='continuation_200' else {'f3','f5','f6'}
    if train_leaves!=expected:raise ValueError('Training folios changed')
    return train,evaluation


def metrics(rows):
    if not rows:return None
    n=sum(len(r['reference']) for r in rows);multi=[r for r in rows if len(r['reference'])>=2]
    return {m:{'errors':sum(r['errors'][m] for r in rows),'reference_characters':n,'cer':sum(r['errors'][m] for r in rows)/n,
               'exact_words':sum(r['reference']==r['predictions'][m] for r in rows),'words':len(rows),
               'exact_word_fraction':sum(r['reference']==r['predictions'][m] for r in rows)/len(rows),
               'multicharacter_exact_words':sum(r['reference']==r['predictions'][m] for r in multi),'multicharacter_words':len(multi)}
            for m in rows[0]['predictions']}


def run(a):
    import torch
    from kraken.models import load_models
    from kraken.lib.models import load_any
    from kraken.lib.util import parse_gt_path
    plan=json.loads(a.plan.read_text());execution=json.loads(a.execution.read_text());a.out.mkdir(parents=True,exist_ok=True)
    if sha(a.plan)!=execution['protocol_plan_sha256']:raise ValueError('Changed protocol')
    if sha(a.repo/plan['warmstart_path'])!=plan['warmstart_sha256']:raise ValueError('Changed initial model')
    for name,digest in execution['prepared_hashes'].items():
        if sha(a.prepared/name)!=digest:raise ValueError('Frozen geometry output changed: '+name)
    geometry=json.loads((a.prepared/'geometry_result.json').read_text())
    if geometry['status']!='FOLLOWUP_PREPARED_EXPLORATORY_AFTER_PRIMARY_FAILURE' or len(geometry['pages'])!=5 or not all(p['accepted'] for p in geometry['pages']):raise ValueError('Exploratory geometry subset not accepted')
    rows=json.loads((a.prepared/'dataset.json').read_text())
    for r in rows:
        r['path']=str((a.prepared/'crops'/Path(r['path']).name).resolve());r['mask_path']=str((a.prepared/'crops'/Path(r['mask_path']).name).resolve())
        if sha(r['path'])!=r['image_sha256'] or sha(r['mask_path'])!=r['mask_sha256']:raise ValueError('Crop bytes changed')
        if parse_gt_path(r['path']).text!=r['reference']:raise ValueError('Paired reference parser mismatch')
    train,evaluation=select_rows(rows,a.variant);save(a.out/'dataset.json',rows);save(a.out/'training_ids.json',[r['id'] for r in train])
    torch.set_num_threads(2);torch.manual_seed(plan['seed']);torch.use_deterministic_algorithms(True)
    initial=(a.repo/plan['warmstart_path']).resolve();converted=(a.out/'warmstart.safetensors').resolve()
    cp=subprocess.run(['ketos','convert','--weights-format','safetensors','-o',str(converted),str(initial)],capture_output=True,text=True,timeout=180)
    (a.out/'warmstart_conversion.log').write_text(cp.stdout+'\n'+cp.stderr)
    if cp.returncode:raise RuntimeError('Warm-start conversion failed')
    original_models=load_models(initial,tasks=['recognition']);converted_models=load_models(converted,tasks=['recognition'])
    if len(original_models)!=1 or len(converted_models)!=1:raise ValueError('Expected one source recognizer')
    x,y=original_models[0],converted_models[0];source_state=tensor_manifest(x);converted_state=tensor_manifest(y)
    proof={'source_sha256':sha(initial),'converted_sha256':sha(converted),'source_tensors':source_state,'converted_tensors':converted_state,'tensor_states_equal':source_state==converted_state,'codec_equal':x.codec.c2l==y.codec.c2l}
    save(a.out/'warmstart_equivalence.json',proof)
    if not proof['tensor_states_equal'] or not proof['codec_equal']:raise ValueError('Source tensors or codec changed during conversion')
    source_alphabet=set(''.join(x.codec.c2l));del x,y,original_models,converted_models
    frozen=load_any(str(initial),train=False,device='cpu');initial_predictions=recognize(frozen,evaluation);del frozen
    save(a.out/'frozen_initial_predictions.json',[{'id':r['id'],'reference':r['reference'],'prediction':p} for r,p in zip(evaluation,initial_predictions)])
    training=(a.out/'training').resolve();training.mkdir(exist_ok=True);lst=training/'train.lst';lst.write_text('\n'.join(r['path'] for r in train)+'\n')
    config={'device':'cpu','precision':'32-true','num_workers':0,'num_threads':2,'seed':plan['seed'],'deterministic':True,
            'train':{'training_data':[str(lst)],'evaluation_data':[str(lst)],'checkpoint_path':str(training/'checkpoints'),
                     'format_type':'path','quit':'fixed','epochs':plan['epochs'],'min_epochs':plan['epochs'],'freq':plan['epochs'],
                     'batch_size':plan['batch_size'],'lrate':plan['learning_rate'],'schedule':'constant','augment':False,
                     'bidi_reordering':False,'normalization':'NFC','normalize_whitespace':False,'padding':16,'weights_format':'safetensors','freeze_backbone':0}}
    save(training/'training_config.json',config);command=['ketos','--config',str(training/'training_config.json'),'train','--load',str(converted),'--resize','add'];save(training/'command.json',command)
    started=time.perf_counter()
    with (training/'training.log').open('w') as log:cp=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=2400)
    if cp.returncode:raise RuntimeError('Retraining failed; see training log')
    candidates=[(int(m.group(1)),p) for p in (training/'checkpoints').glob('checkpoint_*.ckpt') if (m:=re.search(r'checkpoint_(\d+)-',p.name))]
    if not candidates:raise ValueError('No checkpoint')
    epoch,checkpoint=max(candidates,key=lambda x:x[0])
    if epoch!=199:raise ValueError('Fixed final epoch not available')
    ckpt=torch.load(checkpoint,map_location='cpu',weights_only=False);global_steps=int(ckpt['global_step']);checkpoint_epoch=int(ckpt['epoch']);del ckpt
    model=a.out/'final_epoch.mlmodel';cp=subprocess.run(['ketos','convert','--weights-format','coreml','-o',str(model),str(checkpoint)],capture_output=True,text=True,timeout=180)
    (a.out/'final_conversion.log').write_text(cp.stdout+'\n'+cp.stderr)
    if cp.returncode:raise RuntimeError('Final model conversion failed')
    net=load_any(str(model),train=False,device='cpu');codec=net.codec.c2l;save(a.out/'trained_codec.json',codec)
    alphabet=set(''.join(r['reference'] for r in train))
    if not (alphabet|source_alphabet)<=set(''.join(codec)) or any(c<'a' or c>'z' for c in ''.join(codec)):raise ValueError('Unexpected final EVA alphabet')
    final_predictions=recognize(net,evaluation);training_predictions=recognize(net,train)
    features=[]
    for r in train:
        with Image.open(r['path']) as im:f=image_features(im)
        features.append({'id':r['id'],'text':r['reference'],'features':f})
    word=Counter(r['reference'] for r in train).most_common(1)[0][0];char=Counter(''.join(r['reference'] for r in train)).most_common(1)[0][0];length=int(np.median([len(r['reference']) for r in train]));vocabulary={r['reference'] for r in train};scored=[]
    for r,initial_prediction,final_prediction in zip(evaluation,initial_predictions,final_predictions):
        with Image.open(r['path']) as im:nearest,near_id=nearest_text(im,features)
        predictions={'kraken':final_prediction,'frozen_initial':initial_prediction,'nearest_image':nearest,'mode_word':word,'repeat_character':char*length,'empty':''}
        scored.append({'id':r['id'],'folio':r['folio'],'role':r['role'],'reference':r['reference'],'predictions':predictions,'errors':{m:levenshtein(r['reference'],p) for m,p in predictions.items()},'nearest_train_id':near_id,'reference_seen_in_training':r['reference'] in vocabulary})
    train_outputs=[{'id':r['id'],'reference':r['reference'],'prediction':p,'errors':levenshtein(r['reference'],p)} for r,p in zip(train,training_predictions)]
    prior=json.loads((a.repo/'results/kraken_eva_words/runs/aligned_200/result.json').read_text());prior_predictions={r['id']:r['predictions']['kraken'] for r in prior['rows']}
    replays=[{'id':r['id'],'old':prior_predictions[r['id']],'current_frozen':r['predictions']['frozen_initial']} for r in scored if r['role']=='historical_development' and r['predictions']['frozen_initial']!=prior_predictions[r['id']]]
    result={'date':plan['date'],'status':'EXECUTED_EXPLORATORY_EXPANSION_AFTER_PRIMARY_GEOMETRY_FAILURE_NOT_TRANSLATION','design_status':plan['design_status'],'primary_geometry_status':geometry['primary_geometry_status'],'variant':a.variant,'epochs':200,'final_epoch_zero_based':epoch,'checkpoint_epoch':checkpoint_epoch,'optimizer_steps':global_steps,
            'training_words':len(train),'training_reference_characters':sum(len(r['reference']) for r in train),'training_fit_cer':sum(r['errors'] for r in train_outputs)/sum(len(r['reference']) for r in train),'training_exact_words':sum(r['reference']==r['prediction'] for r in train_outputs),
            'metrics':{role:metrics([r for r in scored if r['role']==role]) for role in ['historical_development','reserved']},
            'by_folio':{f:metrics([r for r in scored if r['folio']==f]) for f in sorted({r['folio'] for r in scored})},
            'lexical_strata':{role:{name:metrics([r for r in scored if r['role']==role and r['reference_seen_in_training']==seen]) for name,seen in [('seen',True),('unseen',False)]} for role in ['historical_development','reserved']},
            'rows':scored,'training_predictions':train_outputs,'frozen_initial_historical_replay_differences':replays,
            'evaluation_characters_absent_from_training':{role:dict(Counter(c for r in scored if r['role']==role for c in r['reference'] if c not in alphabet)) for role in ['historical_development','reserved']},
            'plan_sha256':sha(a.plan),'execution_metadata_sha256':sha(a.execution),'prepared_dataset_sha256':sha(a.prepared/'dataset.json'),'geometry_result_sha256':sha(a.prepared/'geometry_result.json'),
            'warmstart_source_sha256':sha(initial),'model_sha256':sha(model),'checkpoint_sha256':sha(checkpoint),'training_log_sha256':sha(training/'training.log'),
            'seconds_training_conversion_evaluation':time.perf_counter()-started,'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA'),
            'environment':{k:importlib.metadata.version(k) for k in ['torch','torchvision','kraken','pillow','numpy','scipy','lightning']},
            'expert_review':'NOT_REVIEWED','translation':'NOT_RUN','scope':'Fixed provisional EVA references; historical leaf4 and reserved leaf7 scored separately; one seed, no independent palaeographic validation.'}
    save(a.out/'result.json',result);print('EXPANSION_TRAINING_RESULT='+json.dumps({k:v for k,v in result.items() if k not in ['rows','training_predictions','by_folio','lexical_strata','environment']},ensure_ascii=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--execution',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--variant',choices=['continuation_200','expanded_200'],required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    try:run(a)
    except Exception as e:save(a.out/'failure.json',{'error':str(e),'traceback':traceback.format_exc(),'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA')});raise
