#!/usr/bin/env python3
"""Create a labelled experimental photographic reading copy, never a translation."""
import argparse,hashlib,json,math
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,A3,landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

NAVY=colors.HexColor('#152a3a');TEAL=colors.HexColor('#147c80');PAPER=colors.HexColor('#f4f1e9');INK=colors.HexColor('#263746');MUTED=colors.HexColor('#657681');ALERT=colors.HexColor('#8b3c28')
def font_setup():
    root=Path('/usr/share/fonts/truetype/dejavu')
    for name,file in [('Reader','DejaVuSans.ttf'),('ReaderBold','DejaVuSans-Bold.ttf'),('ReaderMono','DejaVuSansMono.ttf')]:pdfmetrics.registerFont(TTFont(name,str(root/file)))
def para(c,text,x,y,width,size=9,color=INK,font='Reader',leading=None):
    p=Paragraph(text,ParagraphStyle('p',fontName=font,fontSize=size,leading=leading or size*1.5,textColor=color,spaceAfter=0))
    _,height=p.wrap(width,2000);p.drawOn(c,x,y-height);return y-height
def footer(c,w,h,label):
    c.setStrokeColor(colors.HexColor('#d0d5d4'));c.setLineWidth(.5);c.line(38,34,w-38,34)
    c.setFillColor(MUTED);c.setFont('Reader',6.3);c.drawString(38,23,label);c.drawRightString(w-38,23,str(c.getPageNumber()))
def order_text(order):return ' / '.join(f'{a}|{b}' for a,b in order)
def build(manifest_path,result_path,receipt_path,out,allow_nontext_source_errors=False):
    # JPEGs are already compressed; direct binary streams avoid ASCII85 bloat.
    rl_config.useA85=False
    font_setup();manifest=json.loads(manifest_path.read_text());result=json.loads(result_path.read_text());receipts=json.loads(receipt_path.read_text());rows=manifest['images']
    by={r['canvas_id']:r for r in receipts['images']}
    failures={r['canvas_id']:r for r in receipts['failures']}
    missing=set(r['canvas_id'] for r in rows)-set(by)
    if missing:
        allowed={'https://collections.library.yale.edu/manifests/oid/2002046/canvas/11868207','https://collections.library.yale.edu/manifests/oid/2002046/canvas/11868208'}
        if not allow_nontext_source_errors or not missing<=allowed or missing!=set(failures):raise ValueError('Unapproved missing scan outside non-text binding photographs')
        if any(row['hypothesis_group']!='UNCHANGED' for row in rows if row['canvas_id'] in missing):raise ValueError('Missing a reordered image')
    if set(by)|missing!=set(r['canvas_id'] for r in rows):raise ValueError('Image receipt identities differ from proposed sequence')
    for image in by.values():
        p=Path(image['reader_asset'])
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=image['reader_asset_sha256']:raise ValueError('Changed reader image asset')
    out.parent.mkdir(parents=True,exist_ok=True);c=canvas.Canvas(str(out),pagesize=A4,pageCompression=1)
    c.setTitle('Voynich - Lectura experimental por bifolios - No validada');c.setAuthor('Proyecto Voynich / MedinaParra')
    c.setSubject('Experimental photographic reading order for Q13 and the Q20 core. Not a historical reconstruction or decipherment.')
    w,h=A4;c.setFillColor(PAPER);c.rect(0,0,w,h,fill=1,stroke=0);c.setFillColor(NAVY);c.rect(0,h*.48,w,h*.52,fill=1,stroke=0)
    c.bookmarkPage('cover');c.addOutlineEntry('Portada y alcance','cover',level=0)
    c.setFillColor(colors.HexColor('#9ed5cd'));c.setFont('ReaderBold',9);c.drawString(48,h-63,'PROYECTO VOYNICH  /  26 OCT 2026')
    c.setFillColor(colors.white);c.setFont('ReaderBold',35);c.drawString(48,h-143,'Voynich')
    c.setFont('Reader',23);c.drawString(48,h-185,'Lectura por bifolios')
    para(c,'Copia experimental de 213 posiciones del inventario fotográfico, con reordenación parcial de Q13 y del núcleo de Q20.',48,h-225,w-96,size=12,color=colors.white)
    c.setFillColor(TEAL);c.rect(48,h*.48-4,110,5,fill=1,stroke=0)
    y=h*.43
    y=para(c,'ORDEN EXPERIMENTAL<br/>NO VALIDADO HISTÓRICAMENTE',48,y,w-96,size=15,color=ALERT,font='ReaderBold',leading=21)-19
    y=para(c,'La comprobación textual no confirmó la secuencia elegida. Este documento permite examinar una hipótesis de lectura y regresar al orden de origen; no establece la disposición medieval del manuscrito.',48,y,w-96,size=10)-20
    y=para(c,f'{len(by)} imágenes disponibles · {len(missing)} avisos de captura no disponible<br/>213 posiciones preservadas · 32 posiciones cambiadas<br/>Identificadores originales conservados · Desplegables sin dividir<br/>No contiene una traducción.',48,y,w-96,size=9,color=MUTED)-18
    para(c,'Imágenes: Yale University, Beinecke Rare Book and Manuscript Library, MS 408. Las copias se han remuestreado y comprimido para su lectura; no se han recortado, girado ni reconstruido.',48,y,w-96,size=7.5,color=MUTED)
    footer(c,w,h,'COPIA DE INVESTIGACIÓN - HIPÓTESIS DE LECTURA');c.showPage()
    c.setPageSize(A4);c.bookmarkPage('guide');c.addOutlineEntry('Guía, secuencias y resultados','guide',level=0)
    c.setFillColor(TEAL);c.setFont('ReaderBold',9);c.drawString(44,h-45,'CÓMO LEER ESTA COPIA')
    c.setFillColor(NAVY);c.setFont('ReaderBold',22);c.drawString(44,h-79,'Qué cambia y qué se conserva')
    y=h-109
    y=para(c,'Se ensayan bloques de cuatro caras por bifolio: <b>ar, av, br, bv</b>. Los números impresos aquí identifican siempre los folios originales; no se renumeran los signos ni se inventan hojas perdidas.',44,y,w-88)-18
    for group in result['groups']:
        c.setFillColor(TEAL);c.setFont('ReaderBold',11);c.drawString(44,y,group['id'].replace('_',' '));y-=17
        y=para(c,order_text(group['selected_order']),44,y,w-88,size=10,font='ReaderMono')-8
        check=group['checking'];y=para(c,f"Comprobación TF-IDF: rango {check['rank_best_is_1']} de {check['n']}; cola exacta {check['exact_inclusive_tail']:.3f}. "+('Criterio diagnóstico no superado.' if group['id']=='Q13' else 'Resultado descriptivo, no confirmatorio.'),44,y,w-88,size=8.5,color=MUTED)-20
    y=para(c,'En Q20 se conservan en su lugar los bifolios de borde 103|116 y 104|115. En las demás secciones no cambia ninguna posición. El inventario incluye cubiertas, cantos y desplegables: 213 capturas no equivalen a 213 páginas textuales independientes.',44,y,w-88)-16
    if missing:y=para(c,'No se pudieron descargar las fotografías de los cantos superior e inferior ([Head], [Tail]): el servidor respondió HTTP 403. Sus lugares contienen avisos, no fotografías. Todas las imágenes seleccionadas para Q13/Q20 están disponibles.',44,y,w-88,size=8.2,color=ALERT)-13
    y=para(c,'La secuencia se eligió usando líneas alternas y se comprobó en las restantes. Ambas mitades proceden de las mismas páginas, ya exploradas; no constituyen evidencia histórica independiente. La semejanza de vocabulario no demuestra continuidad de significado.',44,y,w-88)-16
    y=para(c,'Los encabezados muestran el folio y la posición en la secuencia. <b>Fuente</b> es la posición en el inventario fotográfico congelado, no una foliación medieval. Las imágenes del ensayo llevan una etiqueta destacada. Los marcadores del PDF y el índice final permiten localizar cada folio y volver a su posición de origen.',44,y,w-88)-17
    y=para(c,'Fuente y trazabilidad',44,y,w-88,size=10,font='ReaderBold')-7
    y=para(c,'Yale, Beinecke MS 408: collections.library.yale.edu/catalog/2002046<br/>Protocolo y datos: github.com/MedinaParra/Voynich<br/>Rama: experiment/kraken-voynich<br/>Protocolo fijado: f35af8057b36c9ed2cedef979db1ed492b5c50bf',44,y,w-88,size=7.5,color=MUTED)
    if y<55:raise ValueError('Guide page overflow')
    footer(c,w,h,'No es una restauración del orden histórico ni un desciframiento.');c.showPage()
    page_table=[]
    for index,row in enumerate(rows):
        image=by.get(row['canvas_id']);iw,ih=image['image_size'] if image else (1,1);wide=iw/ih>1.2;page_size=landscape(A3) if wide else A4;w,h=page_size;c.setPageSize(page_size)
        key='image_'+row['canvas_id'].rsplit('/',1)[-1];c.bookmarkPage(key)
        if index==0:c.addOutlineEntry('Secuencia experimental de imágenes',key,level=0)
        c.addOutlineEntry(f"{row['folio']} - lectura {row['proposed_position']} / fuente {row['source_position']}",key,level=1)
        c.setFillColor(NAVY);c.setFont('ReaderBold',13);c.drawString(36,h-33,row['folio'])
        group=row['hypothesis_group'];label='POSICIÓN CONSERVADA' if group=='UNCHANGED' else group.replace('_',' ')+' - ENSAYO NO VALIDADO'
        c.setFillColor(MUTED if group=='UNCHANGED' else ALERT);c.setFont('ReaderBold',8);c.drawRightString(w-36,h-31,label)
        c.setFont('Reader',7.5);c.setFillColor(MUTED);c.drawString(36,h-49,f"Secuencia {row['proposed_position']:03d} / 213     Fuente {row['source_position']:03d}     Yale {row['canvas_id'].rsplit('/',1)[-1]}")
        aw=w-72;ah=h-108;scale=min(aw/iw,ah/ih);dw,dh=iw*scale,ih*scale;x=(w-dw)/2;y=45+(ah-dh)/2
        if image:c.drawImage(ImageReader(image['reader_asset']),x,y,width=dw,height=dh,preserveAspectRatio=True,mask=None)
        else:
            c.setFillColor(PAPER);c.roundRect(48,h*.28,w-96,h*.38,8,fill=1,stroke=0)
            yy=para(c,'CAPTURA NO DISPONIBLE',68,h*.59,w-136,size=17,color=ALERT,font='ReaderBold')-22
            yy=para(c,'Fotografía de una superficie no textual de la encuadernación. El servicio público de Yale respondió HTTP 403 para este identificador. Se conserva su posición en el inventario.',68,yy,w-136,size=10)-18
            para(c,row['folio']+'<br/>Yale '+row['canvas_id'].rsplit('/',1)[-1]+'<br/>No se dispone de una fotografía para esta posición.',68,yy,w-136,size=9,color=MUTED)
        footer(c,w,h,'Yale University, Beinecke Library, MS 408 | Copia experimental sin validación histórica')
        page_table.append({**row,'pdf_page':c.getPageNumber(),'image_available':bool(image),'embedded_asset_sha256':image['reader_asset_sha256'] if image else None});c.showPage()
    sorted_table=sorted(page_table,key=lambda r:r['source_position']);per_page=56
    for start in range(0,len(sorted_table),per_page):
        w,h=A4;c.setPageSize(A4)
        if start==0:c.bookmarkPage('index');c.addOutlineEntry('Índice completo por posición de origen','index',level=0)
        c.setFillColor(NAVY);c.setFont('ReaderBold',18);c.drawString(40,h-48,'Índice de correspondencias')
        c.setFont('Reader',8);c.setFillColor(MUTED);c.drawString(40,h-67,'Origen = inventario fotográfico congelado. Lectura = secuencia de esta copia.')
        xs=[40,215,282,350,418];headers=['Folio / captura','Origen','Lectura','PDF','Ensayo']
        c.setFillColor(TEAL);c.setFont('ReaderBold',8)
        for x,t in zip(xs,headers):c.drawString(x,h-91,t)
        y=h-109
        for i,row in enumerate(sorted_table[start:start+per_page]):
            if i%2==0:c.setFillColor(colors.HexColor('#f2f5f4'));c.rect(36,y-3,w-72,11,fill=1,stroke=0)
            c.setFillColor(INK);c.setFont('Reader',7.3)
            group='-' if row['hypothesis_group']=='UNCHANGED' else row['hypothesis_group'].replace('_',' ')
            vals=[row['folio'],str(row['source_position']),str(row['proposed_position']),str(row['pdf_page']),group]
            for x,t in zip(xs,vals):c.drawString(x,y,t)
            y-=11
        footer(c,w,h,'Índice completo | Los identificadores originales no se han sustituido.');c.showPage()
    c.save();pdf=PdfReader(str(out));expected=2+len(rows)+math.ceil(len(rows)/per_page)
    if len(pdf.pages)!=expected:raise ValueError('PDF page count mismatch')
    for row in page_table:
        page=pdf.pages[row['pdf_page']-1];text=page.extract_text()
        if row['folio'] not in text:raise ValueError('Wrong folio label on image page')
        if row['image_available'] and not page.images:raise ValueError('Missing available source image in PDF')
        if not row['image_available'] and 'CAPTURA NO DISPONIBLE' not in text:raise ValueError('Missing explicit unavailable-image notice')
    output={'path':str(out.resolve()),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,
            'pdf_pages':len(pdf.pages),'source_positions':len(rows),'available_source_images':len(by),'unavailable_source_images':len(missing),'changed_source_positions':sum(r['changed_position'] for r in rows),
            'historical_validation':'NOT_ESTABLISHED','translation':'NOT_RUN','image_pages':page_table}
    receipt_path=out.with_suffix('.provenance.json');receipt_path.write_text(json.dumps(output,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k!='image_pages'}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--result',type=Path,required=True);p.add_argument('--receipts',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--allow-nontext-source-errors',action='store_true');a=p.parse_args();build(a.manifest,a.result,a.receipts,a.out,a.allow_nontext_source_errors)
