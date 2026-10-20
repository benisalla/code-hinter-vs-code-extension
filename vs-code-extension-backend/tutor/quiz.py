"""
"Test me": a quiz that covers every concept the professor listed, at a difficulty
matched to how well the student currently knows each one.

  - every concept gets at least one question (nothing the professor taught is skipped)
  - extra questions go to the weakest concepts
  - difficulty per concept comes from learner.target_difficulty (level + mastery)
  - questions the student has already seen are avoided when possible
  - answers stay on the server; grading updates the learner model
"""
import random
import re
import subprocess
import sys
import uuid
from functools import lru_cache
from llm import backend
from llm.constant import GRADE_SYS_PROMPT, GRADE_PROMPT, QUESTION_SYS_PROMPT, QUESTION_PROMPT
from crud.learner_crud import now
from tutor import learner
from tutor.knowledge import topic
from tutor.teaching import style_explanation

MAX_QUESTIONS = 15
DIFFICULTY_NAMES = {1: "easy", 2: "medium", 3: "hard"}

@lru_cache(maxsize=512)
def run_snippet(code):
    """Expected output of a bank snippet (our own code, never the student's)."""
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, timeout=10)
    return out.stdout.strip() if out.returncode == 0 else ("Error: " + out.stderr.strip().splitlines()[-1])

def _norm_output(s):
    s = str(s).strip().strip('`').strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"" and s.count(s[0]) == 2:
        s = s[1:-1]
    return re.sub(r'\s+', ' ', s).strip().lower()

# ----------------------------------------------------------------- building

def _bank_question(concept, topic_name, idx, q):
    question = {"qid": f"{topic_name}-{idx}", "concept": concept["label"], "concept_key": concept["key"],
                "topic": topic_name, "type": q["type"], "difficulty": q["difficulty"], "prompt": q["prompt"],
                "code": q.get("code"), "explanation": q["explanation"]}
    if q["type"] == "mcq":
        order = list(range(len(q["choices"])))
        random.shuffle(order)
        question["choices"] = [q["choices"][i] for i in order]
        question["answer"] = order.index(q["answer"])
    elif q["type"] == "output":
        question["answer"] = run_snippet(q["code"])
    else:
        question["keywords"] = q.get("keywords", [])
        question["answer"] = q["explanation"]
    return question

def _llm_question(concept, difficulty):
    raw = backend.chat(QUESTION_SYS_PROMPT, QUESTION_PROMPT.format(difficulty=DIFFICULTY_NAMES[difficulty], concept=concept["label"]),
                       temperature=0.7, max_new_tokens=250)
    if not raw:
        return None
    m = re.search(r'QUESTION:\s*(.+?)\s*A\)\s*(.+?)\s*B\)\s*(.+?)\s*C\)\s*(.+?)\s*D\)\s*(.+?)\s*ANSWER:\s*([ABCD])\s*(?:EXPLANATION:\s*(.+))?$', raw.strip(), re.S)
    if not m:
        return None
    choices = [c.strip() for c in m.groups()[1:5]]
    if len(set(choices)) < 4:
        return None
    return {"qid": f"llm-{uuid.uuid4().hex[:8]}", "concept": concept["label"], "concept_key": concept["key"],
            "topic": concept["topic"], "type": "mcq", "difficulty": difficulty, "prompt": m.group(1).strip(),
            "code": None, "choices": choices, "answer": "ABCD".index(m.group(6)),
            "explanation": (m.group(7) or "").strip() or "Review this concept with 'Explain concept'."}

def _open_question(concept, difficulty):
    words = [w for w in re.findall(r'[a-zA-Z_]{4,}', concept["label"].lower())]
    return {"qid": f"open-{concept['key']}", "concept": concept["label"], "concept_key": concept["key"],
            "topic": concept["topic"], "type": "open", "difficulty": difficulty,
            "prompt": f"In your own words: what is \"{concept['label']}\", and why does it matter in your exercise?",
            "code": None, "keywords": [[w] for w in words[:3]] + [["example", "for instance", "e.g", "like", "when"]],
            "answer": topic(concept["topic"])["explain"]["intermediate"],
            "explanation": topic(concept["topic"])["explain"]["intermediate"]}

def _choose(profile, concept, used):
    rec = learner.concept_record(profile, concept)
    target = learner.target_difficulty(profile, rec)
    bank = topic(concept["topic"])["questions"] if concept["topic"] != "general" else []
    seen = set(profile["seen_questions"])
    candidates = [(i, q) for i, q in enumerate(bank) if f"{concept['topic']}-{i}" not in used]
    if candidates:
        # right difficulty first; a repeated question costs 1.5 levels of mismatch
        i, q = min(candidates, key=lambda iq: (abs(iq[1]["difficulty"] - target) + 1.5 * (f"{concept['topic']}-{iq[0]}" in seen), random.random()))
        return _bank_question(concept, concept["topic"], i, q)
    if backend.llm_available():
        q = _llm_question(concept, target)
        if q:
            return q
    if f"open-{concept['key']}" not in used:
        return _open_question(concept, target)
    return None

def build_quiz(profile, concepts, scope, n_questions=None):
    concepts = list({c["key"]: c for c in concepts}.values())
    if not concepts:
        raise ValueError("No concepts to test yet: your professor has not listed concepts for these exercises.")
    n = max(len(concepts), min(MAX_QUESTIONS, n_questions or len(concepts) + min(4, len(concepts))))
    weakest_first = sorted(concepts, key=lambda c: learner.concept_record(profile, c)["mastery"])
    plan = list(concepts) + [weakest_first[i % len(weakest_first)] for i in range(n - len(concepts))]

    questions, used = [], set()
    for i, concept in enumerate(plan):
        q = _choose(profile, concept, used)
        if not q:
            continue
        # coverage questions are always asked; extra ones only if they fit the student's level
        target = learner.target_difficulty(profile, learner.concept_record(profile, concept))
        if i >= len(concepts) and q["difficulty"] - target >= 2:
            continue
        used.add(q["qid"])
        questions.append(q)
    # warm up: easy questions first, random order within a difficulty
    random.shuffle(questions)
    questions.sort(key=lambda q: q["difficulty"])
    quiz = {"id": uuid.uuid4().hex[:12], "email": profile["email"], "scope": scope, "created_at": now(),
            "submitted": False, "questions": questions}
    learner.log_event(profile, "quiz_started", quiz_id=quiz["id"], scope=scope, n=len(questions))
    return quiz

def public_quiz(quiz):
    """What the student sees: no answers, no explanations, no keywords."""
    hidden = {"answer", "explanation", "keywords"}
    return {"id": quiz["id"], "scope": quiz["scope"], "created_at": quiz["created_at"],
            "questions": [{k: v for k, v in q.items() if k not in hidden} for q in quiz["questions"]]}

# ------------------------------------------------------------------ grading

def _grade_open(q, answer):
    """Returns (credit in [0,1], feedback)."""
    if not answer or len(answer.split()) < 3:
        return 0.0, "Try to explain it in a full sentence next time."
    text = answer.lower()
    groups = q.get("keywords") or []
    hit = sum(any(k in text for k in group) for group in groups)
    ratio = hit / len(groups) if groups else 0.5
    keyword_credit = 1.0 if ratio >= 0.75 else 0.5 if ratio >= 0.4 else 0.0
    if backend.llm_available():
        raw = backend.chat(GRADE_SYS_PROMPT, GRADE_PROMPT.format(question=q["prompt"], reference=q["answer"], answer=answer),
                           temperature=0.2, max_new_tokens=80)
        m = re.search(r'SCORE:\s*([012])', raw or "")
        if m:
            feedback = (raw[m.end():].strip() or "").splitlines()
            # the model may lower the grade (wrong idea with the right words) but never
            # exceed what the answer's key ideas support: small graders are too generous
            ceiling = 1.0 if ratio >= 0.5 else 0.5 if ratio > 0 else 0.0
            return min(int(m.group(1)) / 2, ceiling), (feedback[0] if feedback else "")
    return keyword_credit, ""

def grade_question(q, answer):
    if q["type"] == "mcq":
        try:
            correct = int(answer) == q["answer"]
        except (TypeError, ValueError):
            correct = False
        return (1.0 if correct else 0.0), ""
    if q["type"] == "output":
        return (1.0 if _norm_output(answer or "") == _norm_output(q["answer"]) else 0.0), ""
    return _grade_open(q, answer or "")

def grade_quiz(profile, quiz, answers):
    level_before = learner.effective_level(profile)
    before = {k: r["mastery"] for k, r in profile["concepts"].items()}
    results, total = [], 0.0
    for q in quiz["questions"]:
        answer = answers.get(q["qid"])
        credit, feedback = grade_question(q, answer)
        total += credit
        concept = {"key": q["concept_key"], "label": q["concept"], "topic": q["topic"]}
        learner.record_answer(profile, concept, credit, difficulty=q["difficulty"])
        if q["qid"] not in profile["seen_questions"]:
            profile["seen_questions"].append(q["qid"])
        expected = q["choices"][q["answer"]] if q["type"] == "mcq" else q["answer"]
        results.append({
            "qid": q["qid"], "concept": q["concept"], "type": q["type"], "prompt": q["prompt"], "code": q.get("code"),
            "your_answer": (q["choices"][int(answer)] if q["type"] == "mcq" and str(answer).isdigit() and int(answer) < len(q["choices"]) else answer),
            "credit": credit, "correct": credit >= 1.0, "expected": expected, "explanation": q["explanation"],
            "feedback": feedback,
            # wrong answers get a short re-teach in the student's own learning style
            "review": None if credit >= 1.0 else style_explanation(profile, q["topic"], short=True),
        })

    per_concept = {}
    for r, q in zip(results, quiz["questions"]):
        c = per_concept.setdefault(q["concept_key"], {"concept": q["concept"], "credit": 0.0, "questions": 0})
        c["credit"] += r["credit"]
        c["questions"] += 1
    for key, c in per_concept.items():
        rec = profile["concepts"][key]
        c.update(mastery_before=before.get(key, learner.PRIOR.get(profile["level"], 0.2)), mastery_after=rec["mastery"],
                 status=learner.status(rec))

    score = round(100 * total / max(1, len(results)))
    level_after = learner.effective_level(profile)
    weak = [c["concept"] for c in per_concept.values() if c["mastery_after"] < 0.5]
    if not weak and score >= 80:
        next_step = "Great work: you have shown you understand these concepts. You are ready to finish and submit your exercise."
    elif weak:
        next_step = "Review " + ", ".join(weak[:3]) + " with \"Explain concept\", then take \"Test me\" again on your weak concepts."
    else:
        next_step = "Good progress. Take \"Test me\" again later to make it stick."

    quiz["submitted"] = True
    quiz["score"] = score
    profile["quiz_history"].append({"quiz_id": quiz["id"], "scope": quiz["scope"], "score": score, "at": now(),
                                    "n": len(results)})
    learner.log_event(profile, "quiz_submitted", quiz_id=quiz["id"], score=score)
    return {"quiz_id": quiz["id"], "score": score, "results": results, "concepts": list(per_concept.values()),
            "level_before": level_before, "level_after": level_after,
            "level_message": None if level_before == level_after else f"Your level moved from {level_before} to {level_after}. The tutor will adapt its hints and questions.",
            "next_step": next_step}
