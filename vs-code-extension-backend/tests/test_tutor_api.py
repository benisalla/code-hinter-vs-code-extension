import json, os
from tests.conftest import ROOT
from tutor.guardrails import _norm

EXERCISES = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "data", "exercises.json")))}

def _hint(client, email, exercise_id, code, **kw):
    r = client.post("/api/tutor/hint", json={"email": email, "exercise_id": exercise_id, "code": code, **kw})
    assert r.status_code == 200, r.json
    return r.json

# ---------------------------------------------------------------- profile

def test_profile_defaults_and_update(client, student):
    r = client.get("/api/tutor/profile", query_string={"email": student["email"]})
    assert r.status_code == 200 and r.json["level"] in ("beginner", "intermediate", "advanced")
    r = client.put("/api/tutor/profile", json={"email": student["email"], "level": "intermediate", "style": "analogies"})
    assert r.json["style"] == "analogies" and r.json["onboarded"]
    assert client.put("/api/tutor/profile", json={"email": student["email"], "style": "telepathy"}).status_code == 400
    assert client.get("/api/tutor/profile", query_string={"email": "nobody@x.com"}).status_code == 404

# ------------------------------------------------------------------ hints

def test_hint_ladder_escalates_then_suggests_the_professor(client, fresh_student):
    email, code = fresh_student["email"], EXERCISES[4]["code_prof"]
    levels = [_hint(client, email, 4, code)["level"] for _ in range(5)]
    assert levels == [1, 2, 3, 4, 4]
    last = _hint(client, email, 4, code)
    assert last["escalate"] and last["escalate_message"]
    assert last["concept"] == "Intentional error identification: using assignment instead of comparison"

def test_pinpoint_hint_names_the_line_not_the_fix(client, fresh_student):
    h = _hint(client, fresh_student["email"], 4, EXERCISES[4]["code_prof"], level=3)
    assert "Line 2" in h["hint"] and "==" not in h["hint"] and h["line"] == 2

def test_more_resets_and_requested_level(client, fresh_student):
    email = fresh_student["email"]
    assert _hint(client, email, 3, "def f(n):\n    pass\n", level=2)["level"] == 2
    assert _hint(client, email, 3, "def f(n):\n    pass\n", more=True)["level"] == 3

def test_hints_never_leak_the_reference_solution(client, fresh_student):
    for style in ("examples", "analogies", "step_by_step", "socratic"):
        client.put("/api/tutor/profile", json={"email": fresh_student["email"], "style": style})
        for ex_id, ex in EXERCISES.items():
            ref = [_norm(l) for l in ex["code_prof"].splitlines() if len(_norm(l)) >= 8]
            for level in (1, 2, 3, 4):
                h = _hint(client, fresh_student["email"], ex_id, "", level=level)["hint"]
                for line in h.splitlines():
                    assert not any(r in _norm(line) for r in ref), (style, ex_id, level, line)

def test_hint_follows_learning_style(client, fresh_student):
    email = fresh_student["email"]
    client.put("/api/tutor/profile", json={"email": email, "style": "analogies"})
    a = _hint(client, email, 3, "", level=2)["hint"]
    client.put("/api/tutor/profile", json={"email": email, "style": "step_by_step"})
    s = _hint(client, email, 3, "", level=2)["hint"]
    assert a != s and "1." in s

def test_explain_concept(client, student):
    r = client.post("/api/tutor/explain", json={"email": student["email"], "concept": "Usage of class variables", "exercise_id": 2})
    assert r.status_code == 200 and r.json["topic"] == "class_variables" and "Check yourself" in r.json["explanation"]

# ---------------------------------------------------------------- Test me

def _perfect_answers(quiz_id):
    from crud.learner_crud import get_quiz
    return {q["qid"]: (q["answer"] if q["type"] != "open" else q["answer"]) for q in get_quiz(quiz_id)["questions"]}

def _wrong_answers(quiz_id):
    from crud.learner_crud import get_quiz
    return {q["qid"]: ((q["answer"] + 1) % len(q["choices"]) if q["type"] == "mcq" else "no idea") for q in get_quiz(quiz_id)["questions"]}

def test_quiz_covers_every_concept_and_hides_answers(client, fresh_student):
    r = client.post("/api/tutor/quiz", json={"email": fresh_student["email"], "scope": "exercise", "exercise_id": 3})
    assert r.status_code == 201
    quiz = r.json
    assert {q["concept"] for q in quiz["questions"]} == {"Function definition", "Looping and list operations", "Fibonacci sequence calculation"}
    assert all("answer" not in q and "explanation" not in q for q in quiz["questions"])
    assert len({q["qid"] for q in quiz["questions"]}) == len(quiz["questions"])

def test_course_quiz_covers_everything_the_professor_taught(client, fresh_student):
    quiz = client.post("/api/tutor/quiz", json={"email": fresh_student["email"], "scope": "course"}).json
    labels = {q["concept"] for q in quiz["questions"]}
    for ex_id in (3, 4):  # professor 2's exercises
        for line in EXERCISES[ex_id]["concepts"].splitlines():
            assert line.split(". ", 1)[1] in labels

def test_perfect_quiz_raises_mastery_and_level(client, fresh_student):
    email = fresh_student["email"]
    for _ in range(3):
        quiz = client.post("/api/tutor/quiz", json={"email": email, "scope": "course"}).json
        res = client.post(f"/api/tutor/quiz/{quiz['id']}/submit", json={"email": email, "answers": _perfect_answers(quiz["id"])}).json
        assert res["score"] == 100
        assert all(c["mastery_after"] >= c["mastery_before"] for c in res["concepts"])
    prof = client.get("/api/tutor/profile", query_string={"email": email}).json
    assert prof["effective_level"] in ("intermediate", "advanced")
    ready = client.get("/api/tutor/readiness", query_string={"email": email, "exercise_id": 3}).json
    assert ready["ready"]

def test_wrong_quiz_lowers_mastery_and_reteaches_in_style(client, fresh_student):
    email = fresh_student["email"]
    client.put("/api/tutor/profile", json={"email": email, "level": "intermediate", "style": "analogies"})
    quiz = client.post("/api/tutor/quiz", json={"email": email, "scope": "exercise", "exercise_id": 4}).json
    res = client.post(f"/api/tutor/quiz/{quiz['id']}/submit", json={"email": email, "answers": _wrong_answers(quiz["id"])}).json
    assert res["score"] == 0
    assert all(c["mastery_after"] < c["mastery_before"] for c in res["concepts"])
    assert all(r["review"] and r["expected"] is not None for r in res["results"])
    assert "Review" in res["next_step"]
    # resubmitting the same quiz is refused
    assert client.post(f"/api/tutor/quiz/{quiz['id']}/submit", json={"email": email, "answers": {}}).status_code == 400

def test_weak_scope_targets_unmastered_concepts(client, fresh_student):
    email = fresh_student["email"]
    quiz = client.post("/api/tutor/quiz", json={"email": email, "scope": "exercise", "exercise_id": 3}).json
    for _ in range(3):
        quiz = client.post("/api/tutor/quiz", json={"email": email, "scope": "exercise", "exercise_id": 3}).json
        client.post(f"/api/tutor/quiz/{quiz['id']}/submit", json={"email": email, "answers": _perfect_answers(quiz["id"])})
    weak = client.post("/api/tutor/quiz", json={"email": email, "scope": "weak"}).json
    assert {q["concept"] for q in weak["questions"]} <= {"Conditional statement errors", "Intentional error identification: using assignment instead of comparison", "Proper operator usage in conditions"}

def test_quiz_needs_a_valid_scope(client, student):
    assert client.post("/api/tutor/quiz", json={"email": student["email"], "scope": "galaxy"}).status_code == 400

# ------------------------------------------------- evaluation, progress, professor

def test_offline_evaluation_feeds_the_learner_model(client, fresh_student):
    r = client.post("/api/evaluate_code", json={"email": fresh_student["email"], "exercise_id": 4, "code": EXERCISES[4]["code_prof"]})
    assert r.status_code == 200
    verdicts = {c["concept"]: c["satisfied"] for c in r.json["concepts"]}
    assert verdicts["Intentional error identification: using assignment instead of comparison"] is False

def test_progress_and_recommendations(client, fresh_student):
    p = client.get("/api/tutor/progress", query_string={"email": fresh_student["email"], "exercise_id": 3}).json
    assert len(p["concepts"]) == 6 and p["counts"]["not_started"] == 6
    assert p["recommendations"] and p["readiness"]["ready"] is False

def test_help_request_reaches_the_professor(client, fresh_student):
    r = client.post("/api/tutor/help_request", json={"email": fresh_student["email"], "exercise_id": 3, "message": "I don't get the swap", "code": "a = b"})
    assert r.status_code == 201 and r.json["prof_id"] == 2
    insights = client.get("/api/tutor/class/2").json
    assert any(h["id"] == r.json["id"] for h in insights["open_help_requests"])
    assert any(s["email"] == fresh_student["email"] for s in insights["students"])
    client.put(f"/api/tutor/help_request/{r.json['id']}", json={"reply": "Come see me Monday"})
    mine = client.get("/api/tutor/help_requests", query_string={"email": fresh_student["email"]}).json
    assert mine[-1]["status"] == "resolved" and mine[-1]["reply"]

def test_beginner_gets_easy_questions_and_advanced_harder_ones(client, fresh_student):
    from crud import student_crud, stud_prof_crud
    email = fresh_student["email"]
    client.put("/api/tutor/profile", json={"email": email, "level": "beginner"})
    easy = client.post("/api/tutor/quiz", json={"email": email, "scope": "course"}).json
    other = student_crud.create_student({"name": "Adv", "password": "p", "email": email.replace("t-", "adv-")})
    stud_prof_crud.create_stud_prof({"student_id": other["id"], "prof_id": 2})
    client.put("/api/tutor/profile", json={"email": other["email"], "level": "advanced"})
    hard = client.post("/api/tutor/quiz", json={"email": other["email"], "scope": "course"}).json
    mean = lambda quiz: sum(q["difficulty"] for q in quiz["questions"]) / len(quiz["questions"])
    assert mean(easy) < 1.5 < mean(hard)
