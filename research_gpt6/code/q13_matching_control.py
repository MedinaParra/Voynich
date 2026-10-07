#!/usr/bin/env python3
"""Frozen Q13 perfect-matching falsification; no ordering or translation.

The primary compares a fixed physical matching to 945/120 alternatives.
TimesFM is optional and descriptive; it cannot change the lexical decision.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

LEAVES = tuple(range(75, 85))
OBSERVED = ((75, 84), (76, 83), (77, 82), (78, 81), (79, 80))
SOURCE_BLOB = '2a4533ab9bdfa85db9bad602d590978953055df1'
SOURCE_SHA256 = 'bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc'
TOL = 1e-12


def canonical(matching):
    return tuple(sorted(tuple(sorted(p)) for p in matching))


def perfect_matchings(nodes):
    nodes = tuple(sorted(nodes))
    if not nodes:
        yield ()
        return
    a = nodes[0]
    for i, b in enumerate(nodes[1:], 1):
        rest = nodes[1:i] + nodes[i + 1:]
        for tail in perfect_matchings(rest):
            yield ((a, b),) + tail


def cross_half_matchings(nodes):
    left = tuple(x for x in nodes if x < 80)
    right = tuple(x for x in nodes if x >= 80)
    if len(left) != len(right):
        raise ValueError('Unequal halves')
    for perm in itertools.permutations(right):
        yield canonical(zip(left, perm))


def edge_key(pair):
    return '|'.join(map(str, sorted(pair)))


def matching_score(matching, edges):
    return math.fsum(edges[edge_key(p)] for p in matching) / len(matching)


def exact_summary(observed, scores, higher=True):
    if not scores or not all(math.isfinite(x) for x in scores + [observed]):
        raise ValueError('Empty or nonfinite reference scores')
    if higher:
        better = sum(x > observed + TOL for x in scores)
        inclusive = sum(x >= observed - TOL for x in scores)
    else:
        better = sum(x < observed - TOL for x in scores)
        inclusive = sum(x <= observed + TOL for x in scores)
    null_mean = math.fsum(scores) / len(scores)
    return {
        'observed': observed, 'rank_best_is_1': better + 1,
        'n_exact': len(scores), 'inclusive_tail_count': inclusive,
        'exact_tail_p': inclusive / len(scores),
        'null_min': min(scores), 'null_mean': null_mean, 'null_max': max(scores),
        'observed_minus_null_mean': observed - null_mean,
        'higher_is_better': higher, 'tie_tolerance': TOL,
    }


def parse_pages(raw, comma_mode):
    if comma_mode not in ('split', 'join'):
        raise ValueError('Unknown comma mode')
    pages = defaultdict(list)
    metadata = {}
    audit = Counter()
    for line in raw.splitlines():
        pm = re.match(r'^<([^>.,]+)>\s*<!', line)
        if pm:
            metadata[pm[1]] = dict(re.findall(r'\$([A-Z])=([^\s>]+)', line))
            continue
        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m[1] or not re.search(r'P[0-9a-z]', m[1].split(',', 1)[1]):
            continue
        page = m[1].split('.', 1)[0]
        if not re.match(r'^f[0-9]+[rv]', page):
            continue
        text = m[2]
        audit['commas'] += text.count(',')
        text = text.replace(',', '.' if comma_mode == 'split' else '')
        text = re.sub(r'<[^>]*>', '|', text)
        for chunk in re.split(r'[.\s|]+', text):
            if not chunk:
                continue
            if re.fullmatch(r'[a-z]{1,64}', chunk):
                pages[page].append(chunk)
                audit['literal_tokens'] += 1
            else:
                audit['discarded_chunks'] += 1
        audit['paragraph_loci'] += 1
    return dict(pages), metadata, dict(audit)


def leaf_number(page):
    return int(re.match(r'^f([0-9]+)', page)[1])


def make_idf(pages):
    train = defaultdict(list)
    for page, words in pages.items():
        leaf = leaf_number(page)
        if leaf not in LEAVES:
            train[leaf].extend(words)
    if not train:
        raise ValueError('No non-Q13 training leaves')
    df = Counter()
    for leaf in sorted(train):
        df.update(set(train[leaf]))
    return {w: math.log((1 + len(train)) / (1 + df[w])) + 1 for w in sorted(df)}, len(train)


def cosine(a, b):
    dot = math.fsum(a[k] * b.get(k, 0.0) for k in sorted(a))
    na = math.sqrt(math.fsum(x * x for x in a.values()))
    nb = math.sqrt(math.fsum(x * x for x in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def tfidf(words, idf):
    c = Counter(words)
    n = len(words)
    return {w: c[w] * idf[w] / n for w in sorted(c) if w in idf} if n else {}


def char3(words):
    c = Counter()
    for w in words:
        s = '^' + w + '$'
        c.update(s[i:i+3] for i in range(len(s) - 2))
    return dict(sorted(c.items()))


def char_js(a, b):
    ca, cb = Counter(''.join(a)), Counter(''.join(b))
    na, nb = sum(ca.values()), sum(cb.values())
    if not na or not nb:
        return 0.0
    terms = []
    for ch in sorted(set(ca) | set(cb)):
        p, q = ca[ch] / na, cb[ch] / nb
        mid = (p + q) / 2
        terms.append((p * math.log2(p / mid) if p else 0) + (q * math.log2(q / mid) if q else 0))
    return 1 - math.fsum(terms) / 2


def nuisance_residual(raw_edges, style_edges, words):
    pairs = list(itertools.combinations(LEAVES, 2))
    design = np.asarray([
        [1.0, style_edges[edge_key((a, b))],
         abs(math.log(len(words[a]) / len(words[b]))), (a-b)**2 / 100.0]
        for a, b in pairs], dtype=np.float64)
    target = np.asarray([raw_edges[edge_key(p)] for p in pairs], dtype=np.float64)
    beta, _, rank, singular = np.linalg.lstsq(design, target, rcond=None)
    residual = target - design @ beta
    return {edge_key(p): float(y) for p, y in zip(pairs, residual)}, {
        'columns': ['intercept', 'char3_cosine', 'absolute_log_token_count_ratio', 'squared_folio_gap_over_100'],
        'coefficients': beta.tolist(), 'matrix_rank': int(rank), 'singular_values': singular.tolist(),
        'physical_pair_labels_used_in_fit': False,
    }


def assess(edges_by_metric, observed=OBSERVED, nodes=LEAVES, higher=True):
    all_m = list(perfect_matchings(nodes))
    cross = set(cross_half_matchings(nodes))
    observed = canonical(observed)
    if observed not in all_m or observed not in cross:
        raise ValueError('Observed matching absent from reference')
    records = []
    for m in all_m:
        records.append({'pairs': [list(p) for p in m], 'cross_half': m in cross,
                        'scores': {name: matching_score(m, e) for name, e in edges_by_metric.items()}})
    summaries = {}
    for name, edges in edges_by_metric.items():
        obs = matching_score(observed, edges)
        summaries[name] = {
            'all': exact_summary(obs, [r['scores'][name] for r in records], higher),
            'cross_half': exact_summary(obs, [r['scores'][name] for r in records if r['cross_half']], higher),
        }
    return summaries, records


def gate_from_summaries(summaries, leave_pair_out):
    gates = {}
    for name in ('tfidf', 'tfidf_residual'):
        for null in ('all', 'cross_half'):
            gates[f'{name}_{null}_p_le_05'] = summaries[name][null]['exact_tail_p'] <= .05
    for side in ('recto', 'verso'):
        for null in ('all', 'cross_half'):
            gates[f'{side}_{null}_positive'] = summaries[f'tfidf_{side}'][null]['observed_minus_null_mean'] > TOL
    gates['all_leave_pair_out_positive'] = all(
        d['summary'][null]['observed_minus_null_mean'] > TOL
        for d in leave_pair_out for null in ('all', 'cross_half'))
    return gates


def validate_metadata(meta):
    for index, pair in enumerate(OBSERVED, 1):
        for leaf in pair:
            for side in ('r', 'v'):
                p = f'f{leaf}{side}'
                required = {'Q': 'M', 'B': str(index), 'L': 'B', 'H': '2'}
                if any(meta.get(p, {}).get(k) != v for k, v in required.items()):
                    raise ValueError(f'Q13 metadata mismatch: {p}')


def lexical_analysis(raw, comma_mode):
    pages, metadata, audit = parse_pages(raw, comma_mode)
    validate_metadata(metadata)
    ids = [f'f{n}{s}' for n in LEAVES for s in ('r', 'v')]
    if any(not pages.get(p) for p in ids):
        raise ValueError('Missing/empty Q13 page')
    idf, n_train = make_idf(pages)
    words = {n: pages[f'f{n}r'] + pages[f'f{n}v'] for n in LEAVES}
    vectors = {n: tfidf(words[n], idf) for n in LEAVES}
    chars = {n: char3(words[n]) for n in LEAVES}
    metrics = {name: {} for name in ('tfidf', 'char3', 'char_js', 'tfidf_recto', 'tfidf_verso')}
    for a, b in itertools.combinations(LEAVES, 2):
        k = edge_key((a, b))
        metrics['tfidf'][k] = cosine(vectors[a], vectors[b])
        metrics['char3'][k] = cosine(chars[a], chars[b])
        metrics['char_js'][k] = char_js(words[a], words[b])
        for side, label in (('r', 'recto'), ('v', 'verso')):
            metrics[f'tfidf_{label}'][k] = cosine(tfidf(pages[f'f{a}{side}'], idf), tfidf(pages[f'f{b}{side}'], idf))
    metrics['tfidf_residual'], nuisance = nuisance_residual(metrics['tfidf'], metrics['char3'], words)
    summary, records = assess(metrics)
    leave_out = []
    for omitted in OBSERVED:
        nodes = tuple(x for x in LEAVES if x not in omitted)
        observed = tuple(p for p in OBSERVED if p != omitted)
        sm, _ = assess({'tfidf': metrics['tfidf']}, observed, nodes)
        leave_out.append({'omitted_pair': list(omitted), 'summary': sm['tfidf']})
    gates = gate_from_summaries(summary, leave_out)
    return {
        'comma_mode': comma_mode, 'gates': gates, 'all_gates_pass': all(gates.values()),
        'summary': summary, 'edge_scores': metrics, 'all_matching_scores': records,
        'leave_pair_out': leave_out, 'nuisance_fit': nuisance, 'parser_audit': audit,
        'outside_q13_idf_training_leaves': n_train, 'outside_q13_vocabulary_size': len(idf),
        'tokens_by_page': {p: len(pages[p]) for p in ids},
        'idf_token_coverage_by_leaf': {str(n): sum(w in idf for w in words[n]) / len(words[n]) for n in LEAVES},
        'metadata_by_page': {p: metadata[p] for p in ids},
    }


def timesfm_edges(page_errors, feature_indices):
    out = {}
    for a, b in itertools.combinations(LEAVES, 2):
        vals = []
        for x, y in ((a, b), (b, a)):
            for sx in ('r', 'v'):
                for sy in ('r', 'v'):
                    v = page_errors[f'f{x}{sx}->f{y}{sy}']
                    vals.append(math.fsum(v[j] for j in feature_indices) / len(feature_indices))
        out[edge_key((a, b))] = math.fsum(vals) / len(vals)
    return out


def timesfm_analysis(raw):
    import random
    import torch
    import timesfm_singulion_q13 as q
    import timesfm_voynich as tfm
    seed = 20261007
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    rows = q.feature_rows(raw)
    ids = q.q13_ids()
    grouped = defaultdict(list)
    outside = []
    for row in rows:
        if row['page'] in ids:
            grouped[row['page']].append(row['x'])
        else:
            outside.append(row['x'])
    horizon, context_cap = 4, 64
    if any(len(grouped[p]) < horizon for p in ids):
        raise ValueError('Q13 page has fewer than four TimesFM rows')
    scales = np.maximum(np.var(np.asarray(outside, dtype=np.float32), axis=0), 1e-8)
    model = tfm.load_model(context_cap, horizon)
    contexts = {p: np.asarray(grouped[p], dtype=np.float32)[-context_cap:] for p in ids}
    predictions = {p: tfm.forecast(model, contexts[p], horizon) for p in ids}
    targets = {p: np.asarray(grouped[p][:horizon], dtype=np.float32) for p in ids}
    page_errors = {name: {} for name in ('model', 'persistence', 'source_mean')}
    for src in ids:
        forecasts = {'model': predictions[src],
                     'persistence': np.repeat(contexts[src][-1:], horizon, axis=0),
                     'source_mean': np.repeat(contexts[src].mean(axis=0, keepdims=True), horizon, axis=0)}
        for tgt in ids:
            if src == tgt:
                continue
            for name, forecast in forecasts.items():
                page_errors[name][f'{src}->{tgt}'] = (((forecast-targets[tgt])**2).mean(axis=0) / scales).astype(float).tolist()
    metrics = {name: timesfm_edges(e, list(range(10))) for name, e in page_errors.items()}
    metrics['model_without_token_count'] = timesfm_edges(page_errors['model'], list(range(1, 10)))
    metrics['model_minus_persistence'] = {k: metrics['model'][k] - metrics['persistence'][k] for k in metrics['model']}
    summary, records = assess(metrics, higher=False)
    return {
        'status': 'PASS_EXECUTED_DESCRIPTIVE', 'model': tfm.MODEL_ID, 'features': tfm.FEATURES,
        'seed': seed, 'context_cap': context_cap, 'horizon': horizon,
        'scales_outside_q13': scales.astype(float).tolist(), 'outside_q13_rows': len(outside),
        'clean_rows_per_page': {p: len(grouped[p]) for p in ids},
        'source_contexts': {p: contexts[p].astype(float).tolist() for p in ids},
        'frozen_predictions': {p: predictions[p].astype(float).tolist() for p in ids},
        'target_rows': {p: targets[p].astype(float).tolist() for p in ids},
        'directed_page_standardized_mse_by_feature': page_errors,
        'edge_scores': metrics, 'summary': summary, 'all_matching_scores': records,
        'lexical_decision_affected': False,
    }


def digest_file(path):
    data = path.read_bytes()
    return {'path': path.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'git_blob': hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}


def summary_record(result):
    return {k: result[k] for k in ('classification', 'status', 'semantic_status', 'source_sha256', 'plan_sha256')} | {
        'runtime': result['runtime'],
        'lexical': {mode: {'gates': d['gates'], 'summary': d['summary'], 'leave_pair_out': d['leave_pair_out']}
                    for mode, d in result['lexical'].items()},
        'timesfm': {'status': result['timesfm']['status'], 'summary': result['timesfm'].get('summary')},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', required=True, type=Path)
    ap.add_argument('--plan', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--timesfm', action='store_true')
    args = ap.parse_args()
    data = args.corpus.read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    sha256 = hashlib.sha256(data).hexdigest()
    plan_data = args.plan.read_bytes()
    plan = json.loads(plan_data)
    if blob != SOURCE_BLOB or sha256 != SOURCE_SHA256:
        raise SystemExit('BLOCKED: corpus hash mismatch')
    if canonical(plan['observed_matching']) != canonical(OBSERVED) or tuple(plan['leaves']) != LEAVES:
        raise SystemExit('BLOCKED: protocol mapping mismatch')
    raw = data.decode('utf-8')
    lexical = {mode: lexical_analysis(raw, mode) for mode in ('split', 'join')}
    result = {
        'classification': 'Q13_PHYSICAL_MATCHING_NOT_ORDER_OR_DECIPHERMENT',
        'status': 'PASS_STRUCTURAL_CANDIDATE' if all(d['all_gates_pass'] for d in lexical.values()) else 'FAIL_STRICT_PAIR_COHERENCE',
        'semantic_status': 'NOT_RUN', 'source_blob': blob, 'source_sha256': sha256,
        'plan_sha256': hashlib.sha256(plan_data).hexdigest(),
        'observed_matching': [list(p) for p in OBSERVED], 'lexical': lexical,
        'timesfm': timesfm_analysis(raw) if args.timesfm else {'status': 'NOT_RUN'},
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__},
        'code_hashes': [digest_file(Path(__file__)), digest_file(Path(__file__).with_name('timesfm_singulion_q13.py')),
                        digest_file(Path(__file__).with_name('timesfm_voynich.py'))],
        'limitations': [
            'Previously inspected Q13: follow-up, not an untouched confirmatory manuscript holdout.',
            'Exact ranks assume exchangeable alternative matching assignments; historical binding was not randomized.',
            'Cross-half restriction and nuisance regression do not remove all drawing, geometry or production confounds.',
            'Recto/verso and leave-pair-out views share physical leaves and are not independent experiments.',
            'One transcription; no independent quire replication.',
            'Secondary TimesFM metrics cannot rescue a failed lexical gate.',
            'No translation or unique reading order is inferred.',
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps(summary_record(result), indent=2, allow_nan=False))
    print('RESULT_SHA256=' + hashlib.sha256(args.out.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
