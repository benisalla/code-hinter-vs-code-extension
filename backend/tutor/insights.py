"""
What the student (and the professor) can see about learning progress.
The tutor "replaces the teacher but not 100%": it tracks every concept and
surfaces who is struggling with what, so the professor knows where to step in.
"""
from crud import exercise_crud, stud_exe_crud, stud_prof_crud, learner_crud, student_crud
from tutor import learner
from tutor.concepts import exercise_concepts

READY_MASTERY = 0.6

def course_exercises(student_id):
    """Exercises of the student's professors plus any exercise they are assigned to."""
    prof_ids = {str(a["prof_id"]) for a in stud_prof_crud.get_all_stud_prof() if str(a.get("student_id")) == str(student_id)}
    assigned = {str(a["exercise_id"]) for a in stud_exe_crud.get_associations_by_student_id(student_id)}
    return [e for e in exercise_crud.get_all_exercises() if str(e.get("id_prof")) in prof_ids or str(e["id"]) in assigned]

def course_concepts(student_id):
    concepts = {}
    for e in course_exercises(student_id):
        for c in exercise_concepts(e):
            concepts.setdefault(c["key"], c)
    return list(concepts.values())

def concept_view(profile, concept):
    rec = learner.concept_record(profile, concept)
    return {"key": concept["key"], "label": concept["label"], "topic": concept["topic"],
            "exercise_id": concept.get("exercise_id"), "mastery": rec["mastery"], "status": learner.status(rec),
            "evidence": rec["evidence"], "hints": rec["hints"]}

def readiness(profile, exercise):
    views = [concept_view(profile, c) for c in exercise_concepts(exercise)]
    missing = [v for v in views if v["status"] == "not_started" or v["mastery"] < READY_MASTERY]
    return {"exercise_id": exercise["id"], "ready": not missing, "concepts": views,
            "missing": [v["label"] for v in missing],
            "message": "You have shown you understand every concept of this exercise." if not missing else
                       "Before your final submission, make sure you understand: " + ", ".join(v["label"] for v in missing) + ". Try \"Test me\" on this exercise."}

def progress(profile, student_id, current_exercise=None):
    views = [concept_view(profile, c) for c in course_concepts(student_id)]
    counts = {s: sum(v["status"] == s for v in views) for s in ("mastered", "almost", "learning", "not_started")}
    weakest = sorted([v for v in views if v["status"] != "mastered"], key=lambda v: (v["status"] != "not_started", v["mastery"]))
    recs = []
    for v in weakest[:3]:
        if v["status"] == "not_started":
            recs.append({"concept": v["label"], "key": v["key"], "action": "test", "text": f"You have not been tested on \"{v['label']}\" yet."})
        else:
            recs.append({"concept": v["label"], "key": v["key"], "action": "explain", "text": f"\"{v['label']}\" is not solid yet ({round(v['mastery'] * 100)}%). Ask for an explanation, then test yourself again."})
    exercise = exercise_crud.get_exercise_by_id(current_exercise) if current_exercise else None
    return {
        "email": profile["email"], "level": profile["level"], "effective_level": learner.effective_level(profile),
        "style": profile["style"], "concepts": views, "counts": counts,
        "coverage": round(100 * counts["mastered"] / len(views)) if views else 0,
        "quiz_history": profile["quiz_history"][-10:],
        "hints_used": sum(r["hints"] for r in profile["concepts"].values()),
        "recommendations": recs,
        "readiness": readiness(profile, exercise) if exercise else None,
    }

def class_insights(prof_id):
    student_ids = [a["student_id"] for a in stud_prof_crud.get_all_stud_prof() if str(a.get("prof_id")) == str(prof_id)]
    profiles = {str(p.get("student_id")): p for p in learner_crud.get_all_profiles()}
    concepts = {}
    for e in exercise_crud.get_exercises_by_prof_id(prof_id):
        for c in exercise_concepts(e):
            concepts.setdefault(c["key"], c)
    concept_rows = []
    for c in concepts.values():
        recs = [p["concepts"][c["key"]] for p in profiles.values() if c["key"] in p["concepts"] and p["concepts"][c["key"]]["evidence"] > 0]
        concept_rows.append({"key": c["key"], "label": c["label"], "students_assessed": len(recs),
                             "avg_mastery": round(sum(r["mastery"] for r in recs) / len(recs), 3) if recs else None,
                             "struggling": sum(r["mastery"] < 0.5 for r in recs),
                             "hints": sum(r["hints"] for r in recs)})
    students = []
    for sid in student_ids:
        s = student_crud.get_student_by_id(sid) or {}
        p = profiles.get(str(sid))
        recs = [r for r in (p or {}).get("concepts", {}).values() if r["evidence"] > 0]
        students.append({"student_id": sid, "name": s.get("name"), "email": s.get("email"),
                         "level": learner.effective_level(p) if p else None,
                         "avg_mastery": round(sum(r["mastery"] for r in recs) / len(recs), 3) if recs else None,
                         "quizzes": len((p or {}).get("quiz_history", [])),
                         "hints": sum(r["hints"] for r in (p or {}).get("concepts", {}).values())})
    concept_rows.sort(key=lambda r: (r["avg_mastery"] is None, r["avg_mastery"] if r["avg_mastery"] is not None else 1))
    return {"prof_id": prof_id, "concepts": concept_rows, "students": students,
            "needs_attention": [s for s in students if s["avg_mastery"] is not None and s["avg_mastery"] < 0.4],
            "open_help_requests": learner_crud.get_help_requests(prof_id=prof_id, status="open")}
