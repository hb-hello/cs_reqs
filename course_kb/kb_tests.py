import unittest

from .build_kb import get_kb_from_program
from .course_kb import Course, Major, And, Or, Passed, Permission, Standing, Taken

class TestCSE(unittest.TestCase):
  def setUp(self):
    kb_list = get_kb_from_program('cse')  ## load the kb for cse courses
    self.kb = {course.id: course for course in kb_list}   ## index by course id

  def get_course(self, cid) -> Course:    ### todo: repeated later, have a base test class
    if cid not in self.kb:
      raise ValueError(f"Course {cid} not found in KB")
    return self.kb[cid]

  def test_cse214(self):      ## simple
    course = self.get_course('CSE 214')
    self.assertEqual(course.credits, 4)   ## credits
    self.assertEqual(course.prereq, Passed("CSE 114", "C"))
  
  def test_cse230(self):      ## or of courses
    course = self.get_course('CSE 230')
    self.assertEqual(course.prereq, Or([Taken('CSE 130'), Taken('CSE 220'), Taken('ESE 124'), Taken('ESG 111'), Taken('BME 120'), Taken('MEC 102')]))
  
  def test_cse390(self):      ## nested and/or with major req
    course = self.get_course('CSE 390')
    self.assertEqual(course.prereq, And([Or([Taken('CSE 214'), Taken('CSE 260')]), Or([Major('CSE'), Major('ISE')])]))
  
  ## override cases
  def test_cse364(self):
    course = self.get_course('CSE 364')
    self.assertEqual(course.prereq, Or([Taken("CSE 334"), Taken("ISE 334")]))
  
  def test_cse488(self):
    course = self.get_course('CSE 488')
    self.assertEqual(course.prereq, And([Major("CSE"), Or([Standing("U3"), Standing("U4")]), Permission("permission of department")]))

class TestPHY(unittest.TestCase):
  def setUp(self):
    kb_list = get_kb_from_program('phy')
    self.kb = {course.id: course for course in kb_list}

  def get_course(self, cid) -> Course:
    if cid not in self.kb:
      raise ValueError(f"Course {cid} not found in KB")
    return self.kb[cid]

  def test_phy126(self): pass

if __name__ == '__main__':
  unittest.main()