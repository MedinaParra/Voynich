#!/usr/bin/env python3
"""Alphabet-renaming invariant diagnostic, not a translator.

Four-outcome normalized models, page/length/position-matched randomization,
complete reversible pair witnesses and a counterexample to semantic uniqueness.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import random

import alien_protocol_data as data

CELLS = 4 * 4 * 3 * 3 * 4
OUTCOMES = 4


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=True, indent=2, sort_keys=True) + '\n')


def gzsave(path, obj):
    with path.open('wb') as fh:
        with gzip.GzipFile(filename='', fileobj=fh, mode='wb', mtime=0) as z:
            z.write((json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(',', ':')) + '\n').encode())


def subseed(seed, label):
    return int.from_bytes(hashlib.sha256((str(seed) + ':' + label).encode()).digest()[:8], 'big')


def length_bin(n):
    return 0 if n <= 3 else 1 if n <= 5 else 2 if n <= 8 else 3


def pair_code(a, b):
    lookup, inverse = {}, []
    result = []
    for word in (a, b):
        encoded = []
        for unit in word:
            if unit not in lookup:
                lookup[unit] = len(inverse)
                inverse.append(unit)
            encoded.append(lookup[unit])
        result.append(encoded)
    return result, inverse


def prepare(rows, mode):
    unique = sorted({w for row in rows for w in row['words']})
    token_units = {w: tuple(data.units(w, mode)) for w in unique}
    alphabet = sorted({u for us in token_units.values() for u in us})
    bit = {u: 1 << i for i, u in enumerate(alphabet)}
    # These are deterministic features, not a vocabulary learned from test labels.
    features = {}
    for w, us in token_units.items():
        mask = 0
        for u in us:
            mask |= bit[u]
        features[w] = (mask, length_bin(len(us)), min(2, len(us) - len(set(us))), len(us), us)
    return features, alphabet


def slots_and_pairs(rows, features):
    slots, pairs, pools = [], [], defaultdict(list)
    for row in rows:
        n, begin = len(row['words']), len(slots)
        for i, raw in enumerate(row['words']):
            slots.append(raw)
            position = 0 if i == 0 else 2 if i == n - 1 else 1
            pools[(row['folio'], features[raw][3], position)].append(begin + i)
        for i in range(n - 1):
            position = int(i == 0) + 2 * int(i + 1 == n - 1)
            pairs.append((begin + i, begin + i + 1, position, row, i))
    ordered = [pools[k] for k in sorted(pools)]
    assert sorted(i for indexes in ordered for i in indexes) == list(range(len(slots)))
    movable = sum(len(ix) for ix in ordered if len({slots[i] for i in ix}) > 1)
    return slots, pairs, ordered, {'slots': len(slots), 'pools': len(ordered),
                                  'slots_in_nonconstant_pools': movable}


def index_and_category(left, right, position, features):
    a, b = features[left], features[right]
    context = (((a[1] * 4 + b[1]) * 3 + a[2]) * 3 + b[2]) * 4 + position
    category = min(3, (a[0] & b[0]).bit_count())
    return context, category


def table(slots, pairs, features):
    result = [0] * (CELLS * OUTCOMES)
    for li, ri, position, _, _ in pairs:
        context, category = index_and_category(slots[li], slots[ri], position, features)
        result[context * 4 + category] += 1
    return result


def shuffle(slots, pools, rng):
    out = list(slots)
    for indexes in pools:
        old = [slots[i] for i in indexes]
        new = list(old)
        rng.shuffle(new)
        assert Counter(old) == Counter(new)
        for i, word in zip(indexes, new):
            out[i] = word
        assert Counter(out[i] for i in indexes) == Counter(old)
    return out


def model_weights(real, null_pooled, replicates):
    base = [0] * ((CELLS // 4) * OUTCOMES)
    for context in range(CELLS):
        for c in range(4):
            base[(context // 4) * 4 + c] += real[context * 4 + c]
    coupling, framing = [], []
    for context in range(CELLS):
        r = real[context * 4:context * 4 + 4]
        n = null_pooled[context * 4:context * 4 + 4]
        z = base[(context // 4) * 4:(context // 4) * 4 + 4]
        rp = [(v + .5) / (sum(r) + 2) for v in r]
        # Pooling with alpha*R is exactly mean counts with the original alpha.
        np = [(v + .5 * replicates) / (sum(n) + 2 * replicates) for v in n]
        bp = [(v + .5) / (sum(z) + 2) for v in z]
        assert abs(sum(rp) - 1) < 1e-12 and abs(sum(np) - 1) < 1e-12
        for c in range(4):
            coupling.append(math.log2(rp[c] / np[c]))
            framing.append(math.log2(rp[c] / bp[c]))
    return coupling, framing


def score(counts, weights):
    n = sum(counts)
    if not n:
        raise ValueError('No heldout pairs')
    return math.fsum(c * w for c, w in zip(counts, weights) if c) / n


def witnesses(path, slots, pairs, features, split, rename):
    with path.open('wb') as fh:
        with gzip.GzipFile(filename='', fileobj=fh, mode='wb', mtime=0) as z:
            for li, ri, position, row, i in pairs:
                left, right = slots[li], slots[ri]
                a, b = features[left][4], features[right][4]
                code, inverse = pair_code(a, b)
                renamed, _ = pair_code(tuple(rename[u] for u in a), tuple(rename[u] for u in b))
                assert code == renamed
                assert [inverse[v] for v in code[0]] == list(a)
                assert [inverse[v] for v in code[1]] == list(b)
                context, c = index_and_category(left, right, position, features)
                rec = {'id': row['id'], 'folio': row['folio'], 'leaf': row['leaf'],
                       'split': split, 'word_index': i, 'line_words': len(row['words']),
                       'left': left, 'right': right, 'units_left': a, 'units_right': b,
                       'code': code, 'inverse': inverse, 'context': context, 'category': c}
                z.write((json.dumps(rec, ensure_ascii=True, sort_keys=True, separators=(',', ':')) + '\n').encode())


def run_case(case_id, rows, mode, plan, out):
    features, alphabet = prepare(rows, mode)
    partition = {role: [row for row in rows if data.split_leaf(row['leaf'], plan['seed']) == role]
                 for role in ['train', 'test']}
    assert not ({r['leaf'] for r in partition['train']} & {r['leaf'] for r in partition['test']})
    train, tp, train_pools, tm = slots_and_pairs(partition['train'], features)
    test, ep, test_pools, em = slots_and_pairs(partition['test'], features)
    if not tp or not ep:
        raise ValueError('Empty physical-leaf partition in ' + case_id)
    real = table(train, tp, features)
    pooled = [0] * len(real)
    train_rng = random.Random(subseed(plan['seed'], case_id + ':train'))
    for _ in range(plan['training_null_replicates']):
        sampled = table(shuffle(train, train_pools, train_rng), tp, features)
        assert sum(sampled) == len(tp)
        pooled = [x + y for x, y in zip(pooled, sampled)]
    coupling, framing = model_weights(real, pooled, plan['training_null_replicates'])
    observed = table(test, ep, features)
    actual = score(observed, coupling)
    null_tables, null_scores = [], []
    test_rng = random.Random(subseed(plan['seed'], case_id + ':test'))
    for _ in range(plan['test_null_replicates']):
        sampled = table(shuffle(test, test_pools, test_rng), ep, features)
        assert sum(sampled) == len(ep)
        null_tables.append(sampled)
        null_scores.append(score(sampled, coupling))
    exceed = sum(s >= actual for s in null_scores)
    tail = (1 + exceed) / (1 + len(null_scores))
    rename_values = list(range(len(alphabet)))
    random.Random(subseed(plan['seed'], case_id + ':rename')).shuffle(rename_values)
    rename = dict(zip(alphabet, rename_values))
    case_dir = out / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    for role, ss, pp in [('train', train, tp), ('test', test, ep)]:
        witnesses(case_dir / (role + '_pairs.jsonl.gz'), ss, pp, features, role, rename)
    certificate = {'schema': 'alien-protocol-counts-v1', 'case_id': case_id,
                   'real_train': real, 'null_train_pooled': pooled,
                   'train_null_replicates': plan['training_null_replicates'],
                   'real_test': observed, 'null_test': null_tables}
    gzsave(case_dir / 'counts.json.gz', certificate)
    return {'id': case_id, 'units': mode, 'lines': len(rows),
            'training_leaves': sorted({r['leaf'] for r in partition['train']}),
            'test_leaves': sorted({r['leaf'] for r in partition['test']}),
            'training_pairs': len(tp), 'test_pairs': len(ep),
            'training_pools': tm, 'test_pools': em,
            'training_null_replicates': plan['training_null_replicates'],
            'test_null_replicates': len(null_scores),
            'coupling_bits_per_pair': round(actual, 12),
            'format_bits_per_pair': round(score(observed, framing), 12),
            'conditional_randomization_tail': tail,
            'null_scores': [round(s, 12) for s in null_scores],
            'null_exceedances': exceed,
            'positive': bool(actual > 0 and tail <= .05),
            'all_pool_multisets_preserved': True,
            'pair_reconstruction_and_global_renaming_checks': len(tp) + len(ep),
            'scope': 'Four-outcome equality coupling only, not a likelihood of meaning or a language identification'}


def run(repo, plan, out):
    out.mkdir(parents=True, exist_ok=True)
    cases, inventories = [], {}
    for name, source in plan['sources'].items():
        p = repo / source['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == source['sha256']
        for commas in plan['commas']:
            rows, inventory = data.parse_ivtff(p, commas)
            inventories[name + '_' + commas] = inventory
            for mode in plan['units']:
                cid = name + '_' + commas + '_' + mode
                cases.append(run_case(cid, rows, mode, plan, out))
    real_cases = list(cases)
    controls = data.controls(plan['seed'])
    for name in plan['controls']:
        cases.append(run_case('control_' + name, controls[name], 'letters', plan, out))
    lookup = {c['id']: c for c in cases}
    gate = (not lookup['control_iid']['positive'] and not lookup['control_iid_layout']['positive']
            and lookup['control_echo']['positive'])
    semantic = data.semantic_certificate()
    save(out / 'semantic_certificate.json', semantic)
    save(out / 'source_inventories.json', inventories)
    summary = {'schema': 'alien-protocol-result-v1', 'seed': plan['seed'], 'cases': cases,
               'synthetic_control_gate': 'PASS' if gate else 'FAIL',
               'robust_across_all_eight_projections': all(c['positive'] for c in real_cases),
               'morphological_rival_positive': lookup['control_morphology']['positive'],
               'semantic_translation': 'NOT_IDENTIFIED', 'Voynich_translation_validated': False,
               'Kraken_training': 'NOT_RUN', 'novelty_claimed': False,
               'scope': 'Exploratory diagnostic on an already explored corpus; known synthetic controls, no external semantic anchors'}
    save(out / 'result.json', summary)
    files = []
    for p in sorted(out.rglob('*')):
        if p.is_file() and p.name != 'file_manifest.json':
            raw = p.read_bytes()
            files.append({'path': p.relative_to(out).as_posix(), 'bytes': len(raw),
                          'sha256': hashlib.sha256(raw).hexdigest()})
    save(out / 'file_manifest.json', {'schema': 'alien-protocol-files-v1', 'files': files})
    print(json.dumps({k: summary[k] for k in ['synthetic_control_gate',
                     'robust_across_all_eight_projections', 'semantic_translation']}))
    for c in cases:
        print(json.dumps({k: c[k] for k in ['id', 'test_pairs', 'coupling_bits_per_pair',
                          'format_bits_per_pair', 'conditional_randomization_tail', 'positive']}))
    return summary


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--plan', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    run(args.repo, json.loads(args.plan.read_text()), args.out)
