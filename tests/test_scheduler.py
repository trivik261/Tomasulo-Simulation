import unittest
from simulate import simulate, parse
class Scheduling(unittest.TestCase):
 def test_raw_and_out_of_order(self):
  r=simulate('MUL R1 R2 R3\nADD R4 R1 R5\nADD R9 R6 R7')
  self.assertEqual(r['registers'][4],11);self.assertEqual(r['registers'][9],13)
  self.assertLess(r['instructions'][2]['start'],r['instructions'][1]['start'])
 def test_waw_and_war(self):
  r=simulate('MUL R1 R2 R3\nADD R4 R1 R5\nADD R1 R6 R7')
  self.assertEqual(r['registers'][1],13);self.assertEqual(r['registers'][4],11)
 def test_store_before_load(self):
  r=simulate('STR R3 12+R2\nLDR R4 12+R2')
  self.assertEqual(r['memory'][14],3);self.assertEqual(r['registers'][4],3)
 def test_same_source_and_destination(self):
  self.assertEqual(simulate('ADD R2 R2 R3')['registers'][2],5)
 def test_invalid_program(self):
  with self.assertRaises(ValueError):parse('ADD R99 R1 R2')
if __name__=='__main__':unittest.main()
