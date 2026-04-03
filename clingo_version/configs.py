from pathlib import Path

# Repository root directory (this file lives at repo root)
ROOT = Path(__file__).resolve().parents[1]

def root_path(*parts: str) -> Path:
    return ROOT.joinpath(*parts)

MAIN_LP = str(root_path('clingo_version', 'cse_req_clingo.lp'))
KB_LP = str(root_path('course_kb', 'kb_complete.lp'))
