#!/usr/bin/env python3
import argparse, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED_BLOB = '4201d762a4bd6e9014e0e796d72dd5c3efb597da'
EXPECTED_SHA256 = 'db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee'
CLASSES = ['Lc','Lf','Ln','Lt','Ls','Lz']
MIN_STRATUM_CLASS_TOKENS = 5
MIN_CLASS_TOTAL = 20
MIN_CLASS_EXCHANGEABLE = 15
MIN_CLASS_EXCHANGEABLE_FOLIOS = 3
MIN_ELIGIBLE_CLASSES = 3
MIN_EXCHANGEABLE_TOKENS = 60
MIN_EXCHANGEABLE_FOLIOS = 8
MIN_EXCHANGEABLE_STRATA = 2


def git_blob_sha1(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def clean_known_tokens(text):
    cleaned = re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;', ' ', text).replace('?', ' ')
    return re.findall(r'(?<![A-Za-z])[A-Za-z]{2,}(?![A-Za-z])', cleaned.lower())


def unit_from_locator(locator):
    loc = re.sub(r'^[@+*=]', '', locator.strip())
    m = re.match(r'(L[A-Za-z0-9]*)', loc)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()

    data = args.source.read_bytes()
    blob = git_blob_sha1(data)
    sha = hashlib.sha256(data).hexdigest()
    base = {
        'classification': 'VISUAL_SUBTYPE_DOCUMENTARY_CONFOUND_IDENTIFIABILITY_NOT_SEMANTICS',
        'git_blob_sha1': blob,
        'sha256': sha,
        'frozen_classes': CLASSES,
    }
    if blob != EXPECTED_BLOB or sha != EXPECTED_SHA256:
        base.update({'status':'BLOCKED','reason':'frozen source hash mismatch'})
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(base, indent=2, sort_keys=True) + '\n')
        print(json.dumps(base, indent=2, sort_keys=True))
        return

    text = data.decode('utf-8', errors='strict')
    page_meta = {}
    tokens = []
    for line in text.splitlines():
        ph = re.match(r'^<([^>.,]+)>\s*<!([^>]*)>', line)
        if ph:
            meta = dict(re.findall(r'\$([A-Z])=([^\s>]+)', ph.group(2)))
            page_meta[ph.group(1)] = {
                'Q': meta.get('Q','?'),
                'L': meta.get('L','?'),
                'H': meta.get('H','?'),
            }
            continue
        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m.group(1):
            continue
        locus, payload = m.groups()
        folio = locus.split('.')[0]
        locator = locus.split(',',1)[1]
        unit = unit_from_locator(locator)
        if unit not in CLASSES:
            continue
        meta = page_meta.get(folio, {'Q':'?','L':'?','H':'?'})
        for tok in clean_known_tokens(payload):
            tokens.append({
                'class': unit,
                'folio': folio,
                'Q': meta['Q'],
                'L': meta['L'],
                'H': meta['H'],
                'token': tok,
            })

    class_total = Counter(t['class'] for t in tokens)
    class_folios = defaultdict(set)
    by_q = defaultdict(Counter)
    by_l = defaultdict(Counter)
    by_h = defaultdict(Counter)
    strata = defaultdict(list)
    for t in tokens:
        class_folios[t['class']].add(t['folio'])
        by_q[t['Q']][t['class']] += 1
        by_l[t['L']][t['class']] += 1
        by_h[t['H']][t['class']] += 1
        strata[(t['Q'],t['L'],t['H'])].append(t)

    exchangeable = {}
    exch_tokens = []
    class_exch_count = Counter()
    class_exch_folios = defaultdict(set)
    for key, rows in sorted(strata.items()):
        counts = Counter(r['class'] for r in rows)
        participating = sorted(c for c,n in counts.items() if n >= MIN_STRATUM_CLASS_TOKENS)
        if len(participating) < 2:
            continue
        kept = [r for r in rows if r['class'] in participating]
        exchangeable['|'.join(key)] = {
            'class_counts': {c: counts[c] for c in participating},
            'kept_tokens': len(kept),
            'folios': sorted(set(r['folio'] for r in kept)),
        }
        exch_tokens.extend(kept)
        for r in kept:
            class_exch_count[r['class']] += 1
            class_exch_folios[r['class']].add(r['folio'])

    confound_eligible = []
    per_class = {}
    for c in CLASSES:
        per_class[c] = {
            'total_tokens': class_total[c],
            'total_folios': len(class_folios[c]),
            'exchangeable_tokens': class_exch_count[c],
            'exchangeable_folios': len(class_exch_folios[c]),
        }
        if (class_total[c] >= MIN_CLASS_TOTAL and
            class_exch_count[c] >= MIN_CLASS_EXCHANGEABLE and
            len(class_exch_folios[c]) >= MIN_CLASS_EXCHANGEABLE_FOLIOS):
            confound_eligible.append(c)

    exch_folios = sorted(set(t['folio'] for t in exch_tokens))
    pass_gate = (
        len(confound_eligible) >= MIN_ELIGIBLE_CLASSES and
        len(exch_tokens) >= MIN_EXCHANGEABLE_TOKENS and
        len(exch_folios) >= MIN_EXCHANGEABLE_FOLIOS and
        len(exchangeable) >= MIN_EXCHANGEABLE_STRATA
    )

    out = dict(base)
    out.update({
        'token_count': len(tokens),
        'per_class': per_class,
        'counts_by_quire': {k: dict(v) for k,v in sorted(by_q.items())},
        'counts_by_currier': {k: dict(v) for k,v in sorted(by_l.items())},
        'counts_by_hand': {k: dict(v) for k,v in sorted(by_h.items())},
        'exchangeable_strata': exchangeable,
        'exchangeable_strata_count': len(exchangeable),
        'exchangeable_token_count': len(exch_tokens),
        'exchangeable_folio_count': len(exch_folios),
        'exchangeable_folios': exch_folios,
        'confound_eligible_classes': confound_eligible,
        'confound_eligible_class_count': len(confound_eligible),
        'thresholds': {
            'min_stratum_class_tokens': MIN_STRATUM_CLASS_TOKENS,
            'min_class_total': MIN_CLASS_TOTAL,
            'min_class_exchangeable': MIN_CLASS_EXCHANGEABLE,
            'min_class_exchangeable_folios': MIN_CLASS_EXCHANGEABLE_FOLIOS,
            'min_eligible_classes': MIN_ELIGIBLE_CLASSES,
            'min_exchangeable_tokens': MIN_EXCHANGEABLE_TOKENS,
            'min_exchangeable_folios': MIN_EXCHANGEABLE_FOLIOS,
            'min_exchangeable_strata': MIN_EXCHANGEABLE_STRATA,
        },
        'status': 'PASS' if pass_gate else 'FAIL',
    })
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
