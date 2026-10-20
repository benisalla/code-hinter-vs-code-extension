"""The LLM path, with a fake model: its output must still go through the guardrails."""
import json, os
import pytest
from llm import backend
from tests.conftest import ROOT

EX3 = [e for e in json.load(open(os.path.join(ROOT, "data", "exercises.json"))) if e["id"] == 3][0]

@pytest.fixture
def fake_llm(monkeypatch):
    replies = {}
    monkeypatch.setenv("CH_LLM_BACKEND", "smol")
    monkeypatch.setattr(backend, "chat", lambda sys_p, user_p, **kw: replies.get("next"))
    return replies

def test_llm_hint_that_leaks_the_solution_is_redacted(client, fresh_student, fake_llm):
    # level 4 with no static finding and a question: the LLM path is taken
    fake_llm["next"] = "Just write:\n    a, b = b, a + b\nand also sequence.append(a) inside the loop, good luck with that."
    h = client.post("/api/tutor/hint", json={"email": fresh_student["email"], "exercise_id": 3, "code": "", "level": 4, "question": "how?"}).json
    assert "a, b = b, a + b" not in h["hint"] and "sequence.append(a)" not in h["hint"]

def test_llm_failure_falls_back_to_rules(client, fresh_student, fake_llm):
    fake_llm["next"] = None
    h = client.post("/api/tutor/hint", json={"email": fresh_student["email"], "exercise_id": 3, "code": "", "level": 1}).json
    assert h["source"] == "rules" and h["hint"]

def test_llm_good_hint_is_used(client, fresh_student, fake_llm):
    fake_llm["next"] = "What two numbers do you need to remember at each step to get the next one?"
    h = client.post("/api/tutor/hint", json={"email": fresh_student["email"], "exercise_id": 3, "code": "", "level": 1, "question": "where do I start?"}).json
    assert h["source"] == "llm" and h["hint"] == fake_llm["next"]

def test_llm_open_answer_grading(fake_llm):
    from tutor.quiz import grade_question
    q = {"type": "open", "prompt": "p", "answer": "ref", "keywords": [["value"], ["identity", "same object"]]}
    fake_llm["next"] = "SCORE: 1\nPartly right, mention identity."
    assert grade_question(q, "it compares the values of things") == (0.5, "Partly right, mention identity.")

def test_generous_llm_grader_is_capped_by_key_ideas(fake_llm):
    from tutor.quiz import grade_question
    q = {"type": "open", "prompt": "p", "answer": "ref", "keywords": [["value"], ["identity", "same object"]]}
    fake_llm["next"] = "SCORE: 2\nPerfect."
    assert grade_question(q, "they are the same thing")[0] == 0.0
    assert grade_question(q, "== compares values, is checks identity")[0] == 1.0

def test_llm_hint_cannot_spell_out_the_fix(client, fresh_student, fake_llm):
    fake_llm["next"] = "Look at line 2. Use `b == 0` there instead of `=`. Then it works. Extra sentence. Another one."
    h = client.post("/api/tutor/hint", json={"email": fresh_student["email"], "exercise_id": 4, "code": "if b = 0:\n    pass", "level": 3, "question": "what is wrong?"}).json
    assert "b == 0" not in h["hint"] and "`=`" in h["hint"]
    assert h["hint"].count(".") <= 4

def test_concepts_are_taught_from_the_curated_bank(client, fresh_student, fake_llm):
    fake_llm["next"] = "A class variable belongs to each instance separately, like a personal diary of every object."
    h = client.post("/api/tutor/hint", json={"email": fresh_student["email"], "exercise_id": 3, "code": "", "level": 2}).json
    assert h["source"] == "rules"
    e = client.post("/api/tutor/explain", json={"email": fresh_student["email"], "concept": "Usage of class variables"}).json
    assert e["source"] == "rules" and "personal diary" not in e["explanation"]
    e = client.post("/api/tutor/explain", json={"email": fresh_student["email"], "concept": "Bit manipulation tricks"}).json
    assert e["source"] == "llm"

def test_llm_generated_question_is_parsed(fake_llm):
    from tutor.quiz import _llm_question
    fake_llm["next"] = "QUESTION: What is 2**3?\nA) 6\nB) 8\nC) 9\nD) 5\nANSWER: B\nEXPLANATION: power."
    q = _llm_question({"label": "Powers", "key": "powers", "topic": "general"}, 1)
    assert q["choices"][q["answer"]] == "8"
    fake_llm["next"] = "garbage"
    assert _llm_question({"label": "Powers", "key": "powers", "topic": "general"}, 1) is None


def test_precise_rule_hint_wins_over_the_llm(client, fresh_student, fake_llm):
    fake_llm["next"] = "Use the equality operator `=` to compare values directly, it is easy."
    h = client.post("/api/tutor/hint", json={"email": fresh_student["email"], "exercise_id": 4, "code": "def d(a, b):\n    if b = 0:\n        return 0\n", "level": 3}).json
    assert h["source"] == "rules" and h["line"] == 2
