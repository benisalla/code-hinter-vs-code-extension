from flask import Blueprint, request, jsonify
from crud import student_crud

student_bp = Blueprint('student', __name__, url_prefix='/api/student')

@student_bp.route('/', methods=['GET'])
def list_students():
    students = student_crud.get_all_students()
    return jsonify(students), 200

@student_bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = student_crud.get_student_by_id(student_id)
    if student:
        return jsonify(student), 200
    return jsonify({"error": "Student not found"}), 404

@student_bp.route('/', methods=['POST'])
def create_student():
    data = request.json
    required_fields = ['email', 'name', 'password']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    student = student_crud.create_student(data)
    return jsonify(student), 201

@student_bp.route('/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.json
    for field in ['email', 'name', 'password']:
        if field in data and not data[field]:
            return jsonify({"error": f"{field} cannot be empty"}), 400
    student = student_crud.update_student(student_id, data)
    if student:
        return jsonify(student), 200
    return jsonify({"error": "Student not found"}), 404

@student_bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student_crud.delete_student(student_id)
    return jsonify({"message": "Student deleted"}), 200

@student_bp.route('/<int:student_id>/exercises', methods=['GET'])
def get_exercises_by_student(student_id):
    exercises = student_crud.get_exercises_by_student_id(student_id)
    return jsonify(exercises), 200

@student_bp.route('/<int:student_id>/professors', methods=['GET'])
def get_professors_by_student(student_id):
    professors = student_crud.get_professors_by_student_id(student_id)
    return jsonify(professors), 200