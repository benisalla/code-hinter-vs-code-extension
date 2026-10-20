"""06: does the learner model really follow the student?

60 simulated students of professor 2 (6 concepts) each have a hidden probability of
knowing every concept. They take four "Test me" quizzes (course scope). A student who
knows a concept answers right; one who does not guesses (1/n_choices on MCQs, wrong
otherwise). We then compare the tutor's mastery estimates with the hidden truth.

Metrics written to examples/output/simulated_students.json:
  - Pearson r between estimated mastery and true knowledge
  - accuracy of "knows it" (true >= 0.5) vs "mastery >= 0.5"
  - level accuracy (effective level vs level implied by the true average)
"""
import json
import os
import random
from _demo import client, show, OUTPUT
from crud import student_crud, stud_prof_crud
from crud.learner_crud import get_quiz, get_profile

random.seed(0)
c = client()
N_STUDENTS, N_QUIZZES = 60, 4

def level_of(avg):
    return "advanced" if avg >= 0.75 else "intermediate" if avg >= 0.45 else "beginner"

pairs, level_hits, history = [], 0, []
for i in range(N_STUDENTS):
    s = student_crud.create_student({"name": f"sim{i}", "password": "x", "email": f"sim{i}@example.com"})
    stud_prof_crud.create_stud_prof({"student_id": s["id"], "prof_id": 2})
    ability = random.random()
    truth = {}
    for _ in range(N_QUIZZES):
        quiz = c.post("/api/tutor/quiz", json={"email": s["email"], "scope": "course"}).json
        answers = {}
        for q in get_quiz(quiz["id"])["questions"]:
            p_know = truth.setdefault(q["concept_key"], min(1, max(0, random.gauss(ability, 0.2))))
            knows = random.random() < p_know
            if q["type"] == "mcq":
                answers[q["qid"]] = q["answer"] if knows else random.randrange(len(q["choices"]))
            else:
                answers[q["qid"]] = q["answer"] if knows else "no idea"
        r = c.post(f"/api/tutor/quiz/{quiz['id']}/submit", json={"email": s["email"], "answers": answers}).json
        history.append(r["score"])
    profile = get_profile(s["email"])
    for key, p_true in truth.items():
        pairs.append((profile["concepts"][key]["mastery"], p_true))
    level_hits += c.get("/api/tutor/profile", query_string={"email": s["email"]}).json["effective_level"] == level_of(sum(truth.values()) / len(truth))

est, true = zip(*pairs)
me, mt = sum(est) / len(est), sum(true) / len(true)
cov = sum((e - me) * (t - mt) for e, t in pairs)
r = cov / ((sum((e - me) ** 2 for e in est) * sum((t - mt) ** 2 for t in true)) ** 0.5)
acc = sum((e >= 0.5) == (t >= 0.5) for e, t in pairs) / len(pairs)
metrics = {"students": N_STUDENTS, "quizzes_each": N_QUIZZES, "concept_estimates": len(pairs),
           "pearson_r_mastery_vs_truth": round(r, 3), "knows_it_accuracy": round(acc, 3),
           "level_accuracy": round(level_hits / N_STUDENTS, 3)}
show("learner-model tracking metrics", json.dumps(metrics, indent=2))
with open(os.path.join(OUTPUT, "simulated_students.json"), "w") as f:
    json.dump(metrics, f, indent=2)
