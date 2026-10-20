"""01: the learner profile. The student says how they learn; the tutor adapts to it,
and later corrects the level from evidence (see 04 and 06)."""
from _demo import client, show, EMAIL

c = client()
show("default profile", c.get("/api/tutor/profile", query_string={"email": EMAIL}).json)
show("available levels and learning styles", c.get("/api/tutor/status").json)
p = c.put("/api/tutor/profile", json={"email": EMAIL, "level": "beginner", "style": "analogies", "goal": "pass the OOP exam"}).json
show("after onboarding", p)
