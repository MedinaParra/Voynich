import inspect,json,unittest
from pathlib import Path
from PIL import Image
from kraken_row_tools import (in_polygon,filter_paragraphs,assemble,matches,
                              levenshtein,pua_text,mask_image,image_features,nearest_text)

def line(i,x0,y,x1,height=10):
    return {'index':i,'bbox_pixels':[x0,y-height,x1,y+1],
            'bbox_normalized':[x0/100,(y-height)/100,x1/100,(y+1)/100],
            'baseline':[[x0,y],[x1,y]],'boundary':None}
def region(p,x0=0,x1=1):
    return {'paragraph':p,'polygons':[[[x0,0],[x1,0],[x1,1],[x0,1]]]}

class Stage2Controls(unittest.TestCase):
    def test_polygon_excludes_drawing_point(self):
        p=[[.1,.1],[.4,.1],[.4,.4],[.1,.4]]
        self.assertTrue(in_polygon((.2,.2),p));self.assertFalse(in_polygon((.8,.8),p))
    def test_filter_discards_outside_baseline(self):
        kept=filter_paragraphs([line(0,10,30,30),line(1,70,30,90)],(100,100),[region(1,0,.4)])
        self.assertEqual([x['index'] for x in kept],[0])
    def test_fragments_on_same_row_are_assembled(self):
        rows,_=assemble([line(0,10,30,35),line(1,65,31,90)],(100,100),[region(1)],.45)
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['member_indices'],[0,1])
    def test_separate_rows_not_collapsed(self):
        rows,_=assemble([line(0,10,30,90),line(1,10,55,90)],(100,100),[region(1)],.45)
        self.assertEqual(len(rows),2)
    def test_complete_link_prevents_bridge_collapse(self):
        rows,_=assemble([line(0,10,30,20),line(1,30,35,40),line(2,50,40,60)],(100,100),[region(1)],.6)
        self.assertEqual(len(rows),2)
    def test_parallel_paragraphs_never_merged(self):
        rows,_=assemble([line(0,5,30,35),line(1,65,30,95)],(100,100),[region(1,0,.4),region(2,.6,1)],.9)
        self.assertEqual(len(rows),2)
    def test_deskew_corrects_disconnected_fragments(self):
        a=line(0,5,20,35);a['baseline']=[[5,17],[35,20]]
        b=line(1,65,26,95);b['baseline']=[[65,23],[95,26]]
        rows,_=assemble([a,b],(100,100),[region(1)],.45,True)
        self.assertEqual(len(rows),1)
    def test_reference_hint_is_not_a_predictor_argument(self):
        self.assertNotIn('reference',inspect.signature(assemble).parameters)
        r=region(1);hint={**r,'reference_count':500,'text':'irrelevant'}
        x=[line(0,10,30,90)]
        self.assertEqual(assemble(x,(100,100),[r])[0],assemble(x,(100,100),[hint])[0])
    def test_empty_segments_remain_empty(self):
        self.assertEqual(assemble([],(100,100),[region(1)]),([],[]))
    def test_duplicate_cannot_double_recall(self):
        m=matches([[0,0,1,1]]*2,[[0,0,1,1]])
        self.assertEqual(m['tp'],1);self.assertEqual(m['fp'],1)
    def test_same_count_wrong_geometry_fails(self):
        self.assertEqual(matches([[0,0,.2,.2]],[[.8,.8,1,1]])['f1'],0)
    def test_pua_is_one_unit_even_outside_bmp(self):
        mapping={'a':chr(0xFF010),'cc':chr(0xFF100),'?':chr(0xFF11F)}
        s=pua_text(['a,cc','?'],mapping)
        self.assertEqual(len(s),4);self.assertEqual(levenshtein(s,s),0)
    def test_unknown_unit_does_not_disappear(self):
        self.assertEqual(pua_text(['?'],{'?':chr(0xFF11F)}),chr(0xFF11F))
    def test_missing_mapping_blocks(self):
        with self.assertRaises(ValueError):pua_text(['a,unmapped'],{'a':'A'})
    def test_edit_error_empty_and_substitution(self):
        self.assertEqual(levenshtein('ABC',''),3);self.assertEqual(levenshtein('ABC','AXC'),1)
    def test_mask_changes_only_outside_regions(self):
        im=Image.new('RGB',(100,100),(40,50,60))
        out=mask_image(im,[{'paragraph':1,'polygons':[[[.1,.1],[.4,.1],[.4,.4],[.1,.4]]]}])
        self.assertEqual(out.getpixel((20,20)),(40,50,60));self.assertEqual(out.getpixel((90,90)),(255,255,255))
    def test_nearest_uses_only_training_text(self):
        im=Image.new('L',(100,20),255)
        train=[{'id':'train','text':'ABC','features':image_features(im)}]
        self.assertEqual(nearest_text(im,train),('ABC','train'))
    def test_reserved_physical_leaves_are_disjoint(self):
        root=Path(__file__).resolve().parents[1]
        p=json.loads((root/'data/kraken_stage2_plan.json').read_text())
        a={x.rstrip('rv') for x in p['ocr']['train_folios']};b={x.rstrip('rv') for x in p['ocr']['test_folios']}
        self.assertFalse(a&b)
        self.assertEqual(p['ocr']['monitor_folios'],p['ocr']['train_folios'])
        self.assertEqual(p['ocr']['freq'],p['ocr']['epochs'])

if __name__=='__main__':unittest.main(verbosity=2)
