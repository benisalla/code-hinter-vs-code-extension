"""
Static checks on the student's code. They locate *where* a problem is and *which
concept* it belongs to; they never produce the corrected code.
"""
import ast

def _finding(topic, line, message):
    return {"topic": topic, "line": line, "message": message}

def _syntax_finding(err, code):
    line = err.lineno or 1
    lines = code.splitlines()
    text = lines[line - 1] if 0 < line <= len(lines) else ""
    stripped = text.strip()
    msg = (err.msg or "").lower()
    if stripped.startswith(("if ", "elif ", "while ")) and ("'=='" in msg or "maybe you meant" in msg or "invalid syntax" in msg) and "=" in stripped and "==" not in stripped:
        return _finding("comparison", line, f"Line {line}: look closely at the operator in this condition. Is it asking a question or storing a value?")
    if stripped.startswith("def (") or stripped.startswith("def("):
        return _finding("constructor", line, f"Line {line}: this `def` has no name. Which special method is meant to run when an object is created?")
    if "indent" in msg:
        return _finding("syntax", line, f"Line {line}: Python is unhappy with the indentation here. Which block does this line belong to?")
    if "expected ':'" in msg or (stripped.startswith(("def ", "class ", "if ", "for ", "while ", "elif ", "else", "try", "except")) and not stripped.endswith(":")):
        return _finding("syntax", line, f"Line {line}: a block opener needs something at the end of the line. What is missing?")
    return _finding("syntax", line, f"Line {line}: Python cannot read this line ({err.msg}). Check this line and the one just above it.")

class _Visitor(ast.NodeVisitor):
    def __init__(self):
        self.findings = []
        self.defined_funcs = {}
        self.called = set()

    def visit_ClassDef(self, node):
        class_vars = {t.id for stmt in node.body if isinstance(stmt, (ast.Assign, ast.AnnAssign))
                      for t in (stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]) if isinstance(t, ast.Name)}
        methods = [s for s in node.body if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))]
        names = {m.name for m in methods}
        for m in methods:
            if m.name.lower() in ("init", "_init_", "__init", "init__", "__int__", "constructor"):
                self.findings.append(_finding("constructor", m.lineno, f"Line {m.lineno}: method `{m.name}` looks like a constructor, but Python only calls one exact name automatically. Is this spelled the way Python expects?"))
            args = m.args.args
            if not any(isinstance(d, ast.Name) and d.id in ("staticmethod", "classmethod") for d in m.decorator_list) and (not args or args[0].arg != "self"):
                self.findings.append(_finding("methods", m.lineno, f"Line {m.lineno}: what does Python pass automatically as the first argument when `{m.name}` is called on an object?"))
            for sub in ast.walk(m):
                if isinstance(sub, ast.AugAssign) and isinstance(sub.target, ast.Attribute) and isinstance(sub.target.value, ast.Name) \
                        and sub.target.value.id == node.name and sub.target.attr not in class_vars:
                    self.findings.append(_finding("class_variables", sub.lineno, f"Line {sub.lineno}: `{node.name}.{sub.target.attr}` is updated here, but where does it get its first value?"))
        if "__init__" not in names and any(isinstance(s, ast.Attribute) and isinstance(s.ctx, ast.Load) and isinstance(s.value, ast.Name) and s.value.id == "self"
                                           for m in methods for s in ast.walk(m)) and not any(isinstance(s, ast.Attribute) and isinstance(s.ctx, ast.Store) for m in methods for s in ast.walk(m)):
            self.findings.append(_finding("constructor", node.lineno, f"Line {node.lineno}: methods of `{node.name}` read data from `self`, but which method stores that data when the object is created?"))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.defined_funcs.setdefault(node.name, node.lineno)
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.findings.append(_finding("functions", node.lineno, f"Line {node.lineno}: a default argument here is a mutable container. When is a default value created: once, or at every call?"))
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.called.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.called.add(node.func.attr)
        self.generic_visit(node)

    def visit_While(self, node):
        if isinstance(node.test, ast.Constant) and node.test.value is True and not any(isinstance(s, (ast.Break, ast.Return)) for s in ast.walk(node)):
            self.findings.append(_finding("loops", node.lineno, f"Line {node.lineno}: this loop repeats forever. What should make it stop?"))
        self.generic_visit(node)

    def visit_Compare(self, node):
        for op, right in zip(node.ops, node.comparators):
            if isinstance(op, (ast.Is, ast.IsNot)) and isinstance(right, ast.Constant) and right.value is not None and not isinstance(right.value, bool):
                self.findings.append(_finding("comparison", node.lineno, f"Line {node.lineno}: `is` checks if two things are the same object. Is that really the question you want to ask here?"))
        self.generic_visit(node)

def analyze(code):
    """Returns {"syntax_error": finding|None, "findings": [finding, ...]}."""
    code = code or ""
    try:
        tree = ast.parse(code)
    except SyntaxError as err:
        return {"syntax_error": _syntax_finding(err, code), "findings": []}
    v = _Visitor()
    v.visit(tree)
    for name, line in v.defined_funcs.items():
        if name not in v.called and not name.startswith("__") and not name.startswith("test"):
            # methods are often called from outside the file; only flag top-level functions
            if any(isinstance(n, ast.FunctionDef) and n.name == name for n in tree.body):
                v.findings.append(_finding("functions", line, f"Line {line}: `{name}` is defined, but is it ever called? How would you check what it returns?"))
    return {"syntax_error": None, "findings": v.findings}

def evaluate_offline(concepts, code):
    """Rule-based stand-in for the LLM evaluation, same "[nbr]) yes/no, explanation" format."""
    result = analyze(code)
    issues = ([result["syntax_error"]] if result["syntax_error"] else []) + result["findings"]
    lines = []
    for i, c in enumerate(concepts, 1):
        hit = next((f for f in issues if f["topic"] == c["topic"]), None)
        if result["syntax_error"] and not hit:
            lines.append(f"{i}) no, code does not run yet (syntax error)")
        elif hit:
            lines.append(f"{i}) no, check line {hit['line']}")
        else:
            lines.append(f"{i}) yes, no problem detected")
    return "\n".join(lines)

def similarity_score(reference, code):
    from difflib import SequenceMatcher
    return round(100 * SequenceMatcher(None, reference or "", code or "").ratio())
