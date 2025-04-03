import json
import os
import crud.student_crud as student_crud
import crud.exercise_crud as exercise_crud

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'stud_exe.json')

def load_stud_exe():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_stud_exe(associations):
    with open(DATA_FILE, 'w') as f:
        json.dump(associations, f, indent=4)

def get_all_stud_exe():
    return load_stud_exe()

def get_stud_exe_by_id(assoc_id):
    for assoc in load_stud_exe():
        if str(assoc["id"]) == str(assoc_id):
            return assoc
    return None

def create_stud_exe(assoc_data):
    associations = load_stud_exe()
    new_id = max([assoc["id"] for assoc in associations], default=0) + 1
    assoc_data["id"] = new_id
    assoc_data.setdefault("score", 0)
    assoc_data.setdefault("status", "in_progress")
    assoc_data.setdefault("code_submitted", None)
    associations.append(assoc_data)
    save_stud_exe(associations)
    return assoc_data

def update_stud_exe(assoc_id, updated_data):
    associations = load_stud_exe()
    for i, assoc in enumerate(associations):
        if str(assoc["id"]) == str(assoc_id):
            assoc.update(updated_data)
            associations[i] = assoc
            save_stud_exe(associations)
            return assoc
    return None

def delete_stud_exe(assoc_id):
    associations = [assoc for assoc in load_stud_exe() if str(assoc["id"]) != str(assoc_id)]
    save_stud_exe(associations)
    return True

def get_associations_by_student_id(student_id):
    return [assoc for assoc in load_stud_exe() if str(assoc.get("student_id")) == str(student_id)]

def get_associations_by_exercise_id(exercise_id):
    return [assoc for assoc in load_stud_exe() if str(assoc.get("exercise_id")) == str(exercise_id)]

def get_associations_by_prof_id(prof_id):
    return [assoc for assoc in load_stud_exe() if str(assoc.get("prof_id")) == str(prof_id)]

def get_submitted_students_by_exercise_id(exercise_id):
    associations = load_stud_exe()
    result = []
    for assoc in associations:
        if str(assoc.get("exercise_id")) == str(exercise_id) and str(assoc.get("status")) == "done":
            student = student_crud.get_student_by_id(assoc.get("student_id"))
            response = {
                "score" : assoc.get("score"),
                "stud_name" : student.get("name"),
                "code_submitted" : assoc.get("code_submitted"),
            }
            result.append(response)
    return result

def get_not_done_exercises_by_student_id(student_id):
    associations = load_stud_exe()
    result = []
    for assoc in associations:
        if str(assoc.get("student_id")) == str(student_id) and str(assoc.get("status")) != "done":
            exercise = exercise_crud.get_exercise_by_id(assoc.get("exercise_id"))
            result.append(exercise)
    return result

def get_association_by_student_and_exercise(student_id, exercise_id):
    for assoc in load_stud_exe():
        if str(assoc.get("student_id")) == str(student_id) and str(assoc.get("exercise_id")) == str(exercise_id):
            return assoc
    return None
