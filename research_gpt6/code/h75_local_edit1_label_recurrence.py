#!/usr/bin/env python3
import argparse, hashlib, json, random, re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

ZL_BLOB = '2a4533ab9bdfa85db9bad602d590978953055df1'
TAK_BLOB = '7f491b574b65e5fba6b553e57372c3fa50e10fec'
SEED = 20261007
PERMUTATIONS = 9999
ALPHA_PER_SOURCE = 0.025
MIN_TOKEN_LENGTH = 4


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


def parse_source(raw: str):
    pages = {}
    labels = []
    paragraph_tokens = defaultdict(list)

    for line in raw.splitlines():
        ph = re.match(r'^<([^>.,]+)>\s*<!([^>]*)>', line)
        if ph:
            meta = dict(re.findall(r'\$([A-Z])=([^\s>]+)', ph.group(2)))
            pages[ph.group(1)] = {
                'Q': meta.get('Q', '?'),
                'L': meta.get('L', '?'),
                'H': meta.get('H', '?'),
            }
            continue

        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m.group(1):
            continue
        locus, text = m.groups()
        folio = locus.split('.')[0]
        locator = locus.split(',', 1)[1]
        typ = locus_type(locator)
        toks = clean_tokens(text)

        if typ == 'L':
            if '?' in text or len(toks) != 1 or len(toks[0]) < MIN_TOKEN_LENGTH:
                continue
            meta = pages.get(folio, {'Q': '?', 'L': '?', 'H': '?'})
            labels.append({
                'folio': folio,
                'token': toks[0],
                'Q': meta['Q'],
                'L': meta['L'],
                'H': meta['H'],
            })
        elif typ == 'P':
            paragraph_tokens[folio].extend(toks)

    dedup = {}
    for r in labels:
        dedup[(r['folio'], r['token'])] = r
    return list(dedup.values()), paragraph_tokens, pages


def opportunity_quartiles(folios, paragraph_tokens):
    ranked = sorted(folios, key=lambda f: (len(paragraph_tokens.get(f, [])), f))
    n = len(ranked)
    q = {}
    for i, fol in enumerate(ranked):
        q[fol] = min(4, (i * 4) // n + 1) if n else None
    return q


def prepare_rows(labels, paragraph_tokens):
    eligible = [r for r in labels if len(paragraph_tokens.get(r['folio'], [])) > 0]
    eligible_folios = sorted(set(r['folio'] for r in eligible))
    quartile = opportunity_quartiles(eligible_folios, paragraph_tokens)

    rows = []
    for r in eligible:
        rr = dict(r)
        rr['token_length'] = len(r['token'])
        rr['p_token_count'] = len(paragraph_tokens[r['folio']])
        rr['p_opportunity_quartile'] = quartile[r['folio']]
        rr['stratum'] = (
            rr['Q'], rr['L'], rr['H'], rr['token_length'], rr['p_opportunity_quartile']
        )
        rows.append(rr)

    strata = defaultdict(list)
    for i, r in enumerate(rows):
        strata[r['stratum']].append(i)

    exchangeable_strata = {}
    exchangeable_indices = []
    for key, idxs in sorted(strata.items(), key=lambda kv: str(kv[0])):
        folios = sorted(set(rows[i]['folio'] for i in idxs))
        if len(idxs) >= 4 and len(folios) >= 2:
            exchangeable_strata[key] = idxs
            exchangeable_indices.extend(idxs)

    return rows, exchangeable_strata, sorted(exchangeable_indices)


def is_edit_distance_one(a: str, b: str) -> bool:
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        mismatches = 0
        for ca, cb in zip(a, b):
            if ca != cb:
                mismatches += 1
                if mismatches > 1:
                    return False
        return mismatches == 1

    if la > lb:
        a, b = b, a
        la, lb = lb, la

    # b is exactly one character longer than a.
    i = j = 0
    skipped = False
    while i < la and j < lb:
        if a[i] == b[j]:
            i += 1
            j += 1
        elif not skipped:
            skipped = True
            j += 1
        else:
            return False
    return True


def build_paragraph_index(paragraph_tokens):
    index = {}
    for folio, toks in paragraph_tokens.items():
        by_len = defaultdict(set)
        for tok in toks:
            if len(tok) >= MIN_TOKEN_LENGTH:
                by_len[len(tok)].add(tok)
        index[folio] = dict(by_len)
    return index


def run_one(name, data, expected_blob):
    blob = git_blob_sha1(data)
    result = {
        'source': name,
        'git_blob_sha1': blob,
        'expected_git_blob_sha1': expected_blob,
        'seed': SEED,
        'permutations_requested': PERMUTATIONS,
        'alpha_bonferroni': ALPHA_PER_SOURCE,
        'minimum_token_length': MIN_TOKEN_LENGTH,
        'distance_rule': 'ordinary_levenshtein_exactly_1_exact_matches_excluded',
    }
    if blob != expected_blob:
        result.update({'status': 'BLOCKED', 'reason': 'frozen source blob mismatch'})
        return result

    labels, paragraph_tokens, _ = parse_source(data.decode('utf-8', errors='strict'))
    rows, exch_strata, exch_idx = prepare_rows(labels, paragraph_tokens)
    paragraph_index = build_paragraph_index(paragraph_tokens)

    @lru_cache(maxsize=None)
    def local_edit1_hit(token, folio):
        by_len = paragraph_index.get(folio, {})
        n = len(token)
        for ln in (n - 1, n, n + 1):
            for ptok in by_len.get(ln, ()):
                if is_edit_distance_one(token, ptok):
                    return True
        return False

    def hit_rate(assigned_tokens):
        hits = sum(1 for i in exch_idx if local_edit1_hit(assigned_tokens[i], rows[i]['folio']))
        return hits, hits / len(exch_idx) if exch_idx else None

    assigned = {i: rows[i]['token'] for i in range(len(rows))}
    observed_hits, observed_rate = hit_rate(assigned)
    represented_folios = sorted(set(rows[i]['folio'] for i in exch_idx))

    result.update({
        'certain_unique_folio_label_rows_len_ge_4': len(labels),
        'eligible_rows_with_paragraph_text': len(rows),
        'exchangeable_rows': len(exch_idx),
        'excluded_nonexchangeable_rows': len(rows) - len(exch_idx),
        'represented_folios': len(represented_folios),
        'exchangeable_strata': len(exch_strata),
        'observed_edit1_local_hits': observed_hits,
        'observed_edit1_local_hit_rate': observed_rate,
        'strata_inventory': {
            '|'.join(map(str, key)): {
                'rows': len(idxs),
                'folios': len(set(rows[i]['folio'] for i in idxs)),
            }
            for key, idxs in exch_strata.items()
        },
    })

    valid = (
        len(exch_idx) >= 60 and
        len(represented_folios) >= 8 and
        len(exch_strata) >= 5 and
        observed_hits >= 1
    )
    if not valid:
        result.update({
            'status': 'BLOCKED',
            'permutations_completed': 0,
            'reason': 'preregistered exchangeability/sample validity gate not met',
        })
        return result

    rng = random.Random(SEED)
    null_rates = []
    for _ in range(PERMUTATIONS):
        perm_assigned = dict(assigned)
        for idxs in exch_strata.values():
            toks = [rows[i]['token'] for i in idxs]
            rng.shuffle(toks)
            for i, tok in zip(idxs, toks):
                perm_assigned[i] = tok
        _, rate = hit_rate(perm_assigned)
        null_rates.append(rate)

    null_mean = sum(null_rates) / len(null_rates)
    p = (1 + sum(v >= observed_rate for v in null_rates)) / (1 + len(null_rates))
    status = 'PASS' if observed_rate > null_mean and p <= ALPHA_PER_SOURCE else 'FAIL'
    result.update({
        'null_mean_edit1_local_hit_rate': null_mean,
        'observed_minus_null_mean_lift': observed_rate - null_mean,
        'monte_carlo_p': p,
        'permutations_completed': len(null_rates),
        'cached_token_folio_comparisons': local_edit1_hit.cache_info().currsize,
        'status': status,
    })
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--zl', type=Path, required=True)
    ap.add_argument('--takahashi', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()

    zl = run_one('ZL', args.zl.read_bytes(), ZL_BLOB)
    tak = run_one('Takahashi_IT2a', args.takahashi.read_bytes(), TAK_BLOB)

    if 'BLOCKED' in (zl['status'], tak['status']):
        overall = 'BLOCKED'
    elif zl['status'] == 'PASS' and tak['status'] == 'PASS':
        overall = 'PASS'
    else:
        overall = 'FAIL'

    out = {
        'classification': 'LOCAL_EDIT_DISTANCE_ONE_LABEL_TO_PARAGRAPH_RECURRENCE_NOT_TRANSLATION',
        'sources': {'ZL': zl, 'Takahashi_IT2a': tak},
        'status': overall,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
