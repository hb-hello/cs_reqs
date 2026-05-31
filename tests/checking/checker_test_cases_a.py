from pprint import pprint  ## for printing witness dictionary
from collections import namedtuple

## a course taken, e.g., Taken('CSE 114', 4, 'A', (2024, 2), 'SB')
Taken = namedtuple('Taken', ['id', 'credits', 'grade', 'when', 'where'])


def test_0():  ## as test() in cs_reqs_2024.da
  taken_ids = {'CSE 114', 'CSE 214', 'CSE 216', 'CSE 215', 'CSE 220', 
               'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416',
               'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310',
               # electives
               'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355',
               # science
               'PHY 131', 'PHY 133', 'AST 203',
               'CSE 300', 'CSE 312'}
  taken = {Taken(cid, 4, 'A', (2024,2), 'SB') for cid in taken_ids}

  checked = {
      'intro': (True, ['CSE 114', 'CSE 214', 'CSE 215', 'CSE 216', 'CSE 220']),
      'adv': (True,
              ['CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 
               'CSE 416']),
      'elect': (True,
                ['CSE 351', 'CSE 352', 'CSE 353', 'CSE 355', 'CSE 360', 
                 'CSE 361']),
      'calc': (True, ['MAT 131', 'MAT 132']),
      'alg': (True, ['AMS 210']),
      'sta': (True, ['AMS 301', 'AMS 310']),
      'sci': (True, ['AST 203', 'PHY 131', 'PHY 133']),
      'ethics': (True, ['CSE 312']),
      'writing': (True, ['CSE 300']),
      'credits_at_SB': (True, ['items123 = 68', 'items23 = 48']),
      'degree': (True, [])
  }

  return taken, checked


def test_01():
  taken, checked = test_0()

  taken -= {c for c in taken if c.id in {'CSE 215', 'CSE 220'}}

  checked['intro'] = (False, ['CSE 114', 'CSE 214', 'CSE 216'])
  checked['credits_at_SB'] = (True, ['items123 = 60', 'items23 = 48'])
  checked['degree'] = (False, [])

  return taken, checked
  

def test_02():
  taken, checked = test_01()

  taken |= {Taken('CSE 215', 4, 'A', (2024,2), 'SB')}

  checked['intro'] = (False, ['CSE 114', 'CSE 214', 'CSE 215', 'CSE 216'])
  checked['credits_at_SB'] = (True, ['items123 = 64', 'items23 = 48'])

  return taken, checked


def test_03():
  taken, checked = test_0()
    
  taken -= {c for c in taken if c.id in {'CSE 352', 'CSE 353', 'CSE 355'}}

  checked['elect'] = (False, ['CSE 351', 'CSE 360', 'CSE 361', 'need 4 total'])
  checked['credits_at_SB'] = (True, ['items123 = 56', 'items23 = 36'])
  checked['degree'] = (False, [])

  return taken, checked


def test_04():
  taken, checked = test_03()
    
  taken |= {Taken(cid, 4, 'A', (2024,2), 'SB')
            for cid in {'CSE 352', 'CSE 353'}}

  checked['elect'] = (True, ['CSE 351', 'CSE 352', 'CSE 353', 'CSE 360', 
                             'CSE 361'])
  checked['credits_at_SB'] = (True, ['items123 = 64', 'items23 = 44'])
  checked['degree'] = (True, [])

  return taken, checked


def test_05():
  taken, checked = test_0()
    
  taken -= {c for c in taken if c.id in {'AST 203'}}
  taken |= {Taken('BIO 201', 4, 'A', (2024,2), 'SB')}

  checked['sci'] = (True, ['BIO 201', 'PHY 131', 'PHY 133'])

  return taken, checked


# test_1 = Year 1 (Fall 2022 + Spring 2023)
# test_2 = Year 2 (+ Fall 2023 + Spring 2024) -> CSE_AMS Two
# test_3 = Year 3 (+ Fall 2024 + Spring 2025) -> corresponds to CSE_AMS Three
# test_4 = Year 4 (+ Fall 2025 in-progress) -> corresponds to CSE_AMS Four

def test_1():
  transfer = {
    Taken('CSE 114', 3, 'A', (2022, 4), 'AP'),
    Taken('AMS 161', 0, 'A', (2022, 4), 'AP'),
    Taken('CHE 131', 4, 'A', (2022, 4), 'AP'),
    Taken('CHE 133', 0, 'A', (2022, 4), 'AP'),
  }
  fall22 = {
    Taken('AMS 210', 3, 'A', (2022, 4), 'SB'),
    Taken('AMS 310', 3, 'A', (2022, 4), 'SB'),
    Taken('CSE 214', 4, 'A', (2022, 4), 'SB'),
    Taken('CSE 215', 3, 'A', (2022, 4), 'SB'),
  }
  spr23 = {
    Taken('AMS 301', 3, 'A', (2023, 2), 'SB'),
    Taken('CSE 216', 3, 'A', (2023, 2), 'SB'),
  }
  taken = transfer | fall22 | spr23

  checked = {
    'intro':   (False, ['CSE 114', 'CSE 214', 'CSE 215', 'CSE 216']),
    'adv':     (False, []),
    'elect':   (False, ['need 4 total']),
    'calc':    (False, []),
    'alg':     (True,  ['AMS 210']),
    'sta':     (True,  ['AMS 301', 'AMS 310']),
    'sci':     (False, ['need a lec/lab combo and more, with >=9 credits and >=2.0 GPA']),
    'ethics':  (False, []),
    'writing': (False, []),
    'credits_at_SB': (False, ['items123 = 10', 'items23 = 0']),
    'degree':  (False, [])
  }
  return taken, checked


def test_2():
  taken, checked = test_1()

  fall23 = {
    Taken('CSE 220', 4, 'A', (2023, 4), 'SB'),
    Taken('CSE 303', 3, 'A', (2023, 4), 'SB'),
    Taken('CSE 316', 3, 'A', (2023, 4), 'SB'),
  }
  spr24 = {
    Taken('CSE 300', 3, 'A', (2024, 2), 'SB'),
    Taken('CSE 312', 3, 'A', (2024, 2), 'SB'),
    Taken('CSE 320', 3, 'A', (2024, 2), 'SB'),
  }
  taken |= fall23 | spr24

  checked['intro']   = (True, ['CSE 114', 'CSE 214', 'CSE 215', 'CSE 216', 'CSE 220'])
  checked['adv']     = (False, ['CSE 303'])
  checked['ethics']  = (True, ['CSE 312'])
  checked['writing'] = (True, ['CSE 300'])
  checked['credits_at_SB'] = (False, ['items123 = 23', 'items23 = 9'])

  return taken, checked


def test_3():
  taken, checked = test_2()

  fall24 = {
    Taken('CSE 360', 3, 'A', (2024, 4), 'SB'),
    Taken('CSE 373', 3, 'A', (2024, 4), 'SB'),
    Taken('PHY 131', 3, 'A', (2024, 4), 'SB'),
  }
  spr25 = {
    Taken('CSE 361', 3, 'A', (2025, 2), 'SB'),
    Taken('CHE 132', 4, 'F', (2025, 2), 'SB'),
  }
  taken |= fall24 | spr25

  checked['adv']   = (False, ['CSE 303', 'CSE 373'])
  checked['elect'] = (False, ['CSE 360', 'CSE 361', 'need 4 total'])
  checked['sci']   = (True,  ['CHE 131', 'CHE 132', 'CHE 133', 'PHY 131'])
  checked['credits_at_SB'] = (True, ['items123 = 32', 'items23 = 18'])

  return taken, checked


def test_4():
  taken, checked = test_3()

  taken -= {c for c in taken if c.id == 'CHE 132' and c.when == (2025, 2)}
  taken |= {Taken('CHE 132', 4, 'D', (2025, 2), 'SB')}

  fall25 = {
    Taken('CSE 310', 3, None, (2025, 4), 'SB'),
    Taken('CSE 416', 3, None, (2025, 4), 'SB'),
    Taken('CHE 132', 4, None, (2025, 4), 'SB'),
  }
  taken |= fall25

  # courses with grade as None will be ignored in the checker - which means the credits cournt won't reflect below values
  # not including in-progress courses in checking
  checked['credits_at_SB'] = (True, ['items123 = 38', 'items23 = 24'])

  return taken, checked


if __name__ == "__main__":
  pprint(test_0())
  pprint(test_01())
  pprint(test_02())
  pprint(test_03())
  pprint(test_04())
