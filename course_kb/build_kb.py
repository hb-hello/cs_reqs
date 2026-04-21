from pprint import pprint
import requests
import re
import argparse
import json
import os
from bs4 import BeautifulSoup 
from .course_kb import *
from .parse_course import course_div_cleanup, parse_course_div, parse_req_text
from .courses import COURSES_CSE_DEGREE, COURSES_OVERRIDES

REQ_TYPES = {'prereq', 'coreq', 'pre_or_coreq', 'anti_req', 'advisory_prereq', 'advisory_coreq', 'advisory_pre_or_coreq'}
REQ_TYPES_IGNORE = {'advisory_prereq', 'advisory_coreq', 'advisory_pre_or_coreq'}

def create_course_namedtuple(course_dict : dict) -> Course:
  ## from course dictionary (returned by parse_course_div) to course namedtuple
  ## input: dictionary with normalized field keys like 'id', 'desc', 'prereq', ...
  print("parsing course:", course_dict.get('id'))

  def get_parsed_req(req: str):
    req_text = course_dict.get(req)
    is_coreq = req in ['coreq', 'advisory_coreq']
    return parse_req_text(req_text, is_coreq) if req_text else None

  return Course(
    id=course_dict.get('id'),
    title=course_dict.get('title'),
    desc=course_dict.get('desc'),
    prereq=get_parsed_req('prereq'),
    coreq=get_parsed_req('coreq'),
    pre_or_coreq=get_parsed_req('pre_or_coreq'),
    anti_req=get_parsed_req('anti_req'),
    advisory_prereq=get_parsed_req('advisory_prereq'),
    advisory_coreq=get_parsed_req('advisory_coreq'),
    advisory_pre_or_coreq=get_parsed_req('advisory_pre_or_coreq'),
    category=course_dict.get('category'),
    credits=course_dict.get('credits'),
    grading=course_dict.get('grading')
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
    if (course.id).startswith('CSE') or course.id in COURSES_CSE_DEGREE:
      with open('courses_cse_degree.html', 'a') as f:
        f.write(str(clean_div))
    if course.id in COURSES_OVERRIDES:                      ## apply overrides if exists
      print(f"Applying override for course {course.id}")
      course = course._replace(**COURSES_OVERRIDES[course.id])
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

class ASTEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, LogicalExpr):
      if isinstance(obj, Not):
        return {type(obj).__name__: obj.negated_expr}
      return {type(obj).__name__: obj.subexprs}
    elif isinstance(obj, (C_or_higher, B_or_higher)):
     return {type(obj).__name__: obj.course_id}
    elif isinstance(obj, Requirement):
      if len(obj.arguments) == 1: ## if only one argument, store it directly instead of a list
        return {type(obj).__name__: obj.arguments[0]}
      return {type(obj).__name__: obj.arguments}

    return super().default(obj)

TYPE_KEY = "__type__"
COURSE_TYPE_VALUE = "Course"

class ASTDecoder(json.JSONDecoder):
  CLASS_MAP = {
    'Course': Course,
    'And': And,
    'Or': Or,
    'Not': Not,
    'Passed': Passed,
    'C_or_higher': C_or_higher,
    'B_or_higher': B_or_higher,
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

  def _decode_typed_object(self, d):
    t = d.pop(TYPE_KEY)

    if t == COURSE_TYPE_VALUE:
      # Course JSON is sparse (None-valued keys omitted), so fill missing
      # Course fields back with None before constructing the namedtuple.
      course_dict = {field: d.get(field, None) for field in Course._fields}
      return Course(**course_dict)

    cls = self.CLASS_MAP.get(t)
    if cls:
      return cls(**d)

    return d

  def _decode_field(self, d):
    ## decode AST nodes
    ## NOTE: "len(d) == 1" means "single-key type-tagged AST node",
    if len(d) != 1:
      return d

    k, v = next(iter(d.items()))
    cls = self.CLASS_MAP.get(k)
    if not cls:
      return d

    if issubclass(cls, LogicalExpr):
      return cls(v)
    elif issubclass(cls, Requirement):
      if cls is C_or_higher: return Passed(v, "C")
      if cls is B_or_higher: return Passed(v, "B")
      if isinstance(v, (list, tuple)):
        return cls(*v)
      return cls(v)

    return d
  
  def object_hook(self, d):
    if TYPE_KEY in d:
      return self._decode_typed_object(d)
    return self._decode_field(d)

def _all_subclasses(cls):
  for subcls in cls.__subclasses__():
    yield subcls
    yield from _all_subclasses(subcls)

def _compact_simple_json_objects(json_text: str) -> str:
  """Compact requirement nodes to one-line objects.

  Requirement examples:
    {"Passed": ["CSE 216", "C"]}
    {"Taken": "CSE 114"}

  Logical nodes (`And`, `Or`, `Not`) remain pretty-printed.
  """
  _REQUIREMENT_KEYS = tuple(
    sorted({subcls.__name__ for subcls in _all_subclasses(Requirement)})
  )

  _REQUIREMENT_ONE_KEY_OBJECT_RE = re.compile(
    rf'(?P<indent>[ \t]*)(?P<prefix>"[^"\n]+":\s*)?\{{\n'
    rf'[ \t]*"(?P<key>{"|".join(re.escape(name) for name in _REQUIREMENT_KEYS)})": (?P<val>.*?)\n'
    rf'(?P=indent)\}}',
    re.MULTILINE | re.DOTALL,
  )

  def _replace(m):
    key = m.group('key')
    if key not in _REQUIREMENT_KEYS:
      return m.group(0)

    try:
      value = json.loads(m.group('val'))
    except json.JSONDecodeError:
      return m.group(0)

    prefix = m.group('prefix') or ''
    return f'{m.group("indent")}{prefix}{json.dumps({key: value}, ensure_ascii=False)}'

  return _REQUIREMENT_ONE_KEY_OBJECT_RE.sub(_replace, json_text)

def serialize_kb_to_json(kb: list[Course], filepath):
  kb_ready_for_json = []
  for course in kb:
    d = course._asdict()
    d[TYPE_KEY] = type(course).__name__
    d = {k: v for k, v in d.items() if v is not None}
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
    
    ## remove None fields
    merged_kb = [{k: v for k, v in entry.items() if v is not None} if isinstance(entry, dict) else entry for entry in merged_kb]

    added_count = len(new_entries)

  json_text = _compact_simple_json_objects(
    json.dumps(merged_kb, cls=ASTEncoder, indent=2)
  )

  with open(filepath, 'w') as f:
    f.write(json_text)
    f.write('\n')
    print(f'JSON KB saved to {filepath} (added {added_count} new entries)')

def deserialize_kb_from_json(filepath) -> list[Course]:
  with open(filepath, 'r') as f:
    kb = json.load(f, cls=ASTDecoder)
    print(f'KB loaded from {filepath} in JSON format')
  return kb

class PrologGenerator:
  suffix_mapping = {
    "prereq": "before",
    "coreq": "together",
    "pre_or_coreq": "before_or_together",
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

  def format_passed_requirement(self, req: Passed, req_type: str) -> str:
    course_id = req.arguments[0]
    grade = req.arguments[1] if len(req.arguments) >= 2 else "C"

    if grade == "C":
      return self.format_req_with_semester(req.name, [course_id], req_type)

    suffix = self.semester_suffix(req_type)
    if suffix == "before":
      return f'passed_before_grade("{course_id}", "{grade}", Sem)'
    return f'passed_{suffix}_grade("{course_id}", "{grade}", Sem)'

  def generate_kb(self) -> list[str]:
    output_lines = []    ## l is a list of strings representing the kb
    output_lines.extend([
      r"%%%%% for unsupported requirements, we put 'unsupported' and assume they are satisfied.",
      r"unsupported_prereq.     %%% assume unsupported prereqs are satisfied",
      r"unsupported_coreq.      %%% assume unsupported coreqs are satisfied",
      r"unsupported_pre_or_coreq. %%% assume unsupported pre_or_coreqs are satisfied",
      r"unsupported_anti_req.   %%% assume unsupported anti-reqs are satisfied",
    ])

    for course in self.kb:
      output_lines.extend(self.generate_course(course))
    return output_lines

  def generate_req_common(self, req_type, req_value, course):
    req_rules = []
    if isinstance(req_value, Or):
      ## in Or, filter out supported requirements first
      subexprs = [op for op in req_value.subexprs if not isinstance(op, UnsupportedRequirement)]
      if not subexprs:
        req_rules.append(f'{req_type}("{course.id}", Sem) :- offered("{course.id}", Sem), unsupported_{req_type}.')
      else:
        for subexpr in subexprs:    ## top level Or, we use multiple rules
          req_rules.append(f'{req_type}("{course.id}", Sem) :- offered("{course.id}", Sem), {self.generate_expr(subexpr, req_type)}.')
    else:
      req_rules.append(f'{req_type}("{course.id}", Sem) :- offered("{course.id}", Sem), {self.generate_expr(req_value, req_type)}.')
    return req_rules

  def generate_req_w_has(self, req_type, req_value, course):
    req_rules = []
    if not req_value:     ## missing requisite not in KB
      return req_rules

    req_rules.append(f'has_{req_type}("{course.id}").')

    req_rules.extend(self.generate_req_common(req_type, req_value, course))
    return req_rules

  def generate_req_wo_has(self, req_type, req_value, course):
    req_rules = []
    if not req_value:      ## missing requisite is assumed to be satisfied
      req_rules.append(f'{req_type}("{course.id}", Sem) :- offered("{course.id}", Sem).')
      return req_rules

    req_rules.extend(self.generate_req_common(req_type, req_value, course))
    return req_rules

  def generate_course(self, course) -> list[str]:
    kb_rules = []    ## l is a list of strings representing the kb

    if isinstance(course.credits, list):
      min_credits = course.credits[0]
      max_credits = course.credits[1]
    else:
      min_credits = max_credits = course.credits

    for credit in range(min_credits, max_credits + 1):
      kb_rules.append(f'credits("{course.id}", {credit}).')

    for req_type in sorted(list(REQ_TYPES - REQ_TYPES_IGNORE)):
      req_value = getattr(course, req_type)
      kb_rules.extend(self.generate_req_w_has(req_type, req_value, course))
    return list(dict.fromkeys(kb_rules))   ## deduplicate with order preserved

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
    if isinstance(req, Taken):
      return self.format_req_with_semester(req.name, req.arguments, req_type)
    elif isinstance(req, Passed):
      return self.format_passed_requirement(req, req_type)
    elif isinstance(req, Coregister):
      return f'taken_together("{req.arguments[0]}")'
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
    negated_expr = expr.subexprs[0]
    s = self.generate_expr(negated_expr, req_type)
    return f'not {s}'

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

  def format_pooled_requirement(self, nodes,  ## types should all be the same. for Passed, grade should all be the same as well
                                req_type: str) -> str:
    suffix = self.semester_suffix(req_type)
    node_type = type(nodes[0])
    node_name = nodes[0].name
    if node_type is Passed:
      all_same_grades = len(set(passed.min_grade for passed in nodes)) == 1
      if not all_same_grades:
        ## mixed or non-default grade disjunctions should not be pooled
        ## because explicit-grade requirements use a different predicate.
        raise ValueError(f'clingo: mixed or non-default grade disjunction, cannot pool: {nodes}')
      grade = nodes[0].min_grade
      pooled_ids = "; ".join(f'"{node.course_id}"' for node in nodes)
      if grade == "C":
        return f'{node_name}_{suffix}(({pooled_ids}), Sem)' if pooled_ids.count(";") >= 1 else f'{node_name}_{suffix}({pooled_ids}, Sem)'
      return f'{node_name}_{suffix}_grade(({pooled_ids}), "{grade}", Sem)' if pooled_ids.count(";") >= 1 else f'{node_name}_{suffix}_grade({pooled_ids}, "{grade}", Sem)'
    if node_type is Taken:
      pooled_ids = "; ".join(f'"{node.arguments[0]}"' for node in nodes)
      return f'{node_name}_{suffix}(({pooled_ids}), Sem)' if pooled_ids.count(";") >= 1 else f'{node_name}_{suffix}({pooled_ids}, Sem)'
    if node_type is Coregister:
      pooled_ids = "; ".join(f'"{node.arguments[0]}"' for node in nodes)
      return f'taken_together(({pooled_ids}), Sem)' if pooled_ids.count(";") >= 1 else f'taken_together({pooled_ids}, Sem)'

  def generate_or(self, expr: Or, req_type) -> str:
    ## filter out unsupported requirements in Or
    subexprs = [op for op in expr.subexprs if not isinstance(op, UnsupportedRequirement)]
    
    ## if all subexprs are unsupported, return unsupported
    if not subexprs:
      return f'unsupported_{req_type}'

    ## if all are with the same requirement type -> pool arguments
    if all(isinstance(op, Requirement) for op in subexprs) and len(set(type(op) for op in subexprs)) == 1:
      node_type, node_name = type(subexprs[0]), subexprs[0].name

      if node_type in [Passed, Taken, Coregister]:
        return self.format_pooled_requirement(subexprs, req_type)

      pooled = "; ".join(self.join_args(op.arguments) for op in subexprs if op)
      return f'{node_name}({pooled})'
    
    # raise ValueError(f'clingo: mixed disjunction, cannot pool: {expr}')
    self.aux_id += 1
    aux_pred = f'aux_or_{self.aux_id}(Sem)'
    for op in subexprs:
      op_str = self.generate_expr(op, req_type)
      self.aux_rules.append(f'{aux_pred} :- {op_str}.')
    return aux_pred

  def generate_not(self, expr: Not, req_type) -> str:
    negated_expr = expr.subexprs[0]
    if isinstance(negated_expr, Or):    ## de morgan for clingo
      negated_and = And(
        *[Not(sub) for sub in negated_expr.subexprs if not isinstance(sub, UnsupportedRequirement)]
      )
      return self.generate_and(negated_and, req_type)
    return f'not {self.generate_expr(negated_expr, req_type)}'

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