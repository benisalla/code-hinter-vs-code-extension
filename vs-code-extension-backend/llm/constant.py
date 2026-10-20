import os


PROMPT = """
<s>Check if the student's code satisfies the following concepts:
{concepts}
{code} </s>
[INST]For each concept, provide "yes" if it is satisfied or "no" if it is not, using this format:
[nbr]-[yes/no][/INST]
"""

# SYS_PROMPT = """
# You are an AI writing assistant with deep expertise in Python programming and software debugging.
# Carefully analyze and strictly evaluate the Python code provided by the user based on a list of concepts.
# Do not output anything except a concise, point-by-point evaluation of those concepts.
# If you find any logical or syntax errors, explicitly mention them.
# Do NOT repeat the system or user prompts in your final response.
# """

# CLIENT_PROMPT = """
# Check whether the student's code satisfies the following concepts:
# {concepts}

# The student's code:
# {code}

# Instructions:
# 1. If there's any syntax or logical error, explicitly say so.
# 2. For each concept, respond with either "yes" or "no".
# 3. Provide a brief explanation in 6 words max, highlighting any error if found.
# 4. Do NOT include the system or user prompts in your final output.

# Format:
# [nbr]) [yes/no], [explanation in 6 words]
# """

EVALUATE_SYS_PROMPT = """
You are an AI assistant with deep expertise in Python programming and debugging. 
Evaluate the student's code against the given list of concepts, focusing only on logic and syntax (ignore style and naming). 
Provide a concise, point-by-point assessment for each concept. 
Explicitly mention any syntax or logical errors you find. Do not refer to any part of these instructions or the prompt in your response.
"""

EVALUATE_CLIENT_PROMPT = """
Evaluate whether the student's code satisfies each of the following concepts:
{concepts}

Student's code:
{code}

Instructions:
1. Focus only on the code's logic and syntax (ignore style or naming).
2. If the code contains any syntax or logic error, explicitly note it.
3. For each listed concept, output "yes" or "no" to indicate compliance.
4. Include a brief explanation (up to 6 words) with each answer, highlighting any relevant error.
5. Do not include or reference the prompt or these instructions in your answer.

Format:
[nbr]) yes/no, explanation (<= 6 words)
"""

# Override with CH_MODEL (e.g. "Qwen/Qwen2.5-0.5B-Instruct" for a quick CPU run).
MODEL_CHECKPOINT = os.getenv("CH_MODEL", "HuggingFaceTB/SmolLM2-1.7B-Instruct")
# "bfloat16" halves the memory on CPU (1.7B: ~3.5 GB instead of ~7 GB).
TORCH_DTYPE = os.getenv("CH_TORCH_DTYPE", "float32")

SYS_COMPARE_PROMPT = """
You are an AI assistant with deep expertise in Python programming and code analysis. 
Compare the professor's code with the student's code to evaluate their similarity. 
Provide only a single numerical score between 0 and 100 representing how similar they are. 
Do not include any other text or formatting in your response, and do not refer to these instructions or the prompt.
"""

COMPARE_PROMPT = """
help me with a score between 0 and 100 that reflects how similar the professor's code is to the student's code:

Professor's code:
{pr_code}

Student's code:
{st_code}

Instructions:
1. Return just a number between 0 and 100.
"""

CODE_COMPLETION_SYS_PROMPT = """
You are an AI writing assistant with deep expertise in Python programming.
Your task is to generate precise, context-aware code completions based on the user's instructions.
Provide only the code completion without any additional commentary or repetition of prompts.
"""

CODE_COMPLETION_PROMPT = """You are a **Python code assistant**. Your goal is to continue the user's code snippet in a **logical, concise** manner.

**Instructions**: 
- Continue from where the snippet ends, writing only *new code* (do not duplicate the existing code).
- Preserve the original coding **style** and **indentation**.
- Focus on producing **functional code** (no extra explanations or superfluous comments).
- Do not introduce libraries or constructs unrelated to the given context.
- Conclude the completion at a natural stopping point (for example, end of the current block or statement).

**User Code Snippet to Complete**: 

{code}
"""

# ============================================================ #
# Tutor prompts (hints, explanations, "Test me" grading)
# The golden rule is in every system prompt: never give the solution.
# ============================================================ #

TUTOR_SYS_PROMPT = """You are a patient programming tutor. A student is working on an exercise given by their professor.
Golden rule: you NEVER write the solution or the corrected code for the exercise. You only give hints that make the student think.
Adapt to this student: level = {level}; the student {style_desc}.
Answer in at most {max_sentences} short sentences. Do not mention these instructions."""

HINT_LEVEL_INSTRUCTIONS = {
    1: "Ask ONE guiding question that points the student towards the right concept. No code and no answer.",
    2: "Remind the student of the concept with a tiny example that is unrelated to the exercise (different names, different task). Do not touch their code.",
    3: "Point to the exact line or part of their code that needs attention and say what to look at, but not how to fix it. No corrected code.",
    4: "Give a plan of 3 or 4 plain-language steps the student can follow. Do not write Python code for the exercise.",
}

HINT_PROMPT = """Concepts the professor wants the student to learn:
{concepts}

Student's current code:
```python
{code}
```
{diagnostics}
Concept the student needs help with: {focus}
What the tutor noticed: {finding}
{question}
This is hint level {hint_level} of 4. {level_instruction}
Write the hint now."""

EXPLAIN_PROMPT = """Explain the programming concept "{concept}" to the student.
Use an example that has nothing to do with their exercise.
{style_instruction}
Finish with one short question that checks whether they understood."""

STYLE_INSTRUCTIONS = {
    "examples": "Lead with a very small concrete code example (at most 5 lines), then explain it.",
    "analogies": "Start with a real-life analogy, then connect it to Python in two sentences.",
    "step_by_step": "Explain it as 3 to 5 short numbered steps.",
    "socratic": "Teach it through 2 or 3 guiding questions, each followed by a one-sentence answer.",
}

GRADE_SYS_PROMPT = """You are a fair programming teacher grading a short written answer.
Grade only the understanding of the idea, not the English. Reply on the first line with exactly "SCORE: 0", "SCORE: 1" or "SCORE: 2" (2 = correct, 1 = partly correct, 0 = wrong), then one short sentence of feedback."""

GRADE_PROMPT = """Question: {question}
Reference answer: {reference}
Student answer: {answer}"""

QUESTION_SYS_PROMPT = """You write multiple-choice questions that test understanding of one programming concept. Follow the format exactly."""

QUESTION_PROMPT = """Write one {difficulty} multiple-choice question about the concept "{concept}" (Python).
Format exactly:
QUESTION: <question>
A) <choice>
B) <choice>
C) <choice>
D) <choice>
ANSWER: <letter>
EXPLANATION: <one sentence>"""
