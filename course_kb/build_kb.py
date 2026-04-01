from pprint import pprint
import requests
import re
import argparse
import json
import os
from bs4 import BeautifulSoup 
from .course_kb import *
from .parse_course import course_div_cleanup, parse_course_div, parse_req_text

## all the courses in CSE that can't be handled by the current parsing logic.
## we add them manually as overrides.
OVERRIDES = {
  # CSE 364: Advanced Multimedia Techniques
  # Prerequisites: CSE/ISE 334
  # 3 credits
  "CSE 364": Course(
    id="CSE 364", title="Advanced Multimedia Techniques",
    desc="SKIPPED",
    prereq=Or([Taken("CSE 334"), Taken("ISE 334")]),
    coreq=None, anti_req=None, pre_or_coreq=None, advisory_prereq=None, advisory_coreq=None, advisory_pre_or_coreq=None,
    credits="3",
    category=None, ### ignore for now
    grading=None
  ),
  # CSE 488: Internship in Computer Science
  # Prerequisites: CSE major, U3 or U4 standing; permission of department
  # SBC:     EXP+
  # 3 credits, S/U grading
  "CSE 488": Course(
    id="CSE 488", title="Internship in Computer Science",
    desc="SKIPPED",
    prereq=And([Major("CSE"), Or([Standing("U3"), Standing("U4")]), Permission("permission of department")]),
    coreq=None, anti_req=None, pre_or_coreq=None, advisory_prereq=None, advisory_coreq=None, advisory_pre_or_coreq=None,
    credits="3",
    category=None, ### ignore for now
    grading="S/U"
  ),
}

REQ_TYPES = {'prereq', 'coreq', 'pre_or_coreq', 'anti_req', 'advisory_prereq', 'advisory_coreq', 'advisory_pre_or_coreq'}
REQ_TYPES_IGNORE = {'advisory_prereq', 'advisory_coreq', 'advisory_pre_or_coreq'}

def create_course_namedtuple(raw_course_dict : dict) -> Course:
  ## from course dictionary (returned by parse_course_div) to course namedtuple
  ## input: dictionary with keys like 'id', 'desc', 'Prerequisite', ..

  ## helper function to check multiple possible string keys for requisites
  ## e.g., "Prerequisite" vs "Prerequisites"
  print("parsing course:", raw_course_dict.get('id'))
  def get_parsed_req(possible_keys):
    lower_dict = {k.lower(): v for k, v in raw_course_dict.items()}
    for key in possible_keys:
      if key.lower() in lower_dict:
        return parse_req_text(lower_dict[key.lower()])
    return None

  return Course(
    id=raw_course_dict.get('id'),
    title=raw_course_dict.get('title'),
    desc=raw_course_dict.get('desc'),
    prereq=get_parsed_req(['Prerequisite', 'Prerequisites']),
    coreq=get_parsed_req(['Corequisite', 'Corequisites']),
    pre_or_coreq=get_parsed_req(['Pre- or Co-requisite', 'Pre- or Co-requisites', 'Pre- or corequisite', 'Pre- or corequisites']),
    anti_req=get_parsed_req(['Anti-requisite', 'Anti-requisites']),
    advisory_prereq=get_parsed_req(['Advisory Prerequisite', 'Advisory Prerequisites']),
    advisory_coreq=get_parsed_req(['Advisory Corequisite', 'Advisory Corequisites']),
    advisory_pre_or_coreq=get_parsed_req(['Advisory pre-or corequisite', 'Advisory pre-or corequisites', 'Advisory Pre-or corequisite']),
    category=raw_course_dict.get('category'),
    credits=raw_course_dict.get('credits'),
    grading=raw_course_dict.get('grading')
  )

def build_course_kb_from_html(html_input: str) -> list[Course]:
  ## input: raw html string
  ## output: a list of course namedtuples
  soup = BeautifulSoup(html_input, "html.parser")
  course_divs = soup.find_all("div", class_="course")   ## find all course divs in html
  
  kb = []
  
  for div in course_divs:
    clean_div = course_div_cleanup(div)                 ## div clean up
    raw_dict = parse_course_div(clean_div)              ## parse the cleaned div into a dictionary of course fields
    course = create_course_namedtuple(raw_dict)     ## convert dict to namedtuple
    if course.id in OVERRIDES:                      ## apply overrides if exists
      print(f"Applying override for course {course.id}")
      course = OVERRIDES[course.id]
    kb.append(course)

  return kb

def get_kb_from_program(prog: str):
  base_url = 'https://www.stonybrook.edu/sb/bulletin/current-fall24/academicprograms/{prog}/courses.php'
  url = base_url.format(prog=prog)
  resp = requests.get(url)
  if resp.status_code == 200:
    html_input = resp.text
    kb = build_course_kb_from_html(html_input)
    return kb
  else:
    print("Failed to retrieve course data. Status code:", resp.status_code)
    return []

TYPE_KEY = "__type__"

class ASTEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, LogicalExpr):
      return {type(obj).__name__: obj.subexprs}
      
    elif isinstance(obj, Requirement):
      return {type(obj).__name__: obj.arguments}

    return super().default(obj)

class ASTDecoder(json.JSONDecoder):
  CLASS_MAP = {
    'Course': Course,
    'And': And,
    'Or': Or,
    'Not': Not,
    'Passed': Passed,
    'Taken': Taken,
    'Coregister': Coregister,
    'Major': Major,
    'Standing': Standing,
    'Permission': Permission,
    'UnsupportedRequirement': UnsupportedRequirement,
    'Requirement': Requirement
  }
  
  def __init__(self, *args, **kwargs):
    kwargs['object_hook'] = self.object_hook
    super().__init__(*args, **kwargs)
  
  def object_hook(self, d):
    ## 1. Top-Level Course namedtuple (Has the "__type__" key)
    if TYPE_KEY in d:
      t = d.pop(TYPE_KEY)
      if t in self.CLASS_MAP:
        return self.CLASS_MAP[t](**d)
        
    ## 2. Compact AST Nodes (It's a dictionary with exactly ONE key)
    elif len(d) == 1:
      k, v = list(d.items())[0]  ## Get the single key and its list of values
      if k in self.CLASS_MAP:
        cls = self.CLASS_MAP[k]
        if issubclass(cls, LogicalExpr):
          return cls(v)
        elif issubclass(cls, Requirement):
          return cls(*v)
          
    return d

def serialize_kb_to_json(kb: list[Course], filepath):
  kb_ready_for_json = []
  for course in kb:
    d = course._asdict()
    d[TYPE_KEY] = type(course).__name__
    kb_ready_for_json.append(d)

  merged_kb = kb_ready_for_json
  added_count = len(kb_ready_for_json)

  if os.path.exists(filepath):
    print(f"KB already exists at {filepath}, merging with new entries.")
    with open(filepath, 'r') as f:
      existing_kb = json.load(f)

    existing_ids = {entry.get('id') for entry in existing_kb if isinstance(entry, dict) and entry.get('id')}
    new_entries = [entry for entry in kb_ready_for_json if entry.get('id') not in existing_ids]
    merged_kb = existing_kb + new_entries
    added_count = len(new_entries)

  with open(filepath, 'w') as f:
    json.dump(merged_kb, f, cls=ASTEncoder, indent=2)
    print(f'JSON KB saved to {filepath} (added {added_count} new entries)')

def deserialize_kb_from_json(filepath) -> list[Course]:
  with open(filepath, 'r') as f:
    kb = json.load(f, cls=ASTDecoder)
    print(f'KB loaded from {filepath} in JSON format')
  return kb

class PrologGenerator:
  suffix_mapping = {
    "prereq": "before",
    "coreq": "same",
    "pre_or_coreq": "before_or_same",
    "anti_req": "before",
  }
  ## generates rules from the AST in prolog and clingo format.
  def __init__(self, kb: list[Course]):
    self.kb = kb

  def semester_suffix(self, req_type: str) -> str:
    if req_type in self.suffix_mapping:
      return self.suffix_mapping[req_type]
    else: raise ValueError(f"Unknown requirement type: {req_type}")

  def join_args(self, args: list[str]) -> str:
    return ",".join(f'"{a}"' for a in args)

  def format_req_with_semester(self, name: str, args: list[str], req_type: str) -> str:
    suffix = self.semester_suffix(req_type)
    if len(args) == 1:
      return f'{name}_{suffix}("{args[0]}", Sem)'
    return f'{name}_{suffix}(({self.join_args(args)}), Sem)'

  def generate_kb(self) -> list[str]:
    output_lines = []    ## l is a list of strings representing the kb
    output_lines.extend([
      r"%%%%% for unsupported requirements, we put 'unsupported' and assume they are satisfied.",
      r"unsupported_prereq.     %%% assume unsupported prereqs are satisfied",
      r"unsupported_coreq.      %%% assume unsupported coreqs are satisfied",
    ])

    for course in self.kb:
      output_lines.extend(self.generate_course(course))
    return output_lines

  def generate_course(self, course) -> list[str]:
    l = []    ## l is a list of strings representing the kb

    ## generate course facts (course/2)
    pat_credits = r'^(?P<min_credit>\d+)(?:-(?P<max_credit>\d+))?$'
    m = re.match(pat_credits, course.credits)
    if m:
      min_credit = int(m.group('min_credit'))
      max_credit = int(m.group('max_credit')) if m.group('max_credit') else min_credit
    
    for credit in range(min_credit, max_credit + 1):
      l.append(f'course("{course.id}", {credit}).')

    for req_type in REQ_TYPES - REQ_TYPES_IGNORE:
      req_value = getattr(course, req_type)
      if req_value is not None:
        l.append(f'has_{req_type}("{course.id}").')       ## add has_requisite fact for each course with that type of requisite
        if isinstance(req_value, Or):
          subexprs = [op for op in req_value.subexprs if not isinstance(op, UnsupportedRequirement)]
          
          if not subexprs:
            l.append(f'{req_type}("{course.id}", Sem) :- semester(Sem), unsupported_{req_type}.')
          else:
            for subexpr in subexprs:
              l.append(f'{req_type}("{course.id}", Sem) :- semester(Sem), {self.generate_expr(subexpr, req_type)}.')
        else:
          l.append(f'{req_type}("{course.id}", Sem) :- semester(Sem),{self.generate_expr(req_value, req_type)}.')
    return list(dict.fromkeys(l))   ## deduplicate with order preserved

  def generate_expr(self, expr: Expr, req_type: str) -> str:
    if isinstance(expr, Requirement): return self.generate_requirement(expr, req_type)
    elif isinstance(expr, And): return self.generate_and(expr, req_type)
    elif isinstance(expr, Or): return self.generate_or(expr, req_type)
    elif isinstance(expr, Not): return self.generate_not(expr, req_type)
    else:
      print("unsupported expr type:", type(expr))
      return "unsupported: " + str(expr)

  ## same requirement output for both prolog and clingo
  def generate_requirement(self, req: Requirement, req_type) -> str:
    ## for passed and taken, add semester
    if isinstance(req, (Passed, Taken)):
      return self.format_req_with_semester(req.name, req.arguments, req_type)
    elif isinstance(req, Coregister):
      return f'taken_same("{req.arguments[0]}")'
    elif isinstance(req, Permission):
      return f'permission'
    elif isinstance(req, UnsupportedRequirement):
      ## ignore unsupported. we assert unsupported as a fact in clingo.
      ## for prereq and coreq, we assume unsupported requirements are satisfied. 
      ## for anti-req, unsupported requirements are assumed to be not satisfied.
      return f'unsupported_{req_type}'
    
    arg_str = self.join_args(req.arguments)
    return f'{req.name}({arg_str})'

  def generate_and(self, expr: And, req_type) -> str:
    if len(expr.subexprs) == 1:
      return self.generate_expr(expr.subexprs[0], req_type)
    parts = []
    for op in expr.subexprs:
      s = self.generate_expr(op, req_type)
      if isinstance(op, LogicalExpr) and len(op.subexprs) > 1: ## add parentheses around Or
        s = f'({s})'
      parts.append(s)
    return ','.join(parts)

  def generate_or(self, expr: Or, req_type) -> str:
    parts = []
    for op in expr.subexprs:
      s = self.generate_expr(op, req_type)
      if isinstance(op, And) and len(op.subexprs) > 1:
        s = f'({s})'
      parts.append(s)
    return ';'.join(parts)
  
  def generate_not(self, expr: Not, req_type) -> str:
    negated_expr = expr.subexpr
    s = self.generate_expr(negated_expr, req_type)
    return f'not ({s})'

class ClingoGenerator(PrologGenerator):
  ## same as PrologGenerator, only overridding conjunction and disjunction for pooling
  def __init__(self, kb: list[Course]):
    super().__init__(kb)
    self.aux_id = 0       ## auxiliary rules for Or: when pooling is not possible, we need to generate extra rules.
    self.aux_rules = []
  
  def generate_kb(self) -> list[str]:
    output_lines = super().generate_kb()
    if self.aux_rules:
      output_lines.extend(self.aux_rules)
    return output_lines

  def generate_and(self, expr: And, req_type) -> str:
    if len(expr.subexprs) == 1:
      return self.generate_expr(expr.subexprs[0], req_type)
    parts = []
    for op in expr.subexprs:                ## don't add parentheses for subexprs in And
      s = self.generate_expr(op, req_type)
      parts.append(s)
    return ','.join(parts)

  def pool_requirement_arguments(self, reqs: list[Requirement]) -> str:
    return "; ".join(self.join_args(op.arguments) for op in reqs if op)

  def format_pooled_sem_requirement(self, name: str, pooled: str, req_type: str) -> str:
    suffix = self.semester_suffix(req_type)
    return f'{name}_{suffix}(({pooled}), Sem)' if pooled.count(";") >= 1 else f'{name}_{suffix}({pooled}, Sem)'

  def generate_or(self, expr: Or, req_type) -> str:
    ## filter out unsupported requirements in Or
    subexprs = [op for op in expr.subexprs if not isinstance(op, UnsupportedRequirement)]
    
    ## if all subexprs are unsupported, return unsupported
    if not subexprs:
      return f'unsupported_{req_type}'

    ## if all are with the same requirement type -> pool arguments
    if all(isinstance(op, Requirement) for op in subexprs) and len(set(type(op) for op in subexprs)) == 1:
      pooled = self.pool_requirement_arguments(subexprs)
      node_type, node_name = type(subexprs[0]), subexprs[0].name

      if node_type is Taken:   ## taken takes semester argument
        return self.format_pooled_sem_requirement(node_name, pooled, req_type)

      if node_type is Passed:  ## passed takes semester argument
        if req_type == "coreq": print("coreq shouldn't have passed requirements, but found:", subexprs)
        return self.format_pooled_sem_requirement(node_name, pooled, req_type)
      
      if node_type is Coregister:  ## coregister is treated as taken_same
        return self.format_pooled_sem_requirement('taken', pooled, 'coreq')

      return f'{node_name}({pooled})'
    
    # raise ValueError(f'clingo: mixed disjunction, cannot pool: {expr}')
    self.aux_id += 1
    aux_pred = f'aux_or_{self.aux_id}(Sem)'
    for op in subexprs:
      op_str = self.generate_expr(op, req_type)
      self.aux_rules.append(f'{aux_pred} :- semester(Sem), {op_str}.')
    return aux_pred

COURSES_CSE_DEGREE = {    ## courses listed in the degree requirements.
  'CSE 114', 'CSE 214', 'CSE 216',  ## prog
  'CSE 160', 'CSE 161', 'CSE 260', 'CSE 261',  ## prog2
  'CSE 215',  ## dmath
  'CSE 150',  ## dmath2
  'CSE 220',  ## sys
  'CSE 303',  ## theory
  'CSE 350',  ## theory2
  'CSE 373',  ## algo
  'CSE 385',  ## algo2
  'CSE 310', 'CSE 316', 'CSE 320', 'CSE 416',  ## common
  'AMS 151', 'AMS 161',  ## calc
  'MAT 125', 'MAT 126', 'MAT 127',  ## calc2
  'MAT 131', 'MAT 132',  ## calc3
  'MAT 211',  ## alg
  'AMS 210',  ## alg2
  'AMS 301',  ## fmath
  'AMS 310',  ## sta
  'AMS 311',  ## sta2
  'BIO 201', 'BIO 204',  ## bio
  'BIO 202', 'BIO 204',  ## bio2
  'BIO 203', 'BIO 204',  ## bio3
  'CHE 131', 'CHE 133',  ## che
  'CHE 152', 'CHE 154',  ## che2
  'PHY 126', 'PHY 133',  ## phy
  'PHY 131', 'PHY 133',  ## phy2
  'PHY 141', 'PHY 133',  ## phy3
  'CSE 312',  ## ethics
  'CSE 300',  ## writing
  'WRT 101', 'WRT 102', ## needed for writing
  'CSE 475', 'CSE 495', 'CSE 300', 'CSE 301', 'CSE 312',  ## elect_exclude
  'AST 203', 'AST 205', 'CHE 132', 'CHE 321', 'CHE 322', 'CHE 331', 'CHE 332', 'GEO 102', 'GEO 103', 'GEO 112', 'GEO 123', 'GEO 122', 'PHY 125', 'PHY 127', 'PHY 132', 'PHY 134', 'PHY 142', 'PHY 251', 'PHY 252'  ## sci_more
}

COURSES_CSE_DEGREE |= { ## missing prereq courses from the above courses
  'AMS 110', 'AMS 261', 'AMS 361', 'AMS 412',  ## ams
  'BME 120',  ## bme
  'CHE 129', 'CHE 383',  ## che
  'ESE 124', 'ESE 280',  ## ese
  'ESG 111',  ## esg
  'ISE 108', 'ISE 208', 'ISE 218', 'ISE 334',  ## ise
  'MAT 130', 'MAT 141', 'MAT 142', 'MAT 171',  ## mat calc & prep
  'MAT 200', 'MAT 203', 'MAT 205', 'MAT 250',  ## mat intermediate
  'MAT 303', 'MAT 307',  ## mat advanced
  'MEC 102', 'MEC 262',  ## mec
  'PHY 122', 'PHY 124'   ## phy
}

def main():
  parser = argparse.ArgumentParser(
    description='Generate course KB for specified programs in Stony Brook. \n'
                'The generated KB can be serialized into a JSON file or exported in prolog/clingo format.\n'
                'To generate KB for specific programs, use -p or --prog followed by program codes (e.g., -p cse phy). To generate for all programs (relevant to the CSE degree program), use -a or --all.\n'
                'For output, use either -s/--show to print the KB to console, or -f/--file to save it to a file. If language is specified with -l/--language, the KB will be exported in that format; otherwise, it will be saved as a JSON file.\n')

  group_input = parser.add_mutually_exclusive_group(required=True)  ## input: generate KB or load from file
  group_input.add_argument('-p', '--prog', nargs='+', help="Generate KB for one or more specific programs (e.g., -p cse phy).")
  group_input.add_argument('-a', '--all', action='store_true', help="Generate KB for all programs relevant in evaluating CSE degree requirement.")
  group_input.add_argument('-i', '--input', metavar='FILEPATH', help="Load KB from a previously saved JSON file.")
  
  group_output = parser.add_mutually_exclusive_group()  ## output: either print or save to file
  group_output.add_argument('-f', '--file', metavar='FILEPATH', help="Save KB to path. If language is specified then the KB will be export to the specific language. Otherwise, it will be saved to a JSON file.")
  group_output.add_argument('-s', '--show', action='store_true', help="Print the KB in the console.")

  parser.add_argument('-l', '--language', choices=['prolog', 'clingo'], help="Export format: prolog or clingo (default: prolog)")

  args = parser.parse_args()
  
  ## generate KB
  kb = []
  if args.input:    ## load KB from JSON
    print(f"Loading KB from {args.input}...")
    kb = deserialize_kb_from_json(args.input)
  else:             ## generate KB from programs
    if args.all:
      kb = get_kb_from_program('cse')  ## always include CSE courses in KB
      other_programs = ['ams', 'mat', 'bio', 'che', 'phy', 'geo', 'ast', 'wrt']
      kb.extend([course for prog in other_programs for course in get_kb_from_program(prog) if course.id in COURSES_CSE_DEGREE])  ## filter courses relevant to CSE degree requirements
    else:
      for prog in args.prog:
        kb.extend(get_kb_from_program(prog))

  ## output KB
  if args.language: ## to prolog or clingo
    generator = PrologGenerator(kb) if args.language == 'prolog' else ClingoGenerator(kb)
    output_text = "\n".join(generator.generate_kb())
    if args.show: print(output_text)
    else:
      ext = "pl" if args.language == "prolog" else "lp"
      filepath = args.file if args.file else f'./course_kb_{args.language}.{ext}'
      with open(filepath, 'w') as f:
        f.write(output_text)
      print(f'{args.language} KB saved to {filepath}.')
  else:             ## to JSON
    if args.show: pprint(kb)
    else:
      filepath = args.file if args.file else './course_kb.json'
      serialize_kb_to_json(kb, filepath)

if __name__ == "__main__":
  main()