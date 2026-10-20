import os
import logging
from llm.smol.smol_instance import smol

log = logging.getLogger(__name__)

# "smol"    -> local Hugging Face model (CH_MODEL, SmolLM2-1.7B-Instruct by default)
# "offline" -> no LLM at all: the tutor answers from its rule-based knowledge bank
def backend_name():
    return os.getenv("CH_LLM_BACKEND", "smol").strip().lower()

def llm_available():
    return backend_name() != "offline"

def chat(sys_prompt, user_prompt, temperature=0.7, max_new_tokens=300):
    """Returns the model's answer, or None when no LLM is configured or it fails.
    Every tutor feature treats None as "use the rule-based fallback"."""
    if not llm_available():
        return None
    try:
        return smol.chat(sys_prompt, user_prompt, temperature=temperature, max_new_tokens=max_new_tokens)
    except Exception as e:
        log.warning("LLM call failed, falling back to rules: %s", e)
        return None
