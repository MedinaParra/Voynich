#!/usr/bin/env python3
import argparse, hashlib, json, random, re
from collections import defaultdict
from pathlib import Path

SEED_A = 20261007
SEED_B = 20261008
BLOBS = {
    'A': '2a4533ab9bdfa85db9bad602d590978953055df1',
    'B': '7f491b574b65e5fba6b553e57372c3fa50e10fec',
}
MIN_EVENTS = 100
MIN_FOLIOS = 15


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
                if len(t) >= 5:
                    running[(fol, cur, hand, len(t), t[:2])].append(t)
    return labels, running


def internal_a(t):
    b = t[2:-1]
    return b.count('a') / len(b)


def build_common(labels_a, run_a, labels_b, run_b):
    events = []
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
        pa = run_a.get(key, [])
        pb = run_b.get(key, [])
        if not pa or not pb:
            continue
        events.append({
            'locus': locus,
            'folio': a['folio'],
            'prefix': t[:2],
            'label': t,
            'pool_a': pa,
            'pool_b': pb,
        })
    return events


def residual(label, pool):
    baseline = sum(internal_a(t) for t in pool) / len(pool)
    return internal_a(label) - baseline


def evaluate(events, pool_key, nperm, seed):
    rows = []
    total_p_occ = 0
    for e in events:
        pool = e[pool_key]
        total_p_occ += len(pool)
        rows.append({
            'folio': e['folio'],
            'prefix': e['prefix'],
            'residual': residual(e['label'], pool),
            'pool_n': len(pool),
        })

    by_folio = defaultdict(list)
    by_prefix = defaultdict(list)
    for r in rows:
        by_folio[r['folio']].append(r['residual'])
        by_prefix[r['prefix']].append(r['residual'])

    folio_means = {f: sum(v) / len(v) for f, v in by_folio.items()}
    primary = sum(folio_means.values()) / len(folio_means)
    event_weighted = sum(r['residual'] for r in rows) / len(rows)

    rng = random.Random(seed)
    null = []
    folios = sorted(folio_means)
    for _ in range(nperm):
        vals = []
        for f in folios:
            sign = 1 if rng.randrange(2) else -1
            vals.append(folio_means[f] * sign)
        null.append(sum(vals) / len(vals))
    p = (1 + sum(x >= primary for x in null)) / (1 + len(null))

    prefix_desc = {}
    for pref in sorted(by_prefix):
        vals = by_prefix[pref]
        if len(vals) >= 5:
            prefix_desc[pref] = {
                'events': len(vals),
                'mean_residual_a': sum(vals) / len(vals),
            }

    return {
        'events': len(rows),
        'folios': len(folio_means),
        'compatible_p_occurrences_total': total_p_occ,
        'equal_folio_weighted_mean_residual_a': primary,
        'event_weighted_mean_residual_a': event_weighted,
        'null_mean': sum(null) / len(null),
        'p_one_sided': p,
        'permutations_completed': len(null),
        'prefix_descriptive': prefix_desc,
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
        'classification': 'H71_EXACT_PREFIX_BASELINE_RESIDUAL_NOT_TRANSLATION',
        'source_a_blob': blob_sha(ba),
        'source_b_blob': blob_sha(bb),
        'seed_a': SEED_A,
        'seed_b': SEED_B,
        'minimum_events': MIN_EVENTS,
        'minimum_folios': MIN_FOLIOS,
        'permutations_requested_each_source': args.permutations,
    }
    if out['source_a_blob'] != BLOBS['A'] or out['source_b_blob'] != BLOBS['B']:
        out.update({'status': 'BLOCKED', 'reason': 'frozen source blob mismatch'})
        write(args.out, out)
        return

    la, ra = parse(ba.decode())
    lb, rb = parse(bb.decode())
    events = build_common(la, ra, lb, rb)
    folios = len(set(e['folio'] for e in events))
    out.update({
        'aligned_exact_prefix_events': len(events),
        'represented_folios': folios,
    })
    if len(events) < MIN_EVENTS or folios < MIN_FOLIOS:
        out.update({'status': 'BLOCKED', 'reason': 'preregistered event/folio threshold not met'})
        write(args.out, out)
        return

    A = evaluate(events, 'pool_a', args.permutations, SEED_A)
    B = evaluate(events, 'pool_b', args.permutations, SEED_B)
    out['source_a'] = A
    out['source_b'] = B

    passed = (
        A['permutations_completed'] == 999 and
        B['permutations_completed'] == 999 and
        A['equal_folio_weighted_mean_residual_a'] > 0 and
        B['equal_folio_weighted_mean_residual_a'] > 0 and
        A['p_one_sided'] <= 0.05 and
        B['p_one_sided'] <= 0.05
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
