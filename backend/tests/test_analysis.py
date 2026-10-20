import json, os
from tutor.code_analysis import analyze, evaluate_offline
from tutor.concepts import parse_concepts, topic_for, exercise_concepts
from tutor.guardrails import sanitize_hint, REDACTED
from tests.conftest import ROOT

EXERCISES = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "data", "exercises.json")))}

def test_parse_concepts():
    assert parse_concepts("1. Class creation\n2) Method definition\n- Loops\n\n") == ["Class creation", "Method definition", "Loops"]

def test_seed_concepts_map_to_topics():
    assert [c["topic"] for c in exercise_concepts(EXERCISES[1])] == ["classes", "methods", "classes"]
    assert [c["topic"] for c in exercise_concepts(EXERCISES[2])] == ["constructor", "methods", "class_variables"]
    assert [c["topic"] for c in exercise_concepts(EXERCISES[3])] == ["functions", "loops", "sequences"]
    assert [c["topic"] for c in exercise_concepts(EXERCISES[4])] == ["conditionals", "comparison", "comparison"]
    assert topic_for("Something unrelated") == "general"

def test_syntax_errors_are_located_and_linked_to_a_concept():
    assert analyze(EXERCISES[2]["code_prof"])["syntax_error"]["topic"] == "constructor"
    err = analyze(EXERCISES[4]["code_prof"])["syntax_error"]
    assert err["topic"] == "comparison" and err["line"] == 2

def test_ast_findings():
    found = analyze("class A:\n    def __init__(self):\n        A.n += 1\n")["findings"]
    assert found[0]["topic"] == "class_variables"
    found = analyze("class B:\n    def init(self, x):\n        self.x = x\n")["findings"]
    assert any(f["topic"] == "constructor" for f in found)
    found = analyze("while True:\n    x = 1\n")["findings"]
    assert any(f["topic"] == "loops" for f in found)

def test_findings_never_contain_the_fix():
    for e in EXERCISES.values():
        r = analyze(e["code_prof"])
        for f in ([r["syntax_error"]] if r["syntax_error"] else []) + r["findings"]:
            assert "==" not in f["message"] and "__init__" not in f["message"]

def test_offline_evaluation_format():
    out = evaluate_offline(exercise_concepts(EXERCISES[4]), EXERCISES[4]["code_prof"])
    assert out.splitlines()[1].startswith("2) no")

def test_guardrail_redacts_reference_code():
    ref = EXERCISES[3]["code_prof"]
    hint = "Try this:\n```python\ndef fibonacci(n):\n    a, b = 0, 1\n```\nAlso a, b = b, a + b is the trick."
    out = sanitize_hint(hint, ref, "", max_code_lines=0)
    assert "a, b = b, a + b" not in out and "def fibonacci" not in out
    assert REDACTED in out and "code removed" in out

def test_guardrail_keeps_lines_the_student_already_wrote():
    ref = "def fibonacci(n):\n    sequence = []\n"
    out = sanitize_hint("Your line `def fibonacci(n):` is fine.", ref, "def fibonacci(n):\n    pass")
    assert "def fibonacci(n)" in out
