#!/usr/bin/env python3
"""Matched head-reset training and same-process reversible EVA evaluation."""
import argparse
from collections import Counter
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import time
import traceback
from eva_unit_tools import read,sha,save,encode,expand,restore_and_load,slices,PRIVATE
from kraken_eva_word_training import recognize,tensor_manifest
from kraken_row_tools import levenshtein


def environment():
    return {p:importlib.metadata.version(p) for p in ['torch','torchvision','kraken','pillow','numpy','scipy','lightning']}


def train(a):
    import torch
    from kraken.models import load_models
    from kraken.models.writers import write_safetensors
    from kraken.lib.codec import PytorchCodec
    from kraken.lib.models import load_any
    from kraken.lib.util import parse_gt_path
    plan=read(a.plan);source=a.repo/plan['source_model_path']
    if sha(source)!=plan['source_model_sha256']:raise ValueError('Source weights changed')
    rows,training,evaluation=restore_and_load(a.repo,plan)
    for r in rows:
        if expand(encode(r['reference'],a.variant),a.variant)!=r['reference']:raise ValueError('Unit mapping is not reversible')
    save(a.out/'source_dataset.json',read(a.repo/plan['prepared_dataset_path']))
    labels=[];images=(a.out/'training_images').resolve();images.mkdir(exist_ok=True)
    for r in training:
        dest=images/(r['id']+'.png');shutil.copy2(r['path'],dest);text=encode(r['reference'],a.variant);gt=dest.with_suffix('.gt.txt');gt.write_text(text)
        if sha(dest)!=r['image_sha256'] or parse_gt_path(str(dest)).text!=text:raise ValueError('Real Kraken paired input mismatch')
        labels.append({'id':r['id'],'folio':r['folio'],'reference':r['reference'],'encoded_text':text,'path':str(dest),'image_sha256':sha(dest),'label_sha256':sha(gt)})
    save(a.out/'training_labels.json',labels)
    alphabet=sorted(set(''.join(r['encoded_text'] for r in labels)));codec=PytorchCodec(alphabet,strict=True)
    torch.set_num_threads(2);torch.manual_seed(plan['seed']);torch.use_deterministic_algorithms(True)
    models=load_models(source,tasks=['recognition'])
    if len(models)!=1:raise ValueError('Expected one source model')
    model=models[0];before=tensor_manifest(model);head_name=list(model.nn.named_children())[-1][0];head_keys=[k for k in before if k.startswith(head_name+'.')];body_keys=[k for k in before if k not in head_keys]
    if len(head_keys)!=2 or len(body_keys)!=12:raise ValueError('Unexpected source parameter partition')
    model.resize_output(codec.max_label+1);model.add_codec(codec)
    # The legacy add_codec helper stores JSON text; the safetensors writer
    # requires the structured codec object in its per-model metadata.
    model.user_metadata['codec']=codec.c2l
    torch.manual_seed(plan['seed']);model.init_weights(idx=slice(-1,None));after=tensor_manifest(model)
    proof={'source_sha256':sha(source),'output_layer':head_name,'head_keys':head_keys,'backbone_keys':body_keys,'source_tensors':before,'reset_tensors':after,
           'backbone_unchanged':all(before[k]==after[k] for k in body_keys),'head_changed':any(before[k]!=after[k] for k in head_keys),'codec':codec.c2l,'unit_alphabet_size':len(alphabet),'ctc_output_size':codec.max_label+1,'reset_seed':plan['seed']}
    save(a.out/'head_reset_proof.json',proof)
    if not proof['backbone_unchanged'] or not proof['head_changed']:raise ValueError('Matched head reset did not preserve backbone and change head')
    prepared=(a.out/'initial_reset.safetensors').resolve();write_safetensors([model],prepared);loaded=load_models(prepared,tasks=['recognition'])[0]
    proof.update(initial_reset_sha256=sha(prepared),serialized_tensors=tensor_manifest(loaded),serialization_tensors_equal=tensor_manifest(loaded)==after,serialization_codec_equal=loaded.codec.c2l==codec.c2l)
    save(a.out/'head_reset_proof.json',proof)
    if not proof['serialization_tensors_equal'] or not proof['serialization_codec_equal']:raise ValueError('Reset model serialization changed tensors or codec')
    del loaded,model,models
    root=(a.out/'training').resolve();root.mkdir(exist_ok=True);lst=root/'train.lst';lst.write_text('\n'.join(r['path'] for r in labels)+'\n')
    config={'device':'cpu','precision':'32-true','num_workers':0,'num_threads':2,'seed':plan['seed'],'deterministic':True,
            'train':{'training_data':[str(lst)],'evaluation_data':[str(lst)],'checkpoint_path':str(root/'checkpoints'),'format_type':'path','quit':'fixed','epochs':200,'min_epochs':200,'freq':200,'batch_size':16,'lrate':.001,'schedule':'constant','augment':False,'bidi_reordering':False,'normalization':'NFC','normalize_whitespace':False,'padding':16,'weights_format':'safetensors','freeze_backbone':0}}
    save(root/'training_config.json',config);command=['ketos','--config',str(root/'training_config.json'),'train','--load',str(prepared),'--resize','fail'];save(root/'command.json',command);started=time.perf_counter()
    with (root/'training.log').open('w') as log:completed=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=2400)
    if completed.returncode:raise RuntimeError('Training failed; see log')
    checkpoints=[(int(m.group(1)),p) for p in (root/'checkpoints').glob('checkpoint_*.ckpt') if (m:=re.search(r'checkpoint_(\d+)-',p.name))]
    if not checkpoints:raise ValueError('No trained checkpoint')
    epoch,checkpoint=max(checkpoints,key=lambda x:x[0])
    if epoch!=199:raise ValueError('Fixed final checkpoint unavailable')
    state=torch.load(checkpoint,weights_only=False,map_location='cpu');steps=int(state['global_step']);checkpoint_epoch=int(state['epoch']);del state
    if steps!=plan['expected_optimizer_steps'] or checkpoint_epoch!=199:raise ValueError('Unexpected actual optimizer steps or final epoch')
    final=a.out/'final_epoch.mlmodel';cp=subprocess.run(['ketos','convert','--weights-format','coreml','-o',str(final),str(checkpoint)],capture_output=True,text=True,timeout=180);(a.out/'final_conversion.log').write_text(cp.stdout+'\n'+cp.stderr)
    if cp.returncode:raise RuntimeError('Final conversion failed')
    net=load_any(str(final),train=False,device='cpu');save(a.out/'trained_codec.json',net.codec.c2l)
    if net.codec.c2l!=codec.c2l:raise ValueError('Trained output codec unexpectedly changed')
    raw=recognize(net,training);predictions=[]
    for r,p,label in zip(training,raw,labels):
        text=expand(p,a.variant);predictions.append({'id':r['id'],'reference':r['reference'],'encoded_reference':label['encoded_text'],'raw_prediction':p,'eva_prediction':text,'eva_errors':levenshtein(r['reference'],text),'unit_errors':levenshtein(label['encoded_text'],p)})
    result={'status':'EXECUTED_MATCHED_HEAD_RESET_UNIT_RETRAINING','variant':a.variant,'plan_sha256':sha(a.plan),'source_model_sha256':sha(source),'prepared_dataset_sha256':plan['prepared_dataset_sha256'],'epochs':200,'final_epoch_zero_based':epoch,'checkpoint_epoch':checkpoint_epoch,'optimizer_steps':steps,'training_words':len(training),'training_eva_characters':sum(len(r['reference']) for r in training),'training_encoded_units':sum(len(r['encoded_text']) for r in labels),'unit_alphabet_size':len(alphabet),'ctc_output_size':codec.max_label+1,
            'training_predictions':predictions,'training_eva_errors':sum(r['eva_errors'] for r in predictions),'training_exact_words':sum(r['eva_prediction']==r['reference'] for r in predictions),'training_unit_errors':sum(r['unit_errors'] for r in predictions),
            'model_sha256':sha(final),'checkpoint_sha256':sha(checkpoint),'training_log_sha256':sha(root/'training.log'),'head_reset_proof_sha256':sha(a.out/'head_reset_proof.json'),'seconds_training_conversion_training_inference':time.perf_counter()-started,'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA'),'environment':environment(),'expert_review':'NOT_REVIEWED','translation':'NOT_RUN'}
    save(a.out/'result.json',result);print('UNIT_TRAINING_RESULT='+json.dumps({k:v for k,v in result.items() if k not in ['training_predictions','environment']}),flush=True)


def evaluate(a):
    import torch
    from kraken.lib.models import load_any
    plan=read(a.plan);data,training,evaluation=restore_and_load(a.repo,plan);vocabulary={r['reference'] for r in training};source=a.repo/plan['source_model_path']
    if sha(source)!=plan['source_model_sha256']:raise ValueError('Frozen source changed')
    models={'source':source};model_hashes={'source':sha(source)}
    for variant in plan['variants']:
        root=a.runs/('eva-unit-'+variant);r=read(root/'result.json');path=root/'final_epoch.mlmodel'
        if r['variant']!=variant or r['plan_sha256']!=sha(a.plan) or r['model_sha256']!=sha(path):raise ValueError('Frozen trained model changed')
        models[variant]=path;model_hashes[variant]=sha(path)
    torch.set_num_threads(2);torch.manual_seed(plan['seed']);torch.use_deterministic_algorithms(True);passes=[];calls=[];seconds=[]
    for pass_index in range(2):
        outputs={};counts={};timings={}
        for name,path in models.items():
            net=load_any(str(path),train=False,device='cpu');count={'n':0}
            def forward(*args):count['n']+=1
            handle=net.nn.nn.register_forward_hook(forward);started=time.perf_counter();outputs[name]=recognize(net,evaluation);timings[name]=time.perf_counter()-started;handle.remove();counts[name]=count['n'];del net
        passes.append(outputs);calls.append(counts);seconds.append(timings)
    baseline=read(a.repo/plan['cached_baselines_path']);cached={r['id']:r for r in baseline['rows']};scored=[]
    for i,r in enumerate(evaluation):
        raw={name:pred[i] for name,pred in passes[0].items()};guesses={name:expand(p,'reset_letters' if name=='source' else name) for name,p in raw.items()};prior=cached[r['id']]
        if prior['reference']!=r['reference']:raise ValueError('Cached image comparator label changed')
        guesses['nearest_image']=prior['predictions']['nearest_image']
        scored.append({'id':r['id'],'folio':r['folio'],'role':r['role'],'reference':r['reference'],'seen_in_training':r['reference'] in vocabulary,'raw_predictions':raw,'predictions':guesses,'errors':{name:levenshtein(r['reference'],p) for name,p in guesses.items()},'nearest_train_id':prior['nearest_train_id']})
    replay=[{'model':name,'id':r['id'],'pass0':passes[0][name][i],'pass1':passes[1][name][i]} for name in models for i,r in enumerate(evaluation) if passes[0][name][i]!=passes[1][name][i]]
    primary_rows=[r for r in scored if r['role']=='reserved' and not r['seen_in_training']]
    if len(primary_rows)!=76 or sum(len(r['reference']) for r in primary_rows)!=446:raise ValueError('Primary lexical stratum changed')
    previous=read(a.repo/'results/kraken_expansion/common_evaluation/result.json');old={r['id']:r['predictions']['expanded_200'] for r in previous['rows']};old_differences=[{'id':r['id'],'previous_common':old[r['id']],'current_source':r['predictions']['source']} for r in scored if old[r['id']]!=r['predictions']['source']]
    result={'status':'EXECUTED_EXPLORATORY_EVA_UNIT_COMMON_EVALUATION','plan_sha256':sha(a.plan),'primary_pass':0,'passes':2,'model_sha256':model_hashes,'prepared_dataset_sha256':plan['prepared_dataset_sha256'],'cached_baselines_sha256':sha(a.repo/plan['cached_baselines_path']),
            'metrics':slices(scored),'by_folio':{folio:slices([r for r in scored if r['folio']==folio]) for folio in sorted({r['folio'] for r in scored})},'rows':scored,'all_pass_raw_predictions':passes,'forward_calls':calls,'seconds':seconds,'within_process_replay_differences':replay,'source_differences_from_previous_common':old_differences,
            'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA'),'environment':environment(),'hardware':{'machine':platform.machine(),'threads':torch.get_num_threads(),'logical_cpus':os.cpu_count()},'expert_review':'NOT_REVIEWED','translation':'NOT_RUN','new_training_in_evaluation':'NOT_RUN','scope':plan['scope']}
    save(a.out/'result.json',result);print('UNIT_EVALUATION_RESULT='+json.dumps({k:v for k,v in result.items() if k not in ['rows','all_pass_raw_predictions','by_folio','environment']}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['train','evaluate']);p.add_argument('--plan',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--variant',choices=['reset_letters','reset_groups']);p.add_argument('--runs',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    try:
        if a.mode=='train':
            if not a.variant:raise ValueError('Training condition required')
            train(a)
        else:
            if not a.runs:raise ValueError('Trained models directory required')
            evaluate(a)
    except Exception as e:save(a.out/'failure.json',{'error':str(e),'traceback':traceback.format_exc(),'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA')});raise
