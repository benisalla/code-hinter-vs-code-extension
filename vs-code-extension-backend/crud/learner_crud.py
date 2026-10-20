from datetime import datetime, timezone
from utils.storage import LOCK, load_json, save_json

# learners.json = {email: profile}; quizzes.json = {quiz_id: quiz}; help_requests.json = [request]
LEARNERS = 'learners.json'
QUIZZES = 'quizzes.json'
HELP_REQUESTS = 'help_requests.json'

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def new_profile(email, student_id=None):
    return {
        "email": email,
        "student_id": student_id,
        "level": "beginner",          # declared by the student, adapted from evidence
        "style": "examples",          # see tutor.knowledge.STYLES
        "goal": "",
        "onboarded": False,
        "concepts": {},               # concept_key -> mastery record
        "hint_state": {},             # exercise_id -> {"level", "updated_at"}
        "seen_questions": [],
        "quiz_history": [],
        "events": [],
        "created_at": now(),
    }

def get_profile(email, student_id=None):
    with LOCK:
        profile = load_json(LEARNERS, {}).get(email)
    return profile or new_profile(email, student_id)

def save_profile(profile):
    with LOCK:
        learners = load_json(LEARNERS, {})
        learners[profile["email"]] = profile
        save_json(LEARNERS, learners)
    return profile

def get_all_profiles():
    return list(load_json(LEARNERS, {}).values())

def save_quiz(quiz):
    with LOCK:
        quizzes = load_json(QUIZZES, {})
        quizzes[quiz["id"]] = quiz
        save_json(QUIZZES, quizzes)
    return quiz

def get_quiz(quiz_id):
    return load_json(QUIZZES, {}).get(quiz_id)

def create_help_request(data):
    with LOCK:
        requests = load_json(HELP_REQUESTS, [])
        data["id"] = max([r["id"] for r in requests], default=0) + 1
        data.setdefault("status", "open")
        data["created_at"] = now()
        requests.append(data)
        save_json(HELP_REQUESTS, requests)
    return data

def get_help_requests(prof_id=None, status=None):
    return [r for r in load_json(HELP_REQUESTS, [])
            if (prof_id is None or str(r.get("prof_id")) == str(prof_id)) and (status is None or r.get("status") == status)]

def update_help_request(request_id, updated):
    with LOCK:
        requests = load_json(HELP_REQUESTS, [])
        for r in requests:
            if str(r["id"]) == str(request_id):
                r.update(updated)
                save_json(HELP_REQUESTS, requests)
                return r
    return None
