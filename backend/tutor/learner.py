"""
The learner model: what the tutor believes the student understands.

Every concept the professor lists gets a mastery value in [0, 1] that moves with
evidence: quiz answers (strong signal), professor-criteria evaluations (medium)
and hint requests (weak, negative). The student's effective level is derived
from that evidence once there is enough of it, so the tutor follows the student
instead of trusting a one-time self-assessment.
"""
from crud.learner_crud import now
from tutor.knowledge import LEVELS

PRIOR = {"beginner": 0.2, "intermediate": 0.4, "advanced": 0.6}
MIN_EVIDENCE_FOR_LEVEL = 6
MAX_EVENTS = 300

def concept_record(profile, concept):
    rec = profile["concepts"].get(concept["key"])
    if rec is None:
        rec = {"label": concept["label"], "topic": concept["topic"], "mastery": PRIOR.get(profile["level"], 0.2),
               "evidence": 0, "correct": 0, "wrong": 0, "hints": 0, "last_seen": None}
        profile["concepts"][concept["key"]] = rec
    return rec

def _clip(x):
    return max(0.0, min(1.0, x))

def record_answer(profile, concept, correct, difficulty=1, weight=1.0):
    """Quiz answer. Harder questions move mastery more; partial credit is a float in [0, 1]."""
    rec = concept_record(profile, concept)
    credit = float(correct)
    step = (0.15 + 0.07 * difficulty) * weight
    m = rec["mastery"]
    rec["mastery"] = round(_clip(m + step * (credit - m) if credit >= 0.5 else m - step * m * (1 - credit)), 3)
    rec["evidence"] += 1
    rec["correct" if credit >= 0.5 else "wrong"] += 1
    rec["last_seen"] = now()
    return rec

def record_evaluation(profile, concept, satisfied):
    return record_answer(profile, concept, 1.0 if satisfied else 0.0, difficulty=1, weight=0.6)

def record_hint(profile, concept, hint_level):
    rec = concept_record(profile, concept)
    rec["hints"] += 1
    rec["mastery"] = round(_clip(rec["mastery"] - 0.02 * hint_level), 3)
    rec["last_seen"] = now()
    return rec

def log_event(profile, kind, **data):
    profile["events"].append({"kind": kind, "at": now(), **data})
    del profile["events"][:-MAX_EVENTS]

def status(rec):
    if rec["evidence"] == 0:
        return "not_started"
    if rec["mastery"] >= 0.8:
        return "mastered"
    if rec["mastery"] >= 0.5:
        return "almost"
    return "learning"

def effective_level(profile):
    recs = [r for r in profile["concepts"].values() if r["evidence"] > 0]
    if sum(r["evidence"] for r in recs) < MIN_EVIDENCE_FOR_LEVEL:
        return profile["level"]
    avg = sum(r["mastery"] for r in recs) / len(recs)
    return "advanced" if avg >= 0.75 else "intermediate" if avg >= 0.45 else "beginner"

def target_difficulty(profile, rec):
    """1..3: the question difficulty that stretches this student on this concept."""
    base = LEVELS.index(effective_level(profile))   # 0..2
    if rec["mastery"] < 0.35:
        base -= 1
    elif rec["mastery"] >= 0.75:
        base += 1
    return max(1, min(3, base + 1))
