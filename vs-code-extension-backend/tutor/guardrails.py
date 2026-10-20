"""
The tutor must give hints, never the solution. This module removes anything in a
generated hint that reproduces the professor's reference code (or writes code the
student has not written yet beyond a tiny illustration).
"""
import re
from difflib import SequenceMatcher

_FENCE = re.compile(r'```[a-zA-Z0-9_+-]*\n?(.*?)```', re.S)
REDACTED = "… (this part is yours to write)"

def _norm(line):
    return re.sub(r'\s+', '', line)

def _reference_lines(reference_code, student_code):
    student = {_norm(l) for l in (student_code or "").splitlines()}
    return [n for n in (_norm(l) for l in (reference_code or "").splitlines()) if len(n) >= 8 and n not in student]

def leaks(line, ref_lines, threshold=0.85):
    n = _norm(line)
    if len(n) < 8:
        return False
    return any(r in n or SequenceMatcher(None, n, r).ratio() >= threshold for r in ref_lines)

_INLINE = re.compile(r'`([^`\n]+)`')
_IDENT_OR_OP = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_.]*(\(\))?|[^A-Za-z0-9\s]{1,3})\s*$')
_HEADING = re.compile(r'^\s*#{1,6}\s')

def _strip_unwritten_code(text, student_code):
    """Inline code is fine for names and single operators (`self`, `==`) or for what
    the student already wrote; any other expression could be the fix, so it goes."""
    student = _norm(student_code or "")
    def repl(m):
        span = m.group(1)
        if _IDENT_OR_OP.match(span) or _norm(span) in student:
            return m.group(0)
        return "`…`"
    return _INLINE.sub(repl, text)

def _first_sentences(text, n):
    # drop anything after a markdown heading (small models append "### Next level" essays)
    kept = []
    for line in text.splitlines():
        if _HEADING.match(line):
            break
        kept.append(line)
    units = []
    for line in kept:
        line = re.sub(r'^\s*\*\*[^*]{1,30}:\*\*\s*', '', line).strip()   # "**Hint:**" style labels
        if line:
            units += [u for u in re.split(r'(?<=[.!?])\s+(?=[A-Z`(])', line) if u.strip()]
    return " ".join(units[:n]).strip()

def sanitize_llm_hint(text, reference_code="", student_code="", max_sentences=3):
    """Stricter pass for model-written hints: no code blocks, no unwritten expressions,
    short, then the reference-code check of sanitize_hint."""
    if not text:
        return ""
    text = _FENCE.sub("", text)
    text = _strip_unwritten_code(text, student_code)
    text = _first_sentences(text, max_sentences)
    return sanitize_hint(text, reference_code, student_code, max_code_lines=0)

def sanitize_hint(text, reference_code="", student_code="", max_code_lines=0, max_words=160):
    """max_code_lines=0 removes every code block; >0 keeps short illustrative blocks."""
    if not text:
        return ""
    ref_lines = _reference_lines(reference_code, student_code)

    def _fence(match):
        body = match.group(1).strip("\n")
        lines = body.splitlines()
        if max_code_lines == 0 or len(lines) > max_code_lines:
            return "(code removed: try writing it yourself)"
        return "```python\n" + "\n".join(REDACTED if leaks(l, ref_lines) else l for l in lines) + "\n```"

    text = _FENCE.sub(_fence, text)
    out = []
    for line in text.splitlines():
        out.append(REDACTED if leaks(line, ref_lines) and "```" not in line else line)
    text = "\n".join(out).strip()

    words = text.split(" ")
    if len(words) > max_words:
        text = " ".join(words[:max_words]).rstrip() + " …"
    return text
