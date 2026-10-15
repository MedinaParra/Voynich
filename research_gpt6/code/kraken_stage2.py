#!/usr/bin/env python3
"""Operator-assisted layout and annotation-conditional Kraken OCR pilot."""
from __future__ import annotations
import argparse,base64,hashlib,importlib.metadata as metadata,io,json,os,re,subprocess,time,traceback
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from kraken_row_tools import (assemble,filter_paragraphs,matches,levenshtein,pua_text,
                              mask_image,image_features,nearest_text,row_image_name)
from kraken_layout_pilot import (fetch_bytes,git_blob_sha,sha256,serialize_lines,resized)

def read_json(path):return json.loads(Path(path).read_text())
def write_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,sort_keys=True,ensure_ascii=True,indent=2)+'\n')

def calibrate(old,masks,plan):
    lookup={p['folio']:p for p in masks['pages']}
    candidates=[]
    for tolerance in plan['layout']['calibration']['grid_tolerance_factors']:
        for deskew in plan['layout']['calibration']['grid_deskew']:
            counts={}
            for c in old['cases']:
                if c['method']!='default_neural_baselines' or c['width']!=1800:continue
                if c['folio'] not in plan['layout']['calibration_folios']:continue
                rows,_=assemble(c['lines'],c['image_size'],lookup[c['folio']]['regions'],tolerance,deskew)
                counts[c['folio']]=len(rows)
            if set(counts)!=set(plan['layout']['calibration_folios']):raise ValueError('Calibration case missing')
            loss=sum(abs(counts[f]-old['boxer_reference_counts'][f]) for f in counts)
            candidates.append({'tolerance_factor':tolerance,'deskew':deskew,'absolute_count_error':loss,'counts':counts})
    selected=min(candidates,key=lambda x:(x['absolute_count_error'],x['tolerance_factor'],x['deskew']))
    return {'candidates':candidates,'selected':selected,'scope':'Leaves 1/2 count-proxy calibration only'}

def draw_rows(im,rows,path,truth=None):
    out=im.convert('RGB').copy();draw=ImageDraw.Draw(out)
    if truth:
        for r in truth:
            b=r['bbox'];draw.rectangle([b[0]*im.width,b[1]*im.height,b[2]*im.width,b[3]*im.height],outline='#00a17c',width=2)
    for r in rows:
        draw.rectangle(r['bbox_pixels'],outline='#cc314b',width=3)
    path.parent.mkdir(parents=True,exist_ok=True);out.save(path,quality=88)

def layout_experiment(plan,masks,refs,old,out,result):
    import torch
    from importlib import resources
    from kraken import blla
    from kraken.lib.vgsl import TorchVGSLModel
    torch.manual_seed(20261014);torch.set_num_threads(2)
    model_path=Path(str(resources.files('kraken').joinpath('blla.mlmodel')))
    data=model_path.read_bytes()
    if git_blob_sha(data)!=plan['kraken']['model_blob']:raise ValueError('Default model hash mismatch')
    net=TorchVGSLModel.load_model(str(model_path))
    result['calibration']=calibrate(old,masks,plan)
    selected=result['calibration']['selected']
    result['layout']={'cases':[],'source_images':[]}
    originals={}
    mask_by={p['folio']:p for p in masks['pages']};ref_by={p['folio']:p for p in refs['pages']}
    # The predictor below receives only image geometry and paragraph masks.
    # Reference row boxes are used only after its three outputs are fixed.
    for folio in plan['layout']['diagnostic_folios']+plan['layout']['primary_folios']:
        p=mask_by[folio]
        url=p['service_url']+'/full/1800,/0/default.jpg'
        raw=fetch_bytes(url,out/'images'/f'{folio}.jpg',result['acquired'])
        if sha256(raw)!=p['image_sha256']:raise ValueError('Frozen Yale image changed: '+folio)
        with Image.open(io.BytesIO(raw)) as im:originals[folio]=im.convert('RGB')
        for width in plan['layout']['widths']:
            im=resized(originals[folio],width)
            tick=time.perf_counter()
            seg=blla.segment(im,model=net,device='cpu',raise_on_error=True)
            raw_lines=serialize_lines(seg,im.size)
            assembled,filtered=assemble(raw_lines,im.size,p['regions'],selected['tolerance_factor'],selected['deskew'])
            outputs={'full_page_raw':raw_lines,'paragraph_filter':filtered,
                     'paragraph_filter_and_assembly':assembled}
            truths=ref_by[folio]['lines']
            for variant,lines in outputs.items():
                match=matches([r['bbox_normalized'] for r in lines],[r['bbox'] for r in truths])
                case={'folio':folio,'width':width,'variant':variant,'status':'EXECUTED',
                      'image_size':list(im.size),'lines':lines,'line_count':len(lines),
                      'reference_count':len(truths),'absolute_count_error':abs(len(lines)-len(truths)),
                      'matching':match,'seconds_shared_inference':time.perf_counter()-tick}
                result['layout']['cases'].append(case)
                if width==1800:
                    draw_rows(im,lines,out/'layout_previews'/f'{folio}_{variant}.jpg',truths)
            print('STAGE2_LAYOUT_CASE='+json.dumps({'folio':folio,'width':width,
                  'counts':{v:len(lines) for v,lines in outputs.items()}},separators=(',',':')),flush=True)
    summaries={}
    for width in plan['layout']['widths']:
        for variant in plan['layout']['variants']:
            selected_cases=[c for c in result['layout']['cases'] if c['folio'] in plan['layout']['primary_folios']
                            and c['width']==width and c['variant']==variant]
            tp=sum(c['matching']['tp'] for c in selected_cases)
            predicted=sum(c['line_count'] for c in selected_cases)
            reference=sum(c['reference_count'] for c in selected_cases)
            summaries[f'{variant}_{width}']={'tp':tp,'predicted':predicted,'reference':reference,
                'f1':2*tp/(predicted+reference) if predicted+reference else 1.,
                'relative_count_error':sum(c['absolute_count_error'] for c in selected_cases)/reference,
                'complete':len(selected_cases)==len(plan['layout']['primary_folios'])}
    result['layout']['primary_summaries']=summaries
    g=plan['layout']['gate'];checks=[]
    for width in plan['layout']['widths']:
        corrected=summaries[f'paragraph_filter_and_assembly_{width}'];raw=summaries[f'full_page_raw_{width}']
        checks.append(corrected['complete'] and corrected['f1']>=g['micro_f1_min']
                      and corrected['f1']>raw['f1'] and corrected['relative_count_error']<=g['maximum_relative_count_error'])
    result['layout']['status']='PASS_OPERATOR_ASSISTED_LAYOUT_PILOT' if all(checks) else 'FAIL_OPERATOR_ASSISTED_LAYOUT_PILOT'
    return originals

def prepare_ocr(plan,masks,refs,images,mapping,out):
    source_units=set(mapping.values())|{' '}
    codec={c:[i+1] for i,c in enumerate(sorted(source_units))}
    write_json(out/'ocr/codec.json',codec)
    mask_by={p['folio']:p for p in masks['pages']}
    records=[]
    for page in refs['pages']:
        folio=page['folio'];im=mask_image(images[folio],mask_by[folio]['regions'])
        for row in page['lines']:
            text=pua_text(row['boxer_tokens'],mapping)
            b=row['bbox'];box=(int(b[0]*im.width),int(b[1]*im.height),int(np.ceil(b[2]*im.width)),int(np.ceil(b[3]*im.height)))
            crop=im.crop(box)
            role='train' if folio in plan['ocr']['train_folios'] else 'test'
            path=out/'ocr'/role/row_image_name(row['id']);path.parent.mkdir(parents=True,exist_ok=True)
            crop.save(path)
            path.with_suffix('.gt.txt').write_text(text,encoding='utf-8')
            records.append({'id':row['id'],'folio':folio,'role':role,'path':str(path.resolve()),
                            'image_sha256':sha256(path.read_bytes()),'text':text,
                            'boxer_tokens':row['boxer_tokens'],'source_bbox':b,
                            'review':row['review'],'crop_size':list(crop.size)})
    train=[r for r in records if r['role']=='train'];test=[r for r in records if r['role']=='test']
    if len(train)!=plan['ocr']['train_rows'] or len(test)!=plan['ocr']['test_rows']:raise ValueError('Unexpected row split')
    if {r['folio'].rstrip('rv') for r in train}&{r['folio'].rstrip('rv') for r in test}:raise ValueError('Physical leaf leakage')
    for role in ['train','test']:
        (out/'ocr'/f'{role}.lst').write_text('\n'.join(r['path'] for r in records if r['role']==role)+'\n')
    write_json(out/'ocr/dataset.json',records)
    return train,test

def conditional_ocr(plan,masks,refs,images,mapping,out,result):
    train,test=prepare_ocr(plan,masks,refs,images,mapping,out)
    from kraken.lib.util import parse_gt_path
    for row in train:
        parsed=parse_gt_path(row['path'])
        if parsed.text!=row['text']:
            raise ValueError('Kraken parser did not recover the complete training label: '+row['id'])
    root=(out/'ocr').resolve();opts=plan['ocr']
    config={'device':'cpu','precision':'32-true','num_workers':0,'num_threads':2,
            'seed':opts['seed'],'deterministic':True,'train':{
        'arch':'vgsl','spec':opts['spec'],'training_data':[str(root/'train.lst')],
        'evaluation_data':[str(root/'train.lst')],
        'checkpoint_path':str(root/'checkpoints'),'format_type':'path','codec':str(root/'codec.json'),
        'quit':'fixed','epochs':opts['epochs'],'min_epochs':opts['epochs'],'freq':opts['freq'],
        'batch_size':opts['batch_size'],'lrate':opts['lrate'],'schedule':'constant',
        'augment':False,'bidi_reordering':False,'normalization':'NFC',
        'normalize_whitespace':False,'padding':16,'weights_format':'safetensors'}}
    # JSON is valid YAML; training monitoring receives train.lst only.
    write_json(root/'training_config.json',config)
    result['ocr']={'status':'BLOCKED_DATA_OR_RUNTIME','dataset':{'train_rows':len(train),'test_rows':len(test),
                   'train_folios':opts['train_folios'],'test_folios':opts['test_folios'],
                   'input':'Human-reference box crops with manual paragraph masks'},'training_config':config,
                   'training_labels_parsed_and_verified':len(train)}
    command=['ketos','--config',str(root/'training_config.json'),'train']
    print('STAGE2_TRAINING_STARTED='+json.dumps({'rows':len(train),'epochs':opts['epochs'],'command':command}),flush=True)
    tick=time.perf_counter()
    with (root/'training.log').open('w') as log:
        done=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=900)
    result['ocr']['training_seconds']=time.perf_counter()-tick
    result['ocr']['training_returncode']=done.returncode
    if done.returncode:
        print((root/'training.log').read_text()[-18000:],flush=True)
        raise RuntimeError('Kraken training CLI failed; full log preserved')
    checkpoints=list((root/'checkpoints').glob('checkpoint_*.ckpt'))
    epochs=[(int(m.group(1)),p) for p in checkpoints if (m:=re.search(r'checkpoint_(\d+)-',p.name))]
    if not epochs:raise RuntimeError('No completed training checkpoint')
    epoch,checkpoint=max(epochs,key=lambda x:x[0])
    if epoch!=opts['epochs']-1:raise RuntimeError('Final fixed epoch checkpoint unavailable')
    result['ocr'].update({'training_status':'COMPLETED_FIXED_EPOCHS',
                         'final_epoch_zero_based':epoch,
                         'checkpoint_sha256':sha256(checkpoint.read_bytes()),
                         'training_log_sha256':sha256((root/'training.log').read_bytes())})
    model_path=root/'final_epoch.mlmodel'
    converted=subprocess.run(['ketos','convert','--weights-format','coreml','-o',str(model_path),str(checkpoint)],
                             capture_output=True,text=True,timeout=120)
    (root/'conversion.log').write_text(converted.stdout+'\n'+converted.stderr)
    if converted.returncode:raise RuntimeError('Final-checkpoint model conversion failed: '+converted.stderr[-2000:])
    result['ocr']['model_sha256']=sha256(model_path.read_bytes())
    from kraken.lib.vgsl import TorchVGSLModel
    from kraken import rpred
    from kraken.containers import Segmentation,BBoxLine
    net=TorchVGSLModel.load_model(str(model_path))
    train_info=[]
    for r in train:
        with Image.open(r['path']) as im:features=image_features(im)
        train_info.append({'id':r['id'],'text':r['text'],'features':features})
    frequencies=Counter(c for r in train for c in r['text'] if c!=' ')
    mode=frequencies.most_common(1)[0][0]
    median_length=int(np.median([len(r['text']) for r in train]))
    seen=set(''.join(r['text'] for r in train));unit_names={}
    for name,unit in mapping.items():unit_names.setdefault(unit,name)
    unit_names[mapping['?']]='?';unit_names[' ']='SPACE'
    rows=[]
    for r in test:
        with Image.open(r['path']) as im:
            im=im.convert('RGB')
            seg=Segmentation(type='bbox',imagename=r['path'],text_direction='horizontal-lr',script_detection=False,
                             lines=[BBoxLine(id=r['id'],bbox=(0,0,im.width,im.height))])
            output=list(rpred.rpred(net,im,seg,bidi_reordering=False))
            if len(output)!=1:raise RuntimeError('Recognizer produced an unexpected record count')
            prediction=output[0].prediction
            nearest,nearest_id=nearest_text(im,train_info)
        guesses={'kraken':prediction,'empty_output':'',
                 'repeat_training_mode_to_training_median_length':mode*median_length,
                 'nearest_training_line_by_fixed_image_features':nearest}
        rows.append({'id':r['id'],'folio':r['folio'],'reference':r['text'],'predictions':guesses,
                     'prediction_units':[unit_names.get(c,f'U+{ord(c):X}') for c in prediction],
                     'reference_units':[unit_names.get(c,f'U+{ord(c):X}') for c in r['text']],
                     'errors':{k:levenshtein(r['text'],p) for k,p in guesses.items()},
                     'nonspace_errors':{k:levenshtein(r['text'].replace(' ',''),p.replace(' ','')) for k,p in guesses.items()},
                     'nearest_train_id':nearest_id,'reference_units_count':len(r['text'])})
    n=sum(len(r['reference']) for r in rows);n_no_space=sum(len(r['reference'].replace(' ','')) for r in rows)
    scores={k:{'errors':sum(r['errors'][k] for r in rows),'reference_units':n,
                'gcr':sum(r['errors'][k] for r in rows)/n,
                'nonspace_gcr':sum(r['nonspace_errors'][k] for r in rows)/n_no_space}
            for k in rows[0]['predictions']}
    g=opts['gate'];best_baseline=min(scores[k]['gcr'] for k in opts['baselines'] if k!='empty_output')
    passed=len(rows)==opts['test_rows'] and scores['kraken']['gcr']<=g['gcr_max'] and scores['kraken']['gcr']<best_baseline
    result['ocr'].update({'status':'PASS_CONDITIONAL_OCR_PILOT' if passed else 'FAIL_CONDITIONAL_OCR_PILOT',
        'rows':rows,'metrics':scores,'final_epoch_zero_based':epoch,
        'checkpoint_sha256':sha256(checkpoint.read_bytes()),'model_sha256':sha256(model_path.read_bytes()),
        'training_log_sha256':sha256((root/'training.log').read_bytes()),
        'train_codec_observed_units':len(seen),'test_unseen_units':[f'U+{ord(c):X}' for c in sorted(set(''.join(r['reference'] for r in rows))-seen)],
        'test_unseen_unit_occurrences':sum(c not in seen for r in rows for c in r['reference']),
        'test_unknown_unit_occurrences':sum(r['reference'].count(mapping['?']) for r in rows),
        'model_scope':'Fixed final epoch; training-only monitoring, no test-based selection; manual-reference segmentation.'})
    print('STAGE2_OCR_METRICS='+json.dumps(scores,separators=(',',':')),flush=True)

def run(args):
    plan=read_json(args.plan);masks=read_json(args.masks);refs=read_json(args.reference)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    result={'schema_version':1,'experiment':plan['experiment'],'execution_commit':os.getenv('GITHUB_SHA'),
        'run_id':os.getenv('GITHUB_RUN_ID'),'run_attempt':os.getenv('GITHUB_RUN_ATTEMPT'),
        'plan_sha256':sha256(Path(args.plan).read_bytes()),'masks_sha256':sha256(Path(args.masks).read_bytes()),
        'reference_sha256':sha256(Path(args.reference).read_bytes()),'code_sha256':sha256(Path(__file__).read_bytes()),
        'tools_sha256':sha256(Path(__file__).with_name('kraken_row_tools.py').read_bytes()),
        'acquired':[],'failures':[],'translation':'NOT_RUN','language_identification':'NOT_RUN',
        'annotation_review':'ASSISTANT_SINGLE_REVIEW_PROVISIONAL','layout':{'status':'BLOCKED_DATA_OR_RUNTIME'},
        'ocr':{'status':'BLOCKED_DATA_OR_RUNTIME'}}
    started=time.perf_counter()
    try:
        if metadata.version('kraken')!=plan['kraken']['version']:raise RuntimeError('Kraken version mismatch')
        result['environment']={d.metadata['Name']:d.version for d in metadata.distributions() if d.metadata.get('Name')}
        sha=plan['predecessor']['result_commit']
        url='https://raw.githubusercontent.com/MedinaParra/Voynich/'+sha+'/research_gpt6/results/kraken_pilot/kraken_pilot_result.json'
        raw=fetch_bytes(url,out/'sources/previous_result.json',result['acquired'])
        old=json.loads(raw)
        base='https://raw.githubusercontent.com/alexanderboxer/voynich-attack/'+plan['sources']['boxer_commit']+'/'
        raw_mapping=fetch_bytes(base+'transcription/unicode_dict.json',out/'sources/unicode_dict.json',
                                result['acquired'],plan['sources']['unicode_blob'])
        mapping=json.loads(raw_mapping)
        images=layout_experiment(plan,masks,refs,old,out,result)
        try:conditional_ocr(plan,masks,refs,images,mapping,out,result)
        except Exception as e:
            result['failures'].append({'phase':'ocr','error':type(e).__name__+': '+str(e),'traceback':traceback.format_exc()})
    except Exception as e:
        result['failures'].append({'phase':'setup_or_layout','error':type(e).__name__+': '+str(e),'traceback':traceback.format_exc()})
    result['duration_seconds']=time.perf_counter()-started
    raw=json.dumps(result,sort_keys=True,ensure_ascii=True,separators=(',',':'))+'\n'
    (out/'stage2_result.json').write_text(raw)
    summary={k:v for k,v in result.items() if k not in ['environment','acquired','layout','ocr']}
    summary['layout']={k:v for k,v in result['layout'].items() if k!='cases'}
    summary['layout']['case_summaries']=[{k:c[k] for k in ['folio','width','variant','line_count','reference_count','absolute_count_error']} |
                                        {'f1':c['matching']['f1']} for c in result['layout'].get('cases',[])]
    summary['ocr']={k:v for k,v in result['ocr'].items() if k not in ['rows','training_config']}
    write_json(out/'stage2_summary.json',summary)
    write_json(out/'sha256_manifest.json',{str(p.relative_to(out)):sha256(p.read_bytes()) for p in sorted(out.rglob('*'))
                                         if p.is_file() and p.name!='sha256_manifest.json'})
    print('STAGE2_SUMMARY_JSON='+json.dumps(summary,sort_keys=True,ensure_ascii=True,separators=(',',':')),flush=True)
    print('STAGE2_RESULT_SHA256='+sha256(raw.encode()),flush=True)
    print('STAGE2_RESULT_JSON='+raw.strip(),flush=True)
    for f in ['4r','4v']:
        p=out/'layout_previews'/f'{f}_paragraph_filter_and_assembly.jpg'
        if p.exists():
            with Image.open(p) as im:
                preview=resized(im,750);buf=io.BytesIO();preview.save(buf,format='JPEG',quality=65,optimize=True)
            print('STAGE2_PREVIEW_'+f.upper()+'='+base64.b64encode(buf.getvalue()).decode(),flush=True)
    return 2 if result['failures'] else 0

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['plan','masks','reference','out']:p.add_argument('--'+name,required=True,type=Path)
    raise SystemExit(run(p.parse_args()))
