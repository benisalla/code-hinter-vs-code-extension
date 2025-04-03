import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'exercises.json')

def load_exercises():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_exercises(exercises):
    with open(DATA_FILE, 'w') as f:
        json.dump(exercises, f, indent=4)

def get_all_exercises():
    return load_exercises()

def get_exercise_by_id(exercise_id):
    for exercise in load_exercises():
        if str(exercise["id"]) == str(exercise_id):
            return exercise
    return None

def create_exercise(exercise_data):
    exercises = load_exercises()
    new_id = max([e['id'] for e in exercises], default=0) + 1
    exercise_data['id'] = new_id
    exercises.append(exercise_data)
    save_exercises(exercises)
    return exercise_data

def update_exercise(exercise_id, updated_data):
    exercises = load_exercises()
    for i, exercise in enumerate(exercises):
        if str(exercise["id"]) == str(exercise_id):
            exercise.update(updated_data)
            exercises[i] = exercise
            save_exercises(exercises)
            return exercise
    return None

def delete_exercise(exercise_id):
    exercises = [e for e in load_exercises() if e["id"] != exercise_id]
    save_exercises(exercises)
    return True

def get_exercises_by_prof_id(id_prof):
    exercises = load_exercises()
    return [exercise for exercise in exercises if str(exercise.get('id_prof')) == str(id_prof)]