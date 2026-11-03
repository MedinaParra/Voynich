#!/usr/bin/env python3
import pickle
from pathlib import Path
import tempfile
import unittest
import zipfile
from audit_shared_region import checkpoint_counters, edit


class AuditControls(unittest.TestCase):
    def test_checkpoint_literal_prefix_multiple_protocols(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'checkpoint.ckpt'
            for protocol in [2, 4, 5]:
                with zipfile.ZipFile(p, 'w') as z:
                    z.writestr('checkpoint/data.pkl', pickle.dumps({'epoch': 99, 'global_step': 5600, 'state_dict': 'not loaded'}, protocol=protocol))
                self.assertEqual(checkpoint_counters(p), {'epoch': 99, 'global_step': 5600})

    def test_checkpoint_nonliteral_or_wrong_keys_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'checkpoint.ckpt'
            for value in [{'epoch': '99', 'global_step': 5600}, {'epoch': 99, 'unexpected': 5600}]:
                with zipfile.ZipFile(p, 'w') as z:
                    z.writestr('checkpoint/data.pkl', pickle.dumps(value, protocol=2))
                with self.assertRaises(ValueError):
                    checkpoint_counters(p)

    def test_known_edit_distances(self):
        for a, b, n in [('', '', 0), ('', 'abc', 3), ('kitten', 'sitting', 3), ('cty', 'cty', 0), ('chary', 'char', 1), ('aa', 'a', 1)]:
            self.assertEqual(edit(a, b), n)


if __name__ == '__main__':
    unittest.main(verbosity=2)
