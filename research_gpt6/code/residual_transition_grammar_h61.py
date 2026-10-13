#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re, statistics
from collections import defaultdict
from pathlib import Path

SOURCE_BLOB = '2a4533ab9bdfa85db9bad602d590978953055df1'
SEED = 20261007
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
ALPHA = 1.0
H60_EXPECTED = {'positive_tokens': 780, 'matched_pairs': 495, 'represented_folios': 34, 'excluded_no_match': 285}


def blob_sha(b):
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


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
                key = (fol, meta.get('currier', '?'), meta.get('hand', '?'), len(t))
                running[key].append(t)
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
        pairs.append({'folio': r['folio'], 'positive': r['token'], 'control': control})
    return pairs, excluded


def body(token):
    return token[2:-1]


def fit_model(strings):
    trans = defaultdict(lambda: defaultdict(int))
    totals = defaultdict(int)
    for s in strings:
        for a, b in zip(s, s[1:]):
            trans[a][b] += 1
            totals[a] += 1
    return trans, totals


def mean_loglik(s, model):
    trans, totals = model
    vals = []
    denom_extra = ALPHA * len(ALPHABET)
    for a, b in zip(s, s[1:]):
        vals.append(math.log((trans[a].get(b, 0) + ALPHA) / (totals.get(a, 0) + denom_extra)))
    return sum(vals) / len(vals)


def score(pairs, orientations=None, bodies_override=None, return_per_folio=False):
    # orientation 1 = original positive is L; 0 = identities swapped within pair.
    if orientations is None:
        orientations = [1] * len(pairs)
    if bodies_override is None:
        bodies_override = [(body(p['positive']), body(p['control'])) for p in pairs]

    all_preds = []
    all_truth = []
    per_folio = {}
    folios = sorted(set(p['folio'] for p in pairs))

    for fol in folios:
        tr_idx = [i for i, p in enumerate(pairs) if p['folio'] != fol]
        te_idx = [i for i, p in enumerate(pairs) if p['folio'] == fol]
        train = {0: [], 1: []}
        for i in tr_idx:
            a, b = bodies_override[i]
            lab = orientations[i]
            train[lab].append(a)
            train[1 - lab].append(b)
        models = {c: fit_model(train[c]) for c in (0, 1)}

        fp = []
        ft = []
        for i in te_idx:
            a, b = bodies_override[i]
            lab = orientations[i]
            for s, truth in ((a, lab), (b, 1 - lab)):
                l0 = mean_loglik(s, models[0])
                l1 = mean_loglik(s, models[1])
                pred = 1 if l1 > l0 else 0  # ties -> P/class 0
                fp.append(pred)
                ft.append(truth)
                all_preds.append(pred)
                all_truth.append(truth)
        if return_per_folio:
            rec = []
            for c in (0, 1):
                ix = [j for j, v in enumerate(ft) if v == c]
                rec.append(sum(fp[j] == c for j in ix) / len(ix))
            per_folio[fol] = sum(rec) / 2

    recalls = []
    for c in (0, 1):
        ix = [i for i, v in enumerate(all_truth) if v == c]
        recalls.append(sum(all_preds[i] == c for i in ix) / len(ix))
    ba = sum(recalls) / 2
    return (ba, per_folio) if return_per_folio else ba


def shuffled_bodies(base_bodies, rng):
    out = []
    changed = 0
    total = 0
    for a, b in base_bodies:
        row = []
        for s in (a, b):
            chars = list(s)
            rng.shuffle(chars)
            z = ''.join(chars)
            changed += int(z != s)
            total += 1
            row.append(z)
        out.append(tuple(row))
    return out, changed / total if total else 0.0


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
    if blob_sha(rawb) != SOURCE_BLOB:
        raise SystemExit('frozen corpus mismatch')
    positives, running = parse(rawb.decode())
    h60_pairs, excluded = build_pairs(positives, running)
    h60_folios = len(set(p['folio'] for p in h60_pairs))
    recreated = {
        'positive_tokens': len(positives),
        'matched_pairs': len(h60_pairs),
        'represented_folios': h60_folios,
        'excluded_no_match': excluded,
    }

    out = {
        'classification': 'H61_RESIDUAL_TRANSITION_GRAMMAR_NOT_TRANSLATION',
        'source_blob': SOURCE_BLOB,
        'seed_identity': SEED,
        'seed_order': SEED + 1,
        'h60_recreated': recreated,
        'h60_expected': H60_EXPECTED,
        'permutations_requested_each_null': args.permutations,
        'boundary_ablation': 'token[2:-1]',
        'min_token_length': 5,
        'smoothing_alpha': ALPHA,
    }

    if recreated != H60_EXPECTED:
        out.update({'status': 'BLOCKED', 'reason': 'exact H60 sample was not recreated',
                    'identity_permutations_completed': 0, 'order_randomizations_completed': 0})
        write_out(args.out, out)
        return

    pairs = [p for p in h60_pairs if len(p['positive']) >= 5]
    nfol = len(set(p['folio'] for p in pairs))
    out.update({'retained_pairs': len(pairs), 'represented_folios': nfol,
                'excluded_short_pairs': len(h60_pairs) - len(pairs)})
    if len(pairs) < 100 or nfol < 8:
        out.update({'status': 'BLOCKED', 'reason': 'preregistered H61 sample threshold not met',
                    'identity_permutations_completed': 0, 'order_randomizations_completed': 0})
        write_out(args.out, out)
        return

    observed, per_folio = score(pairs, return_per_folio=True)

    rng_id = random.Random(SEED)
    null_identity = []
    for _ in range(args.permutations):
        orient = [rng_id.randrange(2) for _ in pairs]
        null_identity.append(score(pairs, orientations=orient))

    base_bodies = [(body(p['positive']), body(p['control'])) for p in pairs]
    rng_order = random.Random(SEED + 1)
    null_order = []
    changed_fracs = []
    for _ in range(args.permutations):
        shuffled, frac = shuffled_bodies(base_bodies, rng_order)
        null_order.append(score(pairs, bodies_override=shuffled))
        changed_fracs.append(frac)

    p_identity = (1 + sum(x >= observed for x in null_identity)) / (1 + len(null_identity))
    p_order = (1 + sum(x >= observed for x in null_order)) / (1 + len(null_order))
    mean_order = sum(null_order) / len(null_order)
    valid_counts = len(null_identity) == 999 and len(null_order) == 999
    passed = (valid_counts and observed > 0.5 and p_identity <= 0.05 and p_order <= 0.05 and observed > mean_order)

    out.update({
        'observed_balanced_accuracy': observed,
        'identity_null_mean_ba': sum(null_identity) / len(null_identity),
        'identity_null_median_ba': statistics.median(null_identity),
        'p_identity': p_identity,
        'identity_permutations_completed': len(null_identity),
        'order_null_mean_ba': mean_order,
        'order_null_median_ba': statistics.median(null_order),
        'p_order': p_order,
        'order_randomizations_completed': len(null_order),
        'mean_fraction_residual_bodies_changed_by_shuffle': sum(changed_fracs) / len(changed_fracs),
        'per_folio_balanced_accuracy': per_folio,
        'status': 'PASS' if passed else 'FAIL',
        'language_identification': 'NOT_RUN',
        'semantic_identification': 'NOT_RUN',
        'translation': 'NOT_RUN',
        'decipherment': 'NOT_RUN',
    })
    write_out(args.out, out)


if __name__ == '__main__':
    main()
