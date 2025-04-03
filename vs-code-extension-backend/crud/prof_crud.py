import json
import os
from crud import exercise_crud, stud_prof_crud, student_crud

# Path to the JSON file for professors
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'profs.json')

def load_profs():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_profs(profs):
    with open(DATA_FILE, 'w') as f:
        json.dump(profs, f, indent=4)

def get_all_profs():
    return load_profs()

def get_prof_by_id(prof_id):
    profs = load_profs()
    for prof in profs:
        if prof["id"] == prof_id:
            return prof
    return None

def create_prof(prof_data):
    profs = load_profs()
    new_id = max([prof['id'] for prof in profs], default=0) + 1
    prof_data['id'] = new_id
    profs.append(prof_data)
    save_profs(profs)
    return prof_data

def update_prof(prof_id, updated_data):
    profs = load_profs()
    for i, prof in enumerate(profs):
        if prof["id"] == prof_id:
            prof.update(updated_data)
            profs[i] = prof
            save_profs(profs)
            return prof
    return None

def delete_prof(prof_id):
    profs = load_profs()
    profs = [prof for prof in profs if prof["id"] != prof_id]
    save_profs(profs)
    return True


def get_exercises_by_prof_id(prof_id):
    exercises = exercise_crud.get_all_exercises()
    return [ex for ex in exercises if ex.get("id_prof") == prof_id]

def get_students_by_prof_id(prof_id):
    associations = stud_prof_crud.get_all_stud_prof()
    student_ids = [assoc["student_id"] for assoc in associations if assoc.get("prof_id") == prof_id]
    # Remove duplicates
    student_ids = list(set(student_ids))
    return [student_crud.get_student_by_id(sid) for sid in student_ids if student_crud.get_student_by_id(sid)]
