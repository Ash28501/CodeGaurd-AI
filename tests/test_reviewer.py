"""Reviewer tests with a mocked Ollama server (run in CI where httpx is installed)."""

import asyncio
import json

import pytest

httpx = pytest.importorskip("httpx")

from app.reviewer import ReviewError, review_code  # noqa: E402


def _client(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def test_review_code_returns_normalized_review():
    captured = {}

    def handler(request):
        captured["body"] = json.loads(request.content)
        content = json.dumps(
            {
                "score": 4,
                "summary": "Has a bug.",
                "issues": [
                    {"severity": "high", "category": "bug", "line": 2, "description": "Division by zero", "suggestion": "Guard b"}
                ],
            }
        )
        return httpx.Response(200, json={"message": {"content": content}})

    review = asyncio.run(review_code("def f(a, b):\n    return a / b", client=_client(handler)))
    assert review["score"] == 4 and review["issues"][0]["line"] == 2
    assert captured["body"]["format"] == "json" and captured["body"]["stream"] is False


def test_review_code_wraps_connection_errors():
    def handler(request):
        raise httpx.ConnectError("refused")

    with pytest.raises(ReviewError, match="Ollama"):
        asyncio.run(review_code("x = 1", client=_client(handler)))


def test_review_code_rejects_empty_input():
    with pytest.raises(ReviewError):
        asyncio.run(review_code("   "))
