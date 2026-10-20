"""03: the same concept explained four ways, one per learning style, and at three levels."""
from _demo import client, show, EMAIL

c = client()
concept = "Usage of class variables"
for style in ("examples", "analogies", "step_by_step", "socratic"):
    c.put("/api/tutor/profile", json={"email": EMAIL, "style": style, "level": "beginner"})
    show(f"{concept} | style={style}", c.post("/api/tutor/explain", json={"email": EMAIL, "concept": concept, "exercise_id": 2}).json["explanation"])
c.put("/api/tutor/profile", json={"email": EMAIL, "style": "examples", "level": "advanced"})
show(f"{concept} | advanced", c.post("/api/tutor/explain", json={"email": EMAIL, "concept": concept}).json["explanation"])
