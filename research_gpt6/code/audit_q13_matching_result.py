#!/usr/bin/env python3
"""Replay archived numeric evidence without downloading TimesFM weights."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np

import q13_matching_control as q


def audit(result):
    t = result['timesfm']
    if t['status'] != 'PASS_EXECUTED_DESCRIPTIVE':
        raise ValueError('TimesFM evidence missing')
    scales = np.asarray(t['scales_outside_q13'], dtype=np.float32)
    loss_count = 0
    maximum_loss_delta = 0.0
    for src, pred in t['frozen_predictions'].items():
        context = np.asarray(t['source_contexts'][src], dtype=np.float32)
        forecasts = {
            'model': np.asarray(pred, dtype=np.float32),
            'persistence': np.repeat(context[-1:], 4, axis=0),
            'source_mean': np.repeat(context.mean(axis=0, keepdims=True), 4, axis=0),
        }
        for tgt, target in t['target_rows'].items():
            if src == tgt:
                continue
            target = np.asarray(target, dtype=np.float32)
            for name, forecast in forecasts.items():
                replay = (((forecast-target)**2).mean(axis=0) / scales).astype(float)
                saved = np.asarray(t['directed_page_standardized_mse_by_feature'][name][src+'->'+tgt])
                delta = float(np.max(np.abs(replay-saved)))
                if delta > 1e-7:
                    raise ValueError(f'Forecast-loss mismatch: {src}, {tgt}, {name}')
                maximum_loss_delta = max(maximum_loss_delta, delta)
                loss_count += len(saved)
    sets = [('lexical_'+m, d) for m, d in result['lexical'].items()] + [('timesfm', t)]
    record_count = score_count = summary_count = 0
    for label, data in sets:
        seen = set()
        values = {name: {'all': [], 'cross_half': []} for name in data['edge_scores']}
        for record in data['all_matching_scores']:
            matching = q.canonical(record['pairs'])
            if len(matching) != 5 or sorted(itertools.chain.from_iterable(matching)) != list(q.LEAVES) or matching in seen:
                raise ValueError('Duplicate or incomplete matching')
            seen.add(matching)
            record_count += 1
            cross = all((a < 80) != (b < 80) for a, b in matching)
            if cross != record['cross_half']:
                raise ValueError('Cross-half flag mismatch')
            for name, edges in data['edge_scores'].items():
                value = sum(edges[q.edge_key(p)] for p in matching) / 5
                if abs(value-record['scores'][name]) > 1e-12:
                    raise ValueError('Matching-score mismatch')
                values[name]['all'].append(value)
                if cross:
                    values[name]['cross_half'].append(value)
                score_count += 1
        if len(seen) != 945:
            raise ValueError('Missing perfect matchings')
        higher = label.startswith('lexical')
        for name, edges in data['edge_scores'].items():
            observed = sum(edges[q.edge_key(p)] for p in q.OBSERVED) / 5
            for null, vals in values[name].items():
                summary = data['summary'][name][null]
                if len(vals) != (945 if null == 'all' else 120):
                    raise ValueError('Incorrect reference size')
                tail = sum(x >= observed-1e-12 for x in vals) if higher else sum(x <= observed+1e-12 for x in vals)
                better = sum(x > observed+1e-12 for x in vals) if higher else sum(x < observed-1e-12 for x in vals)
                if tail != summary['inclusive_tail_count'] or tail / len(vals) != summary['exact_tail_p'] or better+1 != summary['rank_best_is_1']:
                    raise ValueError('Rank or exact-tail mismatch')
                expected = {'observed': observed, 'null_min': min(vals), 'null_max': max(vals),
                            'null_mean': math.fsum(vals) / len(vals),
                            'observed_minus_null_mean': observed-math.fsum(vals) / len(vals)}
                if any(abs(value-summary[k]) > 1e-12 for k, value in expected.items()):
                    raise ValueError('Reference summary mismatch')
                summary_count += 1
    return {'status': 'PASS_FROZEN_EVIDENCE_REPLAY', 'feature_losses': loss_count,
            'max_loss_abs_difference': maximum_loss_delta, 'matching_records': record_count,
            'matching_scores': score_count, 'exact_summaries': summary_count,
            'new_model_inference': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--result', type=Path, required=True)
    args = parser.parse_args()
    data = args.result.read_bytes()
    summary = audit(json.loads(data))
    summary['input_sha256'] = hashlib.sha256(data).hexdigest()
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
