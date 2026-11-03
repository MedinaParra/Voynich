#!/usr/bin/env python3
"""Assemble reported AI observations and explicitly unapproved editorial proposals."""
import argparse,json
from collections import Counter
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont


def run(repo,out):
    mapping=json.loads((out/'presentation_mapping.json').read_text());queue=json.loads((repo/'results/transcription_boundaries/review_queue.json').read_text())['records'];q={r['id']:r for r in queue}
    ar=json.loads((out/'reviews/review_a.json').read_text());br=json.loads((out/'reviews/review_b.json').read_text());a={r['alias']:r for r in ar['records']};b={r['alias']:r for r in br['records']}
    assert set(a)==set(b)=={r['alias'] for r in mapping['mapping']} and len(a)==24
    preferences={'f3r_w0004':('daimg','La última forma presenta una panza izquierda aparentemente cerrada, distinta de la entrada abierta de la forma alta anterior del mismo grupo.'),'f3r_w0018':('chag','La forma final muestra dos espacios claros separados, con panza lateral que parece cerrada y cola descendente.'),'f3r_w0040':('dago','La forma de cola anterior al óvalo final presenta un cuerpo lateral cerrado; la cola por sí sola no decide el código.')}
    rows=[]
    for m in mapping['mapping']:
        old=q[m['id']];x,y=a[m['alias']],b[m['alias']]
        row={'alias':m['alias'],'id':m['id'],'folio':m['folio'],'source_locus':old['source_link']['locus'],'current_candidate_EVA':old['reference'],'ZL_unique_span':old.get('zl_span_chars'),'AI_A':x,'AI_B':y,'body_observation_agreement':x['body_isolation']==y['body_isolation'],'geometry_action_agreement':x['geometry_action']==y['geometry_action'],'geometry_triage':'both_request_review' if x['geometry_action']==y['geometry_action']=='review_crop' else 'both_retain_candidate' if x['geometry_action']==y['geometry_action']=='retain_candidate' else 'reviewer_disagreement','label_approval':'NOT_APPROVED','geometry_approval':'NOT_APPROVED','expert_review':'NOT_REVIEWED','training_use':'NOT_AUTHORIZED_BY_THIS_REVIEW'}
        if m['id'] in preferences:
            text,reason=preferences[m['id']];row.update(reading_assessment='UNBLINDED_ASSISTANT_PROVISIONAL_PREFERENCE',proposed_EVA=text,reason=reason,alternatives_retained=[old['reference'],text])
        elif m['id'] in ['f3r_w0029','f3r_w0030']:
            row.update(reading_assessment='BOUNDARY_UNRESOLVED',alternatives_retained=['otal.dam','otaldam'],reason='Hay separación gráfica visible entre grupos en el contexto, pero una imagen estática no establece el límite léxico ni el grado de certeza editorial.')
        elif m['id']=='f3r_w0046':
            row.update(reading_assessment='ENDING_UNRESOLVED',alternatives_retained=['ydas','ydar'],reason='La curva terminal es visible; la distinción convencional r/s requiere más comparandos y no se decide por semejanza con letras latinas.')
        elif m['id'] in ['f3r_w0041','f3r_w0042']:
            row.update(reading_assessment='ALIGNMENT_AND_PREFIX_UNRESOLVED',alternatives_retained=['sho.or','sho.vor'],reason='El cuerpo principal se ve, pero la pequeña marca próxima al límite y los extremos textuales ambiguos no justifican asignar un prefijo a una caja.')
        elif m['id']=='f6v_w0096':
            row.update(reading_assessment='GLYPH_AND_BOUNDARY_UNRESOLVED',alternatives_retained=['y.chaiir','y,chaies'],reason='El contexto incluye otras alturas de escritura; se conservan tanto la lectura de los remates como la incertidumbre de separación.')
        else:row.update(reading_assessment='NO_NEW_LETTER_PROPOSAL',reason='Se registra morfología/contexto sin convertir acuerdo de fuente o de IA en una lectura certificada.')
        rows.append(row)
    summary={'status':'ASSISTED_PALEOGRAPHIC_REVIEW_COMPLETE_PROPOSALS_UNAPPROVED','reviewed_cases':len(rows),'native_photographs':4,'blinded_AI_reviewers':2,'root_source_labels_known':True,'human_expert_review':'NOT_REVIEWED','body_observation_agreements':sum(r['body_observation_agreement'] for r in rows),'geometry_action_agreements':sum(r['geometry_action_agreement'] for r in rows),'geometry_triage':dict(Counter(r['geometry_triage'] for r in rows)),'provisional_EVA_preferences':sum('proposed_EVA' in r for r in rows),'labels_changed':0,'geometry_changed':0,'training':'NOT_RUN','new_OCR':'NOT_RUN','translation':'NOT_RUN','agreement_is_not_accuracy':True}
    (out/'assessment.json').write_text(json.dumps({'summary':summary,'records':rows},ensure_ascii=False,indent=2)+'\n');(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    proposals=[{k:r[k] for k in ['id','alias','source_locus','current_candidate_EVA','proposed_EVA','reason','alternatives_retained','label_approval','expert_review','training_use']} for r in rows if 'proposed_EVA' in r]
    (out/'proposals.json').write_text(json.dumps({'status':'PROPOSED_NOT_APPLIED','proposals':proposals},ensure_ascii=False,indent=2)+'\n')
    # Exact original-photo excerpts for the three preferences and within-group/control comparison.
    font=ImageFont.truetype(str(out/'sources/DejaVuSans.ttf'),16);plate=Image.new('RGB',(1200,720),'#fafafa');draw=ImageDraw.Draw(plate)
    aliases=['B01','B03','B18','B23','B24','B08'];by_alias={r['alias']:r for r in mapping['mapping']}
    for i,alias in enumerate(aliases):
        m=by_alias[alias];old=q[m['id']];x=(i%2)*600;y=(i//2)*240
        with Image.open(out/'sources'/(m['folio']+'_native.jpg')) as im:crop=im.convert('RGB').crop(m['native_bounds'])
        factor=min(570/crop.width,170/crop.height);crop=crop.resize((round(crop.width*factor),round(crop.height*factor)),Image.Resampling.NEAREST)
        draw.text((x+10,y+6),alias+' '+m['id'],font=font,fill='black');plate.paste(crop,(x+10,y+31))
        draw.text((x+10,y+209),'VT '+old['reference']+' | ZL span '+old.get('zl_span_chars','ambiguous'),font=font,fill='black')
    plate.save(out/'form_comparison.jpg',quality=92)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.repo,a.out)
