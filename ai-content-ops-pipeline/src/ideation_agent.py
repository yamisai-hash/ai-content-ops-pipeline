"""
ideation_agent.py — local-LLM content ideation.

Wraps a local Ollama model to turn brand + product context into a structured
content idea (hook, caption, format, hashtags). Local-first: no paid API, no
rate limits. If Ollama isn't reachable, it falls back to a deterministic
template so the pipeline still produces *something* reviewable (and says so).
"""
from __future__ import annotations

import json
from typing import Any, Dict

try:
    import requests  # used to call the local Ollama HTTP API
except Exception:  # pragma: no cover - requests is in requirements
    requests = None

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"

_PROMPT = """You are a content strategist for the streetwear brand {brand}.
Write ONE short-form idea for product "{product}".
Return JSON with keys: hook, caption, format (reel|story|image), hashtags (list).
Keep the voice terse and dark-luxury. No emojis."""


def _fallback(brand: str, product: str) -> Dict[str, Any]:
    return {
        "hook": f"{product} — made for the few.",
        "caption": "drop incoming. link in bio.",
        "format": "reel",
        "hashtags": [f"#{brand.lower()}", "#darkluxury", "#streetwear"],
        "source": "fallback-template",
    }


def propose_idea(brand: str, product: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """Return a structured content idea. Uses local Ollama; falls back cleanly."""
    if requests is None:
        return _fallback(brand, product)
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": model,
                  "prompt": _PROMPT.format(brand=brand, product=product),
                  "stream": False, "format": "json"},
            timeout=30,
        )
        resp.raise_for_status()
        idea = json.loads(resp.json()["response"])
        idea["source"] = f"ollama:{model}"
        return idea
    except Exception:
        # Local model unavailable -> deterministic fallback (clearly labeled).
        return _fallback(brand, product)
