#!/usr/bin/env python3
"""Render frozen/unmasked/photo-context candidates without changing annotation."""
import argparse,html,json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from compare_transcription_boundaries import read
from kraken_eva_word_training import crop_word


def render(repo,bundle):
    q=read(bundle/'review_queue.json');geometry=read(bundle/'geometry_words.json');comp=read(bundle/'comparison.json');loci={r['id']:r for r in comp['loci']};pages={};cards=[]
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
    def fit(im,size):
        scale=min(size[0]/im.width,size[1]/im.height)
        return im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.NEAREST)
    for number,r in enumerate(q['records']):
        if r['folio'] not in pages:
            with Image.open(repo/r['source_image_path']) as im:pages[r['folio']]=im.convert('RGB')
        photo=pages[r['folio']];crop,mask,bounds=crop_word(photo,r['polygon'],4);x0,y0,x1,y1=bounds
        card=Image.new('RGB',(800,510),'#f7f7f7');d=ImageDraw.Draw(card)
        title=f"{number+1:02} {r['id']} | VT {r['reference']} | ZL span {r.get('zl_span_chars','AMBIGUOUS/COMPLEX')}"
        d.text((10,8),title,fill='black',font=font);d.text((10,30),'Frozen masked crop                         Original rectangle, no mask',fill='black',font=font)
        card.paste(fit(crop,(370,150)),(10,55));card.paste(fit(photo.crop(bounds),(370,150)),(410,55))
        region=[max(0,x0-80),max(0,y0-75),min(photo.width,x1+80),min(photo.height,y1+75)]
        context=photo.crop(region);cd=ImageDraw.Draw(context)
        for g in geometry:
            if g['folio']!=r['folio']:continue
            b=g['bounds']
            if b[2]<region[0] or b[0]>region[2] or b[3]<region[1] or b[1]>region[3]:continue
            points=[(x-region[0],y-region[1]) for x,y in g['polygon']];cd.line(points+[points[0]],fill='red' if g['id']==r['id'] else '#00b5cc',width=2)
        d.text((10,212),'Photo context: target red; neighboring candidate polygons cyan',fill='black',font=font)
        card.paste(fit(context,(780,215)),(10,237))
        d.text((10,459),r['selection_group']+' | shared dark '+str(round(100*r['shared_dark_fraction'],1))+'%',fill='black',font=font)
        d.text((10,482),'Provisional geometry/text; expert review pending; no repair applied',fill='black',font=font)
        target=bundle/'images'/(r['id']+'.png');target.parent.mkdir(exist_ok=True);card.save(target);cards.append(card)
    for k in range(math.ceil(len(cards)/4)):
        sheet=Image.new('RGB',(1600,1020),'white')
        for i,card in enumerate(cards[4*k:4*k+4]):sheet.paste(card,((i%2)*800,(i//2)*510))
        sheet.save(bundle/('contact_'+str(k+1)+'.jpg'),quality=88)
    parts=['<!doctype html><html lang="es"><meta charset="utf-8"><title>Voynich: revisión de candidatos</title><style>body{font:16px system-ui;margin:2em;max-width:1100px}img{max-width:100%;height:auto}pre{white-space:pre-wrap;background:#eee;padding:1em}article{border-top:1px solid #888;padding:1em 0}</style><h1>Lecturas y límites: 24 candidatos de entrenamiento</h1><p>Revisión visual del asistente y cola para revisión independiente. No se aprueban etiquetas ni límites. Rojo: objetivo; cian: polígonos vecinos. Las alternativas de texto no son probabilidades ni una traducción.</p>']
    for r in q['records']:
        link=r['source_link'];l=loci[link['locus']]
        parts+=['<article><h2>'+html.escape(r['id'])+'</h2><img src="images/'+r['id']+'.png" alt="Recorte y contexto"><pre>'+html.escape('Locus '+link['locus']+'\nVT: '+l['vt']['raw']+'\nZL: '+l['zl']['raw'])+'</pre><p>'+html.escape(', '.join(r['source_flags']) or 'No flags in literal source projection')+'</p><p>'+html.escape(r.get('assistant_observation','Visual review pending'))+'</p></article>']
    (bundle/'review.html').write_text('\n'.join(parts)+ '</html>')
    print({'rendered_candidates':len(cards),'contact_sheets':math.ceil(len(cards)/4)})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--bundle',type=Path,required=True);a=p.parse_args();render(a.repo,a.bundle)
