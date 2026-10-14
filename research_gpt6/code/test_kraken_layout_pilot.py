#!/usr/bin/env python3
"""Scientific failure controls for frozen sources, geometry and scope."""
import unittest
from types import SimpleNamespace
import copy
from PIL import Image
from kraken_layout_pilot import (
    bbox_iou, match_boxes, git_blob_sha, boxer_rows, page_truth,
    serialize_lines, count_loss, proxy_gate,
)


class PilotControls(unittest.TestCase):
    def test_identical_box_and_disjoint_box(self):
        self.assertEqual(bbox_iou([0,0,1,1], [0,0,1,1]), 1.)
        self.assertEqual(bbox_iou([0,0,.2,.2], [.8,.8,1,1]), 0.)

    def test_equal_counts_do_not_prove_geometry(self):
        m = match_boxes([[0,0,.2,.2]], [[.8,.8,1,1]])
        self.assertEqual(m["pred_count"], m["truth_count"])
        self.assertEqual(m["f1"], 0.)

    def test_duplicate_prediction_cannot_double_recall(self):
        b=[0,0,1,1]
        m=match_boxes([b,b],[b])
        self.assertEqual((m["tp"],m["fp"],m["fn"]),(1,1,0))
        self.assertEqual(m["recall"],1.)

    def test_geometry_is_order_invariant(self):
        a=[0,0,.4,.4]; b=[.6,.6,1,1]
        self.assertEqual(match_boxes([a,b],[b,a])["f1"],1.)

    def test_empty_predictions_have_false_negatives(self):
        self.assertEqual(match_boxes([],[[0,0,1,1]])["fn"],1)
        self.assertEqual(match_boxes([[0,0,1,1]],[])["fp"],1)

    def test_invalid_threshold_rejected(self):
        with self.assertRaises(ValueError):
            match_boxes([],[],0)

    def test_csv_does_not_treat_padding_as_words(self):
        raw=b"folio,par,line,t1,t2\n1r,1,1,foo,$\n1r,1,2,$,$\n2r,1,1,bar,$\n"
        rows=boxer_rows(raw,["1r"])
        self.assertEqual(len(rows["1r"]),1)
        self.assertEqual(rows["1r"][0]["tokens"],["foo"])

    def test_missing_folio_rejected(self):
        with self.assertRaises(ValueError):
            boxer_rows(b"folio,par,line,t1\n1r,1,1,a\n",["1v"])

    def test_duplicate_physical_line_rejected(self):
        with self.assertRaises(ValueError):
            boxer_rows(b"folio,par,line,t1\n1r,1,1,a\n1r,1,1,b\n",["1r"])

    def test_page_xml_normalizes_its_own_coordinate_frame(self):
        raw=b'<PcGts><Page imageWidth="100" imageHeight="200"><TextLine><Coords points="10,20 50,20 50,40 10,40"/></TextLine></Page></PcGts>'
        boxes,size=page_truth(raw)
        self.assertEqual(size,(100,200))
        self.assertEqual(boxes,[[.1,.1,.5,.2]])

    def test_missing_page_geometry_rejected(self):
        raw=b'<PcGts><Page imageWidth="100" imageHeight="200"><TextLine/></Page></PcGts>'
        with self.assertRaises(ValueError):page_truth(raw)

    def test_segmentation_normalization_preserves_unclipped_geometry(self):
        seg=SimpleNamespace(lines=[SimpleNamespace(bbox=(10,20,50,40),boundary=None,baseline=None)])
        self.assertEqual(serialize_lines(seg,(100,200))[0]["bbox_normalized"],[.1,.1,.5,.2])

    def test_invalid_line_box_rejected(self):
        seg=SimpleNamespace(lines=[SimpleNamespace(bbox=(10,20,10,40),boundary=None,baseline=None)])
        with self.assertRaises(ValueError):serialize_lines(seg,(100,200))

    def test_missing_case_cannot_pass_count_metric(self):
        self.assertIsNone(count_loss([],{"1r":2},"neural",1800))

    def test_count_metric_penalizes_excess_and_missing(self):
        rows=[{"folio":"1r","method":"n","width":1800,"status":"EXECUTED","line_count":4},
              {"folio":"1v","method":"n","width":1800,"status":"EXECUTED","line_count":1}]
        self.assertEqual(count_loss(rows,{"1r":2,"1v":2},"n",1800)["sum_absolute_error"],3)

    def test_failure_states_are_not_promoted_to_pass(self):
        plan={"pages":[{"folio":"1r","expected_boxer_lines":2}],
              "methods":["n","l"],"widths":{"primary":1800,"robustness":1200},
              "gates":{"max_line_count_change_each_page":1,"count_proxy_max_loss":.15}}
        result={"cases":[{"folio":"1r","method":m,"width":w,"status":"EXECUTED","line_count":2}
                         for m in ["n","l"] for w in [1800,1200]],
                "blank_controls":{m:{"status":"EXECUTED","line_count":0} for m in ["n","l"]},
                "robustness":[{"method":"n","absolute_count_change":0}]}
        self.assertEqual(proxy_gate(result,plan),"PASS_COUNT_PROXY_ONLY")
        missing=copy.deepcopy(result);missing["cases"].pop()
        self.assertEqual(proxy_gate(missing,plan),"BLOCKED_DATA_OR_RUNTIME")
        blank=copy.deepcopy(result);blank["blank_controls"]["n"]["line_count"]=1
        self.assertEqual(proxy_gate(blank,plan),"FAIL_COUNT_PROXY")
        unstable=copy.deepcopy(result);unstable["robustness"][0]["absolute_count_change"]=2
        self.assertEqual(proxy_gate(unstable,plan),"FAIL_COUNT_PROXY")


if __name__ == "__main__":
    unittest.main(verbosity=2)
