"""Link candidate OCR blocks to folio labels in Penn's primary TEI.

Only document identity is reconciled; no transcription is validated.
python reconcile_ljs419_folios.py audit.json OCR.txt TEI.xml --out links.json
"""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

BASE = 'https://openn.library.upenn.edu/Data/0001/ljs419/data/'

def reconcile(audit, payload, tei_payload):
    if hashlib.sha256(payload).hexdigest() != audit['source_sha256']:
        raise ValueError('OCR does not match the audited source hash')
    text = payload.decode('utf-8')
    root = ET.fromstring(tei_payload)
    ns = {'t': 'http://www.tei-c.org/ns/1.0'}
    images = {}
    for surface in root.findall('.//t:surface', ns):
        graphics = surface.findall('t:graphic', ns)
        for graphic in graphics:
            match = re.search(r'0265_(\d{4})', graphic.get('url', ''))
            if match:
                images[match.group(1)] = {'primary_label': surface.get('n'),
                    'web_url': next((BASE + g.get('url') for g in graphics
                                     if g.get('url', '').startswith('web/')), None)}
    refs = list(re.finditer(r'0265_(\d{4})\.tif', text))
    output = []
    for block in audit['blocks']:
        body = text[block['start']:block['end']]
        if hashlib.sha256(body.encode()).hexdigest() != block['block_sha256']:
            raise ValueError('Block hash mismatch')
        preceding = [ref for ref in refs if ref.end() < block['start']]
        reference = preceding[-1] if preceding else None
        index = reference.group(1) if reference else None
        primary = images.get(index, {})
        label = primary.get('primary_label')
        folio = re.fullmatch(r'(?:fol\.\s*)?(\d+[rv])', label or '')
        folio = folio.group(1) if folio else None
        # A missing OCR image reference can leave a stale reference in scope.
        # Long distances are flagged, never interpreted as validation.
        distance = block['start'] - reference.end() if reference else None
        status = 'PRIMARY_IMAGE_LINK_CANDIDATE'
        if not folio or distance is None or distance > 1000:
            status = 'LINK_REQUIRES_REVIEW'
        output.append({'ocr_header_folio': block['folio_as_ocr'],
                       'primary_image_folio': folio, 'primary_surface_label': label,
                       'image_index': index, 'image_url': primary.get('web_url'),
                       'reference_distance_characters': distance,
                       'header_changed': folio is not None and folio != block['folio_as_ocr'],
                       'status': status, 'start': block['start'], 'end': block['end'],
                       'block_sha256': block['block_sha256'], 'flags': block['flags'],
                       'validated_for_training': False})
    labels = Counter(x['primary_image_folio'] for x in output if x['primary_image_folio'])
    expected = {str(i) + side for i in range(1, 100) for side in 'rv'}
    missing = sorted(expected - set(labels), key=lambda x: (int(x[:-1]), x[-1]))
    return {'source_ocr_sha256': audit['source_sha256'],
            'primary_tei_sha256': hashlib.sha256(tei_payload).hexdigest(),
            'primary_tei_url': BASE + 'ljs419_TEI.xml',
            'summary': {'blocks': len(output), 'changed_header_links': sum(x['header_changed'] for x in output),
                        'distinct_primary_folios': len(labels),
                        'duplicate_primary_folios': {k: v for k, v in labels.items() if v > 1},
                        'numbered_folios_without_candidate': missing,
                        'numbered_folios_without_candidate_count': len(missing),
                        'link_status': dict(Counter(x['status'] for x in output)),
                        'validated_transcriptions': 0},
            'warning': 'Primary metadata confirms image identity only. OCR text remains unvalidated.',
            'links': output}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('audit', type=Path)
    p.add_argument('ocr', type=Path)
    p.add_argument('tei', type=Path)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    result = reconcile(json.loads(args.audit.read_text()), args.ocr.read_bytes(), args.tei.read_bytes())
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['summary']))

if __name__ == '__main__':
    main()
