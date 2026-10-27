#!/usr/bin/env python3
"""Frozen-model input controls, with explicit separation of pipeline and network."""
import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import time
import traceback
import warnings

import numpy as np
from PIL import Image, ImageOps

from kraken_repair_experiment import prepare, save, sha
from kraken_row_tools import levenshtein, row_image_name


def decomposition(reference, prediction):
    """One minimal alignment; ties prefer match/substitution, deletion, insertion."""
    n, m = len(reference), len(prediction)
    d = np.zeros((n + 1, m + 1), dtype=np.int32)
    d[:, 0] = np.arange(n + 1); d[0, :] = np.arange(m + 1)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i, j] = min(d[i-1, j-1] + (reference[i-1] != prediction[j-1]),
                          d[i-1, j] + 1, d[i, j-1] + 1)
    counts = Counter(matches=0, substitutions=0, deletions=0, insertions=0)
    i, j = n, m
    while i or j:
        if i and j and d[i, j] == d[i-1, j-1] + (reference[i-1] != prediction[j-1]):
            counts['matches' if reference[i-1] == prediction[j-1] else 'substitutions'] += 1
            i -= 1; j -= 1
        elif i and d[i, j] == d[i-1, j] + 1:
            counts['deletions'] += 1; i -= 1
        else:
            counts['insertions'] += 1; j -= 1
    assert counts['substitutions'] + counts['deletions'] + counts['insertions'] == int(d[n, m])
    return dict(counts)


def transform(im, condition, row_id, seed):
    im = im.convert('RGB')
    metadata = {}
    if condition == 'intact':
        result = im.copy()
    elif condition == 'mirror_x':
        result = ImageOps.mirror(im)
    elif condition == 'tile_shuffle_8':
        if im.width < 8: raise ValueError('Image too narrow for eight tiles')
        boundaries = np.linspace(0, im.width, 9, dtype=int).tolist()
        digest = hashlib.sha256((str(seed) + ':' + row_id).encode()).digest()
        order = list(range(8)); random.Random(int.from_bytes(digest[:8], 'big')).shuffle(order)
        if order == list(range(8)): order = order[1:] + order[:1]
        result = Image.new('RGB', im.size)
        x = 0
        for k in order:
            tile = im.crop((boundaries[k], 0, boundaries[k+1], im.height))
            result.paste(tile, (x, 0)); x += tile.width
        if x != im.width: raise ValueError('Lost tile pixels')
        metadata = {'tile_boundaries': boundaries, 'tile_order': order}
    elif condition == 'white':
        result = Image.new('RGB', im.size, 'white')
    else: raise ValueError('Unknown input condition')
    if result.size != im.size: raise ValueError('Changed input dimensions')
    return result, metadata


def groups_and_draws(rows, count, seed):
    by_folio = defaultdict(list)
    for i, r in enumerate(rows): by_folio[r['folio']].append(i)
    groups = []
    for folio, indices in sorted(by_folio.items()):
        indices.sort(key=lambda i: (rows[i]['crop_size'][0] / rows[i]['crop_size'][1], rows[i]['id']))
        mid = len(indices) // 2
        for half, group in enumerate((indices[:mid], indices[mid:])):
            if len(group) < 2: raise ValueError('Singleton permutation stratum')
            groups.append({'folio': folio, 'aspect_half': half, 'indices': group,
                           'row_ids': [rows[i]['id'] for i in group]})
    rng = np.random.default_rng(seed)
    draws = np.tile(np.arange(len(rows)), (count, 1))
    for k in range(count):
        for g in groups: draws[k, g['indices']] = rng.permutation(g['indices'])
    return groups, draws


def score(rows, predictions):
    errors = sum(levenshtein(r['text'], p) for r, p in zip(rows, predictions))
    n = sum(len(r['text']) for r in rows)
    parts = Counter()
    for r, p in zip(rows, predictions): parts.update(decomposition(r['text'], p))
    return {'errors': errors, 'reference_units': n, 'gcr': errors / n,
            'predicted_units': sum(map(len, predictions)), 'alignment': dict(parts)}


def permutation_summary(rows, predictions, groups, draws):
    matrix = np.array([[levenshtein(r['text'], p) for r in rows] for p in predictions], dtype=np.int32)
    observed = int(np.trace(matrix))
    null = matrix[np.arange(len(rows))[None, :], draws].sum(axis=1)
    return {'observed_errors': observed, 'draws': len(draws), 'groups': groups,
            'seed_algorithm': 'NumPy default_rng/PCG64, common draws across conditions',
            'null_mean_errors': float(null.mean()), 'null_median_errors': float(np.median(null)),
            'null_2_5_percentile': float(np.percentile(null, 2.5)),
            'null_97_5_percentile': float(np.percentile(null, 97.5)),
            'null_errors_le_observed': int((null <= observed).sum()),
            'diagnostic_lower_tail_fraction': (1 + int((null <= observed).sum())) / (len(draws) + 1),
            'null_error_counts': null.tolist(),
            'interpretation': 'Descriptive conditional permutation diagnostic; exchangeability and expert reference validity are not established.'}


def infer_one(net, im, row_id, path, calls):
    from kraken import rpred
    from kraken.containers import Segmentation, BBoxLine
    before = calls[0]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:
            seg = Segmentation(type='bbox', imagename=str(path), text_direction='horizontal-lr',
                               script_detection=False, lines=[BBoxLine(id=row_id, bbox=(0, 0, im.width, im.height))])
            outputs = list(rpred.rpred(net, im, seg, bidi_reordering=False))
            if len(outputs) != 1: raise ValueError('Expected exactly one recognition record, got ' + str(len(outputs)))
            return {'status': 'OK', 'prediction': outputs[0].prediction,
                    'network_forward_calls': calls[0] - before,
                    'warnings': [str(w.message) for w in caught]}
        except Exception as error:
            return {'status': 'ERROR', 'prediction': None, 'network_forward_calls': calls[0] - before,
                    'warnings': [str(w.message) for w in caught],
                    'error': type(error).__name__ + ': ' + str(error)}


def run(args):
    started = time.perf_counter(); args.out.mkdir(parents=True, exist_ok=True)
    plan = json.loads(args.plan.read_text()); plan_sha = sha(args.plan)
    def pinned(path_key, hash_key):
        path = args.repo / plan[path_key]
        if sha(path) != plan[hash_key]: raise ValueError('Frozen input changed: ' + path_key)
        return path
    model = pinned('model_path', 'model_sha256')
    old_result = json.loads(pinned('previous_result_path', 'previous_result_sha256').read_text())
    frozen = json.loads(pinned('frozen_dataset_path', 'frozen_dataset_sha256').read_text())
    preparation_path = pinned('preparation_plan_path', 'preparation_plan_sha256')
    preparation = json.loads(preparation_path.read_text()); preparation['_sha256'] = sha(preparation_path)
    records, mapping, _ = prepare(preparation, args.repo, args.out / 'data', args.repo / plan['source_cache'])
    frozen_by = {(r['id'], r['variant']): r for r in frozen}
    for row in records:
        previous = frozen_by[(row['id'], row['variant'])]
        for key in ['text', 'image_sha256', 'pixel_sha256', 'crop_size', 'role']:
            if row[key] != previous[key]: raise ValueError('Regenerated input differs: ' + row['id'] + '/' + key)
    records = [r for r in records if r['variant'] == 'repaired']
    if Counter(r['role'] for r in records) != Counter(plan['row_counts']): raise ValueError('Changed row split')
    if importlib.metadata.version('kraken') != '7.1': raise ValueError('Wrong Kraken version')
    import torch
    from kraken.lib.models import load_any
    torch.set_num_threads(2)
    torch.manual_seed(plan['seed']); torch.use_deterministic_algorithms(True)
    net = load_any(str(model), train=False, device='cpu')
    calls = [0]
    def forward_hook(module, inputs, output): calls[0] += 1
    hook = net.nn.register_forward_hook(forward_hook)
    results = {}; per_condition = {}
    try:
        for condition in plan['conditions']:
            outputs = []
            for row in records:
                with Image.open(row['path']) as src: im, metadata = transform(src, condition, row['id'], plan['seed'])
                path = args.out / 'inputs' / condition / row_image_name(row['id'])
                path.parent.mkdir(parents=True, exist_ok=True); im.save(path)
                prediction = infer_one(net, im, row['id'], path, calls)
                outputs.append({'id': row['id'], 'folio': row['folio'], 'role': row['role'],
                                'reference': row['text'], 'source_sha256': row['image_sha256'],
                                'input_sha256': sha(path), 'input_size': list(im.size),
                                'input_path': str(path.resolve()), **metadata, **prediction})
            per_condition[condition] = outputs
            save(args.out / 'predictions' / (condition + '.json'), outputs)
    finally: hook.remove()
    replay = {r['id']: r['predictions']['kraken'] for r in old_result['rows']}
    replay_mismatches = [r['id'] for r in per_condition['intact']
                         if r['role'] != 'train' and (r['status'] != 'OK' or r['prediction'] != replay[r['id']])]
    nulls = {}
    for offset, role in enumerate(['train', 'development_evaluation']):
        subset = [r for r in records if r['role'] == role]
        groups, draws = groups_and_draws(subset, plan['permutations'], plan['seed'] + offset)
        intact = [r for r in per_condition['intact'] if r['role'] == role]
        role_results = {}
        for condition in plan['conditions']:
            rows = [r for r in per_condition[condition] if r['role'] == role]
            complete = all(r['status'] == 'OK' for r in rows)
            item = {'rows': len(rows), 'failed_rows': [r['id'] for r in rows if r['status'] != 'OK'],
                    'network_called_rows': sum(r['network_forward_calls'] > 0 for r in rows),
                    'preprocessing_short_circuit_rows': [r['id'] for r in rows if r['status'] == 'OK' and r['network_forward_calls'] == 0],
                    'nonempty_predictions': sum(bool(r['prediction']) for r in rows if r['status'] == 'OK'),
                    'metrics': None}
            if complete:
                predictions = [r['prediction'] for r in rows]
                item['metrics'] = score(subset, predictions)
                item['changed_predictions_vs_intact'] = sum(r['prediction'] != a['prediction'] for r, a in zip(rows, intact))
                null = permutation_summary(subset, predictions, groups, draws)
                nulls[role + '/' + condition] = null
                item['reference_permutation'] = {k: v for k, v in null.items() if k != 'null_error_counts'}
            role_results[condition] = item
        baseline = role_results['intact']['metrics']
        for item in role_results.values():
            if item['metrics'] and baseline:
                item['error_change_vs_intact_percentage_points'] = 100 * (item['metrics']['gcr'] - baseline['gcr'])
        results[role] = role_results
    train = [r for r in records if r['role'] == 'train']
    dev = [r for r in records if r['role'] != 'train']
    seen = set(''.join(r['text'] for r in train))
    unseen = Counter(c for r in dev for c in r['text'] if c not in seen)
    names = {v: k for k, v in mapping.items()}
    result = {'status': 'EXECUTED_FROZEN_MODEL_DEVELOPMENT_DIAGNOSTIC' if not replay_mismatches else 'REPLAY_MISMATCH_REVIEW_REQUIRED',
              'date': plan['date'], 'plan_sha256': plan_sha, 'model_sha256': sha(model),
              'regenerated_original_and_repaired_records_verified': len(frozen),
              'prior_development_predictions_replayed': len(replay), 'replay_mismatches': replay_mismatches,
              'results': results, 'development_unseen_reference_unit_counts': {names.get(k, k): v for k, v in unseen.items()},
              'seconds': time.perf_counter() - started, 'run_id': os.getenv('GITHUB_RUN_ID'),
              'execution_commit': os.getenv('GITHUB_SHA'),
              'environment': {k: importlib.metadata.version(k) for k in ['torch', 'torchvision', 'kraken', 'pillow', 'numpy', 'scipy']},
              'scope': plan['scope'], 'expert_review': 'NOT_REVIEWED', 'translation': 'NOT_RUN'}
    save(args.out / 'permutation_counts.json', nulls)
    save(args.out / 'result.json', result)
    brief = {role: {c: {k: v for k, v in x.items() if k != 'reference_permutation'}
                    for c, x in conditions.items()} for role, conditions in results.items()}
    print('VISUAL_SPECIFICITY_RESULT=' + json.dumps({'status': result['status'], 'results': brief,
                                                    'replay_mismatches': replay_mismatches}, ensure_ascii=True), flush=True)
    if replay_mismatches: raise ValueError('Frozen development predictions did not replay exactly')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--plan', type=Path, required=True); p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    try: run(args)
    except Exception as error:
        save(args.out / 'failure.json', {'error': type(error).__name__ + ': ' + str(error),
                                       'traceback': traceback.format_exc(), 'run_id': os.getenv('GITHUB_RUN_ID')})
        raise
