#!/usr/bin/env python3
import unittest
from eva_unit_tools import encode,expand,PRIVATE,metrics


class Controls(unittest.TestCase):
    def test_longest_connected_group_not_fragmented(self):
        self.assertEqual(encode('cthchsh','reset_groups'),PRIVATE['cth']+PRIVATE['ch']+PRIVATE['sh'])
    def test_all_named_groups_and_neighbors_roundtrip(self):
        for text in ['cfhckhcphcthchsh','chh','cthh','qokedy','daiin','chcthch','acfhaiin','']:
            self.assertEqual(expand(encode(text,'reset_groups'),'reset_groups'),text)
    def test_letter_condition_is_identity(self):
        self.assertEqual(encode('chcthsh','reset_letters'),'chcthsh')
    def test_unknown_private_output_rejected(self):
        with self.assertRaises(ValueError):expand(chr(0xE1FF),'reset_groups')
    def test_uncertainty_marker_not_silently_dropped(self):
        with self.assertRaises(ValueError):encode('ch*','reset_groups')
    def test_character_metric_keeps_eva_denominator(self):
        r=[{'reference':'cth','predictions':{'grouped':'sh'},'errors':{'grouped':2}}]
        self.assertEqual(metrics(r)['grouped']['eva_characters'],3);self.assertEqual(metrics(r)['grouped']['cer'],2/3)
    def test_private_output_forbidden_in_letter_control(self):
        with self.assertRaises(ValueError):expand(PRIVATE['ch'],'reset_letters')


if __name__=='__main__':unittest.main(verbosity=2)
