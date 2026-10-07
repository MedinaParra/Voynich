#!/usr/bin/env python3
"""Frozen TimesFM Q13 singulion-order test.

Uses the exact 10-dimensional paragraph representation already frozen in
`timesfm_voynich.py`. For each Q13 page, TimesFM sees only that source page and
forecasts the first H clean paragraph rows of a possible next page. Predictions
are generated once per source page, before any candidate ordering is scored.
The pairwise loss matrix is therefore order-independent and cannot adapt to the
Layfield-Davis target order.

This is structural continuity testing, not decipherment.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import timesfm_voynich as tfm

Q13_FOLIOS = tuple(range(75, 85))
BIFOLIA = ((75, 84), (76, 83), (77, 82), (78, 81), (79, 80))
LAYFIELD_DAVIS = ((77, 82), (78, 81), (75, 84), (76, 83), (79, 80))


def page_id(locus: str):
    m = re.match(r'^(f[0-9]+[rv])', locus)
    return m.group(1) if m else None


def feature_rows(raw: str):
    """Same cleaning and FEATURES as the already-frozen TimesFM experiment."""
    out = []
    for line in raw.splitlines():
        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m.group(1) or not re.search(r'P[0-9a-z]', m.group(1).split(',',1)[1]):
            continue
        locus, text = m.groups()
        clean = re.sub(r'<[^>]*>', '', text)
        if ',' in text or '<->' in text or not re.fullmatch(r'[a-z.\s]+', clean):
            continue
        words = [w for w in re.split(r'[.\s]+', clean.strip()) if w]
        if len(words) < 4:
            continue
        chars = ''.join(words)
        n = len(words)
        frac = lambda ch: chars.count(ch) / len(chars) if chars else 0.0
        x = [
            n,
            sum(map(len, words)) / n,
            len(set(words)) / n,
            tfm.entropy(chars),
            frac('q'), frac('o'), frac('y'), frac('d'),
            sum(w.startswith('q') for w in words) / n,
            sum(w.endswith('y') for w in words) / n,
        ]
        out.append({'locus': locus, 'page': page_id(locus), 'x': x})
    return out


def q13_ids():
    return [f'f{n}{s}' for n in Q13_FOLIOS for s in ('r','v')]


def current_sequence():
    return q13_ids()


def singulion_sequence(order):
    seq = []
    for a,b in order:
        seq.extend((f'f{a}r', f'f{a}v', f'f{b}r', f'f{b}v'))
    return seq


def seq_loss(seq, pair_loss, boundary_only=False):
    pairs = list(zip(seq, seq[1:]))
    if boundary_only:
        pairs = [pairs[i] for i in range(3, len(pairs), 4)]
    vals = [pair_loss[(a,b)] for a,b in pairs]
    return float(np.mean(vals))


def seq_naive(seq, pair_naive, boundary_only=False):
    pairs = list(zip(seq, seq[1:]))
    if boundary_only:
        pairs = [pairs[i] for i in range(3, len(pairs), 4)]
    return float(np.mean([pair_naive[(a,b)] for a,b in pairs]))


def lower_rank(value, null):
    n = len(null)
    return {
        'rank_best_is_1': 1 + sum(x < value for x in null),
        'n_exact_permutations': n,
        'good_percentile': 100.0 * sum(x >= value for x in null) / n,
        'exact_lower_tail_p_including_observed': sum(x <= value for x in null) / n,
        'null_min': min(null),
        'null_mean': float(np.mean(null)),
        'null_max': max(null),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--context', type=int, default=64)
    ap.add_argument('--horizon', type=int, default=4)
    a = ap.parse_args()

    data = a.corpus.read_bytes()
    if tfm.git_blob_sha1(data) != tfm.SOURCE_BLOB:
        raise SystemExit('Corpus blob mismatch')
    rows = feature_rows(data.decode('utf-8'))
    ids = q13_ids()
    q13 = defaultdict(list)
    train = []
    q13_set = set(ids)
    for r in rows:
        if r['page'] in q13_set:
            q13[r['page']].append(r['x'])
        else:
            train.append(r['x'])
    missing = [p for p in ids if len(q13[p]) < a.horizon]
    if missing:
        raise SystemExit(f'Q13 pages with fewer than horizon rows: {missing}')
    train = np.asarray(train, dtype=np.float32)
    scales = np.maximum(np.var(train, axis=0), 1e-8)

    # Compile once. Each source-page forecast is generated once and then frozen.
    model = tfm.load_model(a.context, a.horizon)
    predictions = {}
    source_context_rows = {}
    for src in ids:
        arr = np.asarray(q13[src], dtype=np.float32)
        ctx = arr[-min(a.context, len(arr)):]
        predictions[src] = tfm.forecast(model, ctx, a.horizon)
        source_context_rows[src] = len(ctx)

    pair_loss = {}
    pair_naive = {}
    for src in ids:
        pred = predictions[src]
        src_last = np.asarray(q13[src][-1], dtype=np.float32)[None,:]
        naive = np.repeat(src_last, a.horizon, axis=0)
        for tgt in ids:
            if src == tgt:
                continue
            target = np.asarray(q13[tgt][:a.horizon], dtype=np.float32)
            pair_loss[(src,tgt)] = float((((pred-target)**2).mean(axis=0) / scales).mean())
            pair_naive[(src,tgt)] = float((((naive-target)**2).mean(axis=0) / scales).mean())

    current = current_sequence()
    proposed = singulion_sequence(LAYFIELD_DAVIS)
    current_loss = seq_loss(current, pair_loss)
    current_naive = seq_naive(current, pair_naive)
    proposed_loss = seq_loss(proposed, pair_loss)
    proposed_naive = seq_naive(proposed, pair_naive)
    proposed_boundary = seq_loss(proposed, pair_loss, True)
    proposed_boundary_naive = seq_naive(proposed, pair_naive, True)

    recs = []
    for perm in itertools.permutations(BIFOLIA):
        seq = singulion_sequence(perm)
        recs.append({
            'order': [f'{x}|{y}' for x,y in perm],
            'loss_all': seq_loss(seq, pair_loss),
            'loss_boundary': seq_loss(seq, pair_loss, True),
            'naive_all': seq_naive(seq, pair_naive),
            'naive_boundary': seq_naive(seq, pair_naive, True),
        })
    null_all = [r['loss_all'] for r in recs]
    null_boundary = [r['loss_boundary'] for r in recs]
    rank_all = lower_rank(proposed_loss, null_all)
    rank_boundary = lower_rank(proposed_boundary, null_boundary)
    best = min(recs, key=lambda r: (r['loss_all'], r['order']))
    best_boundary = min(recs, key=lambda r: (r['loss_boundary'], r['order']))

    pass_order = proposed_loss < current_loss and rank_all['good_percentile'] > 95.0
    result = {
        'classification': 'TIMESFM_Q13_SINGULION_ORDER_NOT_DECIPHERMENT',
        'status': 'PASS_ORDER' if pass_order else 'FAIL_ORDER',
        'source_blob': tfm.SOURCE_BLOB,
        'model': tfm.MODEL_ID,
        'features': tfm.FEATURES,
        'representation_policy': 'identical clean paragraph feature representation to timesfm_voynich.py',
        'prediction_policy': 'one frozen forecast per source page; first H clean rows of every candidate target scored post hoc; no target/order-specific forecasting',
        'scaling_policy': 'feature variances computed only from corpus rows outside Q13',
        'context_cap': a.context,
        'horizon': a.horizon,
        'clean_rows_per_q13_page': {p: len(q13[p]) for p in ids},
        'source_context_rows': source_context_rows,
        'layfield_davis_order': [f'{x}|{y}' for x,y in LAYFIELD_DAVIS],
        'current_bound_loss': current_loss,
        'current_bound_naive_loss': current_naive,
        'current_skill_vs_persistence': 1.0-current_loss/current_naive if current_naive > 0 else None,
        'layfield_davis_loss': proposed_loss,
        'layfield_davis_naive_loss': proposed_naive,
        'layfield_davis_skill_vs_persistence': 1.0-proposed_loss/proposed_naive if proposed_naive > 0 else None,
        'layfield_minus_current_loss': proposed_loss-current_loss,
        'layfield_davis_exact_rank_all': rank_all,
        'layfield_davis_boundary_loss': proposed_boundary,
        'layfield_davis_boundary_naive_loss': proposed_boundary_naive,
        'layfield_davis_boundary_skill_vs_persistence': 1.0-proposed_boundary/proposed_boundary_naive if proposed_boundary_naive > 0 else None,
        'layfield_davis_exact_rank_boundary': rank_boundary,
        'fraction_fixed_bifolium_orders_beating_current': sum(x < current_loss for x in null_all)/len(null_all),
        'best_exact_order_all': best,
        'best_exact_order_boundary': best_boundary,
        'decision_rule': 'PASS_ORDER iff Layfield-Davis model loss is below current binding and is better than >95% of all 120 fixed-orientation bifolium permutations.',
        'limitations': [
            'Q13 only; exact Q20 published sequence has not been independently extracted.',
            'Immediate source-page forecasting tests local structural continuity, not semantics.',
            'Fixed bifolium internal orientation; orientation sensitivity is separate.',
            'TimesFM is pretrained on generic time series, not a language model.',
        ],
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
