#!/usr/bin/env python3
import argparse, hashlib, json, re
from collections import defaultdict
from pathlib import Path

EXPECTED = {
    'IT': 'db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee',
    'CD': 'edc18e6de699c50d575925d4f469685ccbbe22c9755b9b8a3b002f83253cbde5',
    'FG': 'a1460a05ff610a406e62b4095a8f8e88c04653c1ef4aa5ad6428ddb1ac01fe06',
    'GC': 'b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f',
}
CLASSES = ['Lc','Lf','Ln','Lt']
ALLOWED_STRATA = {
    'Lc': {('O','A','1'),('S','A','1')},
    'Lf': {('O','A','1'),('S','A','1')},
    'Ln': {('M','B','2')},
    'Lt': {('M','B','2')},
}
MIN_TOKENS = 20
MIN_FOLIOS = 5


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def known_tokens(payload):
    # Preserve alphabet-specific alphanumeric symbols; discard unresolved spans.
    s = re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;', ' ', payload)
    pieces = re.split(r'[.\s]+', s)
    out = []
    for p in pieces:
        p = p.strip()
        if not p or '?' in p:
            continue
        # Keep only standalone transcription alphanumeric runs.
        runs = re.findall(r'[A-Za-z0-9]+', p)
        if len(runs) == 1 and runs[0]:
            out.append(runs[0])
    return out


def parse_records(data):
    text = data.decode('utf-8', errors='strict')
    records = {}
    page_meta = {}
    for line in text.splitlines():
        ph = re.match(r'^<(f\d+[rv]\d*)>\s*<!([^>]*)>', line)
        if ph:
            m = dict(re.findall(r'\$([A-Z])=([^\s>]+)', ph.group(2)))
            page_meta[ph.group(1)] = {'Q':m.get('Q','?'),'L':m.get('L','?'),'H':m.get('H','?')}
            continue
        lm = re.match(r'^<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)$', line)
        if not lm:
            continue
        fol, num, locator, payload = lm.groups()
        records[(fol, int(num))] = {
            'folio': fol,
            'number': int(num),
            'locator': locator,
            'payload': payload,
            'tokens': known_tokens(payload),
            'meta': page_meta.get(fol, {'Q':'?','L':'?','H':'?'}),
        }
    return records


def it_unit(locator):
    loc = re.sub(r'^[@+*=]', '', locator.strip())
    m = re.match(r'(L[A-Za-z0-9]*)', loc)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--it', type=Path, required=True)
    ap.add_argument('--cd', type=Path, required=True)
    ap.add_argument('--fg', type=Path, required=True)
    ap.add_argument('--gc', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    paths = {'IT':a.it,'CD':a.cd,'FG':a.fg,'GC':a.gc}
    hashes = {k:sha256(p.read_bytes()) for k,p in paths.items()}
    out = {
        'classification':'CROSS_ALPHABET_VISUAL_LABEL_LOCUS_COVERAGE_NOT_SEMANTICS',
        'sha256':hashes,
        'expected_sha256':EXPECTED,
        'frozen_classes':CLASSES,
        'min_tokens_per_class':MIN_TOKENS,
        'min_folios_per_class':MIN_FOLIOS,
    }
    bad = [k for k in EXPECTED if hashes[k] != EXPECTED[k]]
    if bad:
        out.update({'status':'BLOCKED','reason':'frozen source hash mismatch','mismatched_sources':bad})
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); return

    parsed = {k:parse_records(p.read_bytes()) for k,p in paths.items()}
    it = parsed['IT']
    eligible = []
    for key,r in it.items():
        unit = it_unit(r['locator'])
        if unit not in CLASSES:
            continue
        meta = r['meta']
        if (meta['Q'],meta['L'],meta['H']) not in ALLOWED_STRATA[unit]:
            continue
        eligible.append((key,unit,r))

    it_counts = defaultdict(int)
    for _,c,_ in eligible: it_counts[c] += 1
    out['it_eligible_locus_counts'] = {c:it_counts[c] for c in CLASSES}

    source_results = {}
    mappable_sets = {}
    replication_eligible = []
    for src in ['CD','FG','GC']:
        present = defaultdict(int)
        mappable = defaultdict(int)
        folios = defaultdict(set)
        ids = set()
        for key,c,r in eligible:
            rr = parsed[src].get(key)
            if rr is not None:
                present[c] += 1
            if rr is not None and len(r['tokens']) == 1 and len(rr['tokens']) == 1:
                mappable[c] += 1
                folios[c].add(key[0])
                ids.add(key)
        eligible_src = all(mappable[c] >= MIN_TOKENS and len(folios[c]) >= MIN_FOLIOS for c in CLASSES)
        if eligible_src: replication_eligible.append(src)
        source_results[src] = {
            'exact_locus_present': {c:present[c] for c in CLASSES},
            'single_token_mappable': {c:mappable[c] for c in CLASSES},
            'mapped_folios': {c:len(folios[c]) for c in CLASSES},
            'replication_eligible': eligible_src,
        }
        mappable_sets[src] = ids

    pairwise = {}
    srcs = ['CD','FG','GC']
    for i in range(len(srcs)):
        for j in range(i+1,len(srcs)):
            a1,a2=srcs[i],srcs[j]
            pairwise[f'{a1}&{a2}'] = len(mappable_sets[a1] & mappable_sets[a2])
    all_three = len(mappable_sets['CD'] & mappable_sets['FG'] & mappable_sets['GC'])
    out.update({
        'source_results':source_results,
        'replication_eligible_sources':replication_eligible,
        'replication_eligible_source_count':len(replication_eligible),
        'pairwise_single_token_locus_overlap':pairwise,
        'all_three_single_token_locus_overlap':all_three,
        'status':'PASS' if len(replication_eligible) >= 2 else 'FAIL',
    })
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
