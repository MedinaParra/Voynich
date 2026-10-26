#!/usr/bin/env python3
"""Audit scores, source identity, source positions and every embedded reader JPEG."""
import argparse,collections,csv,hashlib,json,math
from pathlib import Path
from pypdf import PdfReader

def sha(data):return hashlib.sha256(data).hexdigest()
def run(result_path,manifest_path,mapping_path,corpus_path,pdf_path,out):
    result=json.loads(result_path.read_text());manifest=json.loads(manifest_path.read_text())['images'];source=list(csv.DictReader(mapping_path.open(newline='')))
    provenance=json.loads(pdf_path.with_suffix('.provenance.json').read_text());reader=PdfReader(str(pdf_path));checked=0;failures=[]
    def check(name,actual,expected=True):
        nonlocal checked
        checked+=1
        ok=math.isclose(actual,expected,rel_tol=1e-10,abs_tol=1e-12) if isinstance(actual,(int,float)) and isinstance(expected,(int,float)) else actual==expected
        if not ok:failures.append({'check':name,'actual':actual,'expected':expected})
    check('source_corpus_sha256',sha(corpus_path.read_bytes()),result['corpus_sha256']);check('mapping_sha256',sha(mapping_path.read_bytes()),result['image_mapping_sha256'])
    check('inventory_count',len(source),213);check('manifest_count',len(manifest),len(source))
    check('same_canvas_multiset',collections.Counter(r['canvas_id'] for r in manifest),collections.Counter(r['canvas_id'] for r in source))
    check('unique_canvas_ids',len({r['canvas_id'] for r in manifest}),213)
    by={r['canvas_id']:(i+1,r) for i,r in enumerate(source)}
    changed=0
    for i,row in enumerate(manifest,1):
        old,original=by[row['canvas_id']];check('proposed_position',row['proposed_position'],i);check('source_position',row['source_position'],old)
        check('folio_identity',row['folio'],original['folio']);check('service_identity',row['image_service_url'],original['image_service_url'])
        check('changed_flag',row['changed_position'],old!=i);changed+=old!=i
        if row['hypothesis_group']=='UNCHANGED':check('non_target_kept',i,old)
    check('changed_count',changed,result['changed_image_positions']);check('expected_changed_count',changed,32)
    for group in result['groups']:
        candidates=group['permutations'];expected=math.factorial(len(group['pairs']));check(group['id']+':candidate_count',len(candidates),expected)
        signatures={tuple(tuple(p) for p in c['order']) for c in candidates};check(group['id']+':unique_candidates',len(signatures),expected)
        selected=tuple(tuple(p) for p in group['selected_order']);record=next(c for c in candidates if tuple(tuple(p) for p in c['order'])==selected)
        check(group['id']+':selected_on_selection_half',record['selection']>=max(c['selection'] for c in candidates)-1e-12)
        for field,label in [('checking','checking'),('checking_char_trigrams','checking_char_trigrams')]:
            values=[c[field] for c in candidates];score=record[field];summary=group[label]
            check(group['id']+':'+field+':score',score,summary['score'])
            check(group['id']+':'+field+':rank',1+sum(v>score+1e-12 for v in values),summary['rank_best_is_1'])
            check(group['id']+':'+field+':tail',sum(v>=score-1e-12 for v in values)/len(values),summary['exact_inclusive_tail'])
        expanded=[f'f{leaf}{side}' for pair in selected for leaf in pair for side in ('r','v')]
        check(group['id']+':orientation',expanded,group['proposed_pages'])
        placed=['f'+r['folio'] for r in manifest if r['hypothesis_group']==group['id']]
        check(group['id']+':manifest_matches_selection',placed,expanded)
        if group['id']=='Q13':check('Q13_diagnostic_is_fail',group['diagnostic'],'NOT_SUPPORTED_IN_LINE_SPLIT')
    check('idf_target_exclusion',not set(result['idf_training_leaves'])&set(result['excluded_target_leaves']))
    check('pdf_hash',sha(pdf_path.read_bytes()),provenance['sha256']);check('pdf_pages',len(reader.pages),219)
    check('pdf_positions',len(provenance['image_pages']),213)
    embedded=0;missing=[]
    for row in provenance['image_pages']:
        check('pdf_page_offset',row['pdf_page'],row['proposed_position']+2)
        page=reader.pages[row['pdf_page']-1];text=page.extract_text();check('pdf_folio_label:'+row['folio'],row['folio'] in text)
        resources=page['/Resources'];xobjects=resources.get('/XObject',{})
        if hasattr(xobjects,'get_object'):xobjects=xobjects.get_object()
        images=[v.get_object() for v in xobjects.values() if v.get_object().get('/Subtype')=='/Image']
        if row['image_available']:
            check('one_source_image:'+row['folio'],len(images),1)
            if len(images)==1:check('embedded_JPEG_bytes:'+row['folio'],sha(images[0].get_data()),row['embedded_asset_sha256']);embedded+=1
        else:
            missing.append(row['folio']);check('missing_notice:'+row['folio'],'CAPTURA NO DISPONIBLE' in text);check('no_invented_image:'+row['folio'],len(images),0);check('unavailable_is_non_target',row['hypothesis_group'],'UNCHANGED')
    check('available_image_count',embedded,211);check('unavailable_nontext',sorted(missing),['[Head]','[Tail]'])
    report={'date':'2026-10-26','checks':checked,'mismatches':failures,'status':'PASS' if not failures else 'FAIL','embedded_jpegs_verified':embedded,'missing_nontext_images':missing,'image_identities':213,'changed_positions':changed,'pdf_pages':len(reader.pages),'pdf_sha256':sha(pdf_path.read_bytes()),'result_sha256':sha(result_path.read_bytes()),'scope':'Numerical ranks, source identities and embedded JPEG bytes; not historical validation or semantic decipherment'}
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps(report));return not failures
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--result',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--mapping',type=Path,required=True);p.add_argument('--corpus',type=Path,required=True);p.add_argument('--pdf',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();raise SystemExit(not run(a.result,a.manifest,a.mapping,a.corpus,a.pdf,a.out))
