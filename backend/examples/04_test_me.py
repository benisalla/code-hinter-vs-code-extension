"""04: "Test me". A quiz over every concept of the exercise; we answer half the questions
right and show the graded result, per-concept mastery before/after and the next step."""
from _demo import client, show, EMAIL
from crud.learner_crud import get_quiz

c = client()
quiz = c.post("/api/tutor/quiz", json={"email": EMAIL, "scope": "exercise", "exercise_id": 2}).json
show(f"quiz {quiz['id']}: {len(quiz['questions'])} questions (answers stay on the server)")
for i, q in enumerate(quiz["questions"], 1):
    print(f"{i}. [{q['concept']} | {q['type']} | difficulty {q['difficulty']}] {q['prompt']}")
    if q.get("code"):
        print("   " + q["code"].replace("\n", "\n   "))
    for j, choice in enumerate(q.get("choices") or []):
        print(f"   {j}) {choice}")

answers = {}
for i, q in enumerate(get_quiz(quiz["id"])["questions"]):
    right = i % 2 == 0
    if q["type"] == "mcq":
        answers[q["qid"]] = q["answer"] if right else (q["answer"] + 1) % len(q["choices"])
    else:
        answers[q["qid"]] = q["answer"] if right else "I am not sure"
r = c.post(f"/api/tutor/quiz/{quiz['id']}/submit", json={"email": EMAIL, "answers": answers}).json
show(f"score {r['score']}%")
for c_ in r["concepts"]:
    print(f"- {c_['concept']}: {c_['mastery_before']:.2f} -> {c_['mastery_after']:.2f} ({c_['status']})")
for res in r["results"]:
    if not res["correct"]:
        print(f"\n x {res['prompt']}\n   expected: {res['expected']}\n   why: {res['explanation']}\n   review:\n{res['review']}")
show("next step", r["next_step"])
