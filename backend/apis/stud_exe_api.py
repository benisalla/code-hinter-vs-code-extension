from flask import Blueprint, request, jsonify
from crud import stud_exe_crud

stud_exe_bp = Blueprint('stud_exe', __name__, url_prefix='/api/stud_exe')

@stud_exe_bp.route('/', methods=['GET'])
def list_stud_exe():
    return jsonify(stud_exe_crud.get_all_stud_exe()), 200

@stud_exe_bp.route('/<int:assoc_id>', methods=['GET'])
def get_stud_exe(assoc_id):
    association = stud_exe_crud.get_stud_exe_by_id(assoc_id)
    if association:
        return jsonify(association), 200
    return jsonify({"error": "Association not found"}), 404

@stud_exe_bp.route('/', methods=['POST'])
def create_stud_exe():
    data = request.json
    if not all(key in data for key in ["student_id", "exercise_id", "prof_id"]):
        return jsonify({"error": "student_id, exercise_id, and prof_id are required"}), 400
    association = stud_exe_crud.create_stud_exe(data)
    return jsonify(association), 201

@stud_exe_bp.route('/<int:assoc_id>', methods=['PUT'])
def update_stud_exe(assoc_id):
    association = stud_exe_crud.update_stud_exe(assoc_id, request.json)
    if association:
        return jsonify(association), 200
    return jsonify({"error": "Association not found"}), 404

@stud_exe_bp.route('/<int:assoc_id>', methods=['DELETE'])
def delete_stud_exe(assoc_id):
    stud_exe_crud.delete_stud_exe(assoc_id)
    return jsonify({"message": "Association deleted"}), 200

@stud_exe_bp.route('/student/<int:student_id>', methods=['GET'])
def get_stud_exe_by_student(student_id):
    associations = stud_exe_crud.get_associations_by_student_id(student_id)
    return jsonify(associations), 200

@stud_exe_bp.route('/exercise/<int:exercise_id>', methods=['GET'])
def get_stud_exe_by_exercise(exercise_id):
    associations = stud_exe_crud.get_associations_by_exercise_id(exercise_id)
    return jsonify(associations), 200

@stud_exe_bp.route('/prof/<int:prof_id>', methods=['GET'])
def get_stud_exe_by_prof(prof_id):
    associations = stud_exe_crud.get_associations_by_prof_id(prof_id)
    return jsonify(associations), 200

@stud_exe_bp.route('/exercise/<int:exercise_id>/submitted', methods=['GET'])
def get_submitted_students(exercise_id):
    associations = stud_exe_crud.get_submitted_students_by_exercise_id(exercise_id)
    return jsonify(associations), 200