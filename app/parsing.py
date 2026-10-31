"""Prompt construction and parsing/validation of the model's JSON review.

Kept free of network and web dependencies so it can be unit-tested directly.
"""

from __future__ import annotations

import json
import re

SEVERITIES = ("critical", "high", "medium", "low")
CATEGORIES = ("bug", "security", "performance", "maintainability", "style")

SYSTEM_PROMPT = (
    "You are a strict senior software engineer performing a professional code review. "
    "Respond with JSON only, no prose and no markdown fences."
)

SCHEMA_HINT = """{
  "score": <integer 1-10, overall quality>,
  "summary": "<one or two sentences>",
  "issues": [
    {
      "severity": "critical|high|medium|low",
      "category": "bug|security|performance|maintainability|style",
      "line": <integer line number or null>,
      "description": "<what is wrong and why it matters>",
      "suggestion": "<concrete fix>"
    }
  ],
  "refactored_code": "<improved version of the code, or null>"
}"""

MAX_CODE_CHARS = 20_000


def build_prompt(code: str, language: str) -> str:
    numbered = "\n".join(f"{i:>4} | {line}" for i, line in enumerate(code.splitlines(), 1))
    return (
        f"Review the following {language} code for bugs, security vulnerabilities, performance problems, "
        f"and maintainability issues. Reference line numbers from the left margin.\n\n"
        f"Return JSON exactly in this shape:\n{SCHEMA_HINT}\n\n"
        f"Code:\n{numbered}"
    )


def _extract_json(text: str) -> dict:
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise ValueError("model response contained no JSON object") from None
        return json.loads(text[start : end + 1])


def _as_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_review(raw: dict) -> dict:
    """Coerce a model response into the documented schema."""
    issues = []
    for item in raw.get("issues") or []:
        if not isinstance(item, dict) or not str(item.get("description", "")).strip():
            continue
        severity = str(item.get("severity", "medium")).lower()
        category = str(item.get("category", "maintainability")).lower()
        issues.append(
            {
                "severity": severity if severity in SEVERITIES else "medium",
                "category": category if category in CATEGORIES else "maintainability",
                "line": _as_int(item.get("line")),
                "description": str(item["description"]).strip(),
                "suggestion": str(item.get("suggestion", "")).strip(),
            }
        )
    issues.sort(key=lambda i: SEVERITIES.index(i["severity"]))
    score = _as_int(raw.get("score"), 5)
    return {
        "score": min(10, max(1, score)),
        "summary": str(raw.get("summary") or "No summary provided.").strip(),
        "issues": issues,
        "refactored_code": raw.get("refactored_code") or None,
    }


def parse_review(text: str) -> dict:
    return normalize_review(_extract_json(text))
