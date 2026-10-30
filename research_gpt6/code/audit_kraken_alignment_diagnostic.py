#!/usr/bin/env python3
"""Independent scaled-probability CTC and whole-canvas overlap audit."""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics

import numpy as np
from PIL import Image


def data(path):
    b = path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix(path.suffix + '.gz').read_bytes())
    return b


def read(path):
    return json.loads(data(path))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def probability_logmass(p, target):
    """Sum paths in probability space; prune states unable to finish on time.

    Per-frame normalization plus a reachability bound prevents irrelevant early
    prefix states from dominating the scale for very long, rare target strings.
    No call to the diagnostic's log-space recurrence.
    """
    p = np.asarray(p, dtype=np.float64)
    if len(p) == 0:
        return 0.0 if not target else -math.inf
    symbols = [0]
    for token in target:
        symbols.extend([int(token), 0])
    n = len(symbols)
    needed = [0] * n
    for s in range(n-3, -1, -1):
        choices = [needed[s+1]]
        if symbols[s+2] and symbols[s+2] != symbols[s]:
            choices.append(needed[s+2])
        needed[s] = 1+min(choices)
    state = np.zeros(n, dtype=np.float64)
    state[0] = 1
    scale_log = 0.0
    for index, frame in enumerate(p):
        nxt = np.zeros(n, dtype=np.float64)
        remaining = len(p)-index-1
        for s, token in enumerate(symbols):
            if needed[s] > remaining:
                continue
            total = state[s]
            if s:
                total += state[s-1]
            if s > 1 and token != 0 and token != symbols[s-2]:
                total += state[s-2]
            nxt[s] = total*frame[token]
        scale = float(nxt.sum())
        if scale == 0:
            return -math.inf
        state = nxt/scale
        scale_log += math.log(scale)
    final = float(state[-1] + (state[-2] if n > 1 else 0))
    return math.log(final)+scale_log if final else -math.inf


def metrics(rows):
    if not rows:
        return None
    wrong = [r for r in rows if r['reference'] != r['beam_prediction']]
    multiple = [r for r in rows if len(r['same_length_candidates']) >= 2]
    characters = sum(map(len, (r['reference'] for r in rows)))
    margins = [r['log_margin_per_reference_character'] for r in rows if r['log_margin_per_reference_character'] is not None]
    return {'words': len(rows), 'eva_characters': characters, 'beam_errors': sum(r['beam_errors'] for r in rows),
            'beam_cer': sum(r['beam_errors'] for r in rows)/characters, 'beam_exact_words': len(rows)-len(wrong),
            'incorrect_predictions': len(wrong),
            'incorrect_reference_mass_vs_prediction': {c: len([r for r in wrong if r['reference_mass_vs_prediction'] == c]) for c in ['above', 'equal', 'below']},
            'reference_zero_probability': len([r for r in rows if r['reference_log_probability'] is None]),
            'temporal_capacity_failures': len([r for r in rows if r['frames'] < r['minimum_target_frames']]),
            'median_log_margin_per_reference_character': statistics.median(margins) if margins else None,
            'non_singleton_candidate_pools': len(multiple),
            'reference_unique_highest': len([r for r in multiple if r['reference_rank_min'] == 1 and r['reference_rank_max'] == 1]),
            'reference_tied_highest': len([r for r in multiple if r['reference_rank_min'] == 1 and r['reference_rank_max'] != 1]),
            'mean_pairwise_reference_win_fraction': sum(r['pairwise_reference_win_fraction'] for r in multiple)/len(multiple) if multiple else None}


def audit(bundle, repo, plan_path):
    checks = 0
    failures = []
    def check(name, actual, expected=True):
        nonlocal checks
        checks += 1
        if isinstance(actual, float) and isinstance(expected, (float, int)):
            equal = actual == expected or math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-8)
        elif isinstance(actual, np.ndarray):
            equal = bool(np.array_equal(actual, expected))
        else:
            equal = actual == expected
        if not equal:
            failures.append({'check': name, 'actual': str(actual)[:500], 'expected': str(expected)[:500]})
    plan = read(plan_path)
    result = read(bundle/'result.json')
    source = read(repo/plan['prepared_dataset_path'])
    g = read(bundle/'geometry_rows.json')
    rows = read(bundle/'posterior_rows.json')
    prior_root = repo/plan['posterior_root']
    prior = read(prior_root/'result.json')
    codec = read(prior_root/'codec.json')
    check('fixed_plan', result['plan_sha256'], sha(data(plan_path)))
    check('fixed_dataset', sha(data(repo/plan['prepared_dataset_path'])), plan['prepared_dataset_sha256'])
    check('frozen_model', sha(data(repo/plan['source_model_path'])), plan['source_model_sha256'])
    check('frozen_posterior', sha(data(prior_root/'posterior_pass0.npz')), plan['posterior_sha256'])
    check('frozen_previous_archive', sha(data(prior_root/'result.json.gz')), plan['posterior_archive_sha256'])
    check('frozen_codec', sha(data(prior_root/'codec.json')), plan['codec_sha256'])
    check('geometry_ids', [r['id'] for r in g], [r['id'] for r in source])
    check('posterior_ids', [r['id'] for r in rows], [r['id'] for r in prior['rows']])
    for name, value in result['row_file_sha256'].items():
        check(name+'/hash', sha(data(bundle/name)), value)
    by_folio = defaultdict(list)
    by_id = {r['id']: r for r in g}
    prepared = repo/'results/kraken_expansion/followup_prepared/crops'
    if not (prepared/Path(source[0]['mask_path']).name).exists():
        from audit_kraken_expansion import restore_inputs
        restore_inputs(repo/'results/kraken_expansion/primary_geometry', prepared.parent, repo)
    for r in source:
        by_folio[r['folio']].append(r)
    for folio, page in by_folio.items():
        height = max(r['bounds'][3] for r in page)
        width = max(r['bounds'][2] for r in page)
        canvas = np.zeros((height, width), dtype=np.uint16)
        local = {}
        for r in page:
            mp = prepared/Path(r['mask_path']).name
            check(r['id']+'/mask_hash', sha(mp.read_bytes()), r['mask_sha256'])
            with Image.open(mp) as im:
                m = np.array(im, dtype=np.uint8) != 0
            x0, y0, x1, y1 = r['bounds']
            canvas[y0:y1, x0:x1] += m.astype(np.uint16)
            local[r['id']] = m
        for r in page:
            identity = r['id']
            actual = by_id[identity]
            x0, y0, x1, y1 = r['bounds']
            mask = local[identity]
            shared = mask & (canvas[y0:y1, x0:x1] > 1)
            pixels, count = int(mask.sum()), int(shared.sum())
            fraction = count/pixels
            group = 'low_le_1pct' if fraction <= plan['no_overlap_threshold'] else ('high_ge_25pct' if fraction >= plan['overlap_threshold'] else 'middle')
            for key, value in [('mask_pixels', pixels), ('shared_mask_pixels', count), ('shared_mask_fraction', fraction), ('overlap_group', group), ('shared_mask_array_sha256', sha(shared.tobytes()))]:
                check(identity+'/'+key, actual[key], value)
            for key in ['folio', 'role', 'reference', 'image_sha256', 'mask_sha256']:
                check(identity+'/'+key, actual[key], r[key])
            image = prepared/Path(r['path']).name
            check(identity+'/image_hash', sha(image.read_bytes()), r['image_sha256'])
            with Image.open(image) as im:
                gray = np.array(im.convert('L'))
            median = statistics.median(gray[mask].tolist())
            check(identity+'/gray_median', actual['median_mask_gray'], median)
            for delta in plan['ink_proxy_median_deltas']:
                selected = mask & (gray <= median-delta)
                n, k = int(selected.sum()), int((selected & shared).sum())
                expected = {'threshold_gray': median-delta, 'dark_pixels': n, 'shared_dark_pixels': k, 'shared_fraction': k/n if n else None}
                check(identity+'/dark_delta_'+str(delta), actual['ink_proxies'][str(delta)], expected)
    cache = np.load(prior_root/'posterior_pass0.npz', allow_pickle=False)
    pools = defaultdict(set)
    for r in prior['rows']:
        pools[(r['folio'], len(r['reference']))].add(r['reference'])
    vocabulary = {r['reference'] for r in source if r['role'] in ['original_train', 'additional_train']}
    total_scores = 0
    for r, old in zip(rows, prior['rows']):
        identity = r['id']
        for key in ['id', 'folio', 'role', 'reference', 'seen_in_training']:
            check(identity+'/'+key, r[key], old[key])
        check(identity+'/vocabulary', r['seen_in_training'], r['reference'] in vocabulary)
        check(identity+'/prediction', r['beam_prediction'], old['predictions']['beam32'])
        check(identity+'/edit', r['beam_errors'], old['errors']['beam32'])
        check(identity+'/geometry', r['shared_mask_fraction'], by_id[identity]['shared_mask_fraction'])
        check(identity+'/overlap_group', r['overlap_group'], by_id[identity]['overlap_group'])
        p = cache[identity]
        check(identity+'/matrix_hash', r['matrix_sha256'], sha(p.astype(np.float32).tobytes()))
        check(identity+'/frames', r['frames'], len(p))
        check(identity+'/minimum_frames', r['minimum_target_frames'], len(r['reference'])+sum(a == b for a, b in zip(r['reference'], r['reference'][1:])))
        expected_texts = sorted(pools[(r['folio'], len(r['reference']))])
        check(identity+'/candidate_pool', [x['text'] for x in r['same_length_candidates']], expected_texts)
        scores = {}
        for text in sorted(set(expected_texts + [r['beam_prediction']])):
            scores[text] = probability_logmass(p, [codec[c][0] for c in text])
        total_scores += len(scores)
        for item in r['same_length_candidates']:
            value = scores[item['text']]
            check(identity+'/candidate/'+item['text'], item['log_probability'], value if math.isfinite(value) else None)
        a, b = scores[r['reference']], scores[r['beam_prediction']]
        check(identity+'/reference_mass', r['reference_log_probability'], a if math.isfinite(a) else None)
        check(identity+'/predicted_mass', r['beam_log_probability'], b if math.isfinite(b) else None)
        tolerance = plan['log_probability_tie_tolerance']
        relation = 'equal' if a == b or abs(a-b) <= tolerance else ('above' if a > b else 'below')
        check(identity+'/mass_relation', r['reference_mass_vs_prediction'], relation)
        margin = (a-b)/len(r['reference']) if math.isfinite(a) and math.isfinite(b) else None
        check(identity+'/normalized_margin', r['log_margin_per_reference_character'], margin)
        others = [scores[t] for t in expected_texts if t != r['reference']]
        better = sum(v > a+tolerance for v in others)
        ties = sum(v == a or abs(v-a) <= tolerance for v in others)
        wins = sum(a > v+tolerance for v in others)
        check(identity+'/rank_min', r['reference_rank_min'], 1+better)
        check(identity+'/rank_max', r['reference_rank_max'], 1+better+ties)
        check(identity+'/win_fraction', r['pairwise_reference_win_fraction'], (wins+.5*ties)/len(others) if others else None)
    check('ctc_scores', result['exact_ctc_text_scores'], total_scores)
    primary = [r for r in rows if r['role'] == 'reserved' and not r['seen_in_training']]
    check('primary_words', len(primary), 76)
    check('primary_characters', sum(len(r['reference']) for r in primary), 446)
    primary_stats = metrics(primary)
    for key, value in primary_stats.items():
        check('primary/'+key, result['primary_reserved_unseen'][key], value)
    for role in ['historical_development', 'reserved']:
        rs = [r for r in rows if r['role'] == role]
        groups = {'all': rs, 'seen': [r for r in rs if r['seen_in_training']], 'unseen': [r for r in rs if not r['seen_in_training']],
                  'length_1_4': [r for r in rs if len(r['reference']) < 5], 'length_5_6': [r for r in rs if len(r['reference']) in [5, 6]], 'length_7_plus': [r for r in rs if len(r['reference']) > 6]}
        for name, selected in groups.items():
            expected = metrics(selected)
            if expected:
                for k, v in expected.items():
                    check(role+'/'+name+'/'+k, result['metrics'][role][name][k], v)
            else:
                check(role+'/'+name, result['metrics'][role][name], None)
        for subtype, values in [('by_folio', sorted({r['folio'] for r in rs})), ('by_overlap', ['low_le_1pct', 'middle', 'high_ge_25pct'])]:
            field = 'folio' if subtype == 'by_folio' else 'overlap_group'
            for name in values:
                expected = metrics([r for r in rs if r[field] == name])
                actual = result['metrics'][role][subtype][name]
                if expected:
                    for k, v in expected.items():
                        check(role+'/'+subtype+'/'+name+'/'+k, actual[k], v)
                else:
                    check(role+'/'+subtype+'/'+name, actual, None)
    for role in sorted({r['role'] for r in g}):
        rs = [r for r in g if r['role'] == role]
        expected = {'words': len(rs), 'overlap_groups': {name: sum(r['overlap_group'] == name for r in rs) for name in ['low_le_1pct', 'middle', 'high_ge_25pct']},
                    'median_shared_mask_fraction': statistics.median(r['shared_mask_fraction'] for r in rs),
                    'median_shared_dark_fraction': {str(d): statistics.median(v) if (v := [r['ink_proxies'][str(d)]['shared_fraction'] for r in rs if r['ink_proxies'][str(d)]['shared_fraction'] is not None]) else None for d in plan['ink_proxy_median_deltas']}}
        check(role+'/geometric_summary', result['geometric_summary'][role], expected)
    for field in ['new_training', 'new_network_inference', 'translation']:
        check(field, result[field], 'NOT_RUN')
    packet_path = bundle/'review_queue.json'
    packet_words = 0
    if packet_path.exists() or packet_path.with_suffix('.json.gz').exists():
        packet = read(packet_path)
        queue = packet['records']
        training = {r['id']: r for r in source if r['role'] in ['original_train', 'additional_train']}
        check('queue/training_only_ids', sorted(r['id'] for r in queue), sorted(training))
        check('queue/count', packet['words'], len(training))
        check('queue/status', packet['status'], 'PREPARED_UNREVIEWED_TRAINING_QUEUE')
        check('queue/no_review_claim', packet['reviewed_words'], 0)
        check('queue/no_label_changes', packet['label_changes'], 0)
        check('queue/no_geometry_changes', packet['geometry_changes'], 0)
        priorities = sorted(training, key=lambda identity: (-(by_id[identity]['ink_proxies']['40']['shared_fraction'] or 0), -by_id[identity]['shared_mask_fraction'], identity))
        check('queue/priority_order', [r['id'] for r in queue], priorities)
        for rank, row in enumerate(queue, 1):
            identity = row['id']
            source_row = training[identity]
            check(identity+'/queue/rank', row['review_priority'], rank)
            check(identity+'/queue/status', row['review_status'], 'UNREVIEWED')
            check(identity+'/queue/approved_reference', row['approved_reference'], None)
            check(identity+'/queue/approved_polygon', row['approved_polygon'], None)
            check(identity+'/queue/reference', row['candidate_reference'], source_row['reference'])
            for key in ['folio', 'role', 'source_image_path', 'source_image_sha256', 'bounds', 'polygon', 'image_sha256', 'mask_sha256']:
                check(identity+'/queue/'+key, row[key], source_row[key])
            check(identity+'/queue/overlap', row['shared_mask_fraction'], by_id[identity]['shared_mask_fraction'])
            check(identity+'/queue/dark_overlap', row['shared_dark_fraction_delta40'], by_id[identity]['ink_proxies']['40']['shared_fraction'])
        packet_words = len(queue)
    return {'status': 'PASS' if not failures else 'FAIL', 'checks': checks, 'mismatches': failures, 'exact_ctc_scores_recomputed': total_scores,
            'geometry_words_recomputed': len(g), 'posterior_words_recomputed': len(rows), 'primary_reserved_unseen': primary_stats,
            'unreviewed_training_queue_words': packet_words,
            'result_sha256': sha(data(bundle/'result.json')), 'plan_sha256': sha(data(plan_path)),
            'scope': 'Independent probability-space recurrence with reachability pruning versus log DP; whole-page additive mask coverage versus pairwise local intersections; input hashes, ranks, proxies, aggregates and training-only unreviewed queue. No new neural inference or palaeographic validation.',
            'translation': 'NOT_RUN'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    r = audit(a.bundle, a.repo, a.plan)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(r, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: r[k] for k in ['status', 'checks', 'mismatches', 'exact_ctc_scores_recomputed', 'geometry_words_recomputed']}))
    raise SystemExit(r['status'] != 'PASS')
