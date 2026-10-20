"""
Hints and concept explanations.

Hints follow a 4-step ladder, like a teacher who first asks a question and only
gives more support when the student is still stuck:
  1 nudge      a guiding question towards the right concept
  2 concept    the concept again, in the student's learning style, on an unrelated example
  3 pinpoint   where in *their* code to look (line + what to look at)
  4 plan       a plain-language plan; past this the tutor suggests asking the professor
The LLM (when configured) words levels 1, 3 and 4 for this student's code. Level 2 and
concept explanations come from the curated knowledge bank: small models explain
concepts wrongly too often to be trusted with teaching them. Every hint goes through
the guardrails.
"""
from datetime import datetime, timezone
from llm import backend
from llm.constant import (TUTOR_SYS_PROMPT, HINT_PROMPT, HINT_LEVEL_INSTRUCTIONS,
                          EXPLAIN_PROMPT, STYLE_INSTRUCTIONS)
from tutor import learner
from tutor.code_analysis import analyze
from tutor.concepts import topic_for, concept_key
from tutor.guardrails import sanitize_hint, sanitize_llm_hint
from tutor.knowledge import STYLES, topic

MAX_HINT_LEVEL = 4
HINT_LADDER_MINUTES = 20
LEVEL_NAMES = {1: "nudge", 2: "concept", 3: "pinpoint", 4: "plan"}

def _sys_prompt(profile, max_sentences):
    return TUTOR_SYS_PROMPT.format(level=learner.effective_level(profile),
                                   style_desc=STYLES.get(profile["style"], STYLES["examples"]),
                                   max_sentences=max_sentences)

def _pick(items, n):
    return items[n % len(items)] if items else ""

def style_explanation(profile, topic_name, short=False):
    """Rule-based explanation of a topic in the student's style and level."""
    info = topic(topic_name)
    level = learner.effective_level(profile)
    style = profile.get("style", "examples")
    core = info["explain"].get(level, info["explain"]["beginner"])
    if style == "analogies":
        return info["analogy"] if short else f"{info['analogy']}\n\n{core}"
    if style == "step_by_step":
        steps = "\n".join(f"{i}. {s}" for i, s in enumerate(info["steps"], 1))
        return steps if short else f"{core}\n\n{steps}"
    if style == "socratic":
        qs = "\n".join(f"- {q}" for q in info["socratic"])
        return qs if short else f"Think about these:\n{qs}\n\n{core}"
    example = f"```python\n{info['example']}\n```"
    return f"{core}\n\n{example}" if not short else f"For example:\n{example}"

# ------------------------------------------------------------------ hints

def _focus(profile, concepts, analysis, question, diagnostics):
    """Choose the concept the student most likely needs: what the code analysis
    points at, else what the question is about, else the weakest concept."""
    issue = analysis["syntax_error"] or (analysis["findings"][0] if analysis["findings"] else None)
    if issue is None and diagnostics:
        d = diagnostics[0]
        issue = {"topic": topic_for(d.get("message", "")), "line": d.get("line"),
                 "message": f"Line {d.get('line')}: your editor reports \"{d.get('message')}\". What is that message telling you?"}
    candidates = []
    if issue:
        candidates.append(issue["topic"])
    if question:
        candidates.append(topic_for(question))
    for t in candidates:
        for c in concepts:
            if c["topic"] == t:
                return c, issue
    if issue and issue["topic"] != "general":
        t = issue["topic"]
        return {"label": topic(t)["title"], "key": concept_key(topic(t)["title"]), "topic": t}, issue
    if not concepts:
        return {"label": topic("general")["title"], "key": "programming-fundamentals", "topic": "general"}, issue
    weakest = min(concepts, key=lambda c: learner.concept_record(profile, c)["mastery"])
    return weakest, issue

def _next_level(profile, exercise_id, focus_key, more, requested_level):
    if requested_level:
        return max(1, min(MAX_HINT_LEVEL, int(requested_level)))
    state = profile["hint_state"].get(str(exercise_id))
    if not state:
        return 1
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(state["updated_at"])).total_seconds() / 60
    if more or (state.get("focus") == focus_key and age < HINT_LADDER_MINUTES):
        return min(MAX_HINT_LEVEL, state["level"] + 1)
    return 1

def _rule_hint(profile, focus, issue, level, n_hints):
    info = topic(focus["topic"])
    if level == 1:
        return f"Focus on **{focus['label']}**. {_pick(info['socratic'], n_hints)}"
    if level == 2:
        return f"A reminder about **{focus['label']}**:\n\n{style_explanation(profile, focus['topic'])}"
    if level == 3:
        if issue:
            return issue["message"]
        pitfalls = "; ".join(info["pitfalls"])
        return f"Go through your code looking for the classic mistakes with {focus['label'].lower()}: {pitfalls}."
    plan = "\n".join(f"{i}. {s}" for i, s in enumerate(info["steps"], 1))
    return f"Here is a plan you can follow for **{focus['label']}**:\n{plan}"

def _check_question(focus, n_hints):
    return _pick(topic(focus["topic"])["socratic"], n_hints + 1)

def get_hint(profile, exercise, concepts, code, question=None, diagnostics=None, more=False, requested_level=None):
    analysis = analyze(code)
    focus, issue = _focus(profile, concepts, analysis, question, diagnostics or [])
    level = _next_level(profile, exercise["id"], focus["key"], more, requested_level)
    rec = learner.concept_record(profile, focus)
    n_hints = rec["hints"]

    rule_text = _rule_hint(profile, focus, issue, level, n_hints)
    text, source = None, "rules"
    # The LLM speaks only where the rules have nothing precise to say: a free-form question,
    # or a pinpoint/plan step when static analysis found no concrete issue. When the rules
    # know the exact problem, their hint is both correct and solution-free, so it wins.
    use_llm = backend.llm_available() and level != 2 and (bool(question) or (level >= 3 and issue is None))
    if use_llm:
        diag = ""
        if diagnostics:
            diag = "Editor diagnostics:\n" + "\n".join(f"- line {d.get('line')}: {d.get('message')}" for d in diagnostics[:5]) + "\n"
        prompt = HINT_PROMPT.format(
            concepts="\n".join(f"- {c['label']}" for c in concepts) or "- (not specified)",
            code=code[:4000], diagnostics=diag, focus=focus["label"],
            finding=issue["message"] if issue else "nothing specific yet",
            question=f"The student asks: {question}\n" if question else "",
            hint_level=level, level_instruction=HINT_LEVEL_INSTRUCTIONS[level])
        max_sentences = 2 if level == 1 else 4
        raw = backend.chat(_sys_prompt(profile, max_sentences), prompt, temperature=0.6, max_new_tokens=160)
        text = sanitize_llm_hint(raw, exercise.get("code_prof", ""), code, max_sentences=max_sentences)
        if text and len(text.split()) >= 5:
            source = "llm"
        else:
            text = None
    if text is None:
        text = sanitize_hint(rule_text, exercise.get("code_prof", ""), code, max_code_lines=8)

    learner.record_hint(profile, focus, level)
    profile["hint_state"][str(exercise["id"])] = {"level": level, "focus": focus["key"],
                                                  "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    learner.log_event(profile, "hint", exercise_id=exercise["id"], concept=focus["key"], level=level)
    escalate = level >= MAX_HINT_LEVEL
    return {
        "hint": text,
        "level": level,
        "level_name": LEVEL_NAMES[level],
        "max_level": MAX_HINT_LEVEL,
        "concept": focus["label"],
        "concept_key": focus["key"],
        "line": issue.get("line") if issue else None,
        "check_question": _check_question(focus, n_hints),
        "escalate": escalate,
        "escalate_message": "Still stuck after the full hint ladder? That's completely normal. Use \"Ask my professor\" and they will see your code and where you are blocked." if escalate else None,
        "source": source,
    }

# ------------------------------------------------------------ explanations

def explain(profile, concept, exercise=None):
    rule_text = style_explanation(profile, concept["topic"]) + "\n\n**Check yourself:** " + _pick(topic(concept["topic"])["socratic"], 0)
    text, source = None, "rules"
    # known topics: curated explanation; the LLM only covers concepts the bank does not know
    if backend.llm_available() and concept["topic"] == "general":
        prompt = EXPLAIN_PROMPT.format(concept=concept["label"],
                                       style_instruction=STYLE_INSTRUCTIONS.get(profile["style"], STYLE_INSTRUCTIONS["examples"]))
        raw = backend.chat(_sys_prompt(profile, 8), prompt, temperature=0.7, max_new_tokens=350)
        text = sanitize_hint(raw, (exercise or {}).get("code_prof", ""), "", max_code_lines=8, max_words=260)
        if text and len(text.split()) >= 15:
            source = "llm"
        else:
            text = None
    learner.log_event(profile, "explain", concept=concept["key"])
    return {"concept": concept["label"], "topic": concept["topic"], "style": profile["style"],
            "level": learner.effective_level(profile), "explanation": text or rule_text, "source": source}
