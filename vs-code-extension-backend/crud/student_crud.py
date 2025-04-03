import json
import os
from crud import exercise_crud, stud_exe_crud, stud_prof_crud, prof_crud

# Path to the JSON file for students
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'students.json')

def load_students():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_students(students):
    with open(DATA_FILE, 'w') as f:
        json.dump(students, f, indent=4)

def get_all_students():
    return load_students()

def get_student_by_id(student_id):
    students = load_students()
    for student in students:
        if str(student["id"]) == str(student_id):
            return student
    return None

def get_student_id_by_email(email):
    students = load_students()
    for student in students:
        if str(student.get("email")) == str(email):
            return student.get("id")
    return None

def create_student(student_data):
    students = load_students()
    new_id = max([student['id'] for student in students], default=0) + 1
    student_data['id'] = new_id
    student_data.setdefault("score", 0)
    students.append(student_data)
    save_students(students)
    return student_data

def update_student(student_id, updated_data):
    students = load_students()
    for i, student in enumerate(students):
        if str(student["id"]) == str(student_id):
            student.update(updated_data)
            students[i] = student
            save_students(students)
            return student
    return None

def delete_student(student_id):
    students = load_students()
    students = [student for student in students if student["id"] != student_id]
    save_students(students)
    return True


def get_exercises_by_student_id(student_id):
    """
    Return all exercise associations (assignments/submissions) for a given student.
    """
    associations = stud_exe_crud.get_all_stud_exe()
    # For each association, include the full exercise details
    result = []
    for assoc in associations:
        if str(assoc.get("student_id")) == str(student_id):
            ex = exercise_crud.get_exercise_by_id(assoc.get("exercise_id"))
            if ex:
                # Optionally combine association and exercise info
                combined = {"association": assoc, "exercise": ex}
                result.append(combined)
    return result

def get_professors_by_student_id(student_id):
    """
    Return all professors associated with the student.
    """
    associations = stud_prof_crud.get_all_stud_prof()
    prof_ids = [assoc["prof_id"] for assoc in associations if str(assoc.get("student_id")) == str(student_id)]
    prof_ids = list(set(prof_ids))
    return [prof_crud.get_prof_by_id(pid) for pid in prof_ids if prof_crud.get_prof_by_id(pid)]