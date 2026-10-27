#!/usr/bin/env python3
"""Warm-start Kraken on frozen candidate EVA words, with a matched label control."""
import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import traceback

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from kraken_row_tools import image_features, nearest_text, levenshtein


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2)+'\n')
def sample_name(folio,index):return folio+'_w'+str(index).zfill(4)
def crop_word(im, polygon, padding):
    a=np.asarray(polygon,dtype=float)
    if a.shape!=(4,2) or not np.isfinite(a).all():raise ValueError('Invalid word polygon')
    if abs(float(np.dot(a[:,0],np.roll(a[:,1],-1))-np.dot(a[:,1],np.roll(a[:,0],-1))))<1e-6:raise ValueError('Zero-area polygon')
    x0=max(0,math.floor(a[:,0].min())-padding);y0=max(0,math.floor(a[:,1].min())-padding)
    x1=min(im.width,math.ceil(a[:,0].max())+padding);y1=min(im.height,math.ceil(a[:,1].max())+padding)
    if x1<=x0 or y1<=y0:raise ValueError('Empty word crop')
    raw=im.crop((x0,y0,x1,y1)).convert('RGB');mask=Image.new('L',raw.size,0)
    ImageDraw.Draw(mask).polygon([(round(x-x0),round(y-y0)) for x,y in a],fill=255)
    mask=mask.filter(ImageFilter.MaxFilter(2*padding+1)) if padding else mask
    result=Image.composite(raw,Image.new('RGB',raw.size,'white'),mask)
    return result,mask,[x0,y0,x1,y1]


def permuted_training_labels(rows, seed):
    groups=defaultdict(list)
    for i,r in enumerate(rows):
        if r['role']=='train':groups[(r['folio'],len(r['reference']))].append(i)
    assigned={r['id']:{'text':r['reference'],'source_id':r['id']} for r in rows}
    rng=np.random.default_rng(seed)
    for key,indices in sorted(groups.items()):
        order=rng.permutation(indices).tolist()
        for position,i in enumerate(order):
            j=order[(position+1)%len(order)]
            assigned[rows[i]['id']]={'text':rows[j]['reference'],'source_id':rows[j]['id']}
    return assigned


def prepare(plan,repo,out,variant):
    for key,digest in [('words_path','words_sha256'),('geometry_result_path','geometry_result_sha256'),
                       ('geometry_audit_path','geometry_audit_sha256'),('inputs_path','inputs_sha256'),
                       ('warmstart_path','warmstart_sha256')]:
        if sha(repo/plan[key])!=plan[digest]:raise ValueError('Frozen input changed: '+key)
    geometry=json.loads((repo/plan['geometry_result_path']).read_text())
    audit=json.loads((repo/plan['geometry_audit_path']).read_text())
    if geometry['candidate_word_polygons']!=344 or audit['mismatches']:raise ValueError('Candidate geometry preconditions failed')
    words=json.loads((repo/plan['words_path']).read_text());pages={p['folio']:p for p in json.loads((repo/plan['inputs_path']).read_text())['pages']}
    images={};rows=[]
    for w in words:
        if w['yale_polygon'] is None or w['flags']:continue
        f=w['folio'];page=pages[f]
        if '*' in w['eva'] or not w['eva'] or not w['eva'].isascii() or not w['eva'].islower():raise ValueError('Unexpected EVA word')
        if f not in images:
            if sha(repo/page['yale_path'])!=page['yale_sha256']:raise ValueError('Yale image changed')
            with Image.open(repo/page['yale_path']) as im:images[f]=im.convert('RGB')
        crop,mask,bounds=crop_word(images[f],w['yale_polygon'],plan['padding_pixels'])
        name=sample_name(f,w['index']);path=(out/'crops'/(name+'.png')).resolve();path.parent.mkdir(parents=True,exist_ok=True)
        mask_path=path.with_name(name+'_mask.png');crop.save(path);mask.save(mask_path)
        role='train' if f in plan['train_folios'] else 'development'
        rows.append({'id':name,'folio':f,'index':w['index'],'role':role,'reference':w['eva'],
                     'path':str(path),'mask_path':str(mask_path),'bounds':bounds,'crop_size':list(crop.size),
                     'source_image_path':page['yale_path'],'source_image_sha256':page['yale_sha256'],
                     'polygon':w['yale_polygon'],'image_sha256':sha(path),'mask_sha256':sha(mask_path),
                     'reference_status':'CANDIDATE_EVA_SOURCE_NO_NEW_EXPERT_REVIEW'})
    if len(rows)!=344 or Counter(r['role'] for r in rows)!=Counter({'train':197,'development':147}):raise ValueError('Changed physical-leaf split')
    train_leaves={r['folio'][1:-1] for r in rows if r['role']=='train'};dev_leaves={r['folio'][1:-1] for r in rows if r['role']=='development'}
    if train_leaves&dev_leaves:raise ValueError('Physical leaf leakage')
    assignments=permuted_training_labels(rows,plan['seed'])
    for r in rows:
        assigned=assignments[r['id']] if variant=='permuted_200' else {'text':r['reference'],'source_id':r['id']}
        r['training_text']=assigned['text'];r['training_label_source_id']=assigned['source_id']
        Path(r['path']).with_suffix('.gt.txt').write_text(r['training_text'],encoding='utf-8')
    alphabet=set(''.join(r['reference'] for r in rows if r['role']=='train'))
    unseen=Counter(c for r in rows if r['role']=='development' for c in r['reference'] if c not in alphabet)
    summary={'variant':variant,'rows':len(rows),'train_words':197,'development_words':147,
             'train_reference_characters':sum(len(r['reference']) for r in rows if r['role']=='train'),
             'development_reference_characters':sum(len(r['reference']) for r in rows if r['role']=='development'),
             'train_alphabet':''.join(sorted(alphabet)),'development_unseen_characters':dict(unseen),
             'changed_training_labels':sum(r['training_text']!=r['reference'] for r in rows if r['role']=='train'),
             'changed_development_labels':sum(r['training_text']!=r['reference'] for r in rows if r['role']=='development'),
             'labels_permutation':'Seeded cycle within training folio and exact word length; repeated texts can remain unchanged.',
             'source_exclusions':1,'new_expert_review':'NOT_REVIEWED','translation':'NOT_RUN'}
    save(out/'dataset.json',rows);save(out/'preparation.json',summary)
    for folio in ['f3r','f4r']:
        selected=[r for r in rows if r['folio']==folio][:12]
        sheet=Image.new('RGB',(960,4*140),'#eeeeee');draw=ImageDraw.Draw(sheet)
        for i,r in enumerate(selected):
            x=(i%3)*320;y=(i//3)*140
            draw.text((x+5,y+4),r['id']+' | '+r['reference'],fill='black')
            with Image.open(r['path']) as im:
                im.thumbnail((310,110));sheet.paste(im,(x+5,y+23))
        (out/'previews').mkdir(exist_ok=True);sheet.save(out/'previews'/(folio+'_words.jpg'),quality=92)
    return rows,summary


def recognize(net,rows):
    from kraken import rpred
    from kraken.containers import Segmentation,BBoxLine
    outputs=[]
    for r in rows:
        with Image.open(r['path']) as src:
            im=src.convert('RGB');seg=Segmentation(type='bbox',imagename=r['path'],text_direction='horizontal-lr',script_detection=False,
                                                  lines=[BBoxLine(id=r['id'],bbox=(0,0,im.width,im.height))])
            pred=list(rpred.rpred(net,im,seg,bidi_reordering=False))
        if len(pred)!=1:raise ValueError('Recognition did not return one record')
        outputs.append(pred[0].prediction)
    return outputs


def tensor_manifest(net):
    return {k:{'shape':list(v.shape),'dtype':str(v.dtype),'sha256':hashlib.sha256(v.detach().cpu().contiguous().numpy().tobytes()).hexdigest()}
            for k,v in net.nn.nn.state_dict().items()}


def summarize(scored):
    n=sum(len(r['reference']) for r in scored)
    return {method:{'errors':sum(r['errors'][method] for r in scored),'reference_characters':n,
                    'cer':sum(r['errors'][method] for r in scored)/n,
                    'exact_words':sum(r['predictions'][method]==r['reference'] for r in scored),
                    'words':len(scored),'exact_word_fraction':sum(r['predictions'][method]==r['reference'] for r in scored)/len(scored)}
            for method in scored[0]['predictions']}


def train(plan,repo,out,variant,rows):
    import torch
    from kraken.lib.models import load_any
    from kraken.lib.util import parse_gt_path
    if importlib.metadata.version('kraken')!='7.1':raise ValueError('Changed Kraken version')
    train_rows=[r for r in rows if r['role']=='train'];dev=[r for r in rows if r['role']=='development']
    for r in rows:
        if parse_gt_path(r['path']).text!=r['training_text']:raise ValueError('Kraken paired-label parser mismatch')
    torch.set_num_threads(2);torch.manual_seed(plan['seed']);torch.use_deterministic_algorithms(True)
    source=(repo/plan['warmstart_path']).resolve();converted=(out/'warmstart.safetensors').resolve()
    cp=subprocess.run(['ketos','convert','--weights-format','safetensors','-o',str(converted),str(source)],capture_output=True,text=True,timeout=180)
    (out/'warmstart_conversion.log').write_text(cp.stdout+'\n'+cp.stderr)
    if cp.returncode:raise RuntimeError('Warm-start conversion failed')
    original_net=load_any(str(source),train=False,device='cpu');converted_net=load_any(str(converted),train=False,device='cpu')
    original_state=tensor_manifest(original_net);converted_state=tensor_manifest(converted_net)
    equivalence={'source_sha256':sha(source),'converted_sha256':sha(converted),'source_tensors':original_state,
                 'converted_tensors':converted_state,'tensor_states_equal':original_state==converted_state,
                 'codec_equal':original_net.codec.c2l==converted_net.codec.c2l}
    save(out/'warmstart_equivalence.json',equivalence)
    if not equivalence['tensor_states_equal'] or not equivalence['codec_equal']:raise ValueError('Warm-start conversion did not preserve tensor state and codec')
    del original_net,converted_net
    root=(out/'training').resolve();root.mkdir(parents=True,exist_ok=True)
    train_list=root/'train.lst';train_list.write_text('\n'.join(r['path'] for r in train_rows)+'\n')
    config={'device':'cpu','precision':'32-true','num_workers':0,'num_threads':2,'seed':plan['seed'],'deterministic':True,
            'train':{'training_data':[str(train_list)],'evaluation_data':[str(train_list)],
                     'checkpoint_path':str(root/'checkpoints'),'format_type':'path','quit':'fixed','epochs':plan['epochs'],
                     'min_epochs':plan['epochs'],'freq':plan['epochs'],'batch_size':plan['batch_size'],'lrate':plan['learning_rate'],
                     'schedule':'constant','augment':False,'bidi_reordering':False,'normalization':'NFC','normalize_whitespace':False,
                     'padding':16,'weights_format':'safetensors','freeze_backbone':0}}
    save(root/'training_config.json',config)
    command=['ketos','--config',str(root/'training_config.json'),'train','--load',str(converted),'--resize','new']
    save(root/'command.json',command);started=time.perf_counter()
    with (root/'training.log').open('w') as log:
        cp=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=1500)
    if cp.returncode:raise RuntimeError('Training failed; see preserved log')
    candidates=[(int(m.group(1)),p) for p in (root/'checkpoints').glob('checkpoint_*.ckpt') if (m:=re.search(r'checkpoint_(\d+)-',p.name))]
    if not candidates:raise ValueError('No trained checkpoint')
    epoch,checkpoint=max(candidates,key=lambda x:x[0])
    if epoch!=plan['epochs']-1:raise ValueError('Fixed final checkpoint unavailable')
    model=out/'final_epoch.mlmodel'
    cp=subprocess.run(['ketos','convert','--weights-format','coreml','-o',str(model),str(checkpoint)],capture_output=True,text=True,timeout=180)
    (out/'final_conversion.log').write_text(cp.stdout+'\n'+cp.stderr)
    if cp.returncode:raise RuntimeError('Final model conversion failed')
    net=load_any(str(model),train=False,device='cpu');codec=net.codec.c2l;save(out/'trained_codec.json',codec)
    keys=''.join(codec);alphabet=set(''.join(r['reference'] for r in train_rows))
    if not alphabet<=set(keys) or any(ord(c)>=0xF0000 for c in keys):raise ValueError('EVA output codec was not adapted from the old PUA codec')
    dev_predictions=recognize(net,dev);train_predictions=recognize(net,train_rows)
    info=[]
    for r in train_rows:
        with Image.open(r['path']) as im:feat=image_features(im)
        info.append({'id':r['id'],'text':r['reference'],'features':feat})
    mode_word=Counter(r['reference'] for r in train_rows).most_common(1)[0][0]
    mode_char=Counter(''.join(r['reference'] for r in train_rows)).most_common(1)[0][0]
    median_length=int(np.median([len(r['reference']) for r in train_rows]));train_vocabulary={r['reference'] for r in train_rows}
    scored=[]
    for r,pred in zip(dev,dev_predictions):
        with Image.open(r['path']) as im:nearest,near_id=nearest_text(im,info)
        guesses={'kraken':pred,'nearest_image':nearest,'mode_word':mode_word,'repeat_character':mode_char*median_length,'empty':''}
        scored.append({'id':r['id'],'folio':r['folio'],'reference':r['reference'],'predictions':guesses,
                       'errors':{k:levenshtein(r['reference'],v) for k,v in guesses.items()},'nearest_train_id':near_id,
                       'reference_seen_in_true_training_words':r['reference'] in train_vocabulary})
    train_outputs=[{'id':r['id'],'reference':r['reference'],'assigned_training_text':r['training_text'],'prediction':pred,
                    'true_errors':levenshtein(r['reference'],pred),'assigned_errors':levenshtein(r['training_text'],pred)} for r,pred in zip(train_rows,train_predictions)]
    n_train=sum(len(r['reference']) for r in train_rows)
    result={'date':plan['date'],'status':'EXECUTED_EVA_WORD_DEVELOPMENT_RETRAINING_NOT_TRANSLATION','variant':variant,
            'epochs':plan['epochs'],'final_epoch_zero_based':epoch,'training_words':197,'development_words':147,
            'metrics':summarize(scored),'rows':scored,'training_predictions':train_outputs,
            'training_fit_cer_assigned':sum(r['assigned_errors'] for r in train_outputs)/n_train,
            'training_fit_cer_true':sum(r['true_errors'] for r in train_outputs)/n_train,
            'by_folio':{f:summarize([r for r in scored if r['folio']==f]) for f in sorted({r['folio'] for r in scored})},
            'lexical_strata':{key:(summarize(rs) if rs else None) for key,rs in [('seen',[r for r in scored if r['reference_seen_in_true_training_words']]),('unseen',[r for r in scored if not r['reference_seen_in_true_training_words']])]},
            'prediction_character_counts':dict(Counter(''.join(dev_predictions))),
            'plan_sha256':plan['_sha256'],'warmstart_source_sha256':sha(source),'warmstart_converted_sha256':sha(converted),
            'model_sha256':sha(model),'checkpoint_sha256':sha(checkpoint),'training_log_sha256':sha(root/'training.log'),
            'seconds_training_and_evaluation':time.perf_counter()-started,'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA'),
            'environment':{k:importlib.metadata.version(k) for k in ['torch','torchvision','kraken','pillow','numpy','scipy','lightning']},
            'scope':plan['scope'],'metric':'Edit distance per conventional EVA character in word crops; not glyph, phonetic or translation accuracy.',
            'expert_review':'NOT_REVIEWED','translation':'NOT_RUN','language_identification':'NOT_RUN'}
    save(out/'result.json',result)
    print('EVA_WORD_RESULT='+json.dumps({k:v for k,v in result.items() if k not in ['rows','training_predictions','by_folio','lexical_strata','environment']},ensure_ascii=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--variant',choices=['aligned_200','permuted_200'],required=True);p.add_argument('--prepare-only',action='store_true')
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True);phase='preparation'
    try:
        plan=json.loads(args.plan.read_text());plan['_sha256']=sha(args.plan)
        rows,summary=prepare(plan,args.repo,args.out,args.variant);print('EVA_WORD_PREPARATION='+json.dumps(summary),flush=True)
        if not args.prepare_only:phase='warmstart_and_training';train(plan,args.repo,args.out,args.variant,rows)
    except Exception as error:
        save(args.out/'failure.json',{'phase':phase,'error':type(error).__name__+': '+str(error),'traceback':traceback.format_exc(),
                                    'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA')})
        raise
