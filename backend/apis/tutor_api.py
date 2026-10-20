from flask import Blueprint, request, jsonify
from crud import exercise_crud, student_crud, learner_crud
from tutor import learner, teaching, quiz as quiz_engine, insights
from tutor.concepts import exercise_concepts, concept_key, topic_for
from tutor.knowledge import LEVELS, STYLES
from llm import backend

tutor_bp = Blueprint('tutor', __name__, url_prefix='/api/tutor')

def _student(data):
    """Resolves (student_id, profile) from the email, or an error response."""
    email = (data or {}).get("email")
    if not email:
        return None, None, (jsonify({"error": "email is required"}), 400)
    student_id = student_crud.get_student_id_by_email(email)
    if not student_id:
        return None, None, (jsonify({"error": "Student with provided email not found"}), 404)
    profile = learner_crud.get_profile(email, student_id)
    profile["student_id"] = student_id
    return student_id, profile, None

def _exercise(exercise_id):
    exercise = exercise_crud.get_exercise_by_id(exercise_id) if exercise_id is not None else None
    if not exercise:
        return None, (jsonify({"error": "Exercise not found"}), 404)
    return exercise, None

@tutor_bp.route('/status', methods=['GET'])
def status():
    return jsonify({"llm_backend": backend.backend_name(), "llm_available": backend.llm_available(),
                    "levels": LEVELS, "styles": STYLES}), 200

# ------------------------------------------------------------------ profile

@tutor_bp.route('/profile', methods=['GET'])
def get_profile():
    _, profile, err = _student(request.args)
    if err:
        return err
    return jsonify(_public_profile(profile)), 200

@tutor_bp.route('/profile', methods=['PUT'])
def update_profile():
    data = request.json or {}
    _, profile, err = _student(data)
    if err:
        return err
    if "level" in data:
        if data["level"] not in LEVELS:
            return jsonify({"error": f"level must be one of {LEVELS}"}), 400
        profile["level"] = data["level"]
    if "style" in data:
        if data["style"] not in STYLES:
            return jsonify({"error": f"style must be one of {list(STYLES)}"}), 400
        profile["style"] = data["style"]
    if "goal" in data:
        profile["goal"] = str(data["goal"])[:300]
    profile["onboarded"] = True
    learner.log_event(profile, "profile_updated", level=profile["level"], style=profile["style"])
    learner_crud.save_profile(profile)
    return jsonify(_public_profile(profile)), 200

def _public_profile(profile):
    return {k: profile[k] for k in ("email", "level", "style", "goal", "onboarded")} | {
        "effective_level": learner.effective_level(profile)}

# -------------------------------------------------------------------- hints

@tutor_bp.route('/hint', methods=['POST'])
def hint():
    data = request.json or {}
    _, profile, err = _student(data)
    if err:
        return err
    exercise, err = _exercise(data.get("exercise_id"))
    if err:
        return err
    result = teaching.get_hint(profile, exercise, exercise_concepts(exercise), data.get("code") or "",
                               question=data.get("question"), diagnostics=data.get("diagnostics"),
                               more=bool(data.get("more")), requested_level=data.get("level"))
    learner_crud.save_profile(profile)
    return jsonify(result), 200

@tutor_bp.route('/explain', methods=['POST'])
def explain():
    data = request.json or {}
    _, profile, err = _student(data)
    if err:
        return err
    exercise = exercise_crud.get_exercise_by_id(data["exercise_id"]) if data.get("exercise_id") else None
    label = data.get("concept")
    if not label:
        return jsonify({"error": "concept is required"}), 400
    concept = next((c for c in (exercise_concepts(exercise) if exercise else []) if c["key"] in (label, concept_key(label))), None) \
        or {"label": label, "key": concept_key(label), "topic": topic_for(label)}
    result = teaching.explain(profile, concept, exercise)
    learner_crud.save_profile(profile)
    return jsonify(result), 200

@tutor_bp.route('/concepts', methods=['GET'])
def concepts():
    student_id, profile, err = _student(request.args)
    if err:
        return err
    exercise_id = request.args.get("exercise_id")
    if exercise_id:
        exercise, err = _exercise(exercise_id)
        if err:
            return err
        items = exercise_concepts(exercise)
    else:
        items = insights.course_concepts(student_id)
    return jsonify([insights.concept_view(profile, c) for c in items]), 200

# ------------------------------------------------------------------ Test me

@tutor_bp.route('/quiz', methods=['POST'])
def start_quiz():
    data = request.json or {}
    student_id, profile, err = _student(data)
    if err:
        return err
    scope = data.get("scope", "exercise")
    if scope == "exercise":
        exercise, err = _exercise(data.get("exercise_id"))
        if err:
            return err
        concepts = exercise_concepts(exercise)
    elif scope in ("course", "weak"):
        concepts = insights.course_concepts(student_id)
        if scope == "weak":
            concepts = [c for c in concepts if learner.status(learner.concept_record(profile, c)) in ("not_started", "learning", "almost")] or concepts
    else:
        return jsonify({"error": "scope must be 'exercise', 'course' or 'weak'"}), 400
    try:
        quiz = quiz_engine.build_quiz(profile, concepts, scope, data.get("n_questions"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    learner_crud.save_quiz(quiz)
    learner_crud.save_profile(profile)
    return jsonify(quiz_engine.public_quiz(quiz)), 201

@tutor_bp.route('/quiz/<quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    data = request.json or {}
    _, profile, err = _student(data)
    if err:
        return err
    quiz = learner_crud.get_quiz(quiz_id)
    if not quiz or quiz["email"] != profile["email"]:
        return jsonify({"error": "Quiz not found"}), 404
    if quiz.get("submitted"):
        return jsonify({"error": "This quiz was already submitted. Start a new \"Test me\"."}), 400
    result = quiz_engine.grade_quiz(profile, quiz, data.get("answers") or {})
    learner_crud.save_quiz(quiz)
    learner_crud.save_profile(profile)
    return jsonify(result), 200

# ----------------------------------------------------------------- progress

@tutor_bp.route('/progress', methods=['GET'])
def progress():
    student_id, profile, err = _student(request.args)
    if err:
        return err
    return jsonify(insights.progress(profile, student_id, request.args.get("exercise_id"))), 200

@tutor_bp.route('/readiness', methods=['GET'])
def readiness():
    _, profile, err = _student(request.args)
    if err:
        return err
    exercise, err = _exercise(request.args.get("exercise_id"))
    if err:
        return err
    return jsonify(insights.readiness(profile, exercise)), 200

# ------------------------------------------------- the professor stays in the loop

@tutor_bp.route('/help_request', methods=['POST'])
def help_request():
    data = request.json or {}
    student_id, profile, err = _student(data)
    if err:
        return err
    exercise, err = _exercise(data.get("exercise_id"))
    if err:
        return err
    req = learner_crud.create_help_request({
        "student_id": student_id, "email": profile["email"], "prof_id": exercise["id_prof"],
        "exercise_id": exercise["id"], "concept": data.get("concept"),
        "message": str(data.get("message") or "")[:1000], "code": str(data.get("code") or "")[:10000],
        "hints_used": profile["hint_state"].get(str(exercise["id"]), {}).get("level", 0),
    })
    learner.log_event(profile, "help_request", exercise_id=exercise["id"], request_id=req["id"])
    learner_crud.save_profile(profile)
    return jsonify(req), 201

@tutor_bp.route('/class/<int:prof_id>', methods=['GET'])
def class_insights(prof_id):
    return jsonify(insights.class_insights(prof_id)), 200

@tutor_bp.route('/help_request/<int:request_id>', methods=['PUT'])
def resolve_help_request(request_id):
    data = request.json or {}
    updated = learner_crud.update_help_request(request_id, {"status": data.get("status", "resolved"),
                                                             "reply": str(data.get("reply") or "")[:2000]})
    if not updated:
        return jsonify({"error": "Help request not found"}), 404
    return jsonify(updated), 200

@tutor_bp.route('/help_requests', methods=['GET'])
def my_help_requests():
    _, profile, err = _student(request.args)
    if err:
        return err
    return jsonify([r for r in learner_crud.get_help_requests() if r["email"] == profile["email"]]), 200
