from flask import Blueprint, jsonify, request
from llm.mistral import query
from llm.smol.smol_func import evaluate_code, compare_code
from crud import exercise_crud, student_crud, stud_exe_crud
from crud.stud_exe_crud import get_association_by_student_and_exercise, update_stud_exe
from crud.stud_exe_crud import create_stud_exe, get_associations_by_student_id
from llm.smol.smol_func import complete_code
from llm import backend
from crud import learner_crud
from tutor import learner
from tutor.concepts import exercise_concepts
from tutor.code_analysis import evaluate_offline, similarity_score
import re

_EVAL_LINE = re.compile(r'^\s*\[?(\d+)\]?\s*[).:-]\s*(yes|no)\b', re.I | re.M)

def _record_evaluation(email, student_id, exercise, response):
    """Feeds the professor-criteria evaluation into the learner model."""
    concepts = exercise_concepts(exercise)
    profile = learner_crud.get_profile(email, student_id)
    profile["student_id"] = student_id
    verdicts = []
    for num, verdict in _EVAL_LINE.findall(str(response)):
        idx = int(num) - 1
        if 0 <= idx < len(concepts):
            learner.record_evaluation(profile, concepts[idx], verdict.lower() == "yes")
            verdicts.append({"concept": concepts[idx]["label"], "key": concepts[idx]["key"], "satisfied": verdict.lower() == "yes"})
    learner.log_event(profile, "evaluate", exercise_id=exercise["id"])
    learner_crud.save_profile(profile)
    return verdicts

smol_api = Blueprint('smol_api', __name__, url_prefix='/api')

# @smol_api.route('/evaluate_code', methods=['POST'])
# def evaluate_code_api():
#     data = request.json
#     required_fields = ["exercise_id", "email", "code"]
#     missing_fields = [field for field in required_fields if not data.get(field)]
#     if missing_fields:
#         return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

#     student_id = student_crud.get_student_id_by_email(data.get("email"))
#     if not student_id:
#         return jsonify({"error": "Student with provided email not found"}), 404

#     id_exe = data.get("exercise_id")
#     st_code = data.get("code")
    
#     exercise = exercise_crud.get_exercise_by_id(id_exe)
#     if not exercise:
#         return jsonify({"error": "Exercise not found"}), 404

#     try:
#         response = evaluate_code(
#             concepts=exercise["concepts"],
#             st_code=st_code,
#             temperature=1.0,
#             max_new_tokens=500,
#         )
        
#         create_stud_exe({
#             "student_id": student_id,
#             "exercise_id": id_exe,
#             "prof_id": exercise["id_prof"],
#             "code_submitted": st_code,
#             "status": "in_progress",
#             "score": 0
#         })
    
#         return jsonify({"response": response}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



@smol_api.route('/evaluate_code', methods=['POST'])
def evaluate_code_api():
    data = request.json
    required_fields = ["exercise_id", "email", "code"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    student_id = student_crud.get_student_id_by_email(data.get("email"))
    if not student_id:
        return jsonify({"error": "Student with provided email not found"}), 404

    id_exe = data.get("exercise_id")
    st_code = data.get("code")
    
    exercise = exercise_crud.get_exercise_by_id(id_exe)
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404

    try:
        if backend.llm_available():
            response = evaluate_code(
                concepts=exercise["concepts"],
                st_code=st_code,
                temperature=1.0,
                max_new_tokens=500,
            )
        else:
            response = evaluate_offline(exercise_concepts(exercise), st_code)
        concepts = _record_evaluation(data.get("email"), student_id, exercise, response)

        association = get_association_by_student_and_exercise(student_id, id_exe)

        if association:
            update_stud_exe(association["id"], {
                "code_submitted": st_code,
            })
        else:
            create_stud_exe({
                "student_id": student_id,
                "exercise_id": id_exe,
                "prof_id": exercise["id_prof"],
                "code_submitted": st_code,
                "status": "in_progress",
                "score": 0
            })
            
        return jsonify({"response": response, "concepts": concepts}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# @smol_api.route('/compare_code', methods=['POST'])
# def compare_code_api():
#     data = request.json
#     required_fields = ["exercise_id", "email", "code"]
#     missing_fields = [field for field in required_fields if not data.get(field)]
#     if missing_fields:
#         return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

#     student_id = student_crud.get_student_id_by_email(data.get("email"))
#     if not student_id:
#         return jsonify({"error": "Student with provided email not found"}), 404

#     exercise = exercise_crud.get_exercise_by_id(data.get("exercise_id"))
#     if not exercise:
#         return jsonify({"error": "Exercise not found"}), 404

#     # Check if the student has already completed this exercise
#     associations = get_associations_by_student_id(student_id)
#     for assoc in associations:
#         if assoc.get("exercise_id") == data.get("exercise_id") and assoc.get("status") == "done":
#             return jsonify({"error": "You have already completed this exercise."}), 400

#     try:
#         response = compare_code(
#             pr_code=exercise["code_prof"],
#             st_code=data.get("code"),
#             temperature=0.6,
#             max_new_tokens=200
#         )
        
#         create_stud_exe({
#             "student_id": student_id,
#             "exercise_id": data.get("exercise_id"),
#             "prof_id": exercise["id_prof"],
#             "code_submitted": data.get("code"),
#             "status": "done",
#             "score": response
#         })
        
#         return jsonify({"response": response}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



@smol_api.route('/compare_code', methods=['POST'])
def compare_code_api():
    data = request.json
    required_fields = ["exercise_id", "email", "code"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    student_id = student_crud.get_student_id_by_email(data.get("email"))
    if not student_id:
        return jsonify({"error": "Student with provided email not found"}), 404

    exercise = exercise_crud.get_exercise_by_id(data.get("exercise_id"))
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404

    # Check if the student has already completed this exercise
    associations = get_associations_by_student_id(student_id)
    for assoc in associations:
        if str(assoc.get("exercise_id")) == str(data.get("exercise_id")) and assoc.get("status") == "done":
            return jsonify({
                "association_exists": True,
                "message": "You have already completed this exercise."
            }), 200

    try:
        if backend.llm_available():
            response = compare_code(
                pr_code=exercise["code_prof"],
                st_code=data.get("code"),
                temperature=0.6,
                max_new_tokens=200
            )
        else:
            response = similarity_score(exercise["code_prof"], data.get("code"))

        # the first in-progress association (created by "Evaluate") becomes the final submission
        association = get_association_by_student_and_exercise(student_id, data.get("exercise_id"))
        if association:
            update_stud_exe(association["id"], {"code_submitted": data.get("code"), "status": "done", "score": response})
            return jsonify({"association_exists": False, "response": response}), 200

        create_stud_exe({
            "student_id": student_id,
            "exercise_id": data.get("exercise_id"),
            "prof_id": exercise["id_prof"],
            "code_submitted": data.get("code"),
            "status": "done",
            "score": response
        })
        
        return jsonify({
            "association_exists": False,
            "response": response
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@smol_api.route('/complete_code', methods=['POST'])
def complete_code_api():
    data = request.json
    if not data or 'code' not in data:
        return jsonify({"error": "Missing 'code' in request"}), 400
    
    if not backend.llm_available():
        return jsonify({"error": "Code completion needs an LLM backend (CH_LLM_BACKEND=smol)."}), 503

    code = data.get('code')
    temperature = data.get('temperature', 0.9)
    max_new_tokens = data.get('max_new_tokens', 256)
    top_p = data.get('top_p', 0.9)
    do_sample = data.get('do_sample', True)
    
    try:
        response = complete_code(
            code=code,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            top_p=top_p,
            do_sample=do_sample
        )
        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@smol_api.route('/test/', methods=['GET'])
def test_query():
    prompt = (
        "<s>Deep learning is a subfield of machine learning focused on neural networks.</s>\n"
        "[INST] Explain in simple terms. [/INST]"
    )
    try:
        output = query({
            "inputs": prompt,
            "parameters": {
                "temperature": 1,
                "max_length": 1024,
                "top_p": 0.9,
                "top_k": 50,
                "repetition_penalty": 1.1
            }
        })
        return jsonify({"response": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    