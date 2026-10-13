import unittest
from newdomain.layout_rows import associate,evidence
class LayoutRowsTests(unittest.TestCase):
 def obs(self,text,x,y):return {'text':text,'x':x,'y':y,'width':.03,'height':.02}
 def test_geometry_overcomes_reading_order(self):
  rows=associate([self.obs('39F',.7,.8),self.obs('38F',.7,.7),self.obs('甲区',.8,.795),self.obs('乙区',.8,.695)],'doc:2',2)
  self.assertEqual([(r['label'],r['floor'])for r in rows],[('甲区','39F'),('乙区','38F')])
  ctx,_=evidence('甲区在哪层',rows,'资料');self.assertIn('甲区：39F',next(iter(ctx.values())))
 def test_uncertain_number_and_ambiguous_pair_not_guessed(self):
  self.assertEqual(associate([self.obs('I6F',.7,.8),self.obs('甲区',.8,.8)],'x',1),[])
  self.assertEqual(associate([self.obs('39F',.7,.8),self.obs('甲区',.8,.795),self.obs('乙区',.8,.8)],'x',1),[])
 def test_unrelated_question_has_no_card(self):
  self.assertEqual(evidence('介绍研究方向',[],'资料'),({},[]))
