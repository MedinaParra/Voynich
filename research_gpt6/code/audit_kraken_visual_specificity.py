#!/usr/bin/env python3
"""Audit exported input-control evidence; does not execute Kraken or certify labels."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from audit_kraken_stage2 import edit


def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pixels(p):
    with Image.open(p) as im: return np.asarray(im.convert('RGB'))
def multiset(a):
    a = a.astype(np.uint32)
    return np.sort(((a[:, :, 0] << 16) + (a[:, :, 1] << 8) + a[:, :, 2]).ravel())


def run(bundle, repo):
    plan_path = repo / 'data/kraken_visual_specificity_plan.json'
    plan = read(plan_path); result = read(bundle / 'result.json')
    frozen = read(repo / plan['frozen_dataset_path'])
    old = read(repo / plan['previous_result_path'])
    prepared = read(bundle / 'data/dataset.json')
    permutation = read(bundle / 'permutation_counts.json')
    checks = 0; mismatches = []
    def check(name, actual, expected=True):
        nonlocal checks
        checks += 1
        equal = math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-12) if isinstance(actual, (int, float)) and isinstance(expected, (int, float)) else actual == expected
        if not equal: mismatches.append({'check': name, 'actual': actual, 'expected': expected})
    check('plan_sha256', result['plan_sha256'], sha(plan_path))
    check('model_file_sha256', sha(repo / plan['model_path']), plan['model_sha256'])
    check('reported_model_sha256', result['model_sha256'], plan['model_sha256'])
    check('forward_counter_positive_control_passed', result['instrumentation_valid'])
    check('forward_counter_invalid_intact_rows', result['instrumentation_invalid_rows'], [])
    check('frozen_dataset_sha256', sha(repo / plan['frozen_dataset_path']), plan['frozen_dataset_sha256'])
    check('previous_result_sha256', sha(repo / plan['previous_result_path']), plan['previous_result_sha256'])
    check('prepared_records', len(prepared), 122)
    check('prepared_unique_keys', len({(r['id'], r['variant']) for r in prepared}), 122)
    by_frozen = {(r['id'], r['variant']): r for r in frozen}
    by_row = {}
    for row in prepared:
        key = (row['id'], row['variant']); expected = by_frozen[key]
        image_path = bundle / 'data' / row['variant'] / Path(row['path']).name
        a = pixels(image_path)
        for k in ['text', 'image_sha256', 'pixel_sha256', 'crop_size', 'role']:
            check(str(key) + '/' + k, row[k], expected[k])
        check(str(key) + '/actual_png_hash', sha(image_path), expected['image_sha256'])
        check(str(key) + '/actual_pixel_hash', hashlib.sha256(a.tobytes()).hexdigest(), expected['pixel_sha256'])
        check(str(key) + '/label_file', image_path.with_suffix('.gt.txt').read_text(), expected['text'])
        if row['variant'] == 'repaired': by_row[row['id']] = row
    rows = [r for r in prepared if r['variant'] == 'repaired']
    all_outputs = {}
    for condition in plan['conditions']:
        outputs = read(bundle / 'predictions' / (condition + '.json')); all_outputs[condition] = outputs
        check(condition + '/row_count', len(outputs), 61)
        check(condition + '/ordered_ids', [r['id'] for r in outputs], [r['id'] for r in rows])
        for out in outputs:
            row = by_row[out['id']]; name = condition + '/' + row['id']
            src_path = bundle / 'data/repaired' / Path(row['path']).name
            out_path = bundle / 'inputs' / condition / Path(out['input_path']).name
            a = pixels(src_path); b = pixels(out_path)
            check(name + '/reference', out['reference'], row['text'])
            check(name + '/role', out['role'], row['role'])
            check(name + '/source_hash', out['source_sha256'], row['image_sha256'])
            check(name + '/input_hash', out['input_sha256'], sha(out_path))
            check(name + '/dimensions', list(b.shape[1::-1]), row['crop_size'])
            check(name + '/dimensions_metadata', out['input_size'], row['crop_size'])
            check(name + '/forward_count_nonnegative_integer', isinstance(out['network_forward_calls'], int) and out['network_forward_calls'] >= 0)
            if condition == 'intact': check(name + '/positive_forward_control', out['status'] == 'OK' and out['network_forward_calls'] > 0)
            if condition == 'intact': check(name + '/actual_pixels', np.array_equal(a, b))
            elif condition == 'mirror_x': check(name + '/actual_mirror_pixels', np.array_equal(a[:, ::-1], b))
            elif condition == 'white': check(name + '/actual_white_pixels', bool(np.all(b == 255)))
            else:
                check(name + '/pixel_multiset', np.array_equal(multiset(a), multiset(b)))
                check(name + '/order_is_permutation', sorted(out['tile_order']), list(range(8)))
                check(name + '/nonidentity_order', out['tile_order'] != list(range(8)))
                check(name + '/tile_boundaries', out['tile_boundaries'], np.linspace(0, a.shape[1], 9, dtype=int).tolist())
    replay_by = {r['id']: r['predictions']['kraken'] for r in old['rows']}
    replay_differences = []
    for out in all_outputs['intact']:
        if out['role'] != 'train':
            same = out['status'] == 'OK' and out['prediction'] == replay_by[out['id']]
            check('replay/' + out['id'], same)
            if not same: replay_differences.append(out['id'])
    check('reported_replay_differences', result['replay_mismatches'], replay_differences)
    recomputed = {}
    for offset, role in enumerate(['train', 'development_evaluation']):
        reference_rows = [r for r in rows if r['role'] == role]
        by_folio = defaultdict(list)
        for i, r in enumerate(reference_rows): by_folio[r['folio']].append(i)
        expected_groups = []
        for folio, indices in sorted(by_folio.items()):
            indices.sort(key=lambda i: (reference_rows[i]['crop_size'][0] / reference_rows[i]['crop_size'][1], reference_rows[i]['id']))
            mid = len(indices) // 2
            for half, group in enumerate((indices[:mid], indices[mid:])):
                expected_groups.append({'folio': folio, 'aspect_half': half, 'indices': group,
                                        'row_ids': [reference_rows[i]['id'] for i in group]})
        rng = np.random.default_rng(plan['seed'] + offset)
        draws = np.tile(np.arange(len(reference_rows)), (plan['permutations'], 1))
        for draw in draws:
            for group in expected_groups: draw[group['indices']] = rng.permutation(group['indices'])
        for condition in plan['conditions']:
            outs = [r for r in all_outputs[condition] if r['role'] == role]
            summary = result['results'][role][condition]; name = role + '/' + condition
            failed = [r['id'] for r in outs if r['status'] != 'OK']
            check(name + '/failed_rows', summary['failed_rows'], failed)
            check(name + '/called_rows', summary['network_called_rows'], sum(r['network_forward_calls'] > 0 for r in outs))
            check(name + '/short_circuit_rows', summary['preprocessing_short_circuit_rows'], [r['id'] for r in outs if r['status'] == 'OK' and r['network_forward_calls'] == 0])
            check(name + '/nonempty_outputs', summary['nonempty_predictions'], sum(bool(r['prediction']) for r in outs if r['status'] == 'OK'))
            if failed:
                check(name + '/incomplete_not_scored', summary['metrics'], None)
                continue
            target = [r['text'] for r in reference_rows]; predicted = [r['prediction'] for r in outs]
            errors = sum(edit(a, b) for a, b in zip(target, predicted)); n = sum(map(len, target))
            for k, value in {'errors': errors, 'reference_units': n, 'gcr': errors/n, 'predicted_units': sum(map(len, predicted))}.items():
                check(name + '/' + k, summary['metrics'][k], value)
            parts = summary['metrics']['alignment']
            check(name + '/alignment_errors', parts['substitutions'] + parts['deletions'] + parts['insertions'], errors)
            check(name + '/alignment_reference_length', parts['matches'] + parts['substitutions'] + parts['deletions'], n)
            check(name + '/alignment_predicted_length', parts['matches'] + parts['substitutions'] + parts['insertions'], sum(map(len, predicted)))
            matrix = np.array([[edit(a, b) for a in target] for b in predicted])
            null = matrix[np.arange(len(outs))[None, :], draws].sum(axis=1)
            saved_null = permutation[name]
            check(name + '/permutation_groups', saved_null['groups'], expected_groups)
            check(name + '/all_permutation_errors', saved_null['null_error_counts'], null.tolist())
            check(name + '/permutation_observed', saved_null['observed_errors'], errors)
            for k, v in {'null_mean_errors': float(null.mean()), 'null_median_errors': float(np.median(null)),
                         'null_2_5_percentile': float(np.percentile(null, 2.5)), 'null_97_5_percentile': float(np.percentile(null, 97.5)),
                         'null_errors_le_observed': int((null <= errors).sum()),
                         'diagnostic_lower_tail_fraction': (1 + int((null <= errors).sum())) / (len(null) + 1)}.items():
                check(name + '/' + k, saved_null[k], v)
                check(name + '/summary_' + k, summary['reference_permutation'][k], v)
            recomputed[name] = {'errors': errors, 'reference_units': n, 'gcr': errors/n,
                                'diagnostic_lower_tail_fraction': saved_null['diagnostic_lower_tail_fraction']}
    return {'status': 'PASS_EXPORTED_DATA_AUDIT' if not mismatches else 'FAIL', 'checks': checks,
            'mismatches': mismatches, 'recomputed': recomputed,
            'scope': 'Actual exported inputs, preserved predictions and arithmetic audited. No new inference, expert label validation or proof of exchangeability.',
            'translation': 'NOT_RUN'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--repo', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); result = run(args.bundle, args.repo)
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=True))
    if result['mismatches']: raise SystemExit(1)
