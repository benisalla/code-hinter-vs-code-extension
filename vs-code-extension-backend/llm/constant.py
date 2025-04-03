
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

MODEL_CHECKPOINT = "HuggingFaceTB/SmolLM2-1.7B-Instruct"

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