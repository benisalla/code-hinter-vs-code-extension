from crud import prof_crud, student_crud

def sign_up(user_data):
    role = user_data.get("role")
    if role == "prof":
        # Check if a professor with the same name already exists.
        existing_profs = prof_crud.get_all_profs()
        for prof in existing_profs:
            if prof["name"] == user_data.get("name"):
                raise Exception("Professor already exists.")
        # Create the professor
        return prof_crud.create_prof({
            "name": user_data["name"],
            "password": user_data["password"]
        })
    elif role == "student":
        # Check if a student with the same name already exists.
        existing_students = student_crud.get_all_students()
        for student in existing_students:
            if student["name"] == user_data.get("name"):
                raise Exception("Student already exists.")
        # Create the student (default score is 0)
        return student_crud.create_student({
            "name": user_data["name"],
            "password": user_data["password"],
            "score": 0
        })
    else:
        raise Exception("Invalid role specified. Must be 'prof' or 'student'.")

def sign_in(data):
    email = str(data.get("email"))
    password = str(data.get("password"))
    
    # Check in students.
    for user in student_crud.get_all_students():
        if user["email"] == email and user["password"] == password:
            return {"role": "student", "email": email, "id": user["id"], "name": user["name"]}
    
    raise Exception("Invalid credentials.")
