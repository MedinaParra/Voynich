#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re
from collections import Counter, defaultdict
from pathlib import Path

ZL_BLOB = '2a4533ab9bdfa85db9bad602d590978953055df1'
TAKAHASHI_BLOB = '7f491b574b65e5fba6b553e57372c3fa50e10fec'
SEED = 20261007
PERMUTATIONS = 999
ALPHA_PER_DIRECTION = 0.025
FEATURE_NAMES = [
    'unique_fraction',
    'singleton_type_fraction',
    'max_frequency_fraction',
    'adjacent_equal_fraction',
    'first_last_equal',
]


def blob_sha(b):
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def feats(t):
    n = len(t)
    c = Counter(t)
    k = len(c)
    return [
        k / n,
        sum(v == 1 for v in c.values()) / k,
        max(c.values()) / n,
        sum(t[i] == t[i - 1] for i in range(1, n)) / (n - 1),
        float(t[0] == t[-1]),
    ]


def clean_tokens(text):
    clean = re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;', ' ', text).replace('?', ' ')
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])', clean)


def generic_locus_type(pos):
    m = re.search(r'([PLCR])(?:[A-Za-z0-9]*)', pos)
    return m.group(1) if m else None


def parse(raw):
    pages = {}
    positives = []
    running = defaultdict(list)
    for line in raw.splitlines():
        p = re.match(r'^<([^>.,]+)>\s*<!([^>]*)>', line)
        if p:
            m = dict(re.findall(r'\$([A-Z])=([^\s>]+)', p.group(2)))
            pages[p.group(1)] = {'currier': m.get('L', '?'), 'hand': m.get('H', '?')}
            continue
        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m.group(1):
            continue
        locus, text = m.groups()
        fol = locus.split('.')[0]
        pos = locus.split(',', 1)[1]
        meta = pages.get(fol, {})
        toks = clean_tokens(text)
        typ = generic_locus_type(pos)
        if typ == 'L' and len(toks) == 1 and '?' not in text:
            positives.append({'folio': fol, 'token': toks[0], **meta})
            continue
        if typ == 'P':
            for t in toks:
                running[(fol, meta.get('currier', '?'), meta.get('hand', '?'), len(t))].append(t)
    return positives, running


def build_pairs(pos, running):
    rng = random.Random(SEED)
    pairs = []
    excluded = 0
    for r in sorted(pos, key=lambda x: (x['folio'], x['token'], x['currier'], x['hand'])):
        key = (r['folio'], r['currier'], r['hand'], len(r['token']))
        cand = running.get(key, [])
        if not cand:
            excluded += 1
            continue
        control = cand[rng.randrange(len(cand))]
        pairs.append({'folio': r['folio'], 'positive': r['token'], 'control': control, 'key': key})
    return pairs, excluded


def fit_model(pairs):
    X, y = [], []
    for p in pairs:
        X.extend([feats(p['positive']), feats(p['control'])])
        y.extend([1, 0])
    d = len(FEATURE_NAMES)
    mu = [sum(x[j] for x in X) / len(X) for j in range(d)]
    sd = []
    for j in range(d):
        v = sum((x[j] - mu[j]) ** 2 for x in X) / len(X)
        sd.append(math.sqrt(v) if v > 0 else 1.0)
    Z = [[(x[j] - mu[j]) / sd[j] for j in range(d)] for x in X]
    means = {}
    for cls in (0, 1):
        z = [Z[i] for i, yy in enumerate(y) if yy == cls]
        means[cls] = [sum(x[j] for x in z) / len(z) for j in range(d)]
    return mu, sd, means


def d2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def predict(token, model):
    mu, sd, means = model
    x = feats(token)
    z = [(x[j] - mu[j]) / sd[j] for j in range(len(x))]
    return min((0, 1), key=lambda cls: d2(z, means[cls]))


def frozen_predictions(training_pairs, test_pairs):
    predictions = []
    models = {}
    train_counts = {}
    for fol in sorted(set(p['folio'] for p in test_pairs)):
        tr = [p for p in training_pairs if p['folio'] != fol]
        if not tr:
            raise RuntimeError('no training pairs after same-folio exclusion')
        models[fol] = fit_model(tr)
        train_counts[fol] = len(tr)
    for p in test_pairs:
        model = models[p['folio']]
        predictions.append((predict(p['positive'], model), predict(p['control'], model)))
    return predictions, models, train_counts


def balanced_accuracy(predictions, labels):
    truth, predicted = [], []
    for i, (pa, pb) in enumerate(predictions):
        lab = labels[i]
        predicted.extend([pa, pb])
        truth.extend([lab, 1 - lab])
    recalls = []
    for cls in (0, 1):
        idx = [i for i, yy in enumerate(truth) if yy == cls]
        recalls.append(sum(predicted[i] == cls for i in idx) / len(idx))
    return sum(recalls) / 2


def negative_control(test_pairs, running, models, seed_offset):
    rng1 = random.Random(SEED + seed_offset)
    rng2 = random.Random(SEED + seed_offset + 1)
    predictions, labels = [], []
    for p in test_pairs:
        cand = running.get(tuple(p['key']), [])
        if not cand:
            continue
        ia = rng1.randrange(len(cand))
        ib = rng2.randrange(len(cand))
        if len(cand) > 1 and ib == ia:
            ib = (ib + 1) % len(cand)
        model = models[p['folio']]
        predictions.append((predict(cand[ia], model), predict(cand[ib], model)))
        labels.append(1)
    return (balanced_accuracy(predictions, labels) if predictions else None, len(predictions))


def run_direction(name, training_pairs, test_pairs, test_running, seed_offset):
    nfol = len(set(p['folio'] for p in test_pairs))
    result = {
        'direction': name,
        'training_pairs': len(training_pairs),
        'test_pairs': len(test_pairs),
        'test_folios': nfol,
        'permutations_requested': PERMUTATIONS,
        'alpha_bonferroni': ALPHA_PER_DIRECTION,
    }
    if len(training_pairs) < 60 or len(test_pairs) < 60 or nfol < 8:
        result.update({
            'status': 'BLOCKED',
            'permutations_completed': 0,
            'reason': 'preregistered sample-validity threshold not met',
        })
        return result

    pred, models, train_counts = frozen_predictions(training_pairs, test_pairs)
    labels = [1] * len(test_pairs)
    obs = balanced_accuracy(pred, labels)
    rng = random.Random(SEED)
    null = [balanced_accuracy(pred, [rng.randrange(2) for _ in test_pairs]) for _ in range(PERMUTATIONS)]
    pval = (1 + sum(x >= obs for x in null)) / (1 + len(null))
    neg, nneg = negative_control(test_pairs, test_running, models, seed_offset)
    status = 'PASS' if obs > 0.5 and pval <= ALPHA_PER_DIRECTION and len(null) == PERMUTATIONS else 'FAIL'
    result.update({
        'observed_balanced_accuracy': obs,
        'null_mean_balanced_accuracy': sum(null) / len(null),
        'monte_carlo_p': pval,
        'permutations_completed': len(null),
        'negative_control_balanced_accuracy': neg,
        'negative_control_pairs': nneg,
        'min_training_pairs_per_test_folio': min(train_counts.values()),
        'max_training_pairs_per_test_folio': max(train_counts.values()),
        'status': status,
    })
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--zl', type=Path, required=True)
    ap.add_argument('--takahashi', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    zb = a.zl.read_bytes()
    tb = a.takahashi.read_bytes()
    zsha = blob_sha(zb)
    tsha = blob_sha(tb)
    if zsha != ZL_BLOB:
        raise SystemExit(f'frozen ZL mismatch: {zsha}')
    if tsha != TAKAHASHI_BLOB:
        raise SystemExit(f'frozen Takahashi mismatch: {tsha}')

    zpos, zrun = parse(zb.decode())
    tpos, trun = parse(tb.decode())
    zpairs, zexcluded = build_pairs(zpos, zrun)
    tpairs, texcluded = build_pairs(tpos, trun)

    zl_to_t = run_direction('zl_to_takahashi', zpairs, tpairs, trun, 101)
    t_to_zl = run_direction('takahashi_to_zl', tpairs, zpairs, zrun, 201)

    if 'BLOCKED' in (zl_to_t['status'], t_to_zl['status']):
        overall = 'BLOCKED'
    elif zl_to_t['status'] == 'PASS' and t_to_zl['status'] == 'PASS':
        overall = 'PASS'
    else:
        overall = 'FAIL'

    out = {
        'classification': 'BIDIRECTIONAL_SYMBOL_RENAMING_INVARIANT_ZERO_SHOT_STRICT_LABEL_VS_PARAGRAPH_NOT_TRANSLATION',
        'zl_blob': ZL_BLOB,
        'takahashi_blob': TAKAHASHI_BLOB,
        'seed': SEED,
        'feature_names': FEATURE_NAMES,
        'feature_invariance': 'arbitrary_bijective_symbol_renaming',
        'zl_positive_tokens': len(zpos),
        'zl_matched_pairs': len(zpairs),
        'zl_excluded_no_match': zexcluded,
        'takahashi_positive_tokens': len(tpos),
        'takahashi_matched_pairs': len(tpairs),
        'takahashi_excluded_no_match': texcluded,
        'directions': {
            'zl_to_takahashi': zl_to_t,
            'takahashi_to_zl': t_to_zl,
        },
        'status': overall,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
