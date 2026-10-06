"""Fetch primary catalog metadata; inventory is NOT a transcription.

Usage: python acquire_historical_sources.py --out historical_sources
Standard library only. Existing cached responses are reused unless --refresh.
"""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

SOURCES = {
    'ljs419_TEI.xml': 'https://openn.library.upenn.edu/Data/0001/ljs419/data/ljs419_TEI.xml',
    'bellunensis_manifest.json': 'https://bl.digirati.io/iiif/ark:/81055/vdc_100165149757.0x000001',
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('historical_sources'))
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    records = []
    for name, url in SOURCES.items():
        path = args.out / name
        mode = 'cache'
        if args.refresh or not path.exists():
            request = urllib.request.Request(url, headers={'User-Agent': 'VoynichResearch/1.0'})
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read()
            path.write_bytes(payload)
            mode = 'download'
        payload = path.read_bytes()
        records.append({'file': name, 'url': url, 'bytes': len(payload),
                        'sha256': hashlib.sha256(payload).hexdigest(), 'mode': mode})
    root = ET.parse(args.out / 'ljs419_TEI.xml').getroot()
    ns = {'t': 'http://www.tei-c.org/ns/1.0'}
    graphics = [e.attrib for e in root.findall('.//t:graphic', ns)]
    licences = [{'url': e.get('target'), 'statement': ''.join(e.itertext()).strip()}
                for e in root.findall('.//t:licence', ns)]
    manifest = json.loads((args.out / 'bellunensis_manifest.json').read_text())
    canvases = []
    for canvas in manifest['items']:
        annotations = [a for page in canvas.get('items', []) for a in page.get('items', [])]
        images = [a['body']['id'] for a in annotations
                  if isinstance(a.get('body'), dict) and a['body'].get('type') == 'Image']
        canvases.append({'label': canvas.get('label'), 'canvas': canvas['id'], 'images': images})
    result = {'sources': records, 'ljs419': {'text_elements': len(root.findall('.//t:text', ns)),
              'graphic_elements': len(graphics), 'licences': licences, 'graphics': graphics},
              'bellunensis': {'canvas_count': len(canvases), 'rights': manifest.get('rights'),
              'canvases': canvases}, 'warning': 'Metadata and image inventory; not a text corpus.'}
    (args.out / 'historical_sources_manifest.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'sources': records, 'tei_text_elements': result['ljs419']['text_elements'],
                      'tei_graphic_elements': len(graphics), 'bellunensis_canvases': len(canvases)}))

if __name__ == '__main__':
    main()
