#!/usr/bin/env python3
import argparse, hashlib, json, random, re
from collections import Counter, defaultdict
from pathlib import Path

SEED = 20261007
BLOBS = {
    'A': '2a4533ab9bdfa85db9bad602d590978953055df1',
    'B': '7f491b574b65e5fba6b553e57372c3fa50e10fec',
}


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
    p_by_group = defaultdict(Counter)
    p_by_match = defaultdict(list)
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
        meta = pages.get(fol, {'currier': '?', 'hand': '?'})
        currier, hand = meta.get('currier', '?'), meta.get('hand', '?')
        toks = clean_tokens(text)
        lm = re.search(r'(L[A-Za-z]?)', pos)
        if lm and len(toks) == 1 and '?' not in text:
            labels[locus] = {
                'locus': locus, 'folio': fol, 'token': toks[0],
                'currier': currier, 'hand': hand,
            }
            continue
        if generic_locus_type(pos) == 'P':
            for t in toks:
                p_by_group[(currier, hand)][t] += 1
                p_by_match[(fol, currier, hand, len(t))].append(t)
    return labels, p_by_group, p_by_match


def consensus_h66(la, ma, lb, mb):
    out = []
    for locus in sorted(set(la) & set(lb)):
        a, b = la[locus], lb[locus]
        if a['token'] != b['token']:
            continue
        if (a['currier'], a['hand']) != (b['currier'], b['hand']):
            continue
        ka = (a['folio'], a['currier'], a['hand'], len(a['token']))
        kb = (b['folio'], b['currier'], b['hand'], len(b['token']))
        if not ma.get(ka) or not mb.get(kb):
            continue
        out.append(a)
    return out


def freq_bin(n):
    if n <= 1: return '0-1'
    if n == 2: return '2'
    if n <= 4: return '3-4'
    if n <= 8: return '5-8'
    return '9+'


def build_pairs(source_name, types, aligned_type_keys, p_by_group):
    rng = random.Random(SEED)
    pairs, unmatched = [], 0
    for rec in sorted(types, key=lambda x: (x['currier'], x['hand'], x['token'])):
        t = rec['token']
        group = (rec['currier'], rec['hand'])
        counts = p_by_group.get(group, Counter())
        target_bin = freq_bin(counts.get(t, 0))
        candidates = [u for u, n in counts.items()
                      if u.startswith('o') and len(u) == len(t)
                      and (u, rec['currier'], rec['hand']) not in aligned_type_keys
                      and u != t and freq_bin(n) == target_bin]
        candidates = sorted(set(candidates))
        if not candidates:
            unmatched += 1
            continue
        u = candidates[rng.randrange(len(candidates))]
        pairs.append({
            'label': t,
            'control': u,
            'group': group,
            'label_freq_p': counts.get(t, 0),
            'control_freq_p': counts.get(u, 0),
            'label_q_counterpart': int(('q' + t) in counts),
            'control_q_counterpart': int(('q' + u) in counts),
        })
    return pairs, unmatched


def test_pairs(pairs, nperm, seed):
    n = len(pairs)
    if n < 30:
        return {'status': 'BLOCKED', 'matched_type_pairs': n, 'reason': 'preregistered matched-type threshold not met', 'permutations_completed': 0}
    diffs = [p['label_q_counterpart'] - p['control_q_counterpart'] for p in pairs]
    obs = sum(diffs) / n
    rng = random.Random(seed)
    null = []
    for _ in range(nperm):
        s = 0
        for d in diffs:
            s += d if rng.randrange(2) else -d
        null.append(s / n)
    pval = (1 + sum(x >= obs for x in null)) / (1 + len(null))
    lr = sum(p['label_q_counterpart'] for p in pairs) / n
    cr = sum(p['control_q_counterpart'] for p in pairs) / n
    passed = len(null) == 999 and obs > 0 and pval <= 0.05
    return {
        'matched_type_pairs': n,
        'label_q_counterpart_rate': lr,
        'control_q_counterpart_rate': cr,
        'observed_enrichment': obs,
        'null_mean_enrichment': sum(null) / len(null),
        'monte_carlo_p_one_sided': pval,
        'permutations_completed': len(null),
        'status': 'PASS' if passed else 'FAIL',
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
        'classification': 'H67_Q_PREFIX_COUNTERPART_NOT_TRANSLATION',
        'seed': SEED,
        'source_a_blob': blob_sha(ba),
        'source_b_blob': blob_sha(bb),
        'permutations_requested_each_source': args.permutations,
        'frequency_bins': ['0-1', '2', '3-4', '5-8', '9+'],
    }
    if out['source_a_blob'] != BLOBS['A'] or out['source_b_blob'] != BLOBS['B']:
        out.update({'status': 'BLOCKED', 'reason': 'frozen source blob mismatch'})
        write(args.out, out); return

    la, pga, pma = parse(ba.decode())
    lb, pgb, pmb = parse(bb.decode())
    consensus = consensus_h66(la, pma, lb, pmb)
    type_map = {}
    for r in consensus:
        key = (r['token'], r['currier'], r['hand'])
        type_map[key] = {'token': r['token'], 'currier': r['currier'], 'hand': r['hand']}
    all_type_keys = set(type_map)
    eligible = [r for r in type_map.values() if r['token'].startswith('o') and not r['token'].startswith('q')]

    pa, ua = build_pairs('A', eligible, all_type_keys, pga)
    pb, ub = build_pairs('B', eligible, all_type_keys, pgb)
    A = test_pairs(pa, args.permutations, SEED)
    B = test_pairs(pb, args.permutations, SEED + 1)

    out.update({
        'h66_consensus_events': len(consensus),
        'consensus_unique_label_types': len(type_map),
        'eligible_o_initial_label_types': len(eligible),
        'source_a_unmatched_types': ua,
        'source_b_unmatched_types': ub,
        'source_a': A,
        'source_b': B,
    })
    if 'BLOCKED' in (A.get('status'), B.get('status')):
        out['status'] = 'BLOCKED'
    else:
        out['status'] = 'PASS' if A.get('status') == 'PASS' and B.get('status') == 'PASS' else 'FAIL'
    out.update({
        'language_identification': 'NOT_RUN',
        'semantic_identification': 'NOT_RUN',
        'translation': 'NOT_RUN',
        'decipherment': 'NOT_RUN',
    })
    write(args.out, out)


if __name__ == '__main__':
    main()
