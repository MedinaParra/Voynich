#!/usr/bin/env python3
import argparse, hashlib, itertools, json, math, re
from collections import Counter, defaultdict
from pathlib import Path

ZL_BLOB = '2a4533ab9bdfa85db9bad602d590978953055df1'
TAK_BLOB = '7f491b574b65e5fba6b553e57372c3fa50e10fec'

UNITS = ('75|84', '76|83', '77|82', '78|81', '79|80')
UNIT_FOLIOS = {
    '75|84': (75, 84),
    '76|83': (76, 83),
    '77|82': (77, 82),
    '78|81': (78, 81),
    '79|80': (79, 80),
}
CURRENT = ('75|84', '76|83', '77|82', '78|81', '79|80')
REPORTED = ('77|82', '78|81', '75|84', '76|83', '79|80')
MIN_TOKENS_PER_BIFOLIO = 50
MIN_VOCAB = 100
EPS = 1e-15


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def clean_tokens(text: str):
    clean = re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;', ' ', text)
    clean = clean.replace('?', ' ')
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])', clean.lower())


def locus_type(locator: str):
    loc = re.sub(r'^[@+*=]', '', locator.strip())
    m = re.match(r'([PLCR])', loc)
    return m.group(1) if m else None


def parse_q13_paragraph_tokens(raw: str):
    by_folio = defaultdict(list)
    for line in raw.splitlines():
        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m.group(1):
            continue
        locus, payload = m.groups()
        folio_id = locus.split('.')[0]
        fm = re.match(r'^f(\d+)', folio_id)
        if not fm:
            continue
        folio = int(fm.group(1))
        if folio < 75 or folio > 84:
            continue
        locator = locus.split(',', 1)[1]
        if locus_type(locator) != 'P':
            continue
        by_folio[folio].extend(clean_tokens(payload))
    return by_folio


def build_documents(by_folio):
    docs = {}
    for unit in UNITS:
        toks = []
        for folio in UNIT_FOLIOS[unit]:
            toks.extend(by_folio.get(folio, []))
        docs[unit] = Counter(toks)
    return docs


def tfidf_normalized(docs):
    n_docs = len(docs)
    vocab = sorted(set().union(*(set(c.keys()) for c in docs.values())))
    df = {t: sum(t in docs[u] for u in UNITS) for t in vocab}
    idf = {t: math.log((1 + n_docs) / (1 + df[t])) + 1.0 for t in vocab}
    vecs = {}
    for u in UNITS:
        v = {t: docs[u][t] * idf[t] for t in docs[u]}
        norm = math.sqrt(math.fsum(x * x for x in v.values()))
        vecs[u] = {t: x / norm for t, x in v.items()} if norm > 0 else {}
    return vecs, vocab


def cosine(a, b):
    if len(a) > len(b):
        a, b = b, a
    return math.fsum(v * b.get(t, 0.0) for t, v in a.items())


def similarity_matrix(vecs):
    sim = {}
    for a in UNITS:
        for b in UNITS:
            if a == b:
                sim[(a, b)] = 1.0
            elif (b, a) in sim:
                sim[(a, b)] = sim[(b, a)]
            else:
                sim[(a, b)] = cosine(vecs[a], vecs[b])
    return sim


def sequence_score(seq, sim):
    vals = [sim[(seq[i], seq[i + 1])] for i in range(len(seq) - 1)]
    # Sorting before fsum makes reversal symmetry exact for the same edge multiset.
    return math.fsum(sorted(vals)) / len(vals)


def run_source(name, data, expected_blob):
    blob = git_blob_sha1(data)
    out = {
        'source': name,
        'git_blob_sha1': blob,
        'expected_git_blob_sha1': expected_blob,
        'reported_sequence': list(REPORTED),
        'current_nested_sequence': list(CURRENT),
        'physical_units': list(UNITS),
    }
    if blob != expected_blob:
        out.update({'status': 'BLOCKED', 'reason': 'frozen corpus blob mismatch'})
        return out

    by_folio = parse_q13_paragraph_tokens(data.decode('utf-8', errors='strict'))
    folio_counts = {str(f): len(by_folio.get(f, [])) for f in range(75, 85)}
    docs = build_documents(by_folio)
    bifolio_counts = {u: sum(docs[u].values()) for u in UNITS}
    vecs, vocab = tfidf_normalized(docs)

    out.update({
        'folio_p_token_counts': folio_counts,
        'bifolio_p_token_counts': bifolio_counts,
        'vocabulary_types': len(vocab),
    })

    valid = (
        all(folio_counts[str(f)] > 0 for f in range(75, 85)) and
        all(bifolio_counts[u] >= MIN_TOKENS_PER_BIFOLIO for u in UNITS) and
        len(vocab) >= MIN_VOCAB
    )
    if not valid:
        out.update({
            'status': 'BLOCKED',
            'reason': 'preregistered Q13 text/sample validity gate not met',
            'permutations_scored': 0,
        })
        return out

    sim = similarity_matrix(vecs)
    perms = list(itertools.permutations(UNITS))
    scored = [(p, sequence_score(p, sim)) for p in perms]
    if len(scored) != 120:
        out.update({'status': 'BLOCKED', 'reason': 'did not score exactly 120 permutations', 'permutations_scored': len(scored)})
        return out

    reported_score = sequence_score(REPORTED, sim)
    current_score = sequence_score(CURRENT, sim)
    scores = [s for _, s in scored]
    ge = sum(s >= reported_score - EPS for s in scores)
    gt = sum(s > reported_score + EPS for s in scores)
    p_exact = ge / len(scores)
    rank = 1 + gt
    max_score = max(scores)
    maximizers = [list(p) for p, s in scored if abs(s - max_score) <= EPS]
    percentile = sum(s <= reported_score + EPS for s in scores) / len(scores)

    status = 'PASS' if reported_score > current_score and p_exact <= 0.05 else 'FAIL'
    out.update({
        'reported_score': reported_score,
        'current_nested_score': current_score,
        'reported_minus_current': reported_score - current_score,
        'null_mean_score': math.fsum(scores) / len(scores),
        'exact_permutation_p': p_exact,
        'exact_rank': rank,
        'percentile_at_or_below_reported': percentile,
        'maximum_score': max_score,
        'maximizing_sequences': maximizers,
        'permutations_scored': len(scored),
        'pairwise_cosine': {
            a: {b: sim[(a, b)] for b in UNITS if b != a}
            for a in UNITS
        },
        'status': status,
    })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--zl', type=Path, required=True)
    ap.add_argument('--takahashi', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()

    zl = run_source('ZL', args.zl.read_bytes(), ZL_BLOB)
    tak = run_source('Takahashi_IT2a', args.takahashi.read_bytes(), TAK_BLOB)
    if 'BLOCKED' in (zl['status'], tak['status']):
        overall = 'BLOCKED'
    elif zl['status'] == 'PASS' and tak['status'] == 'PASS':
        overall = 'PASS'
    else:
        overall = 'FAIL'

    result = {
        'classification': 'Q13_REPORTED_SINGULION_EXACT_PERMUTATION_P_TEXT_CONTINUITY_NOT_PRIMARY_REPLICATION',
        'sources': {'ZL': zl, 'Takahashi_IT2a': tak},
        'q20_status': 'NOT_RUN_BLOCKED_FOR_EXACT_SEQUENCE',
        'status': overall,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
