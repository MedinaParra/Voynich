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
MIN_EVENTS_LENGTH = 15
MIN_FOLIOS_LENGTH = 8
MIN_LENGTH_STRATA = 2
MIN_EVAL_FOLIOS = 12
POSITIONS = (2, 3, 4)


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
                if len(t) >= 6:
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
        if len(t) < 6:
            continue
        key = (a['folio'], a['currier'], a['hand'], len(t), t[:2])
        pa, pb = run_a.get(key, []), run_b.get(key, [])
        if not pa or not pb:
            continue
        events.append({
            'locus': locus,
            'folio': a['folio'],
            'length': len(t),
            'label': t,
            'pool_a': pa,
            'pool_b': pb,
        })
    return events


def eligible_lengths(events):
    audit, eligible = {}, []
    lengths = sorted(set(e['length'] for e in events))
    for L in lengths:
        rows = [e for e in events if e['length'] == L]
        n = len(rows)
        f = len(set(e['folio'] for e in rows))
        audit[str(L)] = {'events': n, 'folios': f}
        if n >= MIN_EVENTS_LENGTH and f >= MIN_FOLIOS_LENGTH:
            eligible.append(L)
    return eligible, audit


def residual_vector(event, pool_key):
    label = event['label']
    pool = event[pool_key]
    out = []
    for idx in POSITIONS:
        lab = 1.0 if label[idx] == 'a' else 0.0
        base = sum(1.0 if t[idx] == 'a' else 0.0 for t in pool) / len(pool)
        out.append(lab - base)
    return tuple(out)


def mean_vec(vectors):
    return tuple(sum(v[i] for v in vectors) / len(vectors) for i in range(len(POSITIONS)))


def equal_folio_template(rows):
    by_folio = defaultdict(list)
    for r in rows:
        by_folio[r['folio']].append(r['vec'])
    folio_vecs = [mean_vec(vs) for vs in by_folio.values()]
    return mean_vec(folio_vecs) if folio_vecs else None


def mse(vec, template):
    return sum((a - b) ** 2 for a, b in zip(vec, template)) / len(vec)


def lofo(events, pool_key, eligible):
    rows = []
    for e in events:
        if e['length'] in eligible:
            rows.append({'folio': e['folio'], 'length': e['length'], 'vec': residual_vector(e, pool_key)})
    folios = sorted(set(r['folio'] for r in rows))
    fold_rows = []
    for hold in folios:
        train = [r for r in rows if r['folio'] != hold]
        test = [r for r in rows if r['folio'] == hold]
        if not test:
            continue
        rigid = equal_folio_template(train)
        cond = {}
        ok = rigid is not None
        for L in eligible:
            tpl = equal_folio_template([r for r in train if r['length'] == L])
            cond[L] = tpl
            if tpl is None:
                ok = False
        if not ok:
            continue
        rigid_mses = [mse(r['vec'], rigid) for r in test]
        cond_mses = [mse(r['vec'], cond[r['length']]) for r in test]
        mr = sum(rigid_mses) / len(rigid_mses)
        mc = sum(cond_mses) / len(cond_mses)
        fold_rows.append({
            'folio': hold,
            'events': len(test),
            'rigid_mse': mr,
            'length_conditioned_mse': mc,
            'delta_rigid_minus_conditioned': mr - mc,
        })
    return fold_rows


def evaluate(events, pool_key, eligible, nperm, seed):
    folds = lofo(events, pool_key, eligible)
    deltas = [f['delta_rigid_minus_conditioned'] for f in folds]
    if not deltas:
        return {'evaluable_folios': 0, 'folds': [], 'permutations_completed': 0}
    obs = sum(deltas) / len(deltas)
    rng = random.Random(seed)
    null = []
    for _ in range(nperm):
        stat = sum(d * (1 if rng.randrange(2) else -1) for d in deltas) / len(deltas)
        null.append(stat)
    p = (1 + sum(x >= obs for x in null)) / (1 + len(null))
    return {
        'evaluable_folios': len(folds),
        'events': sum(f['events'] for f in folds),
        'mean_delta_rigid_minus_conditioned': obs,
        'mean_rigid_mse': sum(f['rigid_mse'] for f in folds) / len(folds),
        'mean_length_conditioned_mse': sum(f['length_conditioned_mse'] for f in folds) / len(folds),
        'p_one_sided': p,
        'null_mean': sum(null) / len(null),
        'permutations_completed': len(null),
        'folds': folds,
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
        'classification': 'H77_LENGTH_CONDITIONED_MORPHOLOGY_NOT_TRANSLATION',
        'source_a_blob': blob_sha(ba),
        'source_b_blob': blob_sha(bb),
        'seed_a': SEED_A,
        'seed_b': SEED_B,
        'positions_full_token_indices': list(POSITIONS),
        'minimum_events_per_length': MIN_EVENTS_LENGTH,
        'minimum_folios_per_length': MIN_FOLIOS_LENGTH,
        'minimum_length_strata': MIN_LENGTH_STRATA,
        'minimum_evaluable_folios': MIN_EVAL_FOLIOS,
        'permutations_requested_each_source': args.permutations,
    }
    if out['source_a_blob'] != BLOBS['A'] or out['source_b_blob'] != BLOBS['B']:
        out.update({'status': 'BLOCKED', 'reason': 'frozen source blob mismatch'})
        write(args.out, out)
        return

    la, ra = parse(ba.decode())
    lb, rb = parse(bb.decode())
    events = build_common(la, ra, lb, rb)
    eligible, audit = eligible_lengths(events)
    out.update({
        'aligned_exact_prefix_events_len_ge_6': len(events),
        'length_audit': audit,
        'eligible_lengths': eligible,
    })
    if len(eligible) < MIN_LENGTH_STRATA:
        out.update({'status': 'BLOCKED', 'reason': 'preregistered exact-length stratum threshold not met'})
        write(args.out, out)
        return

    A = evaluate(events, 'pool_a', eligible, args.permutations, SEED_A)
    B = evaluate(events, 'pool_b', eligible, args.permutations, SEED_B)
    out['source_a'] = A
    out['source_b'] = B

    if A.get('evaluable_folios', 0) < MIN_EVAL_FOLIOS or B.get('evaluable_folios', 0) < MIN_EVAL_FOLIOS:
        out.update({'status': 'BLOCKED', 'reason': 'preregistered evaluable-folio threshold not met'})
    elif A.get('permutations_completed') != 999 or B.get('permutations_completed') != 999:
        out.update({'status': 'BLOCKED', 'reason': 'randomization count incomplete'})
    else:
        pass_a = A['mean_delta_rigid_minus_conditioned'] > 0 and A['p_one_sided'] <= 0.05
        pass_b = B['mean_delta_rigid_minus_conditioned'] > 0 and B['p_one_sided'] <= 0.05
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
