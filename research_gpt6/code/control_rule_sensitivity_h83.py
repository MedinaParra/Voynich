#!/usr/bin/env python3
import argparse, hashlib, json, random, re
from collections import defaultdict
from pathlib import Path

BLOBS = {
    'A': '2a4533ab9bdfa85db9bad602d590978953055df1',
    'B': '7f491b574b65e5fba6b553e57372c3fa50e10fec',
}
EXPECTED_EVENTS = 122
EXPECTED_FOLIOS = 27
TARGET_INDEX = 4
PRIMARY_SEEDS = {'A': 20261013, 'B': 20261014}
DELTA_SEEDS = {'A': 20261015, 'B': 20261016}


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
    pref = defaultdict(list)
    length = defaultdict(list)
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
            labels[locus] = {'folio': folio, 'token': toks[0], 'currier': currier, 'hand': hand}
            continue
        if generic_locus_type(pos) == 'P':
            for token in toks:
                if len(token) >= 5:
                    pref[(folio, currier, hand, len(token), token[:2])].append(token)
                    length[(folio, currier, hand, len(token))].append(token)
    return labels, pref, length


def build_h72(labels_a, pref_a, labels_b, pref_b):
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
        pa, pb = pref_a.get(key, []), pref_b.get(key, [])
        if not pa or not pb:
            continue
        events.append({
            'locus': locus,
            'folio': a['folio'],
            'currier': a['currier'],
            'hand': a['hand'],
            'token': t,
            'prefix_a': pa,
            'prefix_b': pb,
        })
    return events


def add_length_pools(events, length_a, length_b):
    out = []
    missing = []
    for e in events:
        key = (e['folio'], e['currier'], e['hand'], len(e['token']))
        la, lb = length_a.get(key, []), length_b.get(key, [])
        if not la or not lb:
            missing.append(e['locus'])
            continue
        out.append({**e, 'length_a': la, 'length_b': lb})
    return out, missing


def residual(token, pool):
    lab = 1.0 if token[TARGET_INDEX] == 'a' else 0.0
    base = sum(1.0 if t[TARGET_INDEX] == 'a' else 0.0 for t in pool) / len(pool)
    return lab - base


def aggregate(events, source):
    pref_key = 'prefix_a' if source == 'A' else 'prefix_b'
    len_key = 'length_a' if source == 'A' else 'length_b'
    by_folio_primary = defaultdict(list)
    by_folio_prefix = defaultdict(list)
    by_folio_delta = defaultdict(list)
    all_primary, all_prefix, all_delta = [], [], []
    for e in events:
        rp = residual(e['token'], e[pref_key])
        rl = residual(e['token'], e[len_key])
        d = rp - rl
        by_folio_primary[e['folio']].append(rl)
        by_folio_prefix[e['folio']].append(rp)
        by_folio_delta[e['folio']].append(d)
        all_primary.append(rl)
        all_prefix.append(rp)
        all_delta.append(d)
    def means(d):
        return {f: sum(v) / len(v) for f, v in d.items()}
    fm_primary = means(by_folio_primary)
    fm_prefix = means(by_folio_prefix)
    fm_delta = means(by_folio_delta)
    return {
        'primary_folio_means': fm_primary,
        'prefix_folio_means': fm_prefix,
        'delta_folio_means': fm_delta,
        'length_only_equal_folio_mean_residual_a': sum(fm_primary.values()) / len(fm_primary),
        'exact_prefix_equal_folio_mean_residual_a': sum(fm_prefix.values()) / len(fm_prefix),
        'paired_exact_minus_length_equal_folio_mean': sum(fm_delta.values()) / len(fm_delta),
        'length_only_event_weighted_mean_residual_a': sum(all_primary) / len(all_primary),
        'exact_prefix_event_weighted_mean_residual_a': sum(all_prefix) / len(all_prefix),
        'paired_exact_minus_length_event_weighted_mean': sum(all_delta) / len(all_delta),
    }


def signflip_p(folio_means, seed, nperm):
    folios = sorted(folio_means)
    obs = sum(folio_means.values()) / len(folios)
    rng = random.Random(seed)
    null = []
    for _ in range(nperm):
        signs = {f: (1 if rng.randrange(2) else -1) for f in folios}
        null.append(sum(folio_means[f] * signs[f] for f in folios) / len(folios))
    p = (1 + sum(v >= obs for v in null)) / (1 + len(null))
    return {'observed': obs, 'p_one_sided': p, 'permutations_completed': len(null), 'null_mean': sum(null) / len(null), 'null_max': max(null)}


def evaluate(events, source, nperm):
    agg = aggregate(events, source)
    primary = signflip_p(agg['primary_folio_means'], PRIMARY_SEEDS[source], nperm)
    delta = signflip_p(agg['delta_folio_means'], DELTA_SEEDS[source], nperm)
    return {
        'events': len(events),
        'folios': len(agg['primary_folio_means']),
        'length_only_equal_folio_mean_residual_a': agg['length_only_equal_folio_mean_residual_a'],
        'exact_prefix_equal_folio_mean_residual_a': agg['exact_prefix_equal_folio_mean_residual_a'],
        'paired_exact_minus_length_equal_folio_mean': agg['paired_exact_minus_length_equal_folio_mean'],
        'length_only_event_weighted_mean_residual_a': agg['length_only_event_weighted_mean_residual_a'],
        'exact_prefix_event_weighted_mean_residual_a': agg['exact_prefix_event_weighted_mean_residual_a'],
        'paired_exact_minus_length_event_weighted_mean': agg['paired_exact_minus_length_event_weighted_mean'],
        'primary_length_only_p_one_sided': primary['p_one_sided'],
        'primary_permutations_completed': primary['permutations_completed'],
        'primary_null_mean': primary['null_mean'],
        'primary_null_max': primary['null_max'],
        'paired_delta_p_one_sided': delta['p_one_sided'],
        'delta_permutations_completed': delta['permutations_completed'],
        'delta_null_mean': delta['null_mean'],
        'delta_null_max': delta['null_max'],
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
        'classification': 'H83_CONTROL_RULE_SENSITIVITY_NOT_TRANSLATION',
        'source_a_blob': blob_sha(ba),
        'source_b_blob': blob_sha(bb),
        'target_full_token_index': TARGET_INDEX,
        'primary_seed_a': PRIMARY_SEEDS['A'],
        'primary_seed_b': PRIMARY_SEEDS['B'],
        'delta_seed_a': DELTA_SEEDS['A'],
        'delta_seed_b': DELTA_SEEDS['B'],
        'permutations_requested': args.permutations,
    }
    if out['source_a_blob'] != BLOBS['A'] or out['source_b_blob'] != BLOBS['B']:
        out.update({'status': 'BLOCKED', 'reason': 'BLOCKED_SOURCE'})
        write(args.out, out)
        return

    la, pa, lena = parse(ba.decode())
    lb, pb, lenb = parse(bb.decode())
    h72 = build_h72(la, pa, lb, pb)
    folios = {e['folio'] for e in h72}
    out.update({'h72_reconstructed_events': len(h72), 'h72_reconstructed_folios': len(folios)})
    if len(h72) != EXPECTED_EVENTS or len(folios) != EXPECTED_FOLIOS:
        out.update({'status': 'BLOCKED', 'reason': 'BLOCKED_SAMPLE_DRIFT'})
        write(args.out, out)
        return

    events, missing = add_length_pools(h72, lena, lenb)
    out['missing_length_only_control_loci'] = missing
    out['events_with_both_control_rules'] = len(events)
    if missing or len(events) != EXPECTED_EVENTS:
        out.update({'status': 'BLOCKED', 'reason': 'BLOCKED_CONTROL_CONSTRUCTION'})
        write(args.out, out)
        return
    if args.permutations != 999:
        out.update({'status': 'BLOCKED', 'reason': 'frozen permutation count must be exactly 999'})
        write(args.out, out)
        return

    A = evaluate(events, 'A', args.permutations)
    B = evaluate(events, 'B', args.permutations)
    out['source_a'] = A
    out['source_b'] = B

    complete = all([
        A['primary_permutations_completed'] == 999,
        B['primary_permutations_completed'] == 999,
        A['delta_permutations_completed'] == 999,
        B['delta_permutations_completed'] == 999,
    ])
    if not complete:
        out.update({'status': 'BLOCKED', 'reason': 'incomplete randomization'})
    else:
        pass_a = A['length_only_equal_folio_mean_residual_a'] > 0 and A['primary_length_only_p_one_sided'] <= 0.05
        pass_b = B['length_only_equal_folio_mean_residual_a'] > 0 and B['primary_length_only_p_one_sided'] <= 0.05
        out['status'] = 'PASS' if pass_a and pass_b else 'FAIL'
        out['diagnostic'] = (
            'CONTROL_RULE_ROBUST' if out['status'] == 'PASS' else
            'CONTROL_SENSITIVE' if (
                A['paired_exact_minus_length_equal_folio_mean'] > 0 and A['paired_delta_p_one_sided'] <= 0.05 and
                B['paired_exact_minus_length_equal_folio_mean'] > 0 and B['paired_delta_p_one_sided'] <= 0.05
            ) else 'UNRESOLVED_SAMPLE_OR_CONTROL_EFFECT'
        )

    out.update({
        'lexical_meaning': 'NOT_RUN',
        'semantic_identification': 'NOT_RUN',
        'language_identification': 'NOT_RUN',
        'plaintext': 'NOT_RUN',
        'translation': 'NOT_RUN',
        'decipherment': 'NOT_RUN',
    })
    write(args.out, out)


if __name__ == '__main__':
    main()
