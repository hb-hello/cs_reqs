import re, json
from bs4 import BeautifulSoup, NavigableString, Tag
from .course_kb import *
from openai import OpenAI

USE_LLM_TO_PARSE = False

PAT_COURSE_ID = r'[A-Z]{3}\s[0-9]{3}'  ## course id: 3 uppercase letters followed by 3 digits.
PAT_MAJOR = r'\b[A-Z]{3}\b'            ## major code: 3 uppercase letters

def course_div_cleanup(course_div: BeautifulSoup):  
  ## pre-processing. clean up the course div and return a new div.
  ## we remove redundant tags and attributes, which makes it easier to parse the course fields in the next step.
  ## input: a course div object in beautifulsoup
  ## output: a cleaned course div object in beautifulsoup

  ## remove the "clear" div at the end.
  clear_div = course_div.find("div", class_="clear")
  if clear_div:
    clear_div.decompose()

  ## remove <i> tags. the <i> tags are only used for requisites, but not in a consistent way.
  ##  for example, if there are multiple requisites (say prereq and coreq), only the first one is marked with <i>.
  for i_tag in course_div.find_all("i"):
    i_tag.unwrap()

  ## remove empty divs. for example, <p></p>, or <br>
  for tag in course_div.find_all(True):
    text = tag.get_text(strip=True).replace("\u200b", "")
    if tag.name in {"p", "br", "div"} and text == "":
      tag.decompose()

  ## remove all attributes from all tags
  for tag in course_div.find_all(True):
    tag.attrs = {}

  ## remove whitespace only text children
  ## replace non-breaking space with regular space in all text nodes
  ## replace tabs with spaces
  for node in course_div.find_all(string=True):
    if isinstance(node, NavigableString) and node.strip() == "":
      node.extract()
    else:
      node.replace_with(node.replace('\xa0', ' ').replace('\t', ' '))
 
  return course_div

def parse_course_id_name(child: Tag):    ### todo: refactor the parsing functions
  ## parse the course id and name from <h3> tag.
  ## input: a tag object in beautifulsoup
  ## output: boolean indicating whether parsing is successful, and
  ##         a dictionary with keys 'id' and 'name' if parsing is successful (otherwise None).
  if child.name != "h3": print('expected h3 tag, got:', child); return False, None
  
  pat_course_id_name = rf'^(?P<id>{PAT_COURSE_ID}):\s(?P<title>.+)$'
  m = re.fullmatch(pat_course_id_name, child.get_text(" ", strip=True))

  if m: return True, m.groupdict()
  return False, None

def parse_course_desc(child: Tag):
  ## parse the course description from <p> tag.
  ## input: a tag object in beautifulsoup
  ## output: boolean indicating whether parsing is successful, and
  ##         a dictionary with key 'desc' if parsing is successful (otherwise None).
  if child.name != "p": print('expected p tag, got:', child); return False, None

  pat_course_desc = r'(?P<desc>.+)' ## everything in the tag is considered as description.
  m = re.match(pat_course_desc, child.get_text(" ", strip=True))

  if m: return True, m.groupdict()
  return False, None

def parse_req(child: Tag):
  ## parse the requisites (prerequisite/corequisite/antirequisite) from <p> tag.
  ## input: a tag object in beautifulsoup
  ## output: boolean indicating whether parsing is successful, and
  ##         a dictionary with key requisite names, e.g. 'Prerequisite', 'Corequisite', etc. 
  ##           if parsing is successful (otherwise None).

  ## compiled regex patterns for requisites
  re_requisite = re.compile(r'''
  ^
  (?P<requisite>
      (?:Advisory\s+)?          # optional "Advisory" at the beginning
      (?:
          Anti-requisites?
        | Prerequisites?
        | Corequisites?
        | Pre\s*-?\s*or\s+Co\s*-?\s*requisites?
      )
  ):\s*(?P<value>.+)$
  ''', re.IGNORECASE | re.VERBOSE | re.DOTALL)   ## dotall to match newlines 

  if child.name != "p": return False, None  ## only process <p> tags for requisites.
  m = re_requisite.fullmatch(child.get_text(" ", strip=True))
  if m: return True, {m.group("requisite"): m.group("value")}
  return False, None

def parse_credits(child: Tag):
  ## parse the credits and grading information from <p> tag.
  ## input: a tag object in beautifulsoup
  ## output: boolean indicating whether parsing is successful, and
  ##         a dictionary with keys 'credits' and 'grading' if parsing is successful (otherwise None).
  if child.name != "p": return False, None  ## only process <p> tags for credits.
  pat_credits = r'^(?P<credits>[0-9]+(?:-[0-9]+)?) credits?,?\s*(?P<grading>.+)?$'
  m = re.fullmatch(pat_credits, child.get_text(" ", strip=True))
  if m: return True, m.groupdict()
  return False, None

## def parse_category(child):  ### TODO
## parse categories such as SBC.
##   pass

## def parse_partially_fulfills(child): ### TODO
##   pass

def parse_course_list_1(text: str) -> And | Or | Requirement | None:
  ## standard format
  and_parts = []
  parts = re.split(r'\s*(?:,|and)\s*', text)
  for part in parts:
    if not re.fullmatch(rf'^{PAT_COURSE_ID}(?:\s*or\s*{PAT_COURSE_ID})*$', part, re.IGNORECASE):
      and_parts.append(UnsupportedRequirement(part))
      continue
    or_parts = re.split(r'\s*or\s*', part)
    and_parts.append(build_node(Or, or_parts))
  return build_node(And, and_parts)

def parse_course_list_2(text: str) -> And | Or | Requirement | None:
  ## slashes for 'And'
  course_ids = []
  courses = re.split(r'\s*or\s*', text)
  for course in courses:
    m = re.fullmatch(r'^(?P<dep>[A-Z]{3})\s+(?P<num1>\d{3})/(?P<num2>\d{3})$', course.strip(), re.IGNORECASE)
    if m:
      course_ids.append(f"{m.group('dep')} {m.group('num1')}")
      course_ids.append(f"{m.group('dep')} {m.group('num2')}")
    else:
      return None
  return build_node(Or, course_ids)

def parse_course_list_3(text: str) -> And | Or | Requirement | None:
  ## omitted Dept
  course_ids = []
  parts = re.split(r'\s*or\s*', text)
  current_dept = None
  for part in parts:
    dept = re.search(r'[A-Z]{3}', part)
    if dept:
      current_dept = dept.group()
    nums = re.findall(r'\d{3}', part)
    for num in nums:
      course_ids.append(f'{current_dept} {num}')
  return build_node(Or, course_ids)

re_course_list_parsers = {
  ## identifying list of courses, SEPARATOR is ",", "or", or "and"
  ## grammar: COURSE_ID (SEPARATOR COURSE_ID)*     e.g. "CSE 160 or CSE 214", "CSE 160, CSE 214 or CSE 260"
  re.compile(rf'''^{PAT_COURSE_ID} (?:\s* (?:,|and|or) \s* {PAT_COURSE_ID})*''', re.IGNORECASE | re.VERBOSE): parse_course_list_1,

  ## grammar: DEP NUM1/NUM2 (or DEP NUM1/NUM2)*
  ## e.g. "PHY 125/133 or PHY 131/133 or PHY 141/133"
  re.compile(r'''^[A-Z]{3}\s+\d{3}/\d{3}(?:\s+or\s+[A-Z]{3}\s+\d{3}/\d{3})*$''', re.IGNORECASE | re.VERBOSE): parse_course_list_2,

  ## grammar: DEP (NUM1 (or NUM2)*) (or DEP (NUM1 (or NUM2)*))* 
  ## e.g. "AMS 151 or MAT 125 or 131"
  re.compile(r'''^[A-Z]{3}\s+\d{3}(?:\s+or\s+\d{3})*(?:\s+or\s+[A-Z]{3}\s+\d{3}(?:\s+or\s+\d{3})*)*$''', re.IGNORECASE | re.VERBOSE): parse_course_list_3,
}

re_any_course_list = re.compile(rf'{'|'.join(r.pattern for r in re_course_list_parsers)}', re.IGNORECASE | re.VERBOSE)

def build_node(node: And | Or, items: list[And|Or|Requirement]) -> And | Or | Requirement:
  if len(items) == 1: return items[0]
  return node(items)

def parse_course_list_text(text: str) -> And | Or | str:
  ## input: text that contains a list of courses, found in the requisite text.
  ## output: a structured representation of the course list connected by And and Or.
  text = text.strip()
  
  for pattern, parser_func in re_course_list_parsers.items():
    if re.fullmatch(pattern, text):
      return parser_func(text)
  
  return None

def parse_mixed_or_list(text: str) -> list[str | UnsupportedRequirement] | None:
  """
  Parse disjunctions that may mix course ids (including omitted department code)
  with unsupported text, e.g.
    - "AMS 161 or MAT 127 or 132 or MPE level 9"
    - "MAT 127 or 132 or 142 or AMS 161 or level 9 on the mathematics placement examination"
  Returns a list of either course-id strings or UnsupportedRequirement nodes.
  Returns None if no course-like token is found.
  """
  if re.search(r'\bor\s+higher\b', text, re.IGNORECASE) or re.search(r'\bor\b[^;,.]*\bequivalent\b', text, re.IGNORECASE):
    return [UnsupportedRequirement(text)]

  parts = [p.strip(" ,.") for p in re.split(r'\s+or\s+', text, flags=re.IGNORECASE) if p.strip(" ,.")]
  if not parts:
    return None

  items = []
  current_dept = None
  found_course = False

  for part in parts:
    m_full = re.fullmatch(r'([A-Z]{3})\s+(\d{3})', part, re.IGNORECASE)
    if m_full:
      dept = m_full.group(1).upper()
      num = m_full.group(2)
      current_dept = dept
      items.append(f'{dept} {num}')
      found_course = True
      continue

    m_num = re.fullmatch(r'(\d{3})', part)
    if m_num and current_dept:
      items.append(f'{current_dept} {m_num.group(1)}')
      found_course = True
      continue

    items.append(UnsupportedRequirement(part))

  return items if found_course else None

def apply_requirement_recursive(node: And | Or, requirement: Requirement) -> And | Or:
  ## apply the requirement (e.g. Taken or Passed) to each course in the course list recursively.
  ## e.g. And([ "CSE 160", Or(["CSE 214", "CSE 260"]) ]) with requirement = Passed becomes
  ## And([ passed("CSE 160"), Or([passed("CSE 214"), passed("CSE 260")]) ])
  if isinstance(node, str):                       ## base case
    return requirement(node)
  if isinstance(node, UnsupportedRequirement):
    return node
  if isinstance(node, And):
    return And([apply_requirement_recursive(child, requirement) for child in node.subexprs])
  if isinstance(node, Or):
    return Or([apply_requirement_recursive(child, requirement) for child in node.subexprs])

client = OpenAI()

def parse_with_llm(text: str) -> dict:
  """Sends unsupported text to OpenAI and returns a dictionary matching the AST schema."""
  
  system_prompt = """
    You are an expert course requirement parser. Your job is to convert natural language 
    university prerequisites into a strict JSON Abstract Syntax Tree (AST).
    
    SUPPORTED KEYS:
    - "Taken": ["COURSE_ID"] (e.g. "CSE 334")
    - "Passed": ["COURSE_ID", "GRADE"] (e.g. "CSE 214", "c")
    - "Major": ["MAJOR_CODE"] (e.g. "CSE")
    - "Standing": ["U1"|"U2"|"U3"|"U4"]
    - "Permission": ["permission text"]
    
    LOGICAL KEYS (Can contain other keys):
    - "And": [ ... ]
    - "Or": [ ... ]
    
    UNSUPPORTED KEY:
    If the text contains rules about honors colleges, placement exams, high school equivalents, 
    or anything not listed above, wrap the exact original text in:
    - "UnsupportedRequirement": ["original text"]
    
    CRITICAL PARSING RULES:
    1. STRICT COURSE IDs: "Taken" and "Passed" should ONLY take the clean Course ID (e.g., "PHY 131"). Strip out words like "in", "corequisite", or "grade of".
    2. INFER MISSING DEPARTMENTS: If a course number appears without a department code (e.g., "PHY 125 or 131" or "MAT 131 or 141"), infer the department code from the preceding course (e.g., "PHY 131", "MAT 141").
    3. GRADE DISTRIBUTION: If a grade requirement precedes a list (e.g., "C or higher in MAT 126 or 132 or 142"), apply the "Passed" object and the grade to ALL courses in that grouping. Standardize grades to lowercase (e.g., "c", "b+").
    4. PUNCTUATION LOGIC: 
      - Semicolons (;) usually act as top-level "And" separators. 
      - Commas (,) can act as "And" or "Or" depending on the trailing conjunction (e.g., "A, B, or C" is Or; "A, B, and C" is And). 
      - Slashes (/) between course numbers (e.g., "PHY 122/124") mean "And" (e.g., PHY 122 AND PHY 124).
      - Slashes (/) between department codes (e.g., "CSE/ISE 214") mean "Or" (e.g., CSE 214 OR ISE 214).
    5. MIXED SUPPORT: You can mix supported and unsupported keys inside logical operators. (e.g., "MAT 123 or Level 4 on math placement" becomes an "Or" containing a "Taken" and an "UnsupportedRequirement").
    6. SINGLE ROOT: The JSON must have exactly ONE root object. If there are multiple distinct requirements, wrap them in an "And".
    
    EXAMPLES:
    - "CSE 334 or ISE 334" -> {"Or": [{"Taken": ["CSE 334"]}, {"Taken": ["ISE 334"]}]}
    - "Level 3 on math exam" -> {"UnsupportedRequirement": ["Level 3 on math exam"]}
    - "PHY 126 and 127; or PHY 132" -> {"Or": [{"And": [{"Taken": ["PHY 126"]}, {"Taken": ["PHY 127"]}]}, {"Taken": ["PHY 132"]}]}
    """

  response = client.chat.completions.create(
    model="gpt-4o-mini",  ## fast and cheap
    response_format={ "type": "json_object" },
    messages=[
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": f"Parse this requirement into JSON: {text}"}
    ],
    temperature=0.0       ## Keep it deterministic and strictly factual
  )

  return json.loads(response.choices[0].message.content)

def dict_to_ast(d: dict):
  """Recursively converts the LLM's compact JSON dictionary into Python AST objects."""
  if not isinstance(d, dict) or len(d) != 1:
    return UnsupportedRequirement(str(d))
    
  key, value = list(d.items())[0]
  
  if key == "And": return And([dict_to_ast(child) for child in value])
  if key == "Or": return Or([dict_to_ast(child) for child in value])
  
  if key == "Taken": return Taken(*value)
  if key == "Passed": return Passed(*value)
  if key == "Major": return Major(*value)
  if key == "Standing": return Standing(*value)
  if key == "Permission": return Permission(*value)
  
  if key == "UnsupportedRequirement": return UnsupportedRequirement(*value)
  
  return UnsupportedRequirement(str(d))


def parse_req_text(text: str) -> And | Or | Requirement:
  ## parse prerequisite/corequisite/antirequisite text. 
  ## input:  text string for requsites (pre/co/anti/advisory)
  ## output: a structured representation of the requisites.
  ## for example:
  ##  "WRT 102; CSE or ISE or DAS major; U3 or U4 standing" becomes:
  ##   And([ "taken("WRT 102")", Or([Major("CSE"), Major("ISE"), Major("DAS")]), Or(["U3 standing", "U4 standing"]) ])
  ## 
  ##  "C or higher: CSE 160 or CSE 214; CSE 150 or CSE 215; CSE major" becomes:
  ##  AND(Or([ "passed("CSE 160")", "passed("CSE 214")" ]), Or([ "passed("CSE 150")", "passed("CSE 215")" ]), Major("CSE"))
  ##  
  ## requirements supported:
  ## 1. courses taken (without C or higher, for example: "Prerequisites: AMS 301")
  ##    represented as Taken(course_id).
  ##
  ## 2. C or higher (for example: "C or higher: CSE 160 or CSE 214")
  ##    represented as Passed(course_id).
  ##     for C or higher, we assume it applies to all courses listed after the colon, not just the first set of courses.
  ##     for example, "C or higher: CSE 160 or CSE 214; CSE 150 or CSE 215" means
  ##      (passed("CSE 160"); passed("CSE 214")), (passed("CSE 150"); passed("CSE 215")).
  ## not: (passed("CSE 160"); passed("CSE 214")), (taken("CSE 150"); taken("CSE 215")).
  ##    supported formats: 
  ##     C or higher: CSE 214, CSE 216 or CSE 260    (means passed("CSE 214"), (passed("CSE 216") or passed("CSE 260")))
  ##     C or higher: CSE 214 or 260; CSE 220 or ISE 218
  ##     C or higher in CSE 316 or CSE 351; AMS 310
  ##     C or higher in: CSE 113 or CSE 150 or CSE 215 or MAT 200 or MAT 250; MAT 211 or AMS 210; CSE 214 or CSE 260
  ##
  ## 3. major
  ##    represented as Major(major_name).
  ### the major requirement does not have a consistent format
  ### the formats we have seen include:
  ### "CSE or DAS major"            (no 'major' after CSE)
  ### "CSE Major or ECE major"      (upper case 'Major')
  ### "CSE major or ISE major"      (lower case 'major')
  ## 
  ## 4. standing
  ##    represented as Standing(level).


  ### Assume at most two levels or And and Or, and the top level operator is And.

  ## split the text by ';' (And)
  parts = re.split(r'\s*;\s*', text)
  
  requirements = []             ## list of requirements

  ## regex for recognizing c or higher    ### TODO: b or higher
  # re_c_or_higher_prefix = re.compile(r'''^C\sor\s(?:higher|better)(?:\s+in)?(?:\s*:)?\s+(?P<rest>.+)$''', re.IGNORECASE | re.VERBOSE)
  re_grade_or_higher_prefix = re.compile(r'''^(?P<grade>[A-D]\+?)\sor\s(?:higher|better)(?:\s+in)?(?:\s*:)?\s+(?P<rest>.+)$''', re.IGNORECASE | re.VERBOSE)

  ## identifying major requirement
  ## grammar: PAT_MAJOR (major)? (SEPARATOR PAT_MAJOR (major)?)*
  re_major = re.compile(rf'''
  ^
    \b{PAT_MAJOR}\b           ## first major code, e.g. CSE
    (?:\s+major)?             ## optional "major"
    (?:                       ## zero or more
      \s*
      (?:,|or)                ## separator: ",", "or"
      \s*
      \b{PAT_MAJOR}\b
      (?:\s+major)?           ## optional "major" after each later code
    )*
    \.?                       ## optional period at the end
  $
  ''', re.IGNORECASE | re.VERBOSE)
  
  ## STANDING (SEPARATOR STANDING)* standing (or higher)?
  re_standing = re.compile(r'''
  ^
    \bU[1-4]\b                  ## first standing, e.g. U3
    (?:                         ## zero or more additional standings 
      \s*
      (?:,|or|and)              ## separator: ",", "or", or "and"
      \s*
      \bU[1-4]\b
    )*
    \s+standing                 ## required "standing" at the end
    (?:\s+or\s+higher)?         ## optional "or higher"
  $
  ''', re.IGNORECASE | re.VERBOSE)

  re_permission = re.compile(r'''^permission\sof.*$''', re.IGNORECASE | re.VERBOSE)

  need_passed, grade_required = False, None
  pass_with_grade = lambda cid: Passed(cid, grade_required)

  for part in parts:            ## match each part with supported formats. each case is a full match
    part = part.strip()

    if m := re.fullmatch(re_grade_or_higher_prefix, part):    ## course list with c or higher prefix
      need_passed = True
      grade_required = m.group("grade").upper()  ## C, B, B+, etc.
      rest = m.group("rest")            ## rest should be a course list
      course_list_ast = parse_course_list_text(rest)
      if course_list_ast is not None:
        requirements.append(apply_requirement_recursive(course_list_ast, pass_with_grade))
      else:
        mixed_items = parse_mixed_or_list(rest)
        if mixed_items is not None:
          converted = [pass_with_grade(item) if isinstance(item, str) else item for item in mixed_items]
          requirements.append(build_node(Or, converted))
        else:
          print("unsupported course list format in parse_course_list_text:", text)
          requirements.append(UnsupportedRequirement(part))
    elif m := re.fullmatch(re_any_course_list, part): ## course list
      req = pass_with_grade if need_passed else Taken
      requirements.append(apply_requirement_recursive(parse_course_list_text(part), req))
    elif m := re.fullmatch(re_major, part):               ## major
      ### we assume the major requirement is a disjunction.
      ### therefore after the regex match, we find all the major codes and connect them with Or.
      majors = re.findall(PAT_MAJOR, part)
      requirements.append(build_node(Or, [Major(major) for major in majors]))
    elif m := re.fullmatch(re_standing, part):            ## standing
      ## case1: Ux or higher
      if m := re.fullmatch(r'^\bU(?P<at_least>[1-4])\b\s+standing\s+or\s+higher\b', part, re.IGNORECASE):
        at_least = int(m.group("at_least"))
        standings = [f'U{i}' for i in range(at_least, 5)]
        requirements.append(build_node(Or, [Standing(s) for s in standings]))
      ## case2: Ux or Uy
      elif m := re.fullmatch(r'^\bU[1-4]\b(?:\s*(?:,|or|and)\s*\bU[1-4]\b)*\s+standing\b', part, re.IGNORECASE):
        standings = re.findall(r'\bU[1-4]\b',part, re.IGNORECASE)
        requirements.append(build_node(Or, [Standing(s) for s in standings]))
      else:
        print("unsupported format for standing:", part)
        requirements.append(UnsupportedRequirement(part))
    elif m := re.fullmatch(re_permission, part):
      requirements.append(Permission(part))
    else:
      mixed_items = parse_mixed_or_list(part)
      if mixed_items is not None:
        req = pass_with_grade if need_passed else Taken
        converted = [req(item) if isinstance(item, str) else item for item in mixed_items]
        requirements.append(build_node(Or, converted))
        continue

      if USE_LLM_TO_PARSE:
        print(f"Regex failed, asking LLM to parse: '{part}'")
        try:
          llm_dict = parse_with_llm(part)
          ast_node = dict_to_ast(llm_dict)
          requirements.append(ast_node)
        except Exception as e:
          print(f"LLM failed gracefully ({e}), falling back to UnsupportedRequirement")
          requirements.append(UnsupportedRequirement(part))
      else:
        print("unsupported format for requisite part:", part)
        requirements.append(UnsupportedRequirement(part))

  return build_node(And, requirements)

def parse_course_div(course_div: BeautifulSoup) -> dict: 
  ## parse course div after preprocessing
  ## input: a course div object in beautifulsoup after cleanup
  ## output: a dictionary with course fields: id, desc, credits, grading, and requisites.
  ###        for requisites, we keep the original string as is. if it's 'Prerequisite:' in the text
  ###        then the key is 'Prerequisite'. Similiar for other requisites.
  course = {}

  children = course_div.find_all(recursive=False) ## get all tag children

  ok, res = parse_course_id_name(children[0])     ## the first tag should be the <h3> tag containing the course id and name.
  if ok: course.update(res)
  else: print("can't parse course id:", children[0])

  ok, res = parse_course_desc(children[1])        ## the second tag should be the <p> tag containing the course description.
  if ok: course.update(res)
  else: print("can't parse course desc:", children[1])

  for child in children[2:]:      ## for the rest, the order is not guaranteed as some fields are optional.
    if child.name == 'span' or child.name == 'a':
      continue ### TODO: pan and a are for sbc and partially fulfills, which we currently don't parse.
    parsers = [parse_req,         ## we try to match it with different parsers, returning the first one that works.
               parse_credits]
    
    parsed = False
    for parser in parsers:
      ok, res = parser(child)
      if ok: 
        parsed = True
        course.update(res)
        break
    if not parsed:                ## if it doesn't match any known format, print it out.
      print("can't parse:", child)

  return course

if __name__ == "__main__":
  ## test: cse 237
  print(parse_req_text("CSE 214 or CSE 230 or CSE 260; AMS 210 or MAT 211; CSE or ISE or DAS major"))

  ## test: cse 303
  print(parse_req_text("C or higher: CSE 160 or CSE 214; CSE 150 or CSE 215; CSE major"))

  ## test: cse 305
  print(parse_req_text("C or higher: CSE 214, CSE 216 or CSE 260; CSE or DAS major"))

  ## test: cse 306
  print(parse_req_text("C or higher: CSE 320 or ESE 280; CSE Major or ECE major."))

  ## test: cse 101 (unsupported format)
  print(parse_req_text("Level 3 or higher on the mathematics placement examination"))