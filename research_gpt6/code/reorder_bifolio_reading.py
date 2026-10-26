#!/usr/bin/env python3
"""Hypothetical reading copy: fixed bifolia, line split and exact order checks.

All original image identities survive. The result never certifies an original
historical order or a translation, even when a textual diagnostic passes.
"""
import argparse,csv,hashlib,itertools,json,math,re,unittest
from collections import Counter,defaultdict
from pathlib import Path

TOL=1e-12
def sha(data):return hashlib.sha256(data).hexdigest()
def git_sha(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def expand(order):return [f'f{leaf}{side}' for pair in order for leaf in pair for side in ('r','v')]
def leaf_id(page):return int(re.match(r'^f([0-9]+)',page)[1])
def parse(raw):
    halves=[defaultdict(list),defaultdict(list)];meta={};counts=Counter();audit=Counter()
    for line in raw.splitlines():
        header=re.match(r'^<([^>.,]+)>\s*<!',line)
        if header:meta[header[1]]=dict(re.findall(r'\$([A-Z])=([^\s>]+)',line));continue
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if not m or ',' not in m[1] or not re.search(r'P[0-9a-z]',m[1].split(',',1)[1]):continue
        page=m[1].split('.',1)[0]
        if not re.match(r'^f[0-9]+[rv]',page):continue
        text=re.sub(r'<[^>]*>','|',m[2].replace('<->','|')).replace(',','.')
        tokens=[]
        for token in re.split(r'[.\s|]+',text):
            if not token:continue
            if re.fullmatch(r'[a-z]{1,64}',token):tokens.append(token)
            else:audit['discarded_uncertain_chunks']+=1
        ordinal=counts[page];counts[page]+=1;halves[ordinal%2][page].extend(tokens);audit['paragraph_loci']+=1
    return [dict(x) for x in halves],meta,dict(counts),dict(audit)
def fit_idf(halves,excluded):
    docs=defaultdict(list)
    for half in halves:
        for page,words in half.items():
            leaf=leaf_id(page)
            if leaf not in excluded:docs[leaf].extend(words)
    df=Counter()
    for words in docs.values():df.update(set(words))
    idf={word:math.log((1+len(docs))/(1+n))+1 for word,n in df.items()}
    return idf,sorted(docs)
def tfidf(tokens,idf):
    c=Counter(tokens);n=len(tokens)
    return {word:count/n*idf[word] for word,count in c.items() if word in idf} if n else {}
def trigrams(tokens):
    c=Counter()
    for word in tokens:
        text='^'+word+'$'
        for i in range(len(text)-2):c[text[i:i+3]]+=1
    return dict(c)
def cosine(a,b):
    aa=math.fsum(x*x for x in a.values());bb=math.fsum(x*x for x in b.values())
    return math.fsum(v*b.get(k,0) for k,v in a.items())/math.sqrt(aa*bb) if aa and bb else 0.
def boundary_score(order,features):
    return math.fsum(cosine(features[f'f{a[1]}v'],features[f'f{b[0]}r']) for a,b in zip(order,order[1:]))/(len(order)-1)
def sequence_score(pages,features):
    return math.fsum(cosine(features[a],features[b]) for a,b in zip(pages,pages[1:]))/(len(pages)-1)
def summary(value,values):
    return {'score':value,'rank_best_is_1':1+sum(x>value+TOL for x in values),
            'inclusive_tail_count':sum(x>=value-TOL for x in values),'n':len(values),
            'exact_inclusive_tail':sum(x>=value-TOL for x in values)/len(values),
            'null_min':min(values),'null_mean':math.fsum(values)/len(values),'null_max':max(values)}
def choose(perms,values):
    best=max(values)
    return next(i for i,v in enumerate(values) if v>=best-TOL)
def replace_positions(rows,proposals):
    out=[dict(row) for row in rows];changed_groups={}
    for group,pages in proposals.items():
        desired=[p.removeprefix('f') for p in pages];ids=set(desired)
        if len(ids)!=len(desired):raise ValueError('Repeated target folio')
        locations=[i for i,r in enumerate(rows) if r['folio'] in ids]
        if len(locations)!=len(desired):raise ValueError('Source mapping missing a target page')
        if locations!=list(range(min(locations),max(locations)+1)):raise ValueError('Target scope is not a contiguous source interval')
        by={r['folio']:r for r in rows if r['folio'] in ids}
        for pos,name in zip(locations,desired):out[pos]={**by[name],'hypothesis_group':group}
        changed_groups[group]=locations
    old_ids=[r['canvas_id'] for r in rows];new_ids=[r['canvas_id'] for r in out]
    if len(set(old_ids))!=len(old_ids) or Counter(old_ids)!=Counter(new_ids):raise ValueError('Image identity/coverage failure')
    targets={i for indices in changed_groups.values() for i in indices}
    if any(rows[i]['canvas_id']!=out[i]['canvas_id'] for i in range(len(rows)) if i not in targets):raise ValueError('Changed non-target source position')
    originals={r['canvas_id']:i+1 for i,r in enumerate(rows)}
    return [{'proposed_position':i+1,'source_position':originals[r['canvas_id']],'folio':r['folio'],
             'canvas_id':r['canvas_id'],'image_service_url':r['image_service_url'],
             'hypothesis_group':r.get('hypothesis_group','UNCHANGED'),'changed_position':i+1!=originals[r['canvas_id']]} for i,r in enumerate(out)]

class Controls(unittest.TestCase):
    def test_known_chain(self):
        pairs=tuple((i,i+10) for i in range(5));features={}
        for i,pair in enumerate(pairs):
            features[f'f{pair[0]}r']={f'edge{i-1}':1};features[f'f{pair[1]}v']={f'edge{i}':1}
        perms=list(itertools.permutations(pairs));scores=[boundary_score(p,features) for p in perms]
        self.assertEqual(perms[choose(perms,scores)],pairs);self.assertAlmostEqual(max(scores),1)
    def test_identical_is_no_evidence(self):
        values=[1.]*120;self.assertEqual(summary(1.,values)['exact_inclusive_tail'],1.)
    def test_exact_spaces(self):
        self.assertEqual(len(list(itertools.permutations(range(5)))),120);self.assertEqual(len(list(itertools.permutations(range(4)))),24)
    def test_orientation(self):self.assertEqual(expand([(75,84)]),['f75r','f75v','f84r','f84v'])
    def test_split_preserves_literals_without_uncertain_guesses(self):
        halves,_,_,_=parse('<f1r.1,@P0> <%>daiin<->ol,chedy\n<f1r.2,+P0> qok[ai:ee]n.shey\n')
        self.assertEqual(halves[0]['f1r'],['daiin','ol','chedy']);self.assertEqual(halves[1]['f1r'],['shey'])
    def test_excluded_leaf_never_enters_idf(self):
        _,leaves=fit_idf([{'f1r':['a'],'f75r':['b']},{'f1v':['a'],'f75v':['c']}],{75})
        self.assertEqual(leaves,[1])
    def test_source_identity_and_non_targets(self):
        rows=[{'folio':str(i)+'r','canvas_id':str(i),'image_service_url':str(i)} for i in range(5)]
        m=replace_positions(rows,{'X':['f2r','f1r']})
        self.assertEqual([r['canvas_id'] for r in m],['0','2','1','3','4'])
        self.assertEqual([r['source_position'] for r in m],[1,3,2,4,5])
    def test_missing_or_duplicate_target_blocks(self):
        with self.assertRaises(ValueError):replace_positions([],{'X':['f1r']})
        with self.assertRaises(ValueError):replace_positions([],{'X':['f1r','f1r']})

def run(plan_path,corpus_path,mapping_path,out,prereg):
    tests=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
    if not tests.wasSuccessful():raise RuntimeError('Controls failed')
    plan=json.loads(plan_path.read_text());raw=corpus_path.read_bytes();mapping_raw=mapping_path.read_bytes()
    if sha(raw)!=plan['corpus']['sha256'] or git_sha(raw)!=plan['corpus']['git_blob']:raise ValueError('Corpus provenance mismatch')
    if git_sha(mapping_raw)!=plan['image_mapping']['git_blob']:raise ValueError('Image inventory provenance mismatch')
    rows=list(csv.DictReader(mapping_raw.decode().splitlines()));halves,meta,counts,audit=parse(raw.decode())
    excluded=set(range(75,85))|set(range(103,117));idf,training_leaves=fit_idf(halves,excluded)
    if excluded&set(training_leaves):raise ValueError('Target leakage in IDF')
    groups=[];proposals={}
    for group in plan['groups']:
        pairs=tuple(tuple(x) for x in group['pairs']);page_ids=expand(pairs)
        for a,b in pairs:
            ms=[meta[f'f{leaf}{side}'] for leaf in (a,b) for side in ('r','v')]
            if len({m['B'] for m in ms})!=1 or any(m.get('Q')!=group['quire'] or m.get('H')!=group['hand'] or m.get('L')!=group['currier'] for m in ms):raise ValueError('Physical/hand/Currier metadata check failed')
        if any(not halves[h].get(page) for h in (0,1) for page in page_ids):raise ValueError('Empty line-split side')
        features=[{page:tfidf(half[page],idf) for page in page_ids} for half in halves]
        if any(not d for half in features for d in half.values()):raise ValueError('No external-vocabulary coverage')
        check_chars={page:trigrams(halves[1][page]) for page in page_ids}
        perms=list(itertools.permutations(pairs))
        if len(perms)!=group['exact_permutations']:raise ValueError('Permutation count mismatch')
        selection=[boundary_score(p,features[0]) for p in perms];checking=[boundary_score(p,features[1]) for p in perms]
        char_scores=[boundary_score(p,check_chars) for p in perms];i=choose(perms,selection);chosen=perms[i];ordered=expand(chosen)
        current=[r['folio'] if r['folio'].startswith('f') else 'f'+r['folio'] for r in rows if 'f'+r['folio'] in set(page_ids)]
        if set(current)!=set(page_ids) or len(current)!=len(page_ids):raise ValueError('Current source page coverage mismatch')
        check=summary(checking[i],checking);full=sequence_score(ordered,features[1]);baseline=sequence_score(current,features[1])
        support=check['exact_inclusive_tail']<=.05 and full>baseline+TOL
        g={'id':group['id'],'role':group['role'],'pairs':pairs,'selected_order':chosen,'proposed_pages':ordered,'current_pages':current,
           'selection':summary(selection[i],selection),'checking':check,'checking_char_trigrams':summary(char_scores[i],char_scores),
           'current_full_sequence_check_score':baseline,'proposed_full_sequence_check_score':full,
           'diagnostic':'SUPPORTED_IN_CHECK_LINE_SUBSET_ONLY' if support and group['id']=='Q13' else ('NOT_SUPPORTED_IN_LINE_SPLIT' if group['id']=='Q13' else 'DESCRIPTIVE_ONLY'),
           'historical_validation':'NOT_ESTABLISHED','permutations':[{'order':p,'selection':s,'checking':v,'checking_char_trigrams':c} for p,s,v,c in zip(perms,selection,checking,char_scores)],
           'split_counts':{page:{'selection_tokens':len(halves[0][page]),'check_tokens':len(halves[1][page]),'loci':counts[page]} for page in page_ids}}
        if group.get('reference_order'):
            reference=tuple(tuple(x) for x in group['reference_order']);j=perms.index(reference);g['preexisting_reference_order']={'order':reference,'checking':summary(checking[j],checking)}
        groups.append(g);proposals[group['id']]=ordered
    manifest=replace_positions(rows,proposals)
    if len(manifest)!=plan['image_mapping']['expected_canvases']:raise ValueError('Unexpected source image count')
    out.mkdir(parents=True,exist_ok=True)
    result={'date':'2026-10-26','preregistration_commit':prereg,'plan_sha256':sha(plan_path.read_bytes()),'code_sha256':sha(Path(__file__).read_bytes()),'corpus_sha256':sha(raw),'image_mapping_sha256':sha(mapping_raw),'controls_passed':tests.testsRun,'parser_audit':audit,'idf_training_leaves':training_leaves,'excluded_target_leaves':sorted(excluded),'vocabulary_size':len(idf),'groups':groups,'images':len(manifest),'changed_image_positions':sum(r['changed_position'] for r in manifest),'historical_order':'UNRESOLVED','copy_label':'ORDEN EXPERIMENTAL - NO VALIDADO HISTORICAMENTE','translation':'NOT_RUN','limitations':['The corpus and target pages were previously explored.','Alternating lines within the same page are dependent, not independent historical evidence.','Textual similarity cannot certify a sequence of meanings.','Q20 outer bifolia and every other source position are unchanged.','No image registration, stain analysis or independent physical reconstruction was performed.']}
    (out/'reordering_result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    (out/'reading_manifest.json').write_text(json.dumps({'status':result['copy_label'],'source_order':'Frozen published 213-canvas inventory, not a newly retrieved Yale manifest','images':manifest},sort_keys=True,indent=2)+'\n')
    with (out/'reading_order.csv').open('w',newline='') as fp:
        writer=csv.DictWriter(fp,fieldnames=list(manifest[0]));writer.writeheader();writer.writerows(manifest)
    print(json.dumps({'images':len(manifest),'changed_positions':result['changed_image_positions'],'controls_passed':tests.testsRun,'groups':[{k:g[k] for k in ('id','selected_order','checking','checking_char_trigrams','diagnostic')} for g in groups]}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path);p.add_argument('--corpus',type=Path);p.add_argument('--mapping',type=Path);p.add_argument('--out',type=Path);p.add_argument('--prereg-commit');p.add_argument('--controls-only',action='store_true');a=p.parse_args()
    if a.controls_only:
        tests=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls));raise SystemExit(not tests.wasSuccessful())
    if not all((a.plan,a.corpus,a.mapping,a.out,a.prereg_commit)):p.error('plan, corpus, mapping, out and prereg-commit are required')
    run(a.plan,a.corpus,a.mapping,a.out,a.prereg_commit)
