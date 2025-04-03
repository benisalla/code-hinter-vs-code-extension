from flask import Blueprint, request, jsonify
from crud import exercise_crud

exercise_bp = Blueprint('exercise', __name__, url_prefix='/api/exercise')

@exercise_bp.route('/', methods=['GET'])
def list_exercises():
    exercises = exercise_crud.get_all_exercises()
    return jsonify(exercises), 200

@exercise_bp.route('/prof/<int:id_prof>', methods=['GET'])
def get_exercises_by_prof(id_prof):
    exercises = exercise_crud.get_exercises_by_prof_id(id_prof)
    if exercises:
        return jsonify(exercises), 200
    return jsonify({"error": "Exercises not found"}), 404

@exercise_bp.route('/<int:exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    exercise = exercise_crud.get_exercise_by_id(exercise_id)
    if exercise:
        return jsonify(exercise), 200
    return jsonify({"error": "Exercise not found"}), 404

@exercise_bp.route('/', methods=['POST'])
def create_exercise():
    data = request.json
    if not all(field in data for field in ["code_prof", "concepts", "id_prof"]):
        return jsonify({"error": "code_prof, concepts, and id_prof are required"}), 400
    data.setdefault("id_stud", None)
    data.setdefault("code_stud", None)
    data.setdefault("status", "in_progress")
    exercise = exercise_crud.create_exercise(data)
    
    response = jsonify(exercise)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response, 201

@exercise_bp.route('/<int:exercise_id>', methods=['PUT'])
def update_exercise(exercise_id):
    data = request.json
    exercise = exercise_crud.update_exercise(exercise_id, data)
    if exercise:
        return jsonify(exercise), 200
    return jsonify({"error": "Exercise not found"}), 404

@exercise_bp.route('/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):
    exercise_crud.delete_exercise(exercise_id)
    return jsonify({"message": "Exercise deleted"}), 200

@exercise_bp.route('/', methods=['OPTIONS'])
def options_exercise():
    response = jsonify({'status': 'success'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response, 200
