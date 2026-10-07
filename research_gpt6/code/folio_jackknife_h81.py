#!/usr/bin/env python3
import argparse, hashlib, json, random, re
from collections import defaultdict
from pathlib import Path

SEED_A = 20261009
SEED_B = 20261010
BLOBS = {
    'A': '2a4533ab9bdfa85db9bad602d590978953055df1',
    'B': '7f491b574b65e5fba6b553e57372c3fa50e10fec',
}
EXPECTED_EVENTS = 122
EXPECTED_FOLIOS = 27
MIN_SCENARIO_EVENTS = 90
MIN_SCENARIO_FOLIOS = 25
TARGET_INDEX = 4


def blob_sha(b):
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def clean_tokens(text):
    clean = re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;', ' ', text).replace('?', ' ')
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])', clean)


def generic_locus_type(pos):
    m = re.search(r'([PLCR])(?:[A-Za-z0-9]*)', pos)
    return m.group(1) if m else None


def label_locus_type(pos):
    m = re.search(r'(L[A-Za-z0-9]?)', pos)
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
        lt = label_locus_type(pos)
        if lt and len(toks) == 1 and '?' not in text:
            labels[locus] = {
                'folio': fol,
                'token': toks[0],
                'currier': cur,
                'hand': hand,
                'label_type': lt,
            }
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
        if a['label_type'] != b['label_type']:
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
            'label_type': a['label_type'],
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


def make_scenario(events, pool_key, omitted_folio):
    by_folio = defaultdict(list)
    kept = 0
    for e in events:
        if e['folio'] == omitted_folio:
            continue
        by_folio[e['folio']].append(residual(e, pool_key))
        kept += 1
    folio_means = {f: sum(v) / len(v) for f, v in by_folio.items()}
    mean = sum(folio_means.values()) / len(folio_means) if folio_means else None
    return {
        'events': kept,
        'folios': len(folio_means),
        'mean': mean,
        'folio_means': folio_means,
    }


def evaluate(events, pool_key, parent_folios, nperm, seed):
    scenarios = {f: make_scenario(events, pool_key, f) for f in parent_folios}
    observed_min = min(x['mean'] for x in scenarios.values())
    worst_folios = sorted(f for f, x in scenarios.items() if x['mean'] == observed_min)

    rng = random.Random(seed)
    null_min = []
    for _ in range(nperm):
        signs = {f: (1 if rng.randrange(2) else -1) for f in parent_folios}
        scenario_values = []
        for x in scenarios.values():
            fm = x['folio_means']
            scenario_values.append(sum(fm[f] * signs[f] for f in fm) / len(fm))
        null_min.append(min(scenario_values))

    p = (1 + sum(v >= observed_min for v in null_min)) / (1 + len(null_min))
    return {
        'scenarios': {
            f: {
                'events': x['events'],
                'folios': x['folios'],
                'equal_folio_mean_residual_a': x['mean'],
            }
            for f, x in scenarios.items()
        },
        'worst_case_equal_folio_mean_residual_a': observed_min,
        'worst_case_omitted_folios': worst_folios,
        'worst_case_p_one_sided': p,
        'null_min_mean': sum(null_min) / len(null_min),
        'null_min_max': max(null_min),
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
        'classification': 'H81_FOLIO_JACKKNIFE_NOT_TRANSLATION',
        'source_a_blob': blob_sha(ba),
        'source_b_blob': blob_sha(bb),
        'seed_a': SEED_A,
        'seed_b': SEED_B,
        'target_full_token_index': TARGET_INDEX,
        'expected_parent_events': EXPECTED_EVENTS,
        'expected_parent_folios': EXPECTED_FOLIOS,
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
    parent_folios = sorted(set(e['folio'] for e in events))
    out.update({
        'aligned_exact_prefix_events': len(events),
        'represented_folios': len(parent_folios),
        'parent_folios': parent_folios,
    })

    if len(events) != EXPECTED_EVENTS or len(parent_folios) != EXPECTED_FOLIOS:
        out.update({'status': 'BLOCKED', 'reason': 'BLOCKED_SAMPLE_DRIFT'})
        write(args.out, out)
        return

    support = {}
    for omitted in parent_folios:
        kept = [e for e in events if e['folio'] != omitted]
        support[omitted] = {
            'events': len(kept),
            'folios': len(set(e['folio'] for e in kept)),
        }
    out['scenario_support_audit'] = support

    if len(support) != EXPECTED_FOLIOS:
        out.update({'status': 'BLOCKED', 'reason': 'unexpected leave-one-folio-out scenario count'})
        write(args.out, out)
        return

    if any(x['events'] < MIN_SCENARIO_EVENTS or x['folios'] < MIN_SCENARIO_FOLIOS for x in support.values()):
        out.update({'status': 'BLOCKED', 'reason': 'BLOCKED_CONCENTRATION'})
        write(args.out, out)
        return

    A = evaluate(events, 'pool_a', parent_folios, args.permutations, SEED_A)
    B = evaluate(events, 'pool_b', parent_folios, args.permutations, SEED_B)
    out['source_a'] = A
    out['source_b'] = B

    if A['permutations_completed'] != 999 or B['permutations_completed'] != 999:
        out.update({'status': 'BLOCKED', 'reason': 'randomization count incomplete'})
    else:
        pa = A['worst_case_equal_folio_mean_residual_a'] > 0 and A['worst_case_p_one_sided'] <= 0.05
        pb = B['worst_case_equal_folio_mean_residual_a'] > 0 and B['worst_case_p_one_sided'] <= 0.05
        out['status'] = 'PASS' if pa and pb else 'FAIL'

    out.update({
        'lexical_meaning': 'NOT_RUN',
        'visual_object_mapping': 'NOT_RUN',
        'language_identification': 'NOT_RUN',
        'semantic_identification': 'NOT_RUN',
        'translation': 'NOT_RUN',
        'decipherment': 'NOT_RUN',
    })
    write(args.out, out)


if __name__ == '__main__':
    main()
