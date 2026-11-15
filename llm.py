"""One small helper to talk to the AI model."""

import json

from openai import OpenAI

import config

_client = None


def _get_client():
    global _client
    if _client is None:
        if not config.LLM_API_KEY:
            raise RuntimeError("LLM_API_KEY is missing in .env")
        _client = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)
    return _client


def ask(prompt, want_json=False):
    """Send a prompt, get back text (or a Python dict if want_json=True)."""
    extra = {"response_format": {"type": "json_object"}} if want_json else {}
    response = _get_client().chat.completions.create(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        **extra,
    )
    text = response.choices[0].message.content.strip()
    return json.loads(text) if want_json else text
