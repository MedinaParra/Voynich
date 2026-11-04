#!/usr/bin/env python3
"""Render context-preserving visual-comparison sheets from pinned native tiles.

No cleanup, letter reconstruction, language inference or image-based decoding.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont


def pixel_sha(image):
    return hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2)+'\n')


def prepare(repo, bundle, out):
    data = json.loads((bundle/'regions.json').read_text())
    samples = {s['id']: s for s in data['samples']}
    out.mkdir(parents=True, exist_ok=True)
    (out/'glyphs').mkdir(exist_ok=True); (out/'blind').mkdir(exist_ok=True)
    font_path = repo/'results/assisted_paleography/sources/DejaVuSans.ttf'
    font = ImageFont.truetype(str(font_path), 24)
    small = ImageFont.truetype(str(font_path), 20)
    glyphs, tiles = {}, {}
    for name, s in samples.items():
        tile = Image.open(bundle/s['tile_path']).convert('RGB')
        assert list(tile.size) == s['tile_pixels'] and pixel_sha(tile) == s['tile_rgb_sha256']
        glyph = tile.crop(s['glyph_in_tile'])
        glyph.save(out/'glyphs'/(name+'.png'), compress_level=9)
        glyphs[name], tiles[name] = glyph, tile
    rng = random.Random(20261104)
    mapping, rendered = [], []
    for q in data['queries']:
        roles = [('same_source',q['same_source']),('H',q['H']),('F',q['F']),('distractor',q['distractor'])]
        rng.shuffle(roles)
        slots = [('A','query',q['query'])]+[(chr(66+i),role,name) for i,(role,name) in enumerate(roles)]
        panel = Image.new('RGB',(1440,760),'white');draw = ImageDraw.Draw(panel)
        draw.text((24,14),'Case '+q['id']+' | Compare A with B, C, D, E',font=font,fill='black')
        draw.text((24,47),'Visible strokes only. No letter values, sounds or readings.',font=small,fill='black')
        placements = []
        for index,(label,role,name) in enumerate(slots):
            x,y = (540,85) if index == 0 else ((index-1)*360,410)
            draw.text((x+150,y),label,font=font,fill='black')
            glyph = glyphs[name];new_h=120;new_w=round(glyph.width*new_h/glyph.height)
            assert new_w <= 320
            disp = glyph.resize((new_w,new_h),Image.Resampling.NEAREST)
            gx,gy=x+(340-new_w)//2,y+34;panel.paste(disp,(gx,gy))
            tile = tiles[name];scale=min(320/tile.width,110/tile.height)
            cw,ch=max(1,round(tile.width*scale)),max(1,round(tile.height*scale))
            context=tile.resize((cw,ch),Image.Resampling.NEAREST)
            cx,cy=x+(340-cw)//2,y+180;panel.paste(context,(cx,cy))
            draw.text((x+20,y+302),'Context',font=small,fill='black')
            placements.append({'label':label,'role':role,'sample_id':name,
                'glyph_destination':[gx,gy,gx+new_w,gy+new_h],
                'context_destination':[cx,cy,cx+cw,cy+ch],
                'native_glyph_pixels':list(glyph.size),'native_context_pixels':list(tile.size)})
        path=out/'blind'/(q['id']+'.png');panel.save(path,compress_level=9)
        rendered.append({'case_id':q['id'],'path':'blind/'+q['id']+'.png',
                         'pixels':list(panel.size),'rgb_sha256':pixel_sha(panel),'placements':placements})
        mapping.append({'case_id':q['id'],'family':q['family'],
                        'query_sample':q['query'],'candidates':{a:{'role':b,'sample_id':c} for a,b,c in slots[1:]}})
    write_json(out/'presentation_mapping.json',{'schema':'script-comparanda-mapping-v1','seed':20261104,'cases':mapping})
    write_json(out/'render_manifest.json',{'schema':'script-comparanda-render-v1',
        'font_sha256':hashlib.sha256(font_path.read_bytes()).hexdigest(),
        'resampling':'NEAREST, unchanged RGB samples, aspect ratio preserved up to integer rounding',
        'cases':rendered})
    print(json.dumps({'sheets':len(rendered),'native_samples':len(samples),'comparisons_per_reader':16}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--bundle',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();prepare(a.repo,a.bundle,a.out)
