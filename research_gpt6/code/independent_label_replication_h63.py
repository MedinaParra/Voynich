#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re
from collections import defaultdict
from pathlib import Path

SOURCE_BLOB = '7f491b574b65e5fba6b553e57372c3fa50e10fec'
SEED = 20261007


def blob_sha(b):
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def feats(t):
    return [
        t.count('o') / len(t),
        t.count('a') / len(t),
        t.count('y') / len(t),
        float(t.startswith('q')),
        float(t.endswith('y')),
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
            meta = dict(re.findall(r'\$([A-Z])=([^\s>]+)', p.group(2)))
            pages[p.group(1)] = {'currier': meta.get('L', '?'), 'hand': meta.get('H', '?')}
            continue
        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m.group(1):
            continue
        locus, text = m.groups()
        fol = locus.split('.')[0]
        pos = locus.split(',', 1)[1]
        meta = pages.get(fol, {})
        toks = clean_tokens(text)
        lm = re.search(r'(L[A-Za-z]?)', pos)
        if lm and len(toks) == 1 and '?' not in text:
            positives.append({'folio': fol, 'token': toks[0], **meta})
            continue
        if generic_locus_type(pos) == 'P':
            for t in toks:
                running[(fol, meta.get('currier', '?'), meta.get('hand', '?'), len(t))].append(t)
    return positives, running


def build_pairs(positives, running):
    rng = random.Random(SEED)
    pairs = []
    excluded = 0
    for r in sorted(positives, key=lambda x: (x['folio'], x['token'], x['currier'], x['hand'])):
        key = (r['folio'], r['currier'], r['hand'], len(r['token']))
        cand = running.get(key, [])
        if not cand:
            excluded += 1
            continue
        control = cand[rng.randrange(len(cand))]
        pairs.append({'folio': r['folio'], 'positive': r['token'], 'control': control, 'key': key})
    return pairs, excluded


def standardize(X, T):
    d = len(X[0])
    mu = [sum(x[j] for x in X) / len(X) for j in range(d)]
    sd = []
    for j in range(d):
        v = sum((x[j] - mu[j]) ** 2 for x in X) / len(X)
        sd.append(math.sqrt(v) if v > 0 else 1.0)
    return (
        [[(x[j] - mu[j]) / sd[j] for j in range(d)] for x in X],
        [[(x[j] - mu[j]) / sd[j] for j in range(d)] for x in T],
    )


def d2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def score(pairs, labels=None):
    if labels is None:
        labels = [1] * len(pairs)
    preds = []
    truth = []
    for fol in sorted(set(p['folio'] for p in pairs)):
        tr = [i for i, p in enumerate(pairs) if p['folio'] != fol]
        te = [i for i, p in enumerate(pairs) if p['folio'] == fol]
        if not tr or not te:
            continue
        X, y, T, yt = [], [], [], []
        for i in tr:
            a, b = pairs[i]['positive'], pairs[i]['control']
            lab = labels[i]
            X.extend([feats(a), feats(b)])
            y.extend([lab, 1 - lab])
        for i in te:
            a, b = pairs[i]['positive'], pairs[i]['control']
            lab = labels[i]
            T.extend([feats(a), feats(b)])
            yt.extend([lab, 1 - lab])
        X, T = standardize(X, T)
        means = {}
        for c in (0, 1):
            z = [X[j] for j, v in enumerate(y) if v == c]
            means[c] = [sum(x[k] for x in z) / len(z) for k in range(len(z[0]))]
        pp = [min((0, 1), key=lambda c: d2(x, means[c])) for x in T]
        preds.extend(pp)
        truth.extend(yt)
    recalls = []
    for c in (0, 1):
        ix = [i for i, v in enumerate(truth) if v == c]
        recalls.append(sum(preds[i] == c for i in ix) / len(ix))
    return sum(recalls) / 2


def build_negative(pairs, running):
    rng1 = random.Random(SEED + 1)
    rng2 = random.Random(SEED + 2)
    neg = []
    for x in pairs:
        cand = running.get(tuple(x['key']), [])
        if not cand:
            continue
        i = rng1.randrange(len(cand))
        j = rng2.randrange(len(cand))
        if len(cand) > 1 and j == i:
            j = (j + 1) % len(cand)
        neg.append({'folio': x['folio'], 'positive': cand[i], 'control': cand[j]})
    return neg


def write_out(path, out):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(json.dumps(out, indent=2, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--permutations', type=int, default=999)
    args = ap.parse_args()

    rawb = args.corpus.read_bytes()
    observed_blob = blob_sha(rawb)
    out = {
        'classification': 'H63_INDEPENDENT_STRICT_LABEL_VS_PARAGRAPH_NOT_TRANSLATION',
        'source_repository': 'oklo/voynich_gpt',
        'source_commit': '2d7c61c387ad6962de730caf73c48612bc8f6957',
        'source_path': 'IT2a-n.txt',
        'expected_source_blob': SOURCE_BLOB,
        'observed_source_blob': observed_blob,
        'seed': SEED,
        'permutations_requested': args.permutations,
        'control_generic_locus_type': 'P',
    }
    if observed_blob != SOURCE_BLOB:
        out.update({'status': 'BLOCKED', 'reason': 'frozen independent source blob mismatch', 'permutations_completed': 0})
        write_out(args.out, out)
        return

    positives, running = parse(rawb.decode())
    pairs, excluded = build_pairs(positives, running)
    nfol = len(set(p['folio'] for p in pairs))
    out.update({
        'positive_tokens': len(positives),
        'matched_pairs': len(pairs),
        'represented_folios': nfol,
        'excluded_no_match': excluded,
    })
    if len(pairs) < 60 or nfol < 8:
        out.update({'status': 'BLOCKED', 'reason': 'preregistered independent-source matching/sample threshold not met', 'permutations_completed': 0})
        write_out(args.out, out)
        return

    obs = score(pairs)
    rng = random.Random(SEED)
    null = []
    for _ in range(args.permutations):
        null.append(score(pairs, [rng.randrange(2) for _ in pairs]))
    p = (1 + sum(x >= obs for x in null)) / (1 + len(null))
    neg = build_negative(pairs, running)
    status = 'PASS' if obs > 0.5 and p <= 0.05 and len(null) == 999 else 'FAIL'
    out.update({
        'observed_balanced_accuracy': obs,
        'null_mean_balanced_accuracy': sum(null) / len(null),
        'monte_carlo_p': p,
        'permutations_completed': len(null),
        'negative_control_balanced_accuracy': score(neg) if neg else None,
        'negative_control_pairs': len(neg),
        'status': status,
        'language_identification': 'NOT_RUN',
        'semantic_identification': 'NOT_RUN',
        'translation': 'NOT_RUN',
        'decipherment': 'NOT_RUN',
    })
    write_out(args.out, out)


if __name__ == '__main__':
    main()
