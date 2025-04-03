from flask import Blueprint, request, jsonify
from crud import auth_crud, exercise_crud

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    try:
        user = auth_crud.sign_up(data)
        return jsonify({
            "message": "User registered successfully.",
            "user": user
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/signin', methods=['POST'])
def signin():
    data = request.json
    try:
        user = auth_crud.sign_in(data)
        
        if "exercise_id" not in data:
            return jsonify({"error": "exercise_id is required."}), 400

        exercise = exercise_crud.get_exercise_by_id(data["exercise_id"])
        if not exercise:
            return jsonify({"error": "Exercise not found."}), 404
        
        return jsonify({
            "message": "Sign in successful.",
            "user": user,
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route('/exercise', methods=['POST'])
def check_exercise_existence():
    data = request.json
    exercise_id = data.get('exercise_id')
    if not exercise_id:
        return jsonify({"error": "exercise_id is required."}), 400
    exercise = exercise_crud.get_exercise_by_id(exercise_id)
    if exercise:
        return jsonify({"exists": True}), 200
    else:
        return jsonify({"exists": False, "error": "Exercise not found."}), 404