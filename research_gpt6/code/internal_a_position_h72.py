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
MIN_EVENTS_POSITION = 60
MIN_FOLIOS_POSITION = 15
MIN_ELIGIBLE_POSITIONS = 2


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


def body_len(t):
    return len(t) - 3


def eligible_positions(events):
    out = []
    max_body = max((body_len(e['label']) for e in events), default=0)
    audit = {}
    for k in range(1, max_body + 1):
        rows = [e for e in events if body_len(e['label']) >= k]
        n = len(rows)
        folios = len(set(e['folio'] for e in rows))
        audit[str(k)] = {'events': n, 'folios': folios}
        if n >= MIN_EVENTS_POSITION and folios >= MIN_FOLIOS_POSITION:
            out.append(k)
    return out, audit


def residual_at_position(label, pool, k):
    idx = 2 + (k - 1)
    lab = 1.0 if label[idx] == 'a' else 0.0
    baseline = sum(1.0 if t[idx] == 'a' else 0.0 for t in pool) / len(pool)
    return lab - baseline


def prepare_position(events, pool_key, k):
    rows = []
    pref = Counter()
    for e in events:
        if body_len(e['label']) < k:
            continue
        r = residual_at_position(e['label'], e[pool_key], k)
        rows.append((e['folio'], r))
        pref[e['prefix']] += 1
    by_folio = defaultdict(list)
    for folio, r in rows:
        by_folio[folio].append(r)
    folio_means = {f: sum(v) / len(v) for f, v in by_folio.items()}
    equal_folio = sum(folio_means.values()) / len(folio_means)
    event_weighted = sum(r for _, r in rows) / len(rows)
    return {
        'events': len(rows),
        'folios': len(folio_means),
        'equal_folio_weighted_mean_residual_a': equal_folio,
        'event_weighted_mean_residual_a': event_weighted,
        'folio_means': folio_means,
        'prefix_counts': dict(sorted(pref.items())),
    }


def evaluate(events, pool_key, positions, nperm, seed):
    prepared = {k: prepare_position(events, pool_key, k) for k in positions}
    all_folios = sorted(set().union(*(set(v['folio_means']) for v in prepared.values())))
    rng = random.Random(seed)
    max_null = []
    for _ in range(nperm):
        signs = {f: (1 if rng.randrange(2) else -1) for f in all_folios}
        stats = []
        for k in positions:
            fm = prepared[k]['folio_means']
            stats.append(sum(fm[f] * signs[f] for f in fm) / len(fm))
        max_null.append(max(stats))

    results = {}
    for k in positions:
        p = prepared[k]
        obs = p['equal_folio_weighted_mean_residual_a']
        pfwer = (1 + sum(x >= obs for x in max_null)) / (1 + len(max_null))
        results[str(k)] = {
            'events': p['events'],
            'folios': p['folios'],
            'equal_folio_weighted_mean_residual_a': obs,
            'event_weighted_mean_residual_a': p['event_weighted_mean_residual_a'],
            'p_fwer_one_sided': pfwer,
            'prefix_counts': p['prefix_counts'],
        }
    return {
        'positions': results,
        'permutations_completed': len(max_null),
        'max_null_mean': sum(max_null) / len(max_null),
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
        'classification': 'H72_INTERNAL_A_POSITION_NOT_TRANSLATION',
        'source_a_blob': blob_sha(ba),
        'source_b_blob': blob_sha(bb),
        'seed_a': SEED_A,
        'seed_b': SEED_B,
        'minimum_events_per_position': MIN_EVENTS_POSITION,
        'minimum_folios_per_position': MIN_FOLIOS_POSITION,
        'minimum_eligible_positions': MIN_ELIGIBLE_POSITIONS,
        'permutations_requested_each_source': args.permutations,
    }
    if out['source_a_blob'] != BLOBS['A'] or out['source_b_blob'] != BLOBS['B']:
        out.update({'status': 'BLOCKED', 'reason': 'frozen source blob mismatch'})
        write(args.out, out)
        return

    la, ra = parse(ba.decode())
    lb, rb = parse(bb.decode())
    events = build_common(la, ra, lb, rb)
    positions, audit = eligible_positions(events)
    out.update({
        'aligned_exact_prefix_events': len(events),
        'represented_folios': len(set(e['folio'] for e in events)),
        'position_count_audit': audit,
        'eligible_positions': positions,
    })
    if len(positions) < MIN_ELIGIBLE_POSITIONS:
        out.update({'status': 'BLOCKED', 'reason': 'preregistered eligible-position threshold not met'})
        write(args.out, out)
        return

    A = evaluate(events, 'pool_a', positions, args.permutations, SEED_A)
    B = evaluate(events, 'pool_b', positions, args.permutations, SEED_B)
    out['source_a'] = A
    out['source_b'] = B

    replicated = []
    if A['permutations_completed'] == 999 and B['permutations_completed'] == 999:
        for k in positions:
            ka = A['positions'][str(k)]
            kb = B['positions'][str(k)]
            if (
                ka['equal_folio_weighted_mean_residual_a'] > 0 and
                kb['equal_folio_weighted_mean_residual_a'] > 0 and
                ka['p_fwer_one_sided'] <= 0.05 and
                kb['p_fwer_one_sided'] <= 0.05
            ):
                replicated.append(k)
    out['replicated_positions'] = replicated
    out['status'] = 'PASS' if replicated else 'FAIL'
    out.update({
        'language_identification': 'NOT_RUN',
        'semantic_identification': 'NOT_RUN',
        'translation': 'NOT_RUN',
        'decipherment': 'NOT_RUN',
    })
    write(args.out, out)


if __name__ == '__main__':
    main()
