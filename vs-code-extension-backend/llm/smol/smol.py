import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from llm.constant import (
    MODEL_CHECKPOINT, 
    EVALUATE_CLIENT_PROMPT, 
    EVALUATE_SYS_PROMPT, 
    SYS_COMPARE_PROMPT, 
    COMPARE_PROMPT, 
    CODE_COMPLETION_PROMPT,
    CODE_COMPLETION_SYS_PROMPT)
import threading

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class SmolLM:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_CHECKPOINT)
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_CHECKPOINT).to(DEVICE)

    def apply_chat_template(self, sys_prompt, user_prompt):
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return self.tokenizer.apply_chat_template(messages, tokenize=False)

    def evaluate_code(self, concepts, code, temperature=0.9, max_new_tokens=200, top_p=0.9, do_sample=True):
        # Prepare the user prompt
        user_prompt = EVALUATE_CLIENT_PROMPT.format(concepts=concepts, code=code)

        # Prepare input using chat template
        in_text = self.apply_chat_template(EVALUATE_SYS_PROMPT, user_prompt)
        inputs = self.tokenizer.encode(in_text, return_tensors="pt").to(DEVICE)

        # Generate response
        outputs = self.model.generate(
            inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=do_sample,
        )

        str_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        output =str_output.split("\nassistant")[-1].strip()

        return output
    
    def compare_code(self, pr_code, st_code, temperature=0.5, max_new_tokens=200, top_p=0.9, do_sample=True):
        # Prepare the user prompt
        user_prompt = COMPARE_PROMPT.format(pr_code=pr_code, st_code=st_code)

        # Prepare input using chat template
        in_text = self.apply_chat_template(SYS_COMPARE_PROMPT, user_prompt)
        inputs = self.tokenizer.encode(in_text, return_tensors="pt").to(DEVICE)

        # Generate response
        outputs = self.model.generate(
            inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=do_sample,
        )

        # Decode and return the response
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        result = result.split("\nassistant\n")[-1]
        try:
            score = int(result)
            if score < 0:
              score = 0
            if score > 100:
              score = 100
        except ValueError:
            print("Invalid score format:", result)
            score = 0

        return score
    
    
    def complete_code(self, code, temperature=0.9, max_new_tokens=512, top_p=0.9, do_sample=True):
            # Create a prompt that instructs the model to complete the code snippet.
            user_prompt = CODE_COMPLETION_PROMPT.format(code=code)
            
            # Prepare the input text using the chat template.
            in_text = self.apply_chat_template(CODE_COMPLETION_SYS_PROMPT, user_prompt)
            inputs = self.tokenizer.encode(in_text, return_tensors="pt").to(DEVICE)
            
            # Generate the output from the model.
            outputs = self.model.generate(
                inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
            )
            
            # Decode the generated tokens to a string.
            str_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the relevant completion part. This logic is similar to evaluate_code.
            completion = str_output.split("\nassistant")[-1].strip()
            
            return completion


    def stream_complete_code(self, code, temperature=0.9, max_new_tokens=512, top_p=0.9, do_sample=True):
        """
        Streaming version of complete_code.
        Yields generated text chunks as they are produced.
        """
        # Create a prompt that instructs the model to complete the code snippet.
        user_prompt = f"Complete the following code snippet:\n\n{code}\n"
        # Prepare the input text using the chat template.
        in_text = self.apply_chat_template(SYS_PROMPT, user_prompt)
        inputs = self.tokenizer.encode(in_text, return_tensors="pt").to(DEVICE)
        
        # Initialize a streamer that will yield new text chunks.
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        # Start generation in a background thread.
        generation_thread = threading.Thread(
            target=self.model.generate,
            kwargs={
                "inputs": inputs,
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": do_sample,
                "streamer": streamer
            }
        )
        generation_thread.start()
        
        # Yield each chunk as it comes in.
        for chunk in streamer:
            yield chunk