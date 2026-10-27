#!/usr/bin/env python3
"""Development ablation of old/repaired crops with fixed Kraken training budgets."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import traceback
import urllib.request
from collections import Counter

import numpy as np
from PIL import Image

from kraken_crop_repair import repair, contact_sheet
from kraken_crop_quality import rect
from kraken_row_tools import mask_image, pua_text, row_image_name, image_features, nearest_text, levenshtein


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2) + '\n')


def fetch_bytes(url, path, acquired):
    if not url.startswith(('https://collections.library.yale.edu/iiif/2/', 'https://raw.githubusercontent.com/alexanderboxer/voynich-attack/')):
        raise ValueError('Unexpected acquisition host')
    with urllib.request.urlopen(url, timeout=45) as response:
        raw=response.read(30_000_001)
        if len(raw)>30_000_000:raise ValueError('Unexpected source size')
        record={'url':url,'final_url':response.url,'http_status':response.status,
                'content_type':response.headers.get('Content-Type'),'bytes':len(raw),
                'sha256':hashlib.sha256(raw).hexdigest()}
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);acquired.append(record)
    return raw


def prepare(plan, repo, out, cache=None):
    refs_path = repo / 'data/kraken_line_reference.json'
    masks_path = repo / 'data/kraken_region_masks.json'
    if sha(refs_path) != plan['reference_sha256'] or sha(masks_path) != plan['masks_sha256']:
        raise ValueError('Frozen annotations changed')
    refs = json.loads(refs_path.read_text()); masks = json.loads(masks_path.read_text())
    mask_by = {p['folio']: p for p in masks['pages']}
    acquisitions = []
    mapping_path = out / 'sources/unicode_dict.json'
    if cache and (cache / 'sources/unicode_dict.json').exists():
        mapping_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(cache / 'sources/unicode_dict.json', mapping_path)
    else:
        fetch_bytes(plan['mapping_url'], mapping_path, acquisitions)
    if sha(mapping_path) != plan['mapping_sha256']:
        raise ValueError('Boxer mapping changed')
    mapping = json.loads(mapping_path.read_text())
    save(out / 'codec.json', {c: [i + 1] for i, c in enumerate(sorted(set(mapping.values()) | {' '}))})
    records, pages = [], []
    prior_records = json.loads((repo / 'results/kraken_stage2/ocr/dataset.json').read_text())
    prior_by = {r['id']: r for r in prior_records}
    for page in refs['pages']:
        folio = page['folio']; mp = mask_by[folio]
        source = out / 'images' / (folio + '.jpg')
        if cache and (cache / 'images' / (folio + '.jpg')).exists():
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(cache / 'images' / (folio + '.jpg'), source)
        else:
            fetch_bytes(mp['service_url'] + '/full/1800,/0/default.jpg', source, acquisitions)
        if sha(source) != mp['image_sha256'] or sha(source) != page['image_sha256']:
            raise ValueError('Frozen image changed: ' + folio)
        with Image.open(source) as src: im = src.convert('RGB')
        fixed, diagnostic = repair(im, page['lines'], mp['regions'], plan['repair'])
        masked = mask_image(im, mp['regions']); old = {}; label_names = {}
        for row in page['lines']:
            text = pua_text(row['boxer_tokens'], mapping)
            if text != prior_by[row['id']]['text']:
                raise ValueError('Label changed from prior pilot')
            old[row['id']] = masked.crop(rect(row['bbox'], im.size))
            label_names[row['id']] = ' '.join(row['boxer_tokens'])
        for row, fixed_row in zip(page['lines'], fixed):
            for variant, crop in [('original', old[row['id']]), ('repaired', fixed_row['image'])]:
                path = out / variant / row_image_name(row['id'])
                path.parent.mkdir(parents=True, exist_ok=True); crop.save(path)
                path.with_suffix('.gt.txt').write_text(pua_text(row['boxer_tokens'], mapping), encoding='utf-8')
                rec = {'id': row['id'], 'folio': folio, 'variant': variant, 'path': str(path.resolve()),
                       'role': 'train' if folio in plan['train_folios'] else 'development_evaluation',
                       'text': pua_text(row['boxer_tokens'], mapping), 'image_sha256': sha(path),
                       'pixel_sha256': hashlib.sha256(np.asarray(crop.convert('RGB')).tobytes()).hexdigest(),
                       'crop_size': list(crop.size), 'source_bbox': row['bbox'] if variant == 'original' else fixed_row['bounds'],
                       'reference_status': 'ASSISTANT_PROVISIONAL_PREVIOUSLY_EXPLORED'}
                if variant == 'repaired':
                    np.savez_compressed(out / variant / (path.stem + '_ownership.npz'), mask=fixed_row['mask'])
                    rec['ambiguous_component_ids'] = fixed_row['ambiguous_component_ids']
                records.append(rec)
        contact_sheet(old, fixed, label_names, out / 'previews' / (folio + '_comparison.jpg'))
        pages.append({'folio': folio, 'rows': len(page['lines']), 'image_sha256': sha(source), **diagnostic})
    if len(records) != 122: raise ValueError('Incomplete original/repaired row coverage')
    save(out / 'dataset.json', records)
    pooled = {}
    for key in ['0.06', '0.10', '0.14']:
        n = sum(p['metrics'][key]['positions_before'] for p in pages)
        before = sum(p['metrics'][key]['repeated_before'] for p in pages)
        after = sum(p['metrics'][key]['repeated_after'] for p in pages)
        lost = sum(p['metrics'][key]['lost_candidate_positions'] for p in pages)
        pooled[key] = {'positions': n, 'repeated_before': before, 'repeated_after': after, 'lost_candidate_positions': lost,
                       'repeated_fraction_before': before / n, 'repeated_fraction_after': after / n, 'retained_fraction': (n-lost)/n}
    summary = {'status': 'EXCLUSIVITY_AND_PROXY_CONSERVATION_VERIFIED_REVIEW_REQUIRED', 'pages': pages,
               'pooled': pooled, 'records': len(records), 'reference_rows': 61, 'labels_unchanged': 61,
               'new_expert_validation': 'NOT_REVIEWED', 'registration_voynichese_to_yale': 'NOT_RUN',
               'acquired': acquisitions, 'plan_sha256': plan['_sha256'], 'translation': 'NOT_RUN'}
    save(out / 'preparation.json', summary)
    return records, mapping, summary


def recognize(net, rows):
    from kraken import rpred
    from kraken.containers import Segmentation, BBoxLine
    outputs = []
    for row in rows:
        with Image.open(row['path']) as src:
            im = src.convert('RGB')
            seg = Segmentation(type='bbox', imagename=row['path'], text_direction='horizontal-lr', script_detection=False,
                               lines=[BBoxLine(id=row['id'], bbox=(0,0,im.width,im.height))])
            pred = list(rpred.rpred(net, im, seg, bidi_reordering=False))
        if len(pred) != 1: raise ValueError('Unexpected recognition output')
        outputs.append(pred[0].prediction)
    return outputs


def train_variant(plan, variant_name, records, mapping, out):
    if importlib.metadata.version('kraken') != '7.1': raise ValueError('Unexpected Kraken version')
    from kraken.lib.util import parse_gt_path
    from kraken.lib.models import load_any
    settings = plan['variants'][variant_name]
    selected = [r for r in records if r['variant'] == settings['crop_variant']]
    train = [r for r in selected if r['role'] == 'train']; dev = [r for r in selected if r['role'] != 'train']
    if len(train) != 34 or len(dev) != 27: raise ValueError('Changed split')
    if {r['folio'].rstrip('rv') for r in train} & {r['folio'].rstrip('rv') for r in dev}: raise ValueError('Physical leaf leakage')
    for row in train + dev:
        if parse_gt_path(row['path']).text != row['text']: raise ValueError('Label parser mismatch')
    root = (out / 'runs' / variant_name).resolve(); root.mkdir(parents=True, exist_ok=True)
    train_list = root / 'train.lst'; train_list.write_text('\n'.join(r['path'] for r in train) + '\n')
    config = {'device':'cpu','precision':'32-true','num_workers':0,'num_threads':2,'seed':plan['seed'],'deterministic':True,
              'train':{'arch':'vgsl','spec':plan['vgsl_spec'],'training_data':[str(train_list)],'evaluation_data':[str(train_list)],
              'checkpoint_path':str(root/'checkpoints'),'format_type':'path','codec':str((out/'codec.json').resolve()),
              'quit':'fixed','epochs':settings['epochs'],'min_epochs':settings['epochs'],'freq':settings['epochs'],
              'batch_size':4,'lrate':.001,'schedule':'constant','augment':False,'bidi_reordering':False,
              'normalization':'NFC','normalize_whitespace':False,'padding':16,'weights_format':'safetensors'}}
    save(root / 'training_config.json', config)
    started = time.perf_counter()
    with (root/'training.log').open('w') as log:
        process = subprocess.run(['ketos','--config',str(root/'training_config.json'),'train'],stdout=log,stderr=subprocess.STDOUT,timeout=1500)
    if process.returncode: raise RuntimeError('Training failed; see preserved training.log')
    candidates = [(int(m.group(1)), p) for p in (root/'checkpoints').glob('checkpoint_*.ckpt') if (m:=re.search(r'checkpoint_(\d+)-',p.name))]
    epoch, checkpoint = max(candidates, key=lambda x:x[0])
    if epoch != settings['epochs']-1: raise ValueError('Final fixed epoch unavailable')
    model = root/'final_epoch.mlmodel'
    process = subprocess.run(['ketos','convert','--weights-format','coreml','-o',str(model),str(checkpoint)],capture_output=True,text=True,timeout=120)
    (root/'conversion.log').write_text(process.stdout+'\n'+process.stderr)
    if process.returncode: raise RuntimeError('Model conversion failed')
    net = load_any(str(model), train=False, device='cpu')
    predictions = recognize(net, dev)
    train_predictions = recognize(net, train)
    info = []
    for row in train:
        with Image.open(row['path']) as im: features = image_features(im)
        info.append({'id':row['id'],'text':row['text'],'features':features})
    mode = Counter(c for r in train for c in r['text'] if c!=' ').most_common(1)[0][0]
    length = int(np.median([len(r['text']) for r in train]))
    scored = []
    for row, prediction in zip(dev, predictions):
        with Image.open(row['path']) as im: nearest, near_id = nearest_text(im, info)
        guesses = {'kraken':prediction,'nearest_image':nearest,'repeat_mode':mode*length,'empty':''}
        scored.append({'id':row['id'],'folio':row['folio'],'reference':row['text'],'predictions':guesses,
                       'errors':{k:levenshtein(row['text'],v) for k,v in guesses.items()},'nearest_train_id':near_id})
    n = sum(len(r['reference']) for r in scored)
    metrics = {k:{'errors':sum(r['errors'][k] for r in scored),'reference_units':n,
                  'gcr':sum(r['errors'][k] for r in scored)/n} for k in scored[0]['predictions']}
    seen = set(''.join(r['text'] for r in train)); names={v:k for k,v in mapping.items()}
    result = {'status':'EXECUTED_DEVELOPMENT_DIAGNOSTIC_NOT_CONFIRMATORY','variant':variant_name,
              'crop_variant':settings['crop_variant'],'epochs':settings['epochs'],'final_epoch_zero_based':epoch,
              'seconds':time.perf_counter()-started,'train_rows':len(train),'development_rows':len(dev),
              'metrics':metrics,'rows':scored,'training_fit_gcr':sum(levenshtein(r['text'],p) for r,p in zip(train,train_predictions))/sum(len(r['text']) for r in train),
              'prediction_unit_counts':{names.get(k,'SPACE' if k==' ' else k):v for k,v in Counter(''.join(predictions)).items()},
              'test_unseen_units':[f'U+{ord(c):X}' for c in sorted(set(''.join(r['text'] for r in dev))-seen)],
              'model_sha256':sha(model),'checkpoint_sha256':sha(checkpoint),'training_log_sha256':sha(root/'training.log'),
              'plan_sha256':plan['_sha256'],'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA'),
              'environment':{k:importlib.metadata.version(k) for k in ['torch','torchvision','kraken','pillow','numpy','scipy','lightning']},
              'data_scope':'Previously explored leaves 3/4; assistant-only provisional labels; training-only monitor; fixed final checkpoint.',
              'translation':'NOT_RUN','language_identification':'NOT_RUN'}
    save(root/'result.json', result)
    print('REPAIR_OCR_RESULT='+json.dumps({k:v for k,v in result.items() if k not in ['rows','environment']},ensure_ascii=True),flush=True)
    return result


def main(args):
    out=args.out;out.mkdir(parents=True,exist_ok=True)
    plan=json.loads(args.plan.read_text());plan['_sha256']=sha(args.plan)
    phase='preparation'
    try:
        records,mapping,summary=prepare(plan,args.repo,out,args.cache)
        print('REPAIR_PREPARATION='+json.dumps({k:v for k,v in summary.items() if k not in ['pages','acquired']}),flush=True)
        if args.variant:
            phase='recognition';train_variant(plan,args.variant,records,mapping,out)
    except Exception as error:
        save(out/'failure.json',{'phase':phase,'error':type(error).__name__+': '+str(error),'traceback':traceback.format_exc(),
                                'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA')})
        raise


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--plan',type=Path,required=True);p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--cache',type=Path)
    p.add_argument('--variant',choices=['original_40','repaired_40','repaired_200'])
    main(p.parse_args())
