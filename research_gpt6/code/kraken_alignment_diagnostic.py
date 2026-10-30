#!/usr/bin/env python3
"""Exploratory data/search diagnosis on frozen crops and CTC posteriors.

No training, new network inference, label correction, or translation.
"""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import time

import numpy as np
from PIL import Image


def raw(path):
    path = Path(path)
    return path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix(path.suffix + '.gz').read_bytes())


def read(path):
    return json.loads(raw(path))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def ctc_log_probability(probabilities, target, blank=0):
    """Exact sum over CTC paths for one fixed target, in float64 log space."""
    p = np.asarray(probabilities, dtype=np.float64)
    if p.ndim != 2 or p.shape[1] < 2:
        raise ValueError('Expected time x class probabilities')
    if not np.isfinite(p).all() or (p < 0).any() or (p > 1).any():
        raise ValueError('Invalid probabilities')
    if not np.allclose(p.sum(axis=1), 1, atol=1e-5, rtol=0):
        raise ValueError('Unnormalized probabilities')
    if not 0 <= blank < p.shape[1]:
        raise ValueError('Invalid blank')
    if any(int(c) != c or c == blank or not 0 <= c < p.shape[1] for c in target):
        raise ValueError('Invalid target label')
    states = np.array([blank] + [v for c in target for v in (int(c), blank)])
    alpha = np.full(len(states), -np.inf)
    alpha[0] = 0
    skip = (states[2:] != blank) & (states[2:] != states[:-2])
    logp = np.full(p.shape, -np.inf)
    np.log(p, out=logp, where=p > 0)
    for frame in logp:
        nxt = alpha.copy()
        nxt[1:] = np.logaddexp(nxt[1:], alpha[:-1])
        nxt[2:] = np.logaddexp(nxt[2:], np.where(skip, alpha[:-2], -np.inf))
        alpha = nxt + frame[states]
    return float(np.logaddexp(alpha[-1], alpha[-2])) if len(states) > 1 else float(alpha[0])


def overlap_mask(target, other_masks):
    """Union shared pixels, using crop-local masks in one global frame."""
    bounds, mask = target
    x0, y0, x1, y1 = bounds
    shared = np.zeros(mask.shape, dtype=bool)
    neighbors = []
    for other_id, (ob, om) in other_masks:
        a, b, c, d = max(x0, ob[0]), max(y0, ob[1]), min(x1, ob[2]), min(y1, ob[3])
        if a >= c or b >= d:
            continue
        intersection = mask[b-y0:d-y0, a-x0:c-x0] & om[b-ob[1]:d-ob[1], a-ob[0]:c-ob[0]]
        count = int(intersection.sum())
        if count:
            shared[b-y0:d-y0, a-x0:c-x0] |= intersection
            neighbors.append({'id': other_id, 'shared_mask_pixels': count})
    return shared, neighbors


def finite(value):
    return float(value) if math.isfinite(value) else None


def compare(a, b, tolerance):
    if a == b:
        return 'equal'
    if a > b + tolerance:
        return 'above'
    if b > a + tolerance:
        return 'below'
    return 'equal'


def geometry(rows, prepared, plan):
    masks = {}
    by_folio = defaultdict(list)
    for row in rows:
        image = prepared / 'crops' / Path(row['path']).name
        mask = prepared / 'crops' / Path(row['mask_path']).name
        if digest(image.read_bytes()) != row['image_sha256'] or digest(mask.read_bytes()) != row['mask_sha256']:
            raise ValueError('Changed image/mask ' + row['id'])
        with Image.open(mask) as im:
            m = np.asarray(im.convert('L')) > 0
        x0, y0, x1, y1 = row['bounds']
        if m.shape != (y1-y0, x1-x0) or not m.any():
            raise ValueError('Invalid mask frame ' + row['id'])
        masks[row['id']] = (row['bounds'], m)
        by_folio[row['folio']].append(row['id'])
    out = []
    for row in rows:
        identity = row['id']
        shared, neighbors = overlap_mask(masks[identity], [(j, masks[j]) for j in by_folio[row['folio']] if j != identity])
        mask = masks[identity][1]
        with Image.open(prepared / 'crops' / Path(row['path']).name) as im:
            gray = np.asarray(im.convert('L'))
        median = float(np.median(gray[mask]))
        proxies = {}
        for delta in plan['ink_proxy_median_deltas']:
            dark = mask & (gray <= median-delta)
            n = int(dark.sum())
            overlap = int((dark & shared).sum())
            proxies[str(delta)] = {'threshold_gray': median-delta, 'dark_pixels': n, 'shared_dark_pixels': overlap,
                                    'shared_fraction': overlap/n if n else None}
        pixels = int(mask.sum())
        count = int(shared.sum())
        fraction = count/pixels
        group = 'low_le_1pct' if fraction <= plan['no_overlap_threshold'] else ('high_ge_25pct' if fraction >= plan['overlap_threshold'] else 'middle')
        out.append({'id': identity, 'folio': row['folio'], 'role': row['role'], 'reference': row['reference'],
                    'image_sha256': row['image_sha256'], 'mask_sha256': row['mask_sha256'], 'mask_pixels': pixels,
                    'shared_mask_pixels': count, 'shared_mask_fraction': fraction, 'overlap_group': group,
                    'shared_mask_array_sha256': digest(shared.tobytes(order='C')), 'neighbors': neighbors,
                    'median_mask_gray': median, 'ink_proxies': proxies})
    return out


def summary(rows):
    if not rows:
        return None
    wrong = [r for r in rows if r['reference'] != r['beam_prediction']]
    informative = [r for r in rows if len(r['same_length_candidates']) > 1]
    margins = [r['log_margin_per_reference_character'] for r in rows if r['log_margin_per_reference_character'] is not None]
    n = sum(len(r['reference']) for r in rows)
    return {'words': len(rows), 'eva_characters': n, 'beam_errors': sum(r['beam_errors'] for r in rows),
            'beam_cer': sum(r['beam_errors'] for r in rows)/n, 'beam_exact_words': len(rows)-len(wrong),
            'incorrect_predictions': len(wrong),
            'incorrect_reference_mass_vs_prediction': {k: sum(r['reference_mass_vs_prediction'] == k for r in wrong) for k in ['above', 'equal', 'below']},
            'reference_zero_probability': sum(r['reference_log_probability'] is None for r in rows),
            'temporal_capacity_failures': sum(r['frames'] < r['minimum_target_frames'] for r in rows),
            'median_log_margin_per_reference_character': statistics.median(margins) if margins else None,
            'non_singleton_candidate_pools': len(informative),
            'reference_unique_highest': sum(r['reference_rank_min'] == r['reference_rank_max'] == 1 for r in informative),
            'reference_tied_highest': sum(r['reference_rank_min'] == 1 and r['reference_rank_max'] > 1 for r in informative),
            'mean_pairwise_reference_win_fraction': statistics.mean(r['pairwise_reference_win_fraction'] for r in informative) if informative else None}


def grouped_summary(rows):
    out = {}
    for role in ['historical_development', 'reserved']:
        rs = [r for r in rows if r['role'] == role]
        out[role] = {'all': summary(rs), 'seen': summary([r for r in rs if r['seen_in_training']]),
                     'unseen': summary([r for r in rs if not r['seen_in_training']]),
                     'length_1_4': summary([r for r in rs if len(r['reference']) <= 4]),
                     'length_5_6': summary([r for r in rs if 5 <= len(r['reference']) <= 6]),
                     'length_7_plus': summary([r for r in rs if len(r['reference']) >= 7]),
                     'by_overlap': {g: summary([r for r in rs if r['overlap_group'] == g]) for g in ['low_le_1pct', 'middle', 'high_ge_25pct']},
                     'by_folio': {f: summary([r for r in rs if r['folio'] == f]) for f in sorted({r['folio'] for r in rs})}}
    return out


def run(plan_path, repo, out, protocol_commit):
    started = time.perf_counter()
    plan = read(plan_path)
    posterior = repo / plan['posterior_root']
    for path, expected in [(repo / plan['prepared_dataset_path'], plan['prepared_dataset_sha256']),
                           (repo / plan['source_model_path'], plan['source_model_sha256']),
                           (posterior / 'codec.json', plan['codec_sha256']),
                           (posterior / 'posterior_pass0.npz', plan['posterior_sha256']),
                           (posterior / 'result.json.gz', plan['posterior_archive_sha256'])]:
        if digest(raw(path)) != expected:
            raise ValueError('Frozen input changed ' + str(path))
    source = read(repo / plan['prepared_dataset_path'])
    previous = read(posterior / 'result.json')
    codec = read(posterior / 'codec.json')
    if len(source) != plan['geometry_rows'] or len(previous['rows']) != plan['posterior_rows']:
        raise ValueError('Changed sample count')
    source_by_id = {r['id']: r for r in source}
    prepared = repo / 'results/kraken_expansion/followup_prepared'
    if not (prepared / 'crops' / Path(source[0]['path']).name).exists():
        from audit_kraken_expansion import restore_inputs
        restore_inputs(repo / 'results/kraken_expansion/primary_geometry', prepared, repo)
    geometric = geometry(source, prepared, plan)
    by_id = {r['id']: r for r in geometric}
    save(out / 'geometry_rows.json', geometric)
    pools = defaultdict(set)
    for row in previous['rows']:
        pools[(row['folio'], len(row['reference']))].add(row['reference'])
    cache = np.load(posterior / 'posterior_pass0.npz', allow_pickle=False)
    tolerance = plan['log_probability_tie_tolerance']
    rows = []
    total_scores = 0
    def labels(text):
        if any(c not in codec or len(codec[c]) != 1 for c in text):
            raise ValueError('Text outside fixed single-character codec')
        return tuple(codec[c][0] for c in text)
    for row in previous['rows']:
        identity = row['id']
        if source_by_id[identity]['reference'] != row['reference']:
            raise ValueError('Changed reference')
        p = cache[identity]
        candidates = sorted(pools[(row['folio'], len(row['reference']))])
        texts = sorted(set(candidates + [row['predictions']['beam32']]))
        scores = {text: ctc_log_probability(p, labels(text), plan['ctc_blank']) for text in texts}
        total_scores += len(scores)
        reference_score = scores[row['reference']]
        beam_score = scores[row['predictions']['beam32']]
        others = [scores[text] for text in candidates if text != row['reference']]
        better = sum(compare(v, reference_score, tolerance) == 'above' for v in others)
        tied = sum(compare(v, reference_score, tolerance) == 'equal' for v in others)
        wins = sum(compare(reference_score, v, tolerance) == 'above' for v in others)
        margin = reference_score-beam_score if math.isfinite(reference_score) and math.isfinite(beam_score) else None
        rows.append({'id': identity, 'folio': row['folio'], 'role': row['role'], 'reference': row['reference'],
                     'seen_in_training': row['seen_in_training'], 'beam_prediction': row['predictions']['beam32'],
                     'beam_errors': row['errors']['beam32'], 'frames': len(p),
                     'matrix_sha256': digest(np.asarray(p, dtype=np.float32).tobytes(order='C')),
                     'minimum_target_frames': len(row['reference']) + sum(a == b for a, b in zip(row['reference'], row['reference'][1:])),
                     'reference_log_probability': finite(reference_score), 'beam_log_probability': finite(beam_score),
                     'reference_mass_vs_prediction': compare(reference_score, beam_score, tolerance),
                     'log_margin_per_reference_character': margin/len(row['reference']) if margin is not None else None,
                     'same_length_candidates': [{'text': text, 'log_probability': finite(scores[text])} for text in candidates],
                     'reference_rank_min': better+1, 'reference_rank_max': better+tied+1,
                     'pairwise_reference_win_fraction': (wins + .5*tied)/len(others) if others else None,
                     'shared_mask_fraction': by_id[identity]['shared_mask_fraction'], 'overlap_group': by_id[identity]['overlap_group']})
    primary = [r for r in rows if r['role'] == 'reserved' and not r['seen_in_training']]
    if len(primary) != plan['primary_words'] or sum(len(r['reference']) for r in primary) != plan['primary_eva_characters']:
        raise ValueError('Changed primary stratum')
    save(out / 'posterior_rows.json', rows)
    geometric_summary = {}
    for role in sorted({r['role'] for r in geometric}):
        rs = [r for r in geometric if r['role'] == role]
        geometric_summary[role] = {'words': len(rs), 'overlap_groups': {g: sum(r['overlap_group'] == g for r in rs) for g in ['low_le_1pct', 'middle', 'high_ge_25pct']},
                                   'median_shared_mask_fraction': statistics.median(r['shared_mask_fraction'] for r in rs),
                                   'median_shared_dark_fraction': {str(d): statistics.median(v) if (v := [r['ink_proxies'][str(d)]['shared_fraction'] for r in rs if r['ink_proxies'][str(d)]['shared_fraction'] is not None]) else None for d in plan['ink_proxy_median_deltas']}}
    result = {'status': 'EXECUTED_EXPLORATORY_ALIGNMENT_AND_SEARCH_DIAGNOSTIC', 'protocol_commit': protocol_commit,
              'plan_sha256': digest(raw(plan_path)), 'base_commit': plan['base_commit'], 'source_model_sha256': plan['source_model_sha256'],
              'prepared_dataset_sha256': plan['prepared_dataset_sha256'], 'posterior_sha256': plan['posterior_sha256'],
              'geometry_words': len(geometric), 'posterior_words': len(rows), 'exact_ctc_text_scores': total_scores,
              'primary_reserved_unseen': summary(primary), 'metrics': grouped_summary(rows), 'geometric_summary': geometric_summary,
              'row_file_sha256': {name: digest((out / name).read_bytes()) for name in ['geometry_rows.json', 'posterior_rows.json']},
              'new_training': 'NOT_RUN', 'new_network_inference': 'NOT_RUN', 'translation': 'NOT_RUN', 'expert_review': 'NOT_REVIEWED',
              'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'pillow': Image.__version__},
              'seconds': time.perf_counter()-started,
              'scope': 'Diagnostic on previously examined candidate labels; exact fixed-string CTC mass and annotation-mask overlap do not certify readings or meaning.'}
    save(out / 'result.json', result)
    print(json.dumps({k: result[k] for k in ['status', 'geometry_words', 'posterior_words', 'exact_ctc_text_scores', 'primary_reserved_unseen']}))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--protocol-commit', required=True)
    args = parser.parse_args()
    run(args.plan, args.repo, args.out, args.protocol_commit)
