from tutor.knowledge import TOPICS, LEVELS
from tutor.quiz import run_snippet

def test_every_topic_is_complete():
    for name, t in TOPICS.items():
        for field in ("title", "explain", "analogy", "example", "steps", "socratic", "pitfalls", "questions"):
            assert t[field], f"{name} has no {field}"
        assert set(LEVELS) <= set(t["explain"]), name

def test_every_question_is_valid_and_every_snippet_runs():
    n = 0
    for name, t in TOPICS.items():
        for q in t["questions"]:
            assert q["type"] in ("mcq", "output", "open") and q["difficulty"] in (1, 2, 3)
            if q["type"] == "mcq":
                assert 0 <= q["answer"] < len(q["choices"]) and len(set(q["choices"])) == len(q["choices"])
            if q["type"] == "output":
                out = run_snippet(q["code"])
                assert out and not out.startswith("Error"), (name, q["code"], out)
            if q["type"] == "open":
                assert q["keywords"]
            n += 1
    assert n >= 50

def test_examples_run():
    for name, t in TOPICS.items():
        out = run_snippet(t["example"])
        assert not out.startswith("Error"), (name, out)
