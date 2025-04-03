import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'stud_prof.json')

def load_stud_prof():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_stud_prof(associations):
    with open(DATA_FILE, 'w') as f:
        json.dump(associations, f, indent=4)

def get_all_stud_prof():
    return load_stud_prof()

def get_stud_prof_by_id(assoc_id):
    for assoc in load_stud_prof():
        if assoc["id"] == assoc_id:
            return assoc
    return None

def create_stud_prof(assoc_data):
    associations = load_stud_prof()
    new_id = max([assoc["id"] for assoc in associations], default=0) + 1
    assoc_data["id"] = new_id
    assoc_data.setdefault("notes", "")
    associations.append(assoc_data)
    save_stud_prof(associations)
    return assoc_data

def update_stud_prof(assoc_id, updated_data):
    associations = load_stud_prof()
    for i, assoc in enumerate(associations):
        if assoc["id"] == assoc_id:
            assoc.update(updated_data)
            associations[i] = assoc
            save_stud_prof(associations)
            return assoc
    return None

def delete_stud_prof(assoc_id):
    associations = [assoc for assoc in load_stud_prof() if assoc["id"] != assoc_id]
    save_stud_prof(associations)
    return True

def get_students_by_prof_id(prof_id):
    return [assoc for assoc in load_stud_prof() if assoc.get("prof_id") == prof_id]

def get_professors_by_student_id(student_id):
    return [assoc for assoc in load_stud_prof() if assoc.get("student_id") == student_id]
