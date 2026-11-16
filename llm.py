"""One small helper to talk to the AI model through OpenRouter (free models)."""

import json
import re
import time

from openai import OpenAI

import config

_client = None


def _get_client():
    global _client
    if _client is None:
        if not config.LLM_API_KEY:
            raise RuntimeError("LLM_API_KEY is missing in .env")
        _client = OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL,
            # Optional headers OpenRouter uses to show your app name on its dashboard.
            default_headers={"HTTP-Referer": "https://github.com/m-bhavyaa/gopratle-agent",
                             "X-Title": "GoPratle BDR Agent"},
        )
    return _client


def _clean(text):
    """Free models sometimes add <think>...</think> reasoning or ```json fences. Remove them."""
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.DOTALL)
    return text.replace("```json", "").replace("```", "").strip()


def _to_json(text):
    """Turn the model's answer into a dict, even if it wrote extra words around the JSON."""
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"AI did not return JSON: {text[:200]}")
    return json.loads(match.group(0))


def ask(prompt, want_json=False, attempts=3):
    """Send a prompt, get back text (or a Python dict if want_json=True).
    Free models can be busy (error 429), so we retry a few times."""
    extra = {"response_format": {"type": "json_object"}} if want_json else {}
    for attempt in range(1, attempts + 1):
        try:
            response = _get_client().chat.completions.create(
                model=config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                **extra,
            )
            text = _clean(response.choices[0].message.content)
            if not text:
                raise ValueError("AI returned an empty answer")
            return _to_json(text) if want_json else text
        except Exception as error:
            if attempt == attempts:
                raise RuntimeError(f"AI call failed after {attempts} tries: {error}") from error
            print(f"   [AI busy or bad answer, retrying in {5 * attempt}s] {error}")
            time.sleep(5 * attempt)
