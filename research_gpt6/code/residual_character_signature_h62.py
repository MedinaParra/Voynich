#!/usr/bin/env python3
import argparse, hashlib, json, random, re
from collections import defaultdict
from pathlib import Path

SOURCE_BLOB = '2a4533ab9bdfa85db9bad602d590978953055df1'
SEED = 20261007
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
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
            pages[p.group(1)] = {
                'currier': meta.get('L', '?'),
                'hand': meta.get('H', '?'),
                'quire': meta.get('Q', '?'),
            }
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
        pairs.append({
            'folio': r['folio'],
            'quire': r.get('quire', '?'),
            'positive': r['token'],
            'control': control,
        })
    return pairs, excluded


def residual(token):
    return token[2:-1]


def freq_vec(s):
    n = len(s)
    return [s.count(c) / n for c in ALPHABET]


def pair_diff(pair):
    a = freq_vec(residual(pair['positive']))
    b = freq_vec(residual(pair['control']))
    return [x - y for x, y in zip(a, b)]


def mean_vec(rows, signs=None):
    if signs is None:
        signs = [1.0] * len(rows)
    n = len(rows)
    return [sum(signs[i] * rows[i][j] for i in range(n)) / n for j in range(len(ALPHABET))]


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
    recreated = {
        'positive_tokens': len(positives),
        'matched_pairs': len(h60_pairs),
        'represented_folios': len(set(p['folio'] for p in h60_pairs)),
        'excluded_no_match': excluded,
    }

    out = {
        'classification': 'H62_RESIDUAL_CHARACTER_SIGNATURE_NOT_TRANSLATION',
        'source_blob': SOURCE_BLOB,
        'seed': SEED,
        'h60_expected': H60_EXPECTED,
        'h60_recreated': recreated,
        'boundary_ablation': 'token[2:-1]',
        'min_token_length': 5,
        'alphabet': ALPHABET,
        'permutations_requested': args.permutations,
    }

    if recreated != H60_EXPECTED:
        out.update({'status': 'BLOCKED', 'reason': 'exact H60 sample was not recreated', 'permutations_completed': 0})
        write_out(args.out, out)
        return

    pairs = [p for p in h60_pairs if len(p['positive']) >= 5]
    nfol = len(set(p['folio'] for p in pairs))
    qgroups = defaultdict(list)
    for i, p in enumerate(pairs):
        qgroups[p.get('quire', '?')].append(i)
    evaluable = {q: idx for q, idx in qgroups.items() if q != '?' and len(idx) >= 5}

    out.update({
        'retained_pairs': len(pairs),
        'represented_folios': nfol,
        'excluded_short_pairs': len(h60_pairs) - len(pairs),
        'quire_pair_counts': {q: len(idx) for q, idx in sorted(qgroups.items())},
        'evaluable_quires': sorted(evaluable),
        'evaluable_quire_count': len(evaluable),
    })

    if len(pairs) < 100 or nfol < 8:
        out.update({'status': 'BLOCKED', 'reason': 'preregistered H62 pair/folio threshold not met', 'permutations_completed': 0})
        write_out(args.out, out)
        return
    if len(evaluable) < 8:
        out.update({'status': 'BLOCKED', 'reason': 'preregistered H62 evaluable-quire threshold not met', 'permutations_completed': 0})
        write_out(args.out, out)
        return

    rows = [pair_diff(p) for p in pairs]
    observed = mean_vec(rows)

    rng = random.Random(SEED)
    null_max = []
    for _ in range(args.permutations):
        signs = [1.0 if rng.randrange(2) else -1.0 for _ in rows]
        d = mean_vec(rows, signs)
        null_max.append(max(abs(x) for x in d))

    stats = {}
    significant = []
    for j, c in enumerate(ALPHABET):
        obs = observed[j]
        p_fwer = (1 + sum(x >= abs(obs) for x in null_max)) / (1 + len(null_max))
        stats[c] = {'mean_L_minus_P': obs, 'p_FWER': p_fwer}
        if p_fwer <= 0.05:
            significant.append(c)

    stability = {}
    for c in significant:
        j = ALPHABET.index(c)
        global_sign = 1 if observed[j] > 0 else -1 if observed[j] < 0 else 0
        qdiff = {}
        support = 0
        for q, idxs in sorted(evaluable.items()):
            d = sum(rows[i][j] for i in idxs) / len(idxs)
            qdiff[q] = d
            qsign = 1 if d > 0 else -1 if d < 0 else 0
            if global_sign != 0 and qsign == global_sign:
                support += 1
        frac = support / len(evaluable)
        stability[c] = {
            'global_sign': 'positive' if global_sign > 0 else 'negative' if global_sign < 0 else 'zero',
            'supporting_quires': support,
            'evaluable_quires': len(evaluable),
            'sign_stability': frac,
            'per_quire_mean_L_minus_P': qdiff,
        }

    stable_sig = [c for c in significant if stability[c]['sign_stability'] >= 0.75]
    ranked = sorted(ALPHABET, key=lambda c: stats[c]['mean_L_minus_P'])
    passed = len(null_max) == 999 and bool(stable_sig)

    out.update({
        'character_statistics': stats,
        'significant_characters_FWER_0_05': significant,
        'stability': stability,
        'stable_significant_characters': stable_sig,
        'largest_negative_shift_character': ranked[0],
        'largest_negative_shift': stats[ranked[0]]['mean_L_minus_P'],
        'largest_positive_shift_character': ranked[-1],
        'largest_positive_shift': stats[ranked[-1]]['mean_L_minus_P'],
        'null_max_abs_mean': sum(null_max) / len(null_max),
        'permutations_completed': len(null_max),
        'status': 'PASS' if passed else 'FAIL',
        'language_identification': 'NOT_RUN',
        'semantic_identification': 'NOT_RUN',
        'translation': 'NOT_RUN',
        'decipherment': 'NOT_RUN',
    })
    write_out(args.out, out)


if __name__ == '__main__':
    main()
