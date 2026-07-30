import hashlib
import time
from typing import Any, Dict, List

import ray
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@ray.remote(num_gpus=1)
class DAXWorker:
    def __init__(self, model_name: str, role: str, gpu_id: int):
        self.role = role
        self.gpu_id = gpu_id
        self.device = "cuda"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
        ).to(self.device)

    def infer(self, prompt: str, max_new_tokens: int = 256) -> Dict[str, Any]:
        start = time.time()
        tokens = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        out = self.model.generate(
            **tokens,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.2,
            top_p=0.9,
        )
        text = self.tokenizer.decode(out[0], skip_special_tokens=True)
        elapsed_ms = int((time.time() - start) * 1000)
        return {
            "role": self.role,
            "gpu_id": self.gpu_id,
            "latency_ms": elapsed_ms,
            "output_text": text,
            "output_hash": _sha(text),
        }


def run_parallel(workers: List[ray.actor.ActorHandle], prompt: str) -> List[Dict[str, Any]]:
    futures = [w.infer.remote(prompt) for w in workers]
    return ray.get(futures)
