import re
from tutor.knowledge import TOPICS

# Professors write concepts as free text: "1. Class creation\n2. Method definition".
_BULLET = re.compile(r'^\s*(?:\d+\s*[.)-]|[-*•])\s*')

def parse_concepts(text):
    if not text:
        return []
    if isinstance(text, list):
        lines = text
    else:
        lines = str(text).splitlines()
    return [_BULLET.sub('', line).strip() for line in lines if _BULLET.sub('', line).strip()]

def concept_key(concept):
    return re.sub(r'[^a-z0-9]+', '-', concept.lower()).strip('-')[:80]

def topic_for(concept):
    """Maps a professor's concept to a knowledge-bank topic (first keyword hit, in TOPICS order)."""
    text = concept.lower() + ' '
    for name, info in TOPICS.items():
        for kw in info["keywords"]:
            if re.search(r'\b' + re.escape(kw), text):
                return name
    return "general"

def exercise_concepts(exercise):
    """[{label, key, topic, exercise_id}] for one exercise."""
    return [
        {"label": c, "key": concept_key(c), "topic": topic_for(c), "exercise_id": exercise["id"]}
        for c in parse_concepts(exercise.get("concepts"))
    ]
