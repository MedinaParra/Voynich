"""Selection regression checks; these do not load or certify TimesFM weights."""
import unittest
import numpy as np
from timesfm_voynich import select_validation, skill

class SelectionTests(unittest.TestCase):
    def test_validation_can_select_ensemble(self):
        preds = {128: np.zeros((2, 2)), 256: np.full((2, 2), 2.)}
        best, top, primary, _ = select_validation(preds, np.ones((2, 2)), np.ones(2))
        self.assertEqual(best, 128)
        self.assertEqual(top, [128, 256])
        self.assertEqual(primary, 'top2_ensemble')

    def test_validation_can_select_individual(self):
        preds = {128: np.zeros((2, 2)), 256: np.full((2, 2), 2.)}
        self.assertEqual(select_validation(preds, np.zeros((2, 2)), np.ones(2))[2], 'best_context')

    def test_variance_scaling_changes_context_choice(self):
        preds = {128: np.array([[5., 0.]]), 256: np.array([[0., 1.]])}
        self.assertEqual(select_validation(preds, np.zeros((1, 2)), np.array([100., 1.]))[0], 128)
        self.assertEqual(select_validation(preds, np.zeros((1, 2)), np.ones(2))[0], 256)

    def test_zero_baseline_is_undefined(self):
        self.assertIsNone(skill(np.zeros(2), np.zeros(2)))

if __name__ == '__main__':
    unittest.main()
