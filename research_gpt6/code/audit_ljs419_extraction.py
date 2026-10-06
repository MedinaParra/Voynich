"""Audit section boundaries in a candidate edition's OCR, without publishing text.

Usage: python audit_ljs419_extraction.py OCR.txt --out audit.json
Offsets are zero-based character offsets in decoded UTF-8, end exclusive.
No reading corrections or automatic admission as a training corpus.
"""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

START = re.compile(r'^TRANSCRIPTION \(AS WRITTEN\)\s*$', re.M)
END = re.compile(r'^(?:ENGLISH TRANSLATION|DESCRIPTION OF THE PLATE|IDENTIFICATION|MEDICINAL.*|NOTES.*)\s*$', re.M)
FOLIO = re.compile(r'^f\.\s*(\d+)([rv])\b[^\n]*', re.M)
FLAGS = {
    'editorial_evidence_grade': r'Evidence grade',
    'english_editorial_language': r'\b(?:The leaf|Line \d|under root|in English|plant.name|read here|supplied words|expanded abbrev|lost|direct|recipe)\b',
    'page_footer': r'Patreon|Common Library|free copy',
    'uncertainty_marker': r'\?|\.\.\.|…',
    'square_bracket_intervention': r'\[',
}

def audit(payload):
    text = payload.decode('utf-8')
    # Restrict to the main run beginning with 1r. Introductory examples excluded.
    first = re.search(r'^f\.\s*1r\b', text, re.M)
    last = re.search(r'^PART II\b', text, re.M | re.I)
    lo = first.start() if first else len(text)
    hi = last.start() if last and last.start() > lo else len(text)
    headers = list(FOLIO.finditer(text, lo, hi))
    blocks = []
    for start in START.finditer(text, lo, hi):
        before = [h for h in headers if h.start() < start.start()]
        if not before:
            continue
        header = before[-1]
        n, side = header.group(1), header.group(2)
        next_header = next((h.start() for h in headers if h.start() > start.start()), hi)
        stop = END.search(text, start.end(), next_header)
        end = stop.start() if stop else next_header
        body = text[start.end():end]
        flags = [name for name, pattern in FLAGS.items() if re.search(pattern, body, re.I)]
        masters = list(re.finditer(r'0265_(\d{4})\.(?:tif|jpg)', text[:start.start()]))
        image_folio = None
        if masters:
            index = int(masters[-1].group(1))
            if 4 <= index <= 201:
                image_folio = str((index - 2) // 2) + ('r' if index % 2 == 0 else 'v')
                if image_folio != n + side:
                    flags.append('header_image_folio_mismatch')
        else:
            flags.append('missing_image_reference')
        if not 1 <= int(n) <= 99:
            flags.append('invalid_folio_number')
        if not stop:
            flags.append('missing_end_marker')
        blocks.append({'folio_as_ocr': n + side, 'image_implied_folio': image_folio,
                       'start': start.end(), 'end': end,
                       'line_start_1based': text.count('\n', 0, start.end()) + 1,
                       'line_end_1based': text.count('\n', 0, end) + 1,
                       'characters': len(body), 'wordlike_tokens': len(re.findall(r'\b\w+\b', body)),
                       'block_sha256': hashlib.sha256(body.encode()).hexdigest(),
                       'flags': flags, 'validated_for_training': False})
    eligible_headers = {h.group(1) + h.group(2) for h in headers if 1 <= int(h.group(1)) <= 99}
    found = {b['folio_as_ocr'] for b in blocks}
    counts = Counter(b['folio_as_ocr'] for b in blocks)
    return {'source_sha256': hashlib.sha256(payload).hexdigest(),
            'source_bytes': len(payload), 'status': 'BOUNDARY_AUDIT_ONLY_NOT_VALIDATED_CORPUS',
            'offset_unit': 'decoded UTF-8 character; zero based; end exclusive',
            'summary': {'blocks': len(blocks), 'unique_folio_labels': len(found),
                        'wordlike_tokens_in_candidates': sum(b['wordlike_tokens'] for b in blocks),
                        'flag_counts': dict(Counter(f for b in blocks for f in b['flags'])),
                        'valid_header_labels_without_marker_block': sorted(eligible_headers - found),
                        'duplicate_block_folios': {k: v for k, v in counts.items() if v > 1},
                        'validated_blocks': 0},
            'limitations': ['Flags are heuristic, absence of flags is not validation.',
                            'No OCR folio typo silently repaired.',
                            'Missing transcription marker yields no extracted block.',
                            'Counts include contaminated text and are not historical corpus size.'],
            'blocks': blocks}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ocr', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.ocr.read_bytes())
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['summary'], ensure_ascii=False))

if __name__ == '__main__':
    main()
