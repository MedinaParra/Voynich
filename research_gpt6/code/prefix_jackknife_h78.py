#!/usr/bin/env python3
import argparse, hashlib, json, random, re
from collections import Counter, defaultdict
from pathlib import Path

SEED_A = 20261007
SEED_B = 20261008
BLOBS = {
    'A': '2a4533ab9bdfa85db9bad602d590978953055df1',
    'B': '7f491b574b65e5fba6b553e57372c3fa50e10fec',
}
MIN_MAJOR_EVENTS = 10
MIN_MAJOR_FOLIOS = 5
MIN_MAJOR_PREFIXES = 3
MIN_SCENARIO_EVENTS = 60
MIN_SCENARIO_FOLIOS = 15
TARGET_INDEX = 4


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
            labels[locus] = {'folio': fol, 'token': toks[0], 'currier': cur, 'hand': hand}
            continue
        if generic_locus_type(pos) == 'P':
            for t in toks:
                if len(t) >= 5:
                    running[(fol, cur, hand, len(t), t[:2])].append(t)
    return labels, running


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
        pa, pb = run_a.get(key, []), run_b.get(key, [])
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


def residual(event, pool_key):
    lab = 1.0 if event['label'][TARGET_INDEX] == 'a' else 0.0
    pool = event[pool_key]
    base = sum(1.0 if t[TARGET_INDEX] == 'a' else 0.0 for t in pool) / len(pool)
    return lab - base


def major_prefixes(events):
    audit = {}
    for p in sorted(set(e['prefix'] for e in events)):
        rows = [e for e in events if e['prefix'] == p]
        audit[p] = {'events': len(rows), 'folios': len(set(e['folio'] for e in rows))}
    majors = [p for p, x in audit.items() if x['events'] >= MIN_MAJOR_EVENTS and x['folios'] >= MIN_MAJOR_FOLIOS]
    return majors, audit


def scenario_folio_means(events, pool_key, omitted):
    by_folio = defaultdict(list)
    kept = 0
    for e in events:
        if e['prefix'] == omitted:
            continue
        r = residual(e, pool_key)
        by_folio[e['folio']].append(r)
        kept += 1
    fm = {f: sum(v) / len(v) for f, v in by_folio.items()}
    mean = sum(fm.values()) / len(fm) if fm else None
    return {
        'omitted_prefix': omitted,
        'events': kept,
        'folios': len(fm),
        'equal_folio_mean_residual_a': mean,
        'folio_means': fm,
    }


def evaluate(events, pool_key, majors, nperm, seed):
    scenarios = {p: scenario_folio_means(events, pool_key, p) for p in majors}
    obs_min = min(s['equal_folio_mean_residual_a'] for s in scenarios.values())
    all_folios = sorted(set().union(*(set(s['folio_means']) for s in scenarios.values())))
    rng = random.Random(seed)
    null_min = []
    for _ in range(nperm):
        signs = {f: (1 if rng.randrange(2) else -1) for f in all_folios}
        stats = []
        for s in scenarios.values():
            fm = s['folio_means']
            stats.append(sum(fm[f] * signs[f] for f in fm) / len(fm))
        null_min.append(min(stats))
    p = (1 + sum(x >= obs_min for x in null_min)) / (1 + len(null_min))
    return {
        'scenarios': {
            pfx: {
                'events': s['events'],
                'folios': s['folios'],
                'equal_folio_mean_residual_a': s['equal_folio_mean_residual_a'],
            }
            for pfx, s in scenarios.items()
        },
        'worst_case_equal_folio_mean_residual_a': obs_min,
        'worst_case_p_one_sided': p,
        'null_min_mean': sum(null_min) / len(null_min),
        'permutations_completed': len(null_min),
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

    ba, bb = args.source_a.read_bytes(), args.source_b.read_bytes()
    out = {
        'classification': 'H78_PREFIX_JACKKNIFE_NOT_TRANSLATION',
        'source_a_blob': blob_sha(ba),
        'source_b_blob': blob_sha(bb),
        'seed_a': SEED_A,
        'seed_b': SEED_B,
        'target_full_token_index': TARGET_INDEX,
        'minimum_major_prefix_events': MIN_MAJOR_EVENTS,
        'minimum_major_prefix_folios': MIN_MAJOR_FOLIOS,
        'minimum_major_prefixes': MIN_MAJOR_PREFIXES,
        'minimum_scenario_events': MIN_SCENARIO_EVENTS,
        'minimum_scenario_folios': MIN_SCENARIO_FOLIOS,
        'permutations_requested_each_source': args.permutations,
    }
    if out['source_a_blob'] != BLOBS['A'] or out['source_b_blob'] != BLOBS['B']:
        out.update({'status': 'BLOCKED', 'reason': 'frozen source blob mismatch'})
        write(args.out, out)
        return

    la, ra = parse(ba.decode())
    lb, rb = parse(bb.decode())
    events = build_common(la, ra, lb, rb)
    majors, audit = major_prefixes(events)
    out.update({
        'aligned_exact_prefix_events': len(events),
        'represented_folios': len(set(e['folio'] for e in events)),
        'prefix_audit': audit,
        'major_prefixes': majors,
    })
    if len(majors) < MIN_MAJOR_PREFIXES:
        out.update({'status': 'BLOCKED', 'reason': 'preregistered major-prefix threshold not met'})
        write(args.out, out)
        return

    support = {}
    for p in majors:
        kept = [e for e in events if e['prefix'] != p]
        support[p] = {'events': len(kept), 'folios': len(set(e['folio'] for e in kept))}
    out['scenario_support_audit'] = support
    if any(x['events'] < MIN_SCENARIO_EVENTS or x['folios'] < MIN_SCENARIO_FOLIOS for x in support.values()):
        out.update({'status': 'BLOCKED', 'reason': 'preregistered jackknife scenario support threshold not met'})
        write(args.out, out)
        return

    A = evaluate(events, 'pool_a', majors, args.permutations, SEED_A)
    B = evaluate(events, 'pool_b', majors, args.permutations, SEED_B)
    out['source_a'] = A
    out['source_b'] = B

    if A['permutations_completed'] != 999 or B['permutations_completed'] != 999:
        out.update({'status': 'BLOCKED', 'reason': 'randomization count incomplete'})
    else:
        pass_a = A['worst_case_equal_folio_mean_residual_a'] > 0 and A['worst_case_p_one_sided'] <= 0.05
        pass_b = B['worst_case_equal_folio_mean_residual_a'] > 0 and B['worst_case_p_one_sided'] <= 0.05
        out['status'] = 'PASS' if pass_a and pass_b else 'FAIL'

    out.update({
        'language_identification': 'NOT_RUN',
        'semantic_identification': 'NOT_RUN',
        'translation': 'NOT_RUN',
        'decipherment': 'NOT_RUN',
    })
    write(args.out, out)


if __name__ == '__main__':
    main()
