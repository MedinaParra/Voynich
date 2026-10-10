#!/usr/bin/env python3
import argparse, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path

REQUIRED_HEADER = '# Extracted from LSI_ivtff_0d.txt'
OBJECT_UNITS = ['Lp','Lc','Lf','Ln','Lt','Ls','Lz','La']
MIN_KNOWN_TOKENS = 20
MIN_ELIGIBLE_CLASSES = 4


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean_known_tokens(text: str):
    # Do not join across unresolved material. Strip explicit IVTFF annotations only.
    cleaned = re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;', ' ', text)
    # Any candidate lexical span containing ? is excluded by splitting it away.
    cleaned = cleaned.replace('?', ' ')
    return re.findall(r'(?<![A-Za-z])[A-Za-z]{2,}(?![A-Za-z])', cleaned.lower())


def normalized_unit(locator: str):
    # Locator examples include @Lp, +P0, *P0, =Pt.
    loc = locator.strip()
    loc = re.sub(r'^[@+*=]', '', loc)
    m = re.match(r'(L[A-Za-z0-9]*)', loc)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()

    data = args.source.read_bytes()
    text = data.decode('utf-8', errors='strict')

    out = {
        'classification': 'RICHER_IVTFF_LABEL_SOURCE_ADMISSIBILITY_NOT_SEMANTICS',
        'source_bytes': len(data),
        'git_blob_sha1': git_blob_sha1(data),
        'sha256': sha256(data),
        'required_header_present': REQUIRED_HEADER in text,
        'ivtff_header_present': '#=IVTFF' in text,
        'object_units_frozen': OBJECT_UNITS,
        'min_known_tokens_per_class': MIN_KNOWN_TOKENS,
        'min_eligible_classes': MIN_ELIGIBLE_CLASSES,
    }

    if not out['required_header_present'] or not out['ivtff_header_present']:
        out.update({'status':'BLOCKED','reason':'required frozen provenance/IVTFF header missing'})
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(out, indent=2) + '\n')
        print(json.dumps(out, indent=2))
        return

    records = Counter()
    nonempty_records = Counter()
    known_tokens = Counter()
    known_types = defaultdict(set)
    total_l_records = 0
    total_l_nonempty = 0
    total_l_tokens = 0
    all_types = set()

    for line in text.splitlines():
        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m.group(1):
            continue
        locus, payload = m.groups()
        locator = locus.split(',', 1)[1]
        unit = normalized_unit(locator)
        if not unit:
            continue
        toks = clean_known_tokens(payload)
        records[unit] += 1
        total_l_records += 1
        if toks:
            nonempty_records[unit] += 1
            total_l_nonempty += 1
        known_tokens[unit] += len(toks)
        total_l_tokens += len(toks)
        known_types[unit].update(toks)
        all_types.update(toks)

    units = sorted(records)
    per_unit = {
        u: {
            'records': records[u],
            'nonempty_records': nonempty_records[u],
            'known_tokens': known_tokens[u],
            'known_types': len(known_types[u]),
        }
        for u in units
    }
    eligible = [u for u in OBJECT_UNITS if known_tokens[u] >= MIN_KNOWN_TOKENS]

    out.update({
        'total_lstar_records': total_l_records,
        'total_lstar_nonempty_records': total_l_nonempty,
        'total_lstar_known_tokens': total_l_tokens,
        'total_lstar_known_types': len(all_types),
        'per_unit': per_unit,
        'eligible_object_units': eligible,
        'eligible_object_unit_count': len(eligible),
        'status': 'PASS' if len(eligible) >= MIN_ELIGIBLE_CLASSES else 'FAIL',
    })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
