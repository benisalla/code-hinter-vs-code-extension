from flask import Blueprint, request, jsonify
from crud import prof_crud

prof_bp = Blueprint('prof', __name__, url_prefix='/api/prof')

@prof_bp.route('/', methods=['GET'])
def list_profs():
    profs = prof_crud.get_all_profs()
    return jsonify(profs), 200

@prof_bp.route('/<int:prof_id>', methods=['GET'])
def get_prof(prof_id):
    prof = prof_crud.get_prof_by_id(prof_id)
    if prof:
        return jsonify(prof), 200
    return jsonify({"error": "Professor not found"}), 404

@prof_bp.route('/', methods=['POST'])
def create_prof():
    data = request.json
    if not data.get("name") or not data.get("password"):
        return jsonify({"error": "Name and password are required"}), 400
    prof = prof_crud.create_prof(data)
    return jsonify(prof), 201

@prof_bp.route('/<int:prof_id>', methods=['PUT'])
def update_prof(prof_id):
    data = request.json
    prof = prof_crud.update_prof(prof_id, data)
    if prof:
        return jsonify(prof), 200
    return jsonify({"error": "Professor not found"}), 404

@prof_bp.route('/<int:prof_id>', methods=['DELETE'])
def delete_prof(prof_id):
    prof_crud.delete_prof(prof_id)
    return jsonify({"message": "Professor deleted"}), 200

@prof_bp.route('/<int:prof_id>/exercises', methods=['GET'])
def get_exercises_by_prof(prof_id):
    exercises = prof_crud.get_exercises_by_prof_id(prof_id)
    return jsonify(exercises), 200

@prof_bp.route('/<int:prof_id>/students', methods=['GET'])
def get_students_by_prof(prof_id):
    students = prof_crud.get_students_by_prof_id(prof_id)
    return jsonify(students), 200