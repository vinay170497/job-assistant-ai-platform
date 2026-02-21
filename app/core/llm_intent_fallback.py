# app/core/llm_intent_fallback.py

import requests
import json
from typing import Tuple, List


class OllamaIntentFallback:
    """
    Minimal Ollama-based semantic fallback classifier.
    Only activates when explicitly called.
    """

    def __init__(self, model: str = "llama3.2:3b"):
        self.model = model
        self.base_url = "http://localhost:11434/api/generate"

    def classify(self, query: str, allowed_intents: List[str]) -> Tuple[str, float]:
        prompt = f"""
You are an intent classifier for a strictly job-oriented platform.

Allowed intents:
{allowed_intents}

Rules:
- Choose ONLY one intent from the allowed list.
- If unrelated to jobs/career, return "out_of_scope".
- Respond ONLY in valid JSON.
- Do NOT explain.

Output format:
{{"intent": "...", "confidence": 0.0}}

User Query:
{query}
"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(self.base_url, json=payload, timeout=30)
            response.raise_for_status()

            raw_output = response.json().get("response", "").strip()

            parsed = json.loads(raw_output)

            intent = parsed.get("intent")
            confidence = float(parsed.get("confidence", 0.5))

            return intent, confidence

        except Exception:
            return None, 0.0