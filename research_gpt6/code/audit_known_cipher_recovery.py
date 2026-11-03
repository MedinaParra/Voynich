#!/usr/bin/env python3
"""Independent audit after truth reveal: plaintext, observed key and LM objective.

No solver/evaluator imports. This verifies recoveries on synthetic known ciphers,
not the historical language, cryptosystem or meaning of Voynich.
"""
import argparse
import array
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


def raw(path):
    if path.exists():
        data = path.read_bytes()
        return gzip.decompress(data) if path.suffix == '.gz' else data
    return gzip.decompress(path.with_suffix(path.suffix + '.gz').read_bytes())


def read(path):
    return json.loads(raw(path))


def sha(path):
    return hashlib.sha256(raw(path)).hexdigest()


def letters(text):
    if not isinstance(text, str) or any(c not in ALPHABET+' ' for c in text):
        raise ValueError('Expected lowercase cipher/plaintext and literal spaces only')
    return text.replace(' ', '')


def apply_key(ciphertext, key):
    if not isinstance(key, str) or len(key) != 26 or any(c not in ALPHABET for c in key):
        raise ValueError('Expected 26 lowercase cipher-to-plain assignments')
    return ''.join(' ' if c == ' ' else key[ord(c)-97] for c in ciphertext)


def quantized_score(text, model):
    values = [ord(c)-97 for c in letters(text)]
    total = 0
    for i in range(len(values)-3):
        a,b,c,d = values[i:i+4]
        total += model[((a*26+b)*26+c)*26+d]
    return total


def recovery_metrics(ciphertext, plaintext, truth_key, predicted_key):
    expected = letters(plaintext)
    candidate = letters(apply_key(ciphertext, predicted_key))
    if len(expected) != len(candidate) or not expected:
        raise ValueError('Expected equal, nonzero plaintext lengths')
    correct = sum(a == b for a,b in zip(expected, candidate))
    observed = ''.join(sorted(set(letters(ciphertext))))
    key_correct = sum(predicted_key[ord(c)-97] == truth_key[ord(c)-97] for c in observed)
    return {'character_accuracy':correct/len(expected),
            'characters_correct':correct, 'characters_total':len(expected),
            'all_exact':correct == len(expected),
            'observed_symbol_key_accuracy':key_correct/len(observed),
            'observed_symbols_correct':key_correct,
            'observed_symbols_total':len(observed),
            'unobserved_cipher_symbols':''.join(c for c in ALPHABET if c not in observed)}


def bijective_ceiling(ciphertext, plaintext):
    cipher, plain = letters(ciphertext), letters(plaintext)
    if len(cipher) != len(plain):
        raise ValueError('Unequal plaintext/ciphertext lengths')
    counter = Counter(zip(cipher, plain))
    owner = defaultdict(set)
    for c,p in counter:
        owner[c].add(p)
    if any(len(values) != 1 for values in owner.values()):
        raise ValueError('Ceiling shortcut needs disjoint fixed homophone groups')
    by_plain = defaultdict(list)
    for (c,p),n in counter.items():
        by_plain[p].append(n)
    return sum(max(values) for values in by_plain.values())


class Checks:
    def __init__(self):
        self.count = 0
        self.mismatches = []
    def check(self, name, actual, expected=True):
        self.count += 1
        equal = math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12) if isinstance(actual,float) or isinstance(expected,float) else actual == expected
        if not equal:
            self.mismatches.append({'check':name,'actual':actual,'expected':expected})


def controls(checks):
    # Known shifted key, including plaintext letters absent from this tiny case.
    decrypt = ALPHABET[7:]+ALPHABET[:7]
    plain = 'hij hij'
    metrics = recovery_metrics('abc abc', plain, decrypt, decrypt)
    checks.check('control/exact_plaintext', metrics['all_exact'])
    checks.check('control/only_observed_key_symbols', metrics['observed_symbols_total'], 3)
    checks.check('control/unobserved_not_key_errors', len(metrics['unobserved_cipher_symbols']), 23)
    wrong = list(decrypt);wrong[0],wrong[1] = wrong[1],wrong[0]
    metrics = recovery_metrics('abc abc', plain, decrypt, ''.join(wrong))
    checks.check('control/position_accuracy', metrics['characters_correct'], 2)
    checks.check('control/observed_key_accuracy', metrics['observed_symbols_correct'], 1)
    checks.check('control/disjoint_homophone_ceiling', bijective_ceiling('aabbcc','xxxxzz'), 4)
    model = array.array('i', [0])*(26**4)
    for i,v in [(731,11),(19006,23),(37181,5),(52756,-2)]:model[i] = v
    checks.check('control/int32_ngram_index_and_overlap', quantized_score('abcd abcd',model), 48)
    checks.check('control/short_text_has_no_quadgrams', quantized_score('abc',model), 0)
    return {'cases':'Known shift, wrong used assignments, disjoint homophones, manual quadgram indices',
            'scope':'Mathematical controls, not additional Latin/Voynich experiments'}


def audit(repo, bundle):
    checks = Checks()
    control_summary = controls(checks)
    public_path = bundle/'public/ciphertexts.json'
    truth_path = bundle/'reveal/truth.json'
    pred_path = bundle/'predictions.json'
    eval_path = bundle/'evaluation.json'
    model_path = bundle/'model/lm_int32.bin'
    public, truth, predictions, evaluation = map(read,[public_path,truth_path,pred_path,eval_path])
    public_rows = {r['id']:r for r in public['cases']}
    true_rows = {r['id']:r for r in truth['cases']}
    pred_rows = {r['id']:r for r in predictions['cases']}
    eval_rows = {r['id']:r for r in evaluation['cases']}
    checks.check('case_ids/all_four_files_equal', set(public_rows), set(true_rows))
    checks.check('case_ids/predictions_equal', set(pred_rows), set(true_rows))
    checks.check('case_ids/evaluation_equal', set(eval_rows), set(true_rows))
    for name,document in [('public',public),('truth',truth),('predictions',predictions),('evaluation',evaluation)]:
        checks.check('case_ids/'+name+'/no_duplicates',len(document['cases']),len({r['id'] for r in document['cases']}))
    data = raw(model_path)
    checks.check('model/exact_int32_size',len(data),4*26**4)
    model = array.array('i')
    if model.itemsize != 4:raise ValueError('Host signed int is not32bit')
    model.frombytes(data)
    if sys.byteorder != 'little':model.byteswap()
    checks.check('hash/predictions',sha(pred_path),evaluation['predictions_sha256'])
    checks.check('hash/truth_commitment',sha(truth_path),evaluation['truth_commitment_sha256'])
    checks.check('hash/freeze_receipt',sha(bundle/'freeze.json'),evaluation['freeze_receipt_sha256'])
    checks.check('solver/identity_consistent',predictions['solver_sha256'],evaluation['solver_sha256'])
    manifest_path = bundle/'public/manifest.json'
    if manifest_path.exists():checks.check('hash/public_manifest',sha(manifest_path),evaluation['manifest_sha256'])
    observations=[]
    for name in sorted(true_rows):
        t,p,e,c = true_rows[name],pred_rows[name],eval_rows[name],public_rows[name]
        label = name+'/'
        cipher=t['ciphertext'];plain=t['plaintext'];true_key=t['decryption_key_cipher_to_plain'];key=p['key']
        checks.check(label+'public_cipher_unchanged',cipher,c['ciphertext'])
        checks.check(label+'predicted_key_is_bijection', ''.join(sorted(key)), ALPHABET)
        checks.check(label+'true_key_decodes_actual_message',apply_key(cipher,true_key),plain)
        checks.check(label+'truth_letter_stream',letters(plain),t['letters_plaintext'])
        checks.check(label+'candidate_plaintext_matches_key',apply_key(cipher,key),p['plaintext'])
        checks.check(label+'candidate_letter_stream',letters(p['plaintext']),p['letters_plaintext'])
        checks.check(label+'observed_symbols_declared',''.join(sorted(set(letters(cipher)))) ,''.join(t['observed_cipher_symbols']))
        metrics = recovery_metrics(cipher,plain,true_key,key)
        for field,value in metrics.items():checks.check(label+field,value,e[field])
        for field in ['role','variant','pair_id']:checks.check(label+field,t[field],e[field])
        predicted_score=quantized_score(p['letters_plaintext'],model)
        true_score=quantized_score(t['letters_plaintext'],model)
        checks.check(label+'integer_score/prediction',predicted_score,p['score'])
        checks.check(label+'integer_score/evaluation',predicted_score,e['score'])
        if t['role']!='homophonic_wrong_model':
            checks.check(label+'true_mono_key_is_bijection',''.join(sorted(true_key)),ALPHABET)
            encryption=t['encryption_key_plain_to_cipher']
            checks.check(label+'encryption_is_bijection',''.join(sorted(encryption)),ALPHABET)
            checks.check(label+'encryption_decryption_inverse',''.join(true_key[ord(c)-97] for c in encryption),ALPHABET)
            checks.check(label+'encrypt_truth_matches_cipher',apply_key(plain,encryption),cipher)
        if t['role']=='homophonic_wrong_model':
            ceiling=bijective_ceiling(cipher,plain)
            checks.check(label+'homophonic/structural_count_ceiling',ceiling,t['best_bijective_correct_letters'])
            checks.check(label+'homophonic/evaluation_ceiling',ceiling,e['best_bijective_correct_letters'])
            checks.check(label+'homophonic/true_accuracy_ceiling',ceiling/metrics['characters_total'],t['best_bijective_character_accuracy'])
            checks.check(label+'homophonic/evaluation_accuracy_ceiling',ceiling/metrics['characters_total'],e['best_bijective_character_accuracy'])
            checks.check(label+'homophonic/recovery_cannot_exceed_ceiling',metrics['characters_correct']<=ceiling)
            checks.check(label+'homophonic/ceiling_gap',ceiling/metrics['characters_total']-metrics['character_accuracy'],e['gap_below_bijective_ceiling'])
        observations.append({'id':name,**{k:t[k] for k in ['role','variant','pair_id']},**metrics,
                             'reported_score_verified':predicted_score,'oracle_true_plaintext_score':true_score,
                             'candidate_minus_true_score':predicted_score-true_score,
                             'objective_diagnostic':'exact_plaintext_recovered' if metrics['all_exact'] else 'candidate_outranks_truth' if predicted_score>true_score else 'candidate_below_truth' if predicted_score<true_score else 'objective_tie_with_wrong_text'})
    grouped=defaultdict(list)
    for r in observations:grouped[(r['role'],r['variant'])].append(r)
    summary=[]
    for item in evaluation['summary']:
        group=grouped[(item['role'],item['variant'])]
        actual={'case_count':len(group),'all_exact_count':sum(r['all_exact'] for r in group),
                'mean_character_accuracy':statistics.mean(r['character_accuracy'] for r in group),
                'mean_observed_symbol_key_accuracy':statistics.mean(r['observed_symbol_key_accuracy'] for r in group),
                'mean_score':statistics.mean(r['reported_score_verified'] for r in group)}
        for field,value in actual.items():checks.check('summary/'+item['role']+'/'+item['variant']+'/'+field,value,item[field])
        summary.append({'role':item['role'],'variant':item['variant'],**actual})
    checks.check('summary/all_groups_present',len(evaluation['summary']),len(grouped))
    positives=[r for r in observations if r['role']=='monoalphabetic_positive']
    pair_ids=sorted({r['pair_id'] for r in positives})
    checks.check('positive_cases_correlated_not_independent',len(positives),evaluation['correlated_positive_cases'])
    checks.check('independent_positive_passages',len(pair_ids),evaluation['independent_positive_passages'])
    for record in evaluation['space_pair_key_consistency']:
        ids=record['case_ids'];checks.check('pair/'+record['pair_id']+'/two_presentations',len(ids),2)
        first,second=(true_rows[i] for i in ids);p1,p2=(pred_rows[i] for i in ids)
        observed=set(letters(first['ciphertext']))|set(letters(second['ciphertext']))
        checks.check('pair/'+record['pair_id']+'/full_predicted_keys_equal',p1['key']==p2['key'],record['full_predicted_keys_equal'])
        checks.check('pair/'+record['pair_id']+'/used_predicted_keys_equal',all(p1['key'][ord(c)-97]==p2['key'][ord(c)-97] for c in observed),record['predicted_keys_equal_on_observed_symbols'])
        checks.check('pair/'+record['pair_id']+'/true_keys_equal',first['decryption_key_cipher_to_plain']==second['decryption_key_cipher_to_plain'],record['true_keys_equal'])
        checks.check('pair/'+record['pair_id']+'/one_underlying_passage',record['independent_replicates'],1)
    checks.check('pairs/all_positive_pairs_recorded',len(evaluation['space_pair_key_consistency']),len(pair_ids))
    return {'status':'PASS' if not checks.mismatches else 'FAIL','checks':checks.count,'mismatches':checks.mismatches,
            'control_summary':control_summary,'cases':observations,'summary':summary,
            'strict_positive_recovery_gate_recomputed':bool(positives) and all(r['all_exact'] and r['observed_symbols_correct']==r['observed_symbols_total'] for r in positives),
            'unobserved_key_mapping_evaluated':False,
            'input_hashes':{str(p.relative_to(bundle)):sha(p) for p in [public_path,truth_path,pred_path,eval_path,model_path]},
            'scope':'Independent application of reported keys, exact Hamming and observed-symbol metrics, integer LM scoring including oracle truth, disjoint-homophone bijection ceiling and aggregates. Does not rerun search, certify optimality, enforce historical blinding, infer language, or decipher Voynich.',
            'voynich_translation':'NOT_RUN'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path);p.add_argument('--bundle',type=Path);p.add_argument('--out',type=Path);p.add_argument('--controls-only',action='store_true');a=p.parse_args()
    if a.controls_only:
        c=Checks();summary=controls(c);result={'status':'PASS' if not c.mismatches else 'FAIL','checks':c.count,'mismatches':c.mismatches,'control_summary':summary}
    else:
        if a.repo is None or a.bundle is None or a.out is None:p.error('--repo --bundle and --out required')
        result=audit(a.repo,a.bundle)
    if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','checks','mismatches']}))
    raise SystemExit(0 if result['status']=='PASS' else 1)

if __name__=='__main__':main()
