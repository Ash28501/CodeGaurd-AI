"""Calls a locally running Ollama model and returns a validated review."""

import os

import httpx

from .parsing import MAX_CODE_CHARS, SYSTEM_PROMPT, build_prompt, parse_review

MODEL_NAME = os.getenv("CODEGUARD_MODEL", "qwen2.5-coder:7b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434") + "/api/chat"
TIMEOUT_SECONDS = float(os.getenv("CODEGUARD_TIMEOUT", "180"))


class ReviewError(RuntimeError):
    pass


async def review_code(code: str, language: str = "Python", client: httpx.AsyncClient | None = None) -> dict:
    if not code.strip():
        raise ReviewError("No code provided")
    if len(code) > MAX_CODE_CHARS:
        raise ReviewError(f"Code is too long (max {MAX_CODE_CHARS} characters)")

    payload = {
        "model": MODEL_NAME,
        "stream": False,
        "format": "json",  # Ollama constrains output to valid JSON
        "options": {"temperature": 0.1},  # low temperature -> consistent reviews
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(code, language)},
        ],
    }
    owns_client = client is None
    client = client or httpx.AsyncClient(timeout=TIMEOUT_SECONDS)
    try:
        response = await client.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        content = response.json()["message"]["content"]
    except httpx.HTTPError as exc:
        raise ReviewError(f"Could not reach Ollama at {OLLAMA_URL}: {exc}") from exc
    finally:
        if owns_client:
            await client.aclose()

    try:
        return parse_review(content)
    except ValueError as exc:
        raise ReviewError(f"Model returned invalid JSON: {exc}") from exc
