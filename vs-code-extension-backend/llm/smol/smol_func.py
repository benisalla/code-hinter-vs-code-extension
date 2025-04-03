import torch
from llm.smol.smol import SmolLM
from llm.smol.smol_instance import smol

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def evaluate_code(concepts, st_code, temperature=1.0, max_new_tokens=500, top_p=0.9, do_sample=True):
    try:
        response = smol.evaluate_code(
            concepts=concepts,
            code=st_code,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            top_p=top_p,
            do_sample=do_sample
        )
        return response
    except Exception as e:
        raise Exception("Evaluation failed: " + str(e))
    
# ==========================================#
# This is the original code
# ==========================================#
# def evaluate_code():
#     data = request.json
#     if not data or not data.get("concepts") or not data.get("st_code"):
#         return jsonify({"error": "Concepts and code are required."}), 400
#     try:
#         response = smol.evaluate_code(
#             concepts=data["concepts"],
#             code=data["st_code"],
#             temperature=1.0,
#             max_new_tokens=500,
#         )
#         print("------------------------------")
#         print(f"response is : {response}")
#         return jsonify({"response": response}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



def compare_code(pr_code, st_code, temperature=0.6, max_new_tokens=200, top_p=0.9, do_sample=True):
    """
    Compares professor and student code using the LLM.
    """
    try:
        response = smol.compare_code(
            pr_code=pr_code,
            st_code=st_code,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            top_p=top_p,
            do_sample=do_sample
        )
        return response
    except Exception as e:
        raise Exception("Comparison failed: " + str(e))
    
# ==========================================#
# This is the original code
# ==========================================#
# def compare_code():
#     data = request.json
#     if not data or 'pr_code' not in data or 'st_code' not in data:
#         return jsonify({"error": "Both 'professor_code' and 'student_code' are required."}), 400

#     try:
#         response = smol.compare_code(
#             pr_code=data["pr_code"],
#             st_code=data["st_code"],
#             temperature=0.6, 
#             max_new_tokens=200
#         )
#         return jsonify({"response": response}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



def complete_code(code, temperature=0.9, max_new_tokens=200, top_p=0.9, do_sample=True):
    try:
        response = smol.complete_code(
            code=code,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            top_p=top_p,
            do_sample=do_sample
        )
        return response
    except Exception as e:
        raise Exception("Completion failed: " + str(e))
