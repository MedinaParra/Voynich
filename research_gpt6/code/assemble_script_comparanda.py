#!/usr/bin/env python3
"""Aggregate fixed AI descriptions without adjudicating or changing labels."""
import argparse
from collections import Counter
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

LABELS = ['strong','partial','different','insufficient']


def counts(): return {k:0 for k in LABELS}


def assemble(repo, bundle):
    mapping=json.loads((bundle/'presentation_mapping.json').read_text())['cases']
    reviews={name:json.loads((bundle/'reviews'/(name.lower()+'.json')).read_text()) for name in ['A','B']}
    index={name:{c['case_id']:c['candidates'] for c in review['cases']} for name,review in reviews.items()}
    by_reader={name:counts() for name in reviews}
    by_role={role:{name:counts() for name in reviews} for role in ['same_source','H','F','distractor']}
    rows=[]
    for case in mapping:
        for candidate in ['B','C','D','E']:
            role=case['candidates'][candidate]['role']
            values={name:index[name][case['case_id']][candidate]['label'] for name in reviews}
            assert all(value in LABELS for value in values.values())
            for name,value in values.items():by_reader[name][value]+=1;by_role[role][name][value]+=1
            rows.append({'case_id':case['case_id'],'candidate':candidate,'role':role,
                         'sample_id':case['candidates'][candidate]['sample_id'],
                         'A':values['A'],'B':values['B'],'agree':values['A']==values['B']})
    agreement=sum(row['agree'] for row in rows)
    out={'schema':'script-comparanda-summary-v1','reviewers':['A','B'],'comparisons':16,'judgments':32,
         'agreement':{'exact_label_agreements':agreement,'disagreements':16-agreement},
         'distribution_by_reviewer':by_reader,'by_role':by_role,'paired_rows':rows,
         'scope':'Descriptive source-label-hidden AI judgments on manually selected examples. Agreement is not historical, expert-gold or alphabet-reading accuracy.',
         'expert_validation':False,'language_or_reading_inferred':False,'Voynich_translation':'NOT_RUN'}
    (bundle/'summary.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    regions=json.loads((bundle/'regions.json').read_text())
    font_path=repo/'results/assisted_paleography/sources/DejaVuSans.ttf'
    font=ImageFont.truetype(str(font_path),23);small=ImageFont.truetype(str(font_path),18)
    panel=Image.new('RGB',(1360,930),'white');d=ImageDraw.Draw(panel)
    d.text((24,14),'Recorded source comparison | Forms only; no reading equivalence',font=font,fill='black')
    headers=['Family','Voynich query','Voynich second','HM58316,1r','Fontana,1r row']
    for x,label in zip([20,280,540,800,1060],headers):d.text((x,72),label,font=small,fill='black')
    for row,q in enumerate(regions['queries']):
        y=135+row*180;d.text((20,y+40),q['family'],font=small,fill='black')
        for col,sample in enumerate([q['query'],q['same_source'],q['H'],q['F']]):
            image=Image.open(bundle/'glyphs'/(sample+'.png')).convert('RGB')
            h=105;w=round(image.width*h/image.height)
            image=image.resize((w,h),Image.Resampling.NEAREST)
            x=280+col*260+(220-w)//2;panel.paste(image,(x,y))
            d.text((280+col*260,y+120),sample,font=small,fill='black')
    d.text((20,882),'Native RGB excerpts, proportional display. Full context and source coordinates remain preserved.',font=small,fill='black')
    panel.save(bundle/'identified_atlas.png',compress_level=9)
    print(json.dumps({'agreement':out['agreement'],'by_role':by_role},sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--bundle',type=Path,required=True);a=p.parse_args();assemble(a.repo,a.bundle)
