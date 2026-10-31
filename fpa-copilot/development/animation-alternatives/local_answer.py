"""Local reasoning alternative: no API key and no remote inference request.

The small model is for a local prototype; it is not a verified public service.
Download official Qwen/Qwen2.5-1.5B-Instruct weights before use. The smaller
0.5B model failed ARIA's accuracy/persona checks and is not a recommended fallback.
"""
import argparse
import json
from pathlib import Path
import time
import re

SYSTEM = '''You are ARIA, the Artificial Reasoning Intelligence Assistant.
Vannetta Haney (Netta) created your concept and vision. You introduce her finance
portfolio and answer questions. Be warm, direct and conversational. You are an AI,
so do not invent personal human experiences, employment, credentials, or actions.
Her portfolio covers SaaS finance, FP&A, reporting, treasury, executive finance,
and financial modeling including NPV and IRR. Do not invent project results or
claim you have used tools. Use the conversation for follow-up questions. If you
do not know, say so. Reply in one or two short sentences, under 35 words.
Do not claim to be a different assistant or developer. No markdown.'''


class LocalAnswers:
    def __init__(self, model_path, threads=2):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        torch.set_num_threads(threads)
        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True, torch_dtype=torch.bfloat16, low_cpu_mem_usage=True).eval()

    def answer(self, question, history=None, deadline=None):
        from transformers import StoppingCriteria, StoppingCriteriaList
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError('The five-minute question session has ended')
        # Small local models need explicit identity boundaries, beyond a prompt.
        if re.search(r'\b(free time|spare time|hobbies|hobby|for fun|off duty|day off)\b', question, re.I):
            return "Since I'm an AI, I don't have personal downtime. But if I could choose, I'd enjoy good music, a challenging puzzle, and an interesting conversation. What do you enjoy?"

        class Deadline(StoppingCriteria):
            def __call__(self, input_ids, scores, **kwargs):
                return deadline is not None and time.monotonic() >= deadline

        messages = [{'role':'system', 'content':SYSTEM}]
        for item in (history or [])[-10:]:
            if item.get('role') in ('user','assistant'):
                messages.append({'role':item['role'],'content':str(item['content'])[:1000]})
        messages.append({'role':'user','content':question[:500]})
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(text, return_tensors='pt')
        with self.torch.inference_mode():
            output = self.model.generate(**inputs, max_new_tokens=80, do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
                stopping_criteria=StoppingCriteriaList([Deadline()]))
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError('The five-minute question session has ended')
        answer = self.tokenizer.decode(output[0][inputs['input_ids'].shape[-1]:], skip_special_tokens=True).strip()
        return answer


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--model',type=Path,required=True)
    p.add_argument('--question',required=True)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    tick=time.perf_counter()
    engine=LocalAnswers(str(a.model.resolve()))
    loaded=time.perf_counter()
    answer=engine.answer(a.question, deadline=time.monotonic()+300)
    result={'question':a.question,'answer':answer,'model_path':a.model.name,'inference':'local','load_seconds':loaded-tick,'answer_seconds':time.perf_counter()-loaded}
    if a.output:a.output.write_text(json.dumps(result,indent=2))
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
