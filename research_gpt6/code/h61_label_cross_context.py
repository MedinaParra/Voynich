#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_BLOB = '2a4533ab9bdfa85db9bad602d590978953055df1'
SEED = 20261007
MIN_GROUP_PAIRS = 10
MIN_VIEW_PAIRS = 60


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
    paragraph = defaultdict(list)
    for line in raw.splitlines():
        p = re.match(r'^<([^>.,]+)>\s*<!([^>]*)>', line)
        if p:
            m = dict(re.findall(r'\$([A-Z])=([^\s>]+)', p.group(2)))
            pages[p.group(1)] = {
                'currier': m.get('L', '?'),
                'hand': m.get('H', '?'),
                'quire': m.get('Q', '?'),
            }
            continue
        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m.group(1):
            continue
        locus, text = m.groups()
        fol = locus.split('.')[0]
        pos = locus.split(',', 1)[1]
        meta = pages.get(fol, {'currier': '?', 'hand': '?', 'quire': '?'})
        toks = clean_tokens(text)
        lm = re.search(r'(L[A-Za-z]?)', pos)
        if lm and len(toks) == 1 and '?' not in text:
            positives.append({'folio': fol, 'token': toks[0], **meta})
            continue
        if generic_locus_type(pos) == 'P':
            key0 = (fol, meta['currier'], meta['hand'])
            for t in toks:
                paragraph[(*key0, len(t))].append(t)
    return positives, paragraph


def build_pairs(positives, paragraph):
    rng = random.Random(SEED)
    pairs = []
    excluded = 0
    for r in sorted(positives, key=lambda x: (x['folio'], x['token'], x['currier'], x['hand'], x['quire'])):
        key = (r['folio'], r['currier'], r['hand'], len(r['token']))
        cand = paragraph.get(key, [])
        if not cand:
            excluded += 1
            continue
        control = cand[rng.randrange(len(cand))]
        pairs.append({
            'folio': r['folio'],
            'hand': r['hand'],
            'quire': r['quire'],
            'positive': r['token'],
            'control': control,
        })
    return pairs, excluded


def standardize(train, test):
    d = len(train[0])
    mu = [sum(x[j] for x in train) / len(train) for j in range(d)]
    sd = []
    for j in range(d):
        v = sum((x[j] - mu[j]) ** 2 for x in train) / len(train)
        sd.append(math.sqrt(v) if v > 0 else 1.0)
    return (
        [[(x[j] - mu[j]) / sd[j] for j in range(d)] for x in train],
        [[(x[j] - mu[j]) / sd[j] for j in range(d)] for x in test],
    )


def d2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def eligible_view(pairs, field):
    counts = Counter(p[field] for p in pairs if p[field] not in ('', '?'))
    groups = sorted(g for g, n in counts.items() if n >= MIN_GROUP_PAIRS)
    indices = [i for i, p in enumerate(pairs) if p[field] in groups]
    return groups, indices, counts


def score_view(pairs, field, groups, indices, labels=None):
    if labels is None:
        labels = [1] * len(pairs)
    preds = []
    truth = []
    group_ba = {}
    for held in groups:
        tr = [i for i in indices if pairs[i][field] != held]
        te = [i for i in indices if pairs[i][field] == held]
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
        rec = []
        for c in (0, 1):
            ix = [j for j, v in enumerate(yt) if v == c]
            rec.append(sum(pp[j] == c for j in ix) / len(ix))
        group_ba[held] = sum(rec) / 2
        preds.extend(pp)
        truth.extend(yt)
    rec = []
    for c in (0, 1):
        ix = [i for i, v in enumerate(truth) if v == c]
        if not ix:
            return None, group_ba
        rec.append(sum(preds[i] == c for i in ix) / len(ix))
    return sum(rec) / 2, group_ba


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--permutations', type=int, default=999)
    args = ap.parse_args()

    raw_bytes = args.corpus.read_bytes()
    if blob_sha(raw_bytes) != SOURCE_BLOB:
        raise SystemExit('frozen corpus mismatch')

    positives, paragraph = parse(raw_bytes.decode())
    pairs, excluded = build_pairs(positives, paragraph)
    hand_groups, hand_ix, hand_counts = eligible_view(pairs, 'hand')
    quire_groups, quire_ix, quire_counts = eligible_view(pairs, 'quire')

    out = {
        'classification': 'STRICT_LABEL_VS_PARAGRAPH_CROSS_CONTEXT_NOT_TRANSLATION',
        'source_blob': SOURCE_BLOB,
        'seed': SEED,
        'positive_tokens': len(positives),
        'matched_pairs': len(pairs),
        'excluded_no_match': excluded,
        'minimum_group_pairs': MIN_GROUP_PAIRS,
        'minimum_view_pairs': MIN_VIEW_PAIRS,
        'permutations_requested': args.permutations,
        'views': {
            'hand': {
                'eligible_groups': hand_groups,
                'eligible_pairs': len(hand_ix),
                'all_group_counts': dict(sorted(hand_counts.items())),
            },
            'quire': {
                'eligible_groups': quire_groups,
                'eligible_pairs': len(quire_ix),
                'all_group_counts': dict(sorted(quire_counts.items())),
            },
        },
    }

    blocked = []
    if len(hand_groups) < 2 or len(hand_ix) < MIN_VIEW_PAIRS:
        blocked.append('hand view threshold not met')
    if len(quire_groups) < 2 or len(quire_ix) < MIN_VIEW_PAIRS:
        blocked.append('quire view threshold not met')
    if blocked:
        out.update({'status': 'BLOCKED', 'permutations_completed': 0, 'reason': '; '.join(blocked)})
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(out, indent=2) + '\n')
        print(json.dumps(out, indent=2))
        return

    obs_hand, by_hand = score_view(pairs, 'hand', hand_groups, hand_ix)
    obs_quire, by_quire = score_view(pairs, 'quire', quire_groups, quire_ix)
    rng = random.Random(SEED)
    null_hand, null_quire = [], []
    for _ in range(args.permutations):
        labels = [rng.randrange(2) for _ in pairs]
        h, _ = score_view(pairs, 'hand', hand_groups, hand_ix, labels)
        q, _ = score_view(pairs, 'quire', quire_groups, quire_ix, labels)
        null_hand.append(h)
        null_quire.append(q)

    def summarize(obs, null, per_group):
        p = (1 + sum(x >= obs for x in null)) / (1 + len(null))
        status = 'PASS' if obs > 0.5 and p <= 0.05 and len(null) == 999 else 'FAIL'
        return {
            'observed_balanced_accuracy': obs,
            'null_mean_balanced_accuracy': sum(null) / len(null),
            'monte_carlo_p': p,
            'per_group_balanced_accuracy': per_group,
            'permutations_completed': len(null),
            'status': status,
        }

    hand_summary = summarize(obs_hand, null_hand, by_hand)
    quire_summary = summarize(obs_quire, null_quire, by_quire)
    out['views']['hand'].update(hand_summary)
    out['views']['quire'].update(quire_summary)
    out['permutations_completed'] = min(len(null_hand), len(null_quire))
    out['status'] = 'PASS' if hand_summary['status'] == 'PASS' and quire_summary['status'] == 'PASS' else 'FAIL'

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
