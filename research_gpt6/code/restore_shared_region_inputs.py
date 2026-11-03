#!/usr/bin/env python3
"""Restore original and fixed fresh PNG pairs from preserved photos/geometry."""
import argparse
import gzip
from pathlib import Path
from PIL import Image
from eva_unit_tools import read, sha
from audit_kraken_expansion import restore_inputs
from kraken_eva_word_training import crop_word


def restore(repo):
    root = repo/'results/kraken_shared_region/fresh_data'
    dataset = root/'dataset.json'
    if not dataset.exists():
        dataset.write_bytes(gzip.decompress(dataset.with_suffix('.json.gz').read_bytes()))
    restore_inputs(repo/'results/kraken_expansion/primary_geometry', repo/'results/kraken_expansion/followup_prepared', repo)
    photos = {}
    rows = read(dataset)
    for row in rows:
        folio = row['folio']
        if folio not in photos:
            source = repo/row['source_image_path']
            if sha(source) != row['source_image_sha256']:
                raise ValueError('Fresh photo hash changed')
            with Image.open(source) as im:
                photos[folio] = im.convert('RGB')
        crop, mask, bounds = crop_word(photos[folio], row['polygon'], 4)
        if bounds != row['bounds']:
            raise ValueError('Fresh crop bounds changed')
        image_path, mask_path = root/'crops'/Path(row['path']).name, root/'crops'/Path(row['mask_path']).name
        image_path.parent.mkdir(exist_ok=True)
        if not image_path.exists():
            crop.save(image_path)
        if not mask_path.exists():
            mask.save(mask_path)
        if sha(image_path) != row['image_sha256'] or sha(mask_path) != row['mask_sha256']:
            raise ValueError('Fresh PNG bytes differ: use Pillow12.3.0')
        gt = image_path.with_suffix('.gt.txt')
        if not gt.exists():
            gt.write_text(row['reference'])
        if gt.read_text() != row['reference']:
            raise ValueError('Fresh label changed')
    print({'status': 'RESTORED_ORIGINAL_PIXELS', 'old_words': 724, 'fresh_words': len(rows), 'new_inference': 'NOT_RUN'})


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    restore(p.parse_args().repo)
