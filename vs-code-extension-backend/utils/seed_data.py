from crud import prof_crud, student_crud, exercise_crud, stud_prof_crud, stud_exe_crud

def seed_data():
    # Seed Professors if empty
    profs = prof_crud.get_all_profs()
    if not profs:
        print("Seeding professors...")
        prof1 = prof_crud.create_prof({"name": "Dr. Alice Johnson", "password": "alicepass"})
        prof2 = prof_crud.create_prof({"name": "Dr. Bob Smith", "password": "bobpass"})
    else:
        # Use first two professors if they already exist
        prof1 = profs[0]
        prof2 = profs[1] if len(profs) > 1 else None

    # Seed Students if empty with real names and emails
    students = student_crud.get_all_students()
    if not students:
        print("Seeding students...")
        # Create students for Dr. Alice Johnson
        alice_students_data = [
            {"name": "Emily Johnson", "password": "pass", "email": "emily.johnson@example.com"},
            {"name": "Matthew Williams", "password": "pass", "email": "matthew.williams@example.com"},
            {"name": "Olivia Brown", "password": "pass", "email": "olivia.brown@example.com"},
            {"name": "Joshua Jones", "password": "pass", "email": "joshua.jones@example.com"},
            {"name": "Sophia Garcia", "password": "pass", "email": "sophia.garcia@example.com"}
        ]
        for data in alice_students_data:
            student = student_crud.create_student(data)
            stud_prof_crud.create_stud_prof({
                "student_id": student["id"],
                "prof_id": prof1["id"],
                "notes": "Initial assignment"
            })
        # Create students for Dr. Bob Smith if available
        if prof2:
            bob_students_data = [
                {"name": "Isabella Miller", "password": "pass", "email": "isabella.miller@example.com"},
                {"name": "Alexander Davis", "password": "pass", "email": "alexander.davis@example.com"},
                {"name": "Mia Rodriguez", "password": "pass", "email": "mia.rodriguez@example.com"},
                {"name": "Ethan Martinez", "password": "pass", "email": "ethan.martinez@example.com"},
                {"name": "Ava Hernandez", "password": "pass", "email": "ava.hernandez@example.com"}
            ]
            for data in bob_students_data:
                student = student_crud.create_student(data)
                stud_prof_crud.create_stud_prof({
                    "student_id": student["id"],
                    "prof_id": prof2["id"],
                    "notes": "Initial assignment"
                })

    # Seed Exercises if empty (only professor-created exercise data)
    exercises = exercise_crud.get_all_exercises()
    if not exercises:
        print("Seeding exercises...")
        # Dr. Alice Johnson creates 2 exercises
        ex1 = exercise_crud.create_exercise({
            "code_prof": "print('Hello from Dr. Alice Johnson, Exercise 1')",
            "concepts": "Basics",
            "id_prof": prof1["id"]
        })
        ex2 = exercise_crud.create_exercise({
            "code_prof": "print('Hello from Dr. Alice Johnson, Exercise 2')",
            "concepts": "Advanced",
            "id_prof": prof1["id"]
        })
        # Dr. Bob Smith creates 2 exercises if available
        if prof2:
            ex3 = exercise_crud.create_exercise({
                "code_prof": "print('Hello from Dr. Bob Smith, Exercise 1')",
                "concepts": "Basics",
                "id_prof": prof2["id"]
            })
            ex4 = exercise_crud.create_exercise({
                "code_prof": "print('Hello from Dr. Bob Smith, Exercise 2')",
                "concepts": "Advanced",
                "id_prof": prof2["id"]
            })

    # Seed Student–Exercise Associations if empty
    stud_exes = stud_exe_crud.get_all_stud_exe()
    if not stud_exes:
        print("Seeding student-exercise associations...")
        # Retrieve all stud-prof associations to know which student belongs to which professor
        stud_prof_assocs = stud_prof_crud.get_all_stud_prof()
        all_students = student_crud.get_all_students()
        all_exercises = exercise_crud.get_all_exercises()

        # For each professor, assign each of their students to each exercise they created.
        # Dr. Alice Johnson:
        alice_students = [sp["student_id"] for sp in stud_prof_assocs if sp["prof_id"] == prof1["id"]]
        alice_exercises = [ex for ex in all_exercises if ex["id_prof"] == prof1["id"]]
        for exercise in alice_exercises:
            for stud_id in alice_students:
                stud_exe_crud.create_stud_exe({
                    "student_id": stud_id,
                    "exercise_id": exercise["id"],
                    "prof_id": prof1["id"],
                    "score": 0,
                    "status": "in_progress",
                    "code_submitted": None
                })

        # Dr. Bob Smith:
        if prof2:
            bob_students = [sp["student_id"] for sp in stud_prof_assocs if sp["prof_id"] == prof2["id"]]
            bob_exercises = [ex for ex in all_exercises if ex["id_prof"] == prof2["id"]]
            for exercise in bob_exercises:
                for stud_id in bob_students:
                    stud_exe_crud.create_stud_exe({
                        "student_id": stud_id,
                        "exercise_id": exercise["id"],
                        "prof_id": prof2["id"],
                        "score": 0,
                        "status": "in_progress",
                        "code_submitted": None
                    })
    print("Seeding complete.")