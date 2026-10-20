# How the tutor works

The goal is a tutor that behaves like a good teaching assistant. It does not do the student's
work. It finds out what the student does not understand yet, explains it the way *this* student
understands, checks that they got it, and calls the professor when it is not enough.

## 1. From the professor's concepts to topics

The professor writes concepts as free text in the exercise (`"1. Class creation\n2. Method definition"`).
`tutor/concepts.py` splits them and maps each one to a topic of the knowledge bank by keyword
(`"Usage of class variables"` → `class_variables`, `"using assignment instead of comparison"` →
`comparison`). Mastery is tracked per *concept* (the professor's wording) and taught per *topic*.

## 2. The knowledge bank (`tutor/knowledge.py`)

For each of 16 Python topics (plus a general fallback):

| field | used for |
|---|---|
| `explain.beginner / intermediate / advanced` | the core explanation at the student's level |
| `analogy`, `example`, `steps`, `socratic` | the four learning styles |
| `pitfalls` | pinpoint hints when no static finding exists |
| `questions` | `Test me`: `mcq`, `output` (predict what is printed) and `open` (explain in your own words) |

Expected outputs of `output` questions are not typed by hand. The tutor computes them by running
the snippet in an isolated interpreter, and a test runs every snippet.

## 3. Hints: a ladder, never a solution

| step | name | content | source |
|---|---|---|---|
| 1 | nudge | one guiding question pointing at the concept | rules (LLM if the student asked a question) |
| 2 | concept | the concept in the student's style, on an unrelated example | curated bank only |
| 3 | pinpoint | the line to look at and what to look for | static analysis → rules; LLM when nothing was found |
| 4 | plan | plain-language steps | rules; LLM when nothing was found |
| (after 4) | escalate | "Ask my professor", sent with code + hints used | — |

The **focus concept** is what static analysis points at (syntax error or AST finding), otherwise
what the student's question is about, otherwise the exercise concept with the lowest mastery.
The editor's own diagnostics (Pylance etc.) are sent along and used when the backend finds nothing.

`tutor/code_analysis.py` checks for things like: assignment in a condition, a `def` with no name,
a misspelled `__init__`, a missing `self`, a class variable updated but never defined, `while True`
without `break`, `is` used against a literal, mutable default arguments, and functions defined but
never called. Each finding is phrased as a question about a line, never as the fix.

### Guardrails (`tutor/guardrails.py`)

Every hint is checked before it leaves the server:

1. lines similar (≥ 85 %) to a line of the professor's reference code that the student has not
   written yet are replaced by `… (this part is yours to write)`;
2. LLM hints: code blocks are removed, and inline code is kept only when it is a name, a single
   operator, or something the student already wrote (`` `b == 0` `` → `` `…` ``);
3. LLM hints are cut to 2–4 sentences, and anything after a markdown heading is dropped.

Why rules first: with a real small model (Qwen2.5-0.5B) the guardrails stopped every leak, but the
model still wrote misleading hints ("use the equality operator (`=`)") and explained class
variables backwards. Whenever the rules know the exact problem, their hint is used.

## 4. The learner model (`tutor/learner.py`)

Each concept has `mastery ∈ [0, 1]`, starting at a prior given by the declared level
(beginner 0.2, intermediate 0.4, advanced 0.6).

| evidence | update |
|---|---|
| quiz answer, credit c ∈ {0, ½, 1}, difficulty d | step = 0.15 + 0.07·d; right: m += step·(c − m); wrong: m −= step·m·(1 − c) |
| professor-criteria evaluation (yes/no per concept) | same rule at weight 0.6 |
| hint at ladder step L | m −= 0.02·L |

Status: `not_started` (no evidence), `learning` (< 0.5), `almost` (< 0.8), `mastered`.
After 6 pieces of evidence the **effective level** comes from the average mastery
(≥ 0.75 advanced, ≥ 0.45 intermediate) and replaces the declared level everywhere.

## 5. Test me (`tutor/quiz.py`)

- **Coverage:** every concept in scope gets at least one question. Up to 4 extra questions go to
  the weakest concepts (max 15).
- **Difficulty:** target = effective level, −1 if the concept's mastery < 0.35, +1 if ≥ 0.75.
  The question closest to the target wins, and a question already seen counts as 1.5 levels off.
  Extra questions that are 2+ levels too hard are skipped. Questions are ordered from easy to hard.
- **Scopes:** this exercise, everything the professor taught (all exercises of the student's
  professors), or only the concepts not mastered yet.
- **Grading:** MCQ and output questions are graded exactly. Open answers are graded by the LLM
  (score 0/1/2), but the LLM cannot give more credit than the answer's key ideas support (keyword
  groups). Without an LLM, the keyword groups do the grading.
- **After grading:** mastery before → after for each concept, the expected answer and explanation,
  a short re-teach in the student's style for every mistake, a possible level change, and the
  next step (review X, or "you're ready to submit").

## 6. The professor stays in the loop

- `Ask my professor` creates a help request with the message, the code and the hints already used.
- `GET /api/tutor/class/<prof_id>` lists concepts sorted by class mastery (weakest first), students
  who need attention (average mastery < 0.4), and open help requests. The professor replies with
  `PUT /api/tutor/help_request/<id>`, and the student sees the reply in *My learning progress*.
- Before the final submission (which is irreversible), the extension checks *readiness*: every
  concept of the exercise at mastery ≥ 0.6. If not, it offers `Test me` first.

## 7. Validation

`examples/06_simulated_students.py`: 60 simulated students with hidden per-concept knowledge
(a student who does not know a concept guesses MCQs and fails the rest), 4 course quizzes each.

| metric | value |
|---|---|
| Pearson r, estimated mastery vs. hidden knowledge | 0.86 |
| knows / doesn't know agreement at 0.5 | 82.5 % |
| effective level = true level | 86.7 % |
