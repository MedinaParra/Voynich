"""Locate missing candidate sections; no absence is classified as a blank leaf.
python audit_missing_ljs419.py links.json OCR.txt --out missing.json
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

def audit(links, payload):
    if hashlib.sha256(payload).hexdigest() != links['source_ocr_sha256']:
        raise ValueError('Source OCR hash mismatch')
    text = payload.decode('utf-8')
    rows = []
    for folio in links['summary']['numbered_folios_without_candidate']:
        index = 2 * int(folio[:-1]) + 2 + (folio[-1] == 'v')
        refs = list(re.finditer('0265_' + str(index).zfill(4) + r'\.tif', text))
        headers = list(re.finditer(r'^f\.\s*' + re.escape(folio) + r'\s*[—–]', text, re.M))
        status = 'NO_SECTION_REFERENCE_FOUND'
        if refs:
            status = 'IMAGE_REFERENCE_WITHOUT_EXTRACTED_BLOCK'
        elif headers:
            status = 'HEADER_WITHOUT_IMAGE_REFERENCE_OR_EXTRACTED_BLOCK'
        row = {'folio': folio, 'image_index': str(index).zfill(4), 'status': status,
               'image_reference_count': len(refs), 'exact_header_count': len(headers),
               'validated_for_training': False}
        if refs:
            row['image_reference_line'] = text.count('\n', 0, refs[0].start()) + 1
        if headers:
            row['header_line'] = text.count('\n', 0, headers[0].start()) + 1
        rows.append(row)
    return {'source_sha256': links['source_ocr_sha256'],
            'summary': dict(Counter(r['status'] for r in rows)),
            'warning': 'Only section-location audit. Absence does not imply blank manuscript leaf.',
            'manual_inspection': {'5r': 'Entry found, no standard transcription marker; no prose note claimed by edition.',
                                  '5v': 'Candidate medicinal note located without standard start marker.',
                                  '64r': 'Candidate multi-part note located under header, without image reference or standard start marker.'},
            'folios': rows}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('links', type=Path)
    p.add_argument('ocr', type=Path)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    result = audit(json.loads(args.links.read_text()), args.ocr.read_bytes())
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['summary']))

if __name__ == '__main__':
    main()
