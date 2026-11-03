#!/usr/bin/env python3
"""Measurement display of actual stored selections; no generated glyphs."""
import argparse
import io
from pathlib import Path
import zipfile
import numpy as np
from PIL import Image, ImageDraw
from eva_unit_tools import read, save


def render(repo, bundle):
    records = read(bundle/'runs/shared_ink/perturbation_records.json')
    eligible = [r for r in records if len(r['reference']) >= 4 and r['shared_dark_pixels']]
    selected = sorted(eligible, key=lambda r: (-r['shared_dark_pixels']/r['dark_pixels'], r['id']))[0]
    identity = selected['id']
    path = repo/'results/kraken_expansion/followup_prepared/crops'/(identity+'.png')
    with Image.open(path) as im:
        original = im.convert('RGB')
    rgb = np.array(original)
    canvas = Image.new('RGB', (1080, 560), '#f6f6f6')
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 10), 'Candidate '+identity+' | EVA '+selected['reference']+' | geometry unchanged', fill='black')
    draw.text((12, 30), 'Top: training view. Bottom: selected pixels marked for display; no ink ownership asserted.', fill='black')
    metadata = {'id': identity, 'candidate_reference': selected['reference'],
                'selection_rule': 'Post-diagnostic illustration: largest shared/dark fraction among training references of length >=4, ties by ID; no OCR output used.',
                'panels': {}}
    for column, variant in enumerate(['repeat', 'random_ink', 'shared_ink']):
        record = next(r for r in read(bundle/'runs'/variant/'perturbation_records.json') if r['id'] == identity)
        with zipfile.ZipFile(bundle/'runs'/variant/'selection_masks.zip') as z:
            with Image.open(io.BytesIO(z.read(identity+'.png'))) as im:
                mask = np.array(im) > 0
        pixels = rgb.copy()
        pixels[mask] = ((rgb[mask].astype(np.uint16)+np.array(record['paper_rgb'], dtype=np.uint16)+1)//2).astype(np.uint8)
        overlay = rgb.copy()
        overlay[mask] = np.rint(.55*rgb[mask]+.45*np.array([255, 20, 20])).astype(np.uint8)
        x = column*360+12
        draw.text((x, 61), variant+' | selected '+str(record['selected_pixels']), fill='black')
        size_scale = min(336/original.width, 205/original.height)
        size = (max(1, round(original.width*size_scale)), max(1, round(original.height*size_scale)))
        canvas.paste(Image.fromarray(pixels).resize(size, Image.Resampling.NEAREST), (x, 90))
        canvas.paste(Image.fromarray(overlay).resize(size, Image.Resampling.NEAREST), (x, 327))
        metadata['panels'][variant] = {'selected_pixels': record['selected_pixels'], 'selection_mask_sha256': record['selection_mask_sha256'], 'changed_pixels': record['changed_pixels']}
    canvas.save(bundle/'intervention_example.png')
    save(bundle/'intervention_example.json', metadata)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    a = p.parse_args()
    render(a.repo, a.bundle)
