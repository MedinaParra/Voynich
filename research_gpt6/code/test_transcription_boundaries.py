import unittest
from compare_transcription_boundaries import payload,align

class ParserControls(unittest.TestCase):
    def test_drawing_boundaries(self):
        p=payload('<%>ab<->cd<~>e<$>')
        self.assertEqual(p['tokens'],['ab','cd','e'])
        self.assertEqual([b['kind'] for b in p['boundaries']],['<->','<~>'])
    def test_uncertainties_preserved(self):
        s='a[b:c],{sh}.@192;???';p=payload(s)
        self.assertEqual(''.join(x['raw'] for x in p['nodes']),s)
        self.assertEqual(p['flags'],['alternative','extended_or_unsupported','unreadable'])
    def test_alignment_ambiguity(self):
        self.assertEqual(align('aa','a')['vt_states'][1],[0,1])
    def test_projection(self):
        self.assertEqual(payload('cKh.{Sh}y')['tokens'],['ckh','shy'])

if __name__=='__main__':unittest.main(verbosity=2)
