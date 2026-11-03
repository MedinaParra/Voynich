#!/usr/bin/env python3
"""Matched two-view retraining and frozen-input common evaluation."""
import argparse
from collections import Counter
import hashlib
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import time
import traceback

import numpy as np
from PIL import Image

from eva_unit_tools import read, sha, save, restore_and_load, metrics
from shared_region_tools import prepare_views
from kraken_eva_word_training import recognize, tensor_manifest
from kraken_row_tools import levenshtein, image_features, nearest_text
from ctc_prefix_tools import validate, greedy, prefix_beam


def environment():
    return {p: importlib.metadata.version(p) for p in ['torch', 'torchvision', 'kraken', 'lightning', 'numpy', 'pillow', 'scipy']}


def grouped(rows):
    result = {}
    for role in ['historical_development', 'reserved', 'fresh_reserved']:
        rs = [r for r in rows if r['role'] == role]
        result[role] = {'all': metrics(rs), 'seen': metrics([r for r in rs if r['seen_in_training']]),
                        'unseen': metrics([r for r in rs if not r['seen_in_training']]),
                        'length_1_4': metrics([r for r in rs if len(r['reference']) <= 4]),
                        'length_5_6': metrics([r for r in rs if 5 <= len(r['reference']) <= 6]),
                        'length_7_plus': metrics([r for r in rs if len(r['reference']) >= 7]),
                        'by_folio': {f: metrics([r for r in rs if r['folio'] == f]) for f in sorted({r['folio'] for r in rs})}}
    return result


def train(a):
    import torch
    from kraken.models import load_models
    from kraken.lib.models import load_any
    from kraken.lib.util import parse_gt_path
    from kraken.lib.dataset.augment import DefaultAugmenter
    plan = read(a.plan)
    source = (a.repo/plan['source_model_path']).resolve()
    if sha(source) != plan['source_model_sha256']:
        raise ValueError('Frozen initial weights changed')
    if importlib.metadata.version('kraken') != '7.1':
        raise ValueError('Wrong Kraken version')
    views, records = prepare_views(a.repo, plan, a.out, a.variant)
    for row in views:
        if parse_gt_path(row['path']).text != row['reference']:
            raise ValueError('Real Kraken paired-label parser mismatch')
    torch.set_num_threads(2)
    torch.manual_seed(plan['seed'])
    torch.use_deterministic_algorithms(True)
    aug = DefaultAugmenter()
    expected = plan['stock_augmenter_expected']
    if aug.p != expected['p'] or aug.max_ops != expected['max_ops']:
        raise ValueError('Unexpected stock augmentation defaults')
    module_path = Path(inspect.getfile(DefaultAugmenter))
    code = module_path.read_bytes()
    (a.out/'sources').mkdir(exist_ok=True)
    (a.out/'sources/kraken_augment.py').write_bytes(code)
    save(a.out/'augmentation.json', {'p': aug.p, 'max_ops': aug.max_ops, 'probabilities': aug.probs,
                                   'module_sha256': hashlib.sha256(code).hexdigest(), 'stock_augmentation': True})
    warm = (a.out/'warmstart.safetensors').resolve()
    completed = subprocess.run(['ketos', 'convert', '--weights-format', 'safetensors', '-o', str(warm), str(source)], capture_output=True, text=True, timeout=180)
    (a.out/'warmstart_conversion.log').write_text(completed.stdout+'\n'+completed.stderr)
    if completed.returncode:
        raise RuntimeError('Warm-start conversion failed')
    x = load_models(source, tasks=['recognition'])[0]
    y = load_models(warm, tasks=['recognition'])[0]
    before, after = tensor_manifest(x), tensor_manifest(y)
    codec = x.codec.c2l
    proof = {'source_sha256': sha(source), 'converted_sha256': sha(warm), 'source_tensors': before,
             'converted_tensors': after, 'tensor_states_equal': before == after, 'codec_equal': codec == y.codec.c2l, 'codec': codec}
    save(a.out/'warmstart_equivalence.json', proof)
    if before != after or codec != y.codec.c2l or len(before) != 14:
        raise ValueError('Warm-start changed tensor states or codec')
    if not set(''.join(r['reference'] for r in views)) <= set(codec):
        raise ValueError('Training alphabet outside source codec')
    del x, y
    root = (a.out/'training').resolve()
    root.mkdir(exist_ok=True)
    lst = root/'train.lst'
    lst.write_text('\n'.join(r['path'] for r in views)+'\n')
    config = {'device': 'cpu', 'precision': '32-true', 'num_workers': 0, 'num_threads': 2, 'seed': plan['seed'], 'deterministic': True,
              'train': {'training_data': [str(lst)], 'evaluation_data': [str(lst)], 'checkpoint_path': str(root/'checkpoints'),
                        'format_type': 'path', 'quit': 'fixed', 'epochs': plan['epochs'], 'min_epochs': plan['epochs'],
                        'freq': plan['epochs'], 'batch_size': plan['batch_size'], 'lrate': plan['learning_rate'],
                        'schedule': 'constant', 'augment': True, 'bidi_reordering': False, 'normalization': 'NFC',
                        'normalize_whitespace': False, 'padding': 16, 'weights_format': 'safetensors', 'freeze_backbone': 0}}
    save(root/'training_config.json', config)
    command = ['ketos', '--config', str(root/'training_config.json'), 'train', '--load', str(warm), '--resize', 'fail']
    save(root/'command.json', command)
    started = time.perf_counter()
    with (root/'training.log').open('w') as log:
        completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=3000)
    if completed.returncode:
        raise RuntimeError('Training failed; retain full log')
    checkpoints = [(int(m.group(1)), p) for p in (root/'checkpoints').glob('checkpoint_*.ckpt') if (m := re.search(r'checkpoint_(\d+)-', p.name))]
    if not checkpoints:
        raise ValueError('No checkpoint')
    epoch, checkpoint = max(checkpoints, key=lambda x: x[0])
    state = torch.load(checkpoint, weights_only=False, map_location='cpu')
    steps, actual_epoch = int(state['global_step']), int(state['epoch'])
    del state
    if epoch != plan['epochs']-1 or actual_epoch != epoch or steps != plan['expected_optimizer_steps']:
        raise ValueError('Fixed final epoch/step count not reached')
    final = a.out/'final_epoch.mlmodel'
    completed = subprocess.run(['ketos', 'convert', '--weights-format', 'coreml', '-o', str(final), str(checkpoint)], capture_output=True, text=True, timeout=180)
    (a.out/'final_conversion.log').write_text(completed.stdout+'\n'+completed.stderr)
    if completed.returncode:
        raise RuntimeError('Final conversion failed')
    net = load_any(str(final), train=False, device='cpu')
    trained = tensor_manifest(net.nn)
    if net.codec.c2l != codec or trained == before:
        raise ValueError('Unexpected codec or unchanged trained tensors')
    save(a.out/'trained_codec.json', net.codec.c2l)
    save(a.out/'trained_tensor_records.json', trained)
    count = {'n': 0}
    handle = net.nn.nn.register_forward_hook(lambda *args: count.update(n=count['n']+1))
    predictions = recognize(net, views)
    handle.remove()
    outputs = [{'id': r['id'], 'source_id': r['source_id'], 'view': r['view'], 'reference': r['reference'],
                'prediction': p, 'errors': levenshtein(r['reference'], p)} for r, p in zip(views, predictions)]
    result = {'status': 'EXECUTED_TWO_VIEW_SPATIAL_RETRAINING', 'variant': a.variant, 'plan_sha256': sha(a.plan),
              'source_model_sha256': sha(source), 'prepared_dataset_sha256': plan['prepared_dataset_sha256'],
              'training_words': plan['training_words'], 'training_views': len(views), 'epochs': plan['epochs'],
              'checkpoint_epoch': epoch, 'optimizer_steps': steps, 'model_sha256': sha(final),
              'checkpoint_sha256': sha(checkpoint), 'training_log_sha256': sha(root/'training.log'),
              'warmstart_proof_sha256': sha(a.out/'warmstart_equivalence.json'),
              'training_views_sha256': sha(a.out/'training_views.json'), 'perturbation_records_sha256': sha(a.out/'perturbation_records.json'),
              'training_predictions': outputs, 'training_inference_calls': count['n'],
              'training_fit_by_view': {str(v): {'words': sum(r['view'] == v for r in outputs),
                                             'errors': sum(r['errors'] for r in outputs if r['view'] == v),
                                             'exact_words': sum(r['reference'] == r['prediction'] for r in outputs if r['view'] == v)} for v in [0, 1]},
              'seconds_training_conversion_fit': time.perf_counter()-started, 'run_id': os.getenv('GITHUB_RUN_ID'),
              'execution_commit': os.getenv('GITHUB_SHA'), 'environment': environment(), 'expert_review': 'NOT_REVIEWED', 'translation': 'NOT_RUN'}
    save(a.out/'result.json', result)
    print('SHARED_TRAINING_RESULT='+json.dumps({k: v for k, v in result.items() if k not in ['training_predictions', 'environment']}), flush=True)


def evaluate(a):
    import torch
    from kraken.lib.models import load_any
    plan = read(a.plan)
    dataset, training, rows = restore_and_load(a.repo, plan)
    vocabulary = {r['reference'] for r in training}
    fresh_root = a.repo/plan['fresh_root']
    fresh = read(fresh_root/'fresh_result.json')
    if fresh['plan_sha256'] != sha(a.plan):
        raise ValueError('Changed fresh acquisition protocol')
    fresh_rows = []
    if fresh['status'] == 'PASS_FRESH_GEOMETRY_CANDIDATES':
        if sha(fresh_root/'dataset.json') != fresh['dataset_sha256']:
            raise ValueError('Fresh dataset changed after geometric preparation')
        for item in read(fresh_root/'dataset.json'):
            r = dict(item)
            r['path'] = str((fresh_root/'crops'/Path(r['path']).name).resolve())
            r['mask_path'] = str((fresh_root/'crops'/Path(r['mask_path']).name).resolve())
            if sha(Path(r['path'])) != r['image_sha256'] or sha(Path(r['mask_path'])) != r['mask_sha256']:
                raise ValueError('Frozen fresh crop changed')
            r['role'] = 'fresh_reserved'
            fresh_rows.append(r)
        if {r['folio'] for r in fresh_rows} != set(plan['fresh_folios']):
            raise ValueError('Fresh folio selection changed')
    rows += fresh_rows
    if {r['folio'][:-1] for r in training} & {r['folio'][:-1] for r in rows}:
        raise ValueError('Physical-leaf leakage')
    models = {'source': a.repo/plan['source_model_path']}
    if sha(models['source']) != plan['source_model_sha256']:
        raise ValueError('Frozen source changed')
    for variant in plan['variants']:
        root = a.runs/('shared-region-'+variant)
        metadata = read(root/'result.json')
        model = root/'final_epoch.mlmodel'
        if metadata['variant'] != variant or metadata['plan_sha256'] != sha(a.plan) or metadata['model_sha256'] != sha(model):
            raise ValueError('Changed trained model '+variant)
        models[variant] = model
    torch.set_num_threads(2)
    torch.manual_seed(plan['seed'])
    torch.use_deterministic_algorithms(True)
    scored = [{'id': r['id'], 'folio': r['folio'], 'role': r['role'], 'reference': r['reference'],
               'seen_in_training': r['reference'] in vocabulary, 'predictions': {}, 'errors': {}} for r in rows]
    passes, counts, parity, matrix_replay = [], [], [], []
    capture_records, tensor_checks, files = [], {}, {}
    started = time.perf_counter()
    for pass_index in range(2):
        outputs, calls = {}, {}
        for name, path in models.items():
            net = load_any(str(path), train=False, device='cpu')
            before = tensor_manifest(net.nn)
            codec = net.codec.c2l
            if any(len(c) != 1 or len(v) != 1 for c, v in codec.items()):
                raise ValueError('Expected single-character fixed EVA codec')
            id_text = {v[0]: c for c, v in codec.items()}
            original = net.decoder
            captured = []
            def capture(o, lengths=None):
                values = np.asarray(o)
                if values.ndim == 2:
                    values = values[None, :, :]
                length = values.shape[-1] if lengths is None else int(np.atleast_1d(lengths)[0])
                p = values[0, :, :length].T.copy()
                validate(p)
                captured.append(p)
                return original(o, lengths)
            net.decoder = capture
            counter = {'n': 0}
            handle = net.nn.nn.register_forward_hook(lambda *args: counter.update(n=counter['n']+1))
            probabilities, decoded = {}, []
            for row in rows:
                captured.clear()
                legacy = recognize(net, [row])[0]
                if len(captured) != 1:
                    raise ValueError('Expected exactly one original decoder call')
                p = captured[0]
                custom = ''.join(id_text[i] for i in greedy(p))
                if custom != legacy:
                    parity.append({'pass': pass_index, 'model': name, 'id': row['id'], 'original': legacy, 'custom': custom})
                labels, mass = prefix_beam(p, plan['beam_width'])[0]
                text = ''.join(id_text[i] for i in labels)
                probabilities[row['id']] = p
                decoded.append({'greedy': custom, 'beam32': text, 'beam_logmass': mass})
                capture_records.append({'pass': pass_index, 'model': name, 'id': row['id'], 'image_sha256': row['image_sha256'],
                                        'shape': list(p.shape), 'matrix_sha256': hashlib.sha256(p.astype(np.float32).tobytes()).hexdigest()})
            handle.remove()
            after = tensor_manifest(net.nn)
            if before != after:
                raise ValueError('Evaluation changed weight tensors')
            tensor_checks[str(pass_index)+'/'+name] = {'before': before, 'after': after, 'codec': codec}
            net.decoder = original
            filename = 'posterior_pass'+str(pass_index)+'_'+name+'.npz'
            np.savez_compressed(a.out/filename, **probabilities)
            files[filename] = sha(a.out/filename)
            if pass_index == 1:
                prior = np.load(a.out/('posterior_pass0_'+name+'.npz'), allow_pickle=False)
                matrix_replay += [{'model': name, 'id': r['id']} for r in rows if not np.array_equal(prior[r['id']], probabilities[r['id']])]
            outputs[name] = decoded
            calls[name] = counter['n']
            if counter['n'] != len(rows):
                raise ValueError('Unexpected real neural forward-call count')
            del net
        passes.append(outputs)
        counts.append(calls)
    if parity:
        save(a.out/'interface_parity_failure.json', parity)
        raise ValueError('Original/custom decoder parity failed')
    cached = {r['id']: r for r in read(a.repo/'results/kraken_expansion/runs/expanded_200/result.json')['rows']}
    info = []
    if fresh_rows:
        for r in training:
            with Image.open(r['path']) as im:
                feat = image_features(im)
            info.append({'id': r['id'], 'text': r['reference'], 'features': feat})
    for index, (r, output) in enumerate(zip(rows, scored)):
        for name in models:
            for decoder in ['greedy', 'beam32']:
                output['predictions'][name+'_'+decoder] = passes[0][name][index][decoder]
        if r['id'] in cached:
            near, identity = cached[r['id']]['predictions']['nearest_image'], cached[r['id']]['nearest_train_id']
        else:
            with Image.open(r['path']) as im:
                near, identity = nearest_text(im, info)
        output['predictions']['nearest_image'] = near
        output['nearest_train_id'] = identity
        output['errors'] = {k: levenshtein(r['reference'], v) for k, v in output['predictions'].items()}
    replay = [{'model': name, 'id': r['id'], 'decoder': decoder} for name in models for index, r in enumerate(rows)
              for decoder in ['greedy', 'beam32'] if passes[0][name][index][decoder] != passes[1][name][index][decoder]]
    summary = grouped(scored)
    result = {'status': 'EXECUTED_COMMON_SPATIAL_RETRAINING_EVALUATION', 'plan_sha256': sha(a.plan),
              'model_sha256': {k: sha(v) for k, v in models.items()}, 'prepared_dataset_sha256': plan['prepared_dataset_sha256'],
              'fresh_status': fresh['status'], 'fresh_result_sha256': sha(fresh_root/'fresh_result.json'),
              'fresh_dataset_sha256': fresh.get('dataset_sha256'), 'primary_status': 'AVAILABLE' if fresh_rows else 'BLOCKED',
              'primary_fresh_all': summary['fresh_reserved']['all'], 'primary_fresh_unseen': summary['fresh_reserved']['unseen'],
              'metrics': summary, 'rows': scored, 'all_pass_results': passes, 'forward_calls': counts,
              'interface_parity_checks': len(rows)*len(models)*2, 'interface_parity_differences': parity,
              'matrix_replay_differences': matrix_replay, 'text_replay_differences': replay, 'posterior_file_sha256': files,
              'evaluation_character_coverage': {role: dict(Counter(c for r in rows if r['role'] == role for c in r['reference'] if c not in ''.join(tensor_checks['0/source']['codec']))) for role in ['historical_development', 'reserved', 'fresh_reserved']},
              'source_weights_unchanged': sha(models['source']) == plan['source_model_sha256'],
              'run_id': os.getenv('GITHUB_RUN_ID'), 'execution_commit': os.getenv('GITHUB_SHA'), 'environment': environment(),
              'seconds_common_evaluation': time.perf_counter()-started, 'expert_review': 'NOT_REVIEWED', 'translation': 'NOT_RUN'}
    save(a.out/'capture_records.json', capture_records)
    save(a.out/'tensor_checks.json', tensor_checks)
    save(a.out/'result.json', result)
    print('SHARED_COMMON_RESULT='+json.dumps({k: result[k] for k in ['status', 'primary_status', 'primary_fresh_all', 'primary_fresh_unseen', 'forward_calls', 'text_replay_differences', 'matrix_replay_differences']}), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['train', 'evaluate'])
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--variant', choices=['repeat', 'random_ink', 'shared_ink'])
    p.add_argument('--runs', type=Path)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    try:
        train(a) if a.command == 'train' else evaluate(a)
    except Exception as error:
        save(a.out/'failure.json', {'error': str(error), 'traceback': traceback.format_exc(), 'run_id': os.getenv('GITHUB_RUN_ID'), 'execution_commit': os.getenv('GITHUB_SHA')})
        raise
