"""02: the hint ladder on a buggy submission (exercise 4: `if b = 0:`).
Each request climbs one step: nudge -> concept -> pinpoint -> plan -> "ask your professor".
The tutor never writes the corrected line."""
from _demo import client, show, EMAIL

c = client()
code = "def divide(a, b):\n    if b = 0:\n        return 'Error: Division by zero'\n    return a / b\n\nprint(divide(10, 0))\n"
c.post("/api/stud_prof/", json={"student_id": 1, "prof_id": 2})  # give the seed student professor 2's exercises too
for style in ("examples", "socratic"):
    c.put("/api/tutor/profile", json={"email": EMAIL, "style": style})
    show(f"style = {style}")
    for _ in range(5):
        h = c.post("/api/tutor/hint", json={"email": EMAIL, "exercise_id": 4, "code": code, "more": True}).json
        print(f"\n[step {h['level']}/{h['max_level']} {h['level_name']}] concept: {h['concept']}")
        print(h["hint"])
        if h["escalate"]:
            print("->", h["escalate_message"])
    # a new session on the same exercise starts from step 1 again when not asking for "more"
    c.post("/api/tutor/hint", json={"email": EMAIL, "exercise_id": 4, "code": code, "level": 1})
