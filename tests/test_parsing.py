import pytest

from app.parsing import build_prompt, normalize_review, parse_review


def test_parses_plain_json():
    review = parse_review('{"score": 8, "summary": "Fine.", "issues": []}')
    assert review["score"] == 8 and review["issues"] == []


def test_parses_fenced_json_and_surrounding_prose():
    text = 'Here you go:\n```json\n{"score": 3, "summary": "Risky.", "issues": []}\n```\nThanks'
    assert parse_review(text)["score"] == 3
    assert parse_review('Sure! {"score": 4, "summary": "x"} done')["score"] == 4


def test_rejects_non_json():
    with pytest.raises(ValueError):
        parse_review("I could not review this code.")


def test_normalizes_bad_fields_and_sorts_by_severity():
    review = normalize_review(
        {
            "score": "42",
            "issues": [
                {"severity": "LOW", "category": "style", "line": "3", "description": "naming"},
                {"severity": "catastrophic", "category": "weird", "description": "something"},
                {"severity": "critical", "category": "security", "line": None, "description": "SQL injection"},
                {"severity": "high", "description": "   "},  # empty description dropped
                "not a dict",
            ],
        }
    )
    assert review["score"] == 10  # clamped to 1..10
    assert [i["severity"] for i in review["issues"]] == ["critical", "medium", "low"]
    assert review["issues"][1]["category"] == "maintainability"  # unknown category coerced
    assert review["issues"][2]["line"] == 3
    assert review["summary"] == "No summary provided."


def test_prompt_numbers_lines_and_names_language():
    prompt = build_prompt("a = 1\nb = 2", "Python")
    assert "Python" in prompt
    assert "   1 | a = 1" in prompt and "   2 | b = 2" in prompt
