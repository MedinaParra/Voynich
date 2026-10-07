#!/usr/bin/env python3
import argparse, hashlib, json, random, re
from collections import defaultdict
from pathlib import Path

BLOBS = {
    'A': '2a4533ab9bdfa85db9bad602d590978953055df1',
    'B': '7f491b574b65e5fba6b553e57372c3fa50e10fec',
}
SEED_A = 20261011
SEED_B = 20261012
EXPECTED_H72_EVENTS = 122
EXPECTED_H72_FOLIOS = 27
MIN_H82_EVENTS = 50
MIN_H82_FOLIOS = 15
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
    running_prefix = defaultdict(list)
    running_length = defaultdict(list)
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
        folio = locus.split('.')[0]
        pos = locus.split(',', 1)[1]
        currier, hand = pages.get(folio, ('?', '?'))
        toks = clean_tokens(text)
        if re.search(r'(L[A-Za-z]?)', pos) and len(toks) == 1 and '?' not in text:
            labels[locus] = {
                'folio': folio,
                'token': toks[0],
                'currier': currier,
                'hand': hand,
            }
            continue
        if generic_locus_type(pos) == 'P':
            for token in toks:
                if len(token) >= 5:
                    running_prefix[(folio, currier, hand, len(token), token[:2])].append(token)
                    running_length[(folio, currier, hand, len(token))].append(token)
    return labels, running_prefix, running_length


def aligned_labels(labels_a, labels_b):
    out = []
    for locus in sorted(set(labels_a) & set(labels_b)):
        a, b = labels_a[locus], labels_b[locus]
        if a['token'] != b['token']:
            continue
        if a['currier'] != b['currier'] or a['hand'] != b['hand']:
            continue
        if len(a['token']) < 5:
            continue
        out.append({
            'locus': locus,
            'folio': a['folio'],
            'token': a['token'],
            'currier': a['currier'],
            'hand': a['hand'],
        })
    return out


def h72_members(aligned, pref_a, pref_b):
    members = []
    for e in aligned:
        t = e['token']
        key = (e['folio'], e['currier'], e['hand'], len(t), t[:2])
        if pref_a.get(key) and pref_b.get(key):
            members.append(e)
    return members


def h82_members(aligned, excluded_loci, length_a, length_b):
    members = []
    for e in aligned:
        if e['locus'] in excluded_loci:
            continue
        t = e['token']
        key = (e['folio'], e['currier'], e['hand'], len(t))
        pa = length_a.get(key, [])
        pb = length_b.get(key, [])
        if not pa or not pb:
            continue
        members.append({**e, 'pool_a': pa, 'pool_b': pb})
    return members


def event_residual(e, pool_key):
    label_value = 1.0 if e['token'][TARGET_INDEX] == 'a' else 0.0
    pool = e[pool_key]
    control_value = sum(1.0 if t[TARGET_INDEX] == 'a' else 0.0 for t in pool) / len(pool)
    return label_value - control_value


def evaluate(events, pool_key, seed, nperm):
    by_folio = defaultdict(list)
    for e in events:
        by_folio[e['folio']].append(event_residual(e, pool_key))
    folio_means = {f: sum(v) / len(v) for f, v in by_folio.items()}
    observed = sum(folio_means.values()) / len(folio_means)
    event_weighted = sum(x for vals in by_folio.values() for x in vals) / sum(len(vals) for vals in by_folio.values())

    folios = sorted(folio_means)
    rng = random.Random(seed)
    null = []
    for _ in range(nperm):
        signs = {f: (1 if rng.randrange(2) else -1) for f in folios}
        null.append(sum(folio_means[f] * signs[f] for f in folios) / len(folios))
    p = (1 + sum(v >= observed for v in null)) / (1 + len(null))
    return {
        'events': len(events),
        'folios': len(folios),
        'equal_folio_mean_residual_a': observed,
        'event_weighted_mean_residual_a': event_weighted,
        'p_one_sided': p,
        'permutations_completed': len(null),
        'null_mean': sum(null) / len(null),
        'null_max': max(null),
        'folio_event_counts': {f: len(by_folio[f]) for f in folios},
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
        'classification': 'H82_OUT_OF_SAMPLE_LABEL_REPLICATION_NOT_TRANSLATION',
        'source_a_blob': blob_sha(ba),
        'source_b_blob': blob_sha(bb),
        'seed_a': SEED_A,
        'seed_b': SEED_B,
        'target_full_token_index': TARGET_INDEX,
        'minimum_h82_events': MIN_H82_EVENTS,
        'minimum_h82_folios': MIN_H82_FOLIOS,
        'permutations_requested_each_source': args.permutations,
    }

    if out['source_a_blob'] != BLOBS['A'] or out['source_b_blob'] != BLOBS['B']:
        out.update({'status': 'BLOCKED', 'reason': 'BLOCKED_SOURCE'})
        write(args.out, out)
        return

    la, pa, lena = parse(ba.decode())
    lb, pb, lenb = parse(bb.decode())
    aligned = aligned_labels(la, lb)
    discovery = h72_members(aligned, pa, pb)
    discovery_loci = {e['locus'] for e in discovery}
    discovery_folios = {e['folio'] for e in discovery}
    out.update({
        'aligned_label_events_before_control_matching': len(aligned),
        'h72_reconstructed_events': len(discovery),
        'h72_reconstructed_folios': len(discovery_folios),
    })

    if len(discovery) != EXPECTED_H72_EVENTS or len(discovery_folios) != EXPECTED_H72_FOLIOS:
        out.update({'status': 'BLOCKED', 'reason': 'BLOCKED_SAMPLE_DRIFT'})
        write(args.out, out)
        return

    heldout = h82_members(aligned, discovery_loci, lena, lenb)
    heldout_loci = {e['locus'] for e in heldout}
    overlap = sorted(discovery_loci & heldout_loci)
    heldout_folios = sorted({e['folio'] for e in heldout})
    out.update({
        'h82_heldout_events': len(heldout),
        'h82_heldout_folios': len(heldout_folios),
        'h82_folio_ids': heldout_folios,
        'h72_h82_locus_overlap_count': len(overlap),
        'h72_h82_locus_overlap': overlap,
    })

    if overlap:
        out.update({'status': 'BLOCKED', 'reason': 'H72_H82_LOCUS_OVERLAP'})
        write(args.out, out)
        return
    if len(heldout) < MIN_H82_EVENTS or len(heldout_folios) < MIN_H82_FOLIOS:
        out.update({'status': 'BLOCKED', 'reason': 'BLOCKED_SUPPORT'})
        write(args.out, out)
        return
    if args.permutations != 999:
        out.update({'status': 'BLOCKED', 'reason': 'frozen permutation count must be exactly 999'})
        write(args.out, out)
        return

    A = evaluate(heldout, 'pool_a', SEED_A, args.permutations)
    B = evaluate(heldout, 'pool_b', SEED_B, args.permutations)
    out['source_a'] = A
    out['source_b'] = B

    complete = A['permutations_completed'] == 999 and B['permutations_completed'] == 999
    if not complete:
        out.update({'status': 'BLOCKED', 'reason': 'incomplete randomization'})
    else:
        pass_a = A['equal_folio_mean_residual_a'] > 0 and A['p_one_sided'] <= 0.05
        pass_b = B['equal_folio_mean_residual_a'] > 0 and B['p_one_sided'] <= 0.05
        out['status'] = 'PASS' if pass_a and pass_b else 'FAIL'

    out.update({
        'functional_locus_association': 'TESTED_H82',
        'lexical_meaning': 'NOT_RUN',
        'visual_object_mapping': 'NOT_RUN',
        'semantic_identification': 'NOT_RUN',
        'language_identification': 'NOT_RUN',
        'plaintext': 'NOT_RUN',
        'translation': 'NOT_RUN',
        'decipherment': 'NOT_RUN',
    })
    write(args.out, out)


if __name__ == '__main__':
    main()
