from flask import Blueprint, request, jsonify
from crud import stud_prof_crud

stud_prof_bp = Blueprint('stud_prof', __name__, url_prefix='/api/stud_prof')

@stud_prof_bp.route('/', methods=['GET'])
def list_stud_prof():
    return jsonify(stud_prof_crud.get_all_stud_prof()), 200

@stud_prof_bp.route('/<int:assoc_id>', methods=['GET'])
def get_stud_prof(assoc_id):
    association = stud_prof_crud.get_stud_prof_by_id(assoc_id)
    if association:
        return jsonify(association), 200
    return jsonify({"error": "Association not found"}), 404

@stud_prof_bp.route('/', methods=['POST'])
def create_stud_prof():
    data = request.json
    if not all(key in data for key in ["student_id", "prof_id"]):
        return jsonify({"error": "student_id and prof_id are required"}), 400
    association = stud_prof_crud.create_stud_prof(data)
    return jsonify(association), 201

@stud_prof_bp.route('/<int:assoc_id>', methods=['PUT'])
def update_stud_prof(assoc_id):
    association = stud_prof_crud.update_stud_prof(assoc_id, request.json)
    if association:
        return jsonify(association), 200
    return jsonify({"error": "Association not found"}), 404

@stud_prof_bp.route('/<int:assoc_id>', methods=['DELETE'])
def delete_stud_prof(assoc_id):
    stud_prof_crud.delete_stud_prof(assoc_id)
    return jsonify({"message": "Association deleted"}), 200

@stud_prof_bp.route('/prof/<int:prof_id>', methods=['GET'])
def get_stud_prof_by_prof(prof_id):
    associations = stud_prof_crud.get_students_by_prof_id(prof_id)
    return jsonify(associations), 200

@stud_prof_bp.route('/student/<int:student_id>', methods=['GET'])
def get_stud_prof_by_student(student_id):
    associations = stud_prof_crud.get_professors_by_student_id(student_id)
    return jsonify(associations), 200