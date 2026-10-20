"""05: what the student sees (progress, readiness before the final submission) and what
the professor sees (class insights, help requests). The tutor does not replace the
professor: it tells them where to step in."""
from _demo import client, show, EMAIL

c = client()
p = c.get("/api/tutor/progress", query_string={"email": EMAIL, "exercise_id": 1}).json
show("student progress", f"coverage {p['coverage']}% | counts {p['counts']} | level {p['effective_level']}")
for r in p["recommendations"]:
    print("-", r["text"])
show("ready to submit exercise 1?", p["readiness"]["message"])

c.post("/api/tutor/help_request", json={"email": EMAIL, "exercise_id": 2, "message": "I don't see why Animal.count fails", "code": "class Animal: ..."})
insights = c.get("/api/tutor/class/1").json
show("professor 1: concepts, weakest first")
for row in insights["concepts"]:
    print(f"- {row['label']}: avg mastery {row['avg_mastery']} over {row['students_assessed']} students, {row['struggling']} struggling")
show("open help requests", [(h["email"], h["message"]) for h in insights["open_help_requests"]])
