#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re
from collections import defaultdict
from pathlib import Path

SEED = 20261007
BLOBS = {
    'A': '2a4533ab9bdfa85db9bad602d590978953055df1',
    'B': '7f491b574b65e5fba6b553e57372c3fa50e10fec',
}
MIN_FAMILY = 15
MIN_FAMILIES = 3
MIN_PAIRS = 80
MIN_FOLIOS = 8


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
    labels = {}
    running = defaultdict(list)
    for line in raw.splitlines():
        p = re.match(r'^<([^>.,]+)>\s*<!([^>]*)>', line)
        if p:
            meta = dict(re.findall(r'\$([A-Z])=([^\s>]+)', p.group(2)))
            pages[p.group(1)] = (meta.get('L', '?'), meta.get('H', '?'))
            continue
        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m.group(1):
            continue
        locus, text = m.groups()
        fol = locus.split('.')[0]
        pos = locus.split(',', 1)[1]
        cur, hand = pages.get(fol, ('?', '?'))
        toks = clean_tokens(text)
        if re.search(r'(L[A-Za-z]?)', pos) and len(toks) == 1 and '?' not in text:
            labels[locus] = {
                'folio': fol,
                'token': toks[0],
                'currier': cur,
                'hand': hand,
            }
            continue
        if generic_locus_type(pos) == 'P':
            for t in toks:
                if len(t) >= 2:
                    running[(fol, cur, hand, len(t), t[:2])].append(t)
    return labels, running


def body_a(t):
    b = t[2:-1]
    return b.count('a') / len(b)


def tstat(ds):
    n = len(ds)
    if n < 2:
        return 0.0
    mu = sum(ds) / n
    var = sum((x - mu) ** 2 for x in ds) / (n - 1)
    if var == 0:
        if mu > 0:
            return 1e12
        if mu < 0:
            return -1e12
        return 0.0
    return mu / (math.sqrt(var) / math.sqrt(n))


def build_common(labels_a, run_a, labels_b, run_b):
    shared = []
    for locus in sorted(set(labels_a) & set(labels_b)):
        a, b = labels_a[locus], labels_b[locus]
        if a['token'] != b['token']:
            continue
        if a['currier'] != b['currier'] or a['hand'] != b['hand']:
            continue
        t = a['token']
        if len(t) < 5:
            continue
        key = (a['folio'], a['currier'], a['hand'], len(t), t[:2])
        ca = sorted(run_a.get(key, []))
        cb = sorted(run_b.get(key, []))
        if not ca or not cb:
            continue
        shared.append((locus, a, ca, cb))

    rng_a = random.Random(SEED)
    rng_b = random.Random(SEED + 1)
    events = []
    for locus, a, ca, cb in shared:
        events.append({
            'locus': locus,
            'folio': a['folio'],
            'family': a['token'][:2],
            'label': a['token'],
            'control_a': ca[rng_a.randrange(len(ca))],
            'control_b': cb[rng_b.randrange(len(cb))],
        })
    return events


def eligible_events(events):
    counts = defaultdict(int)
    for e in events:
        counts[e['family']] += 1
    fams = sorted(f for f, n in counts.items() if n >= MIN_FAMILY)
    kept = [e for e in events if e['family'] in set(fams)]
    return kept, fams, dict(sorted(counts.items()))


def evaluate(events, families, control_key, nperm, seed):
    byfam = defaultdict(list)
    pair_diffs = []
    for e in events:
        d = body_a(e['label']) - body_a(e[control_key])
        byfam[e['family']].append(d)
        pair_diffs.append((e['family'], d))

    family_means = {f: sum(byfam[f]) / len(byfam[f]) for f in families}
    family_counts = {f: len(byfam[f]) for f in families}
    macro = sum(family_means[f] for f in families) / len(families)
    pooled = sum(d for _, d in pair_diffs) / len(pair_diffs)
    obs_t = {f: tstat(byfam[f]) for f in families}

    rng = random.Random(seed)
    null_macro = []
    null_max_t = []
    for _ in range(nperm):
        perm_byfam = defaultdict(list)
        for f, d in pair_diffs:
            perm_byfam[f].append(d if rng.randrange(2) else -d)
        pm = {f: sum(perm_byfam[f]) / len(perm_byfam[f]) for f in families}
        null_macro.append(sum(pm[f] for f in families) / len(families))
        null_max_t.append(max(abs(tstat(perm_byfam[f])) for f in families))

    p_primary = (1 + sum(x >= macro for x in null_macro)) / (1 + len(null_macro))
    p_fwer = {
        f: (1 + sum(x >= abs(obs_t[f]) for x in null_max_t)) / (1 + len(null_max_t))
        for f in families
    }
    return {
        'pairs': len(events),
        'folios': len(set(e['folio'] for e in events)),
        'eligible_families': families,
        'family_counts': family_counts,
        'family_mean_diff_a': family_means,
        'family_t_a': obs_t,
        'family_p_fwer_two_sided': p_fwer,
        'equal_family_weighted_mean_diff_a': macro,
        'pooled_event_weighted_mean_diff_a': pooled,
        'primary_null_mean': sum(null_macro) / len(null_macro),
        'primary_p_one_sided': p_primary,
        'permutations_completed': len(null_macro),
    }


def write(path, out):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(json.dumps(out, indent=2, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-a', type=Path, required=True)
    ap.add_argument('--source-b', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--permutations', type=int, default=999)
    args = ap.parse_args()

    ba = args.source_a.read_bytes()
    bb = args.source_b.read_bytes()
    out = {
        'classification': 'H70_PREFIX_FAMILY_INTERNAL_A_NOT_TRANSLATION',
        'seed_a': SEED,
        'seed_b': SEED + 1,
        'source_a_blob': blob_sha(ba),
        'source_b_blob': blob_sha(bb),
        'permutations_requested_each_source': args.permutations,
        'minimum_events_per_family': MIN_FAMILY,
        'minimum_eligible_families': MIN_FAMILIES,
        'minimum_pooled_pairs': MIN_PAIRS,
        'minimum_folios': MIN_FOLIOS,
    }
    if out['source_a_blob'] != BLOBS['A'] or out['source_b_blob'] != BLOBS['B']:
        out.update({'status': 'BLOCKED', 'reason': 'frozen source blob mismatch'})
        write(args.out, out)
        return

    la, ra = parse(ba.decode())
    lb, rb = parse(bb.decode())
    common = build_common(la, ra, lb, rb)
    kept, families, all_family_counts = eligible_events(common)
    out.update({
        'aligned_control_eligible_events_before_family_threshold': len(common),
        'all_prefix_family_counts': all_family_counts,
        'eligible_families': families,
        'retained_pairs': len(kept),
        'represented_folios': len(set(e['folio'] for e in kept)),
    })

    if (len(families) < MIN_FAMILIES or len(kept) < MIN_PAIRS or
            len(set(e['folio'] for e in kept)) < MIN_FOLIOS):
        out.update({'status': 'BLOCKED', 'reason': 'preregistered sample/family threshold not met'})
        write(args.out, out)
        return

    A = evaluate(kept, families, 'control_a', args.permutations, SEED)
    B = evaluate(kept, families, 'control_b', args.permutations, SEED + 1)
    out['source_a'] = A
    out['source_b'] = B

    common_positive = [
        f for f in families
        if A['family_mean_diff_a'][f] > 0 and B['family_mean_diff_a'][f] > 0
    ]
    out['families_positive_in_both_sources'] = common_positive

    valid_perm = A['permutations_completed'] == 999 and B['permutations_completed'] == 999
    passed = (
        valid_perm and
        A['equal_family_weighted_mean_diff_a'] > 0 and
        B['equal_family_weighted_mean_diff_a'] > 0 and
        A['primary_p_one_sided'] <= 0.05 and
        B['primary_p_one_sided'] <= 0.05 and
        len(common_positive) >= 2
    )
    out['status'] = 'PASS' if passed else 'FAIL'
    out.update({
        'language_identification': 'NOT_RUN',
        'semantic_identification': 'NOT_RUN',
        'translation': 'NOT_RUN',
        'decipherment': 'NOT_RUN',
    })
    write(args.out, out)


if __name__ == '__main__':
    main()
