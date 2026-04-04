from pprint import pprint  ## for printing witness dictionary
from collections import namedtuple

## a course taken, e.g., Taken('CSE 114', 4, 'A', (2024, 2), 'SB')
Taken = namedtuple('Taken', ['id', 'credits', 'grade', 'when', 'where'])

def gen_taken(taken_ids):
  return {Taken(cid, 4, 'A', (2024,2), 'SB') for cid in taken_ids}

def test_0():  ## as test() in cs_reqs_2024.da
  taken_ids = {'CSE 114', 'CSE 214', 'CSE 216', 'CSE 215', 'CSE 220',
               'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416',
               'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310',
               # electives
               'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355',
               # science
               'PHY 131', 'PHY 133', 'AST 203',
               'CSE 300', 'CSE 312'}
  taken = gen_taken(taken_ids)

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
      'sta': (True, ['AMS 301']),
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


def test_06():
  taken, checked = test_0()

  taken -= {c for c in taken if c.id in
            {'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416',
             'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355'}}

  checked['adv'] = (False, [])
  checked['elect'] = (False, ['need 4 total'])
  checked['credits_at_SB'] = (False, ['items123 = 20', 'items23 = 0'])
  checked['degree'] = (False, [])

  return taken, checked


if __name__ == "__main__":
  pprint(test_0())
  pprint(test_01())
  pprint(test_02())
  pprint(test_03())
  pprint(test_04())
