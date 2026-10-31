import json
from pathlib import Path

from app.parsing import CATEGORIES

CASES = sorted(Path(__file__).parent.parent.joinpath("eval", "cases").glob("*.json"))


def test_eval_cases_are_well_formed():
    assert len(CASES) == 12
    for path in CASES:
        case = json.loads(path.read_text())
        assert case["expected_category"] in CATEGORIES
        assert case["keywords"] and all(k == k.lower() for k in case["keywords"])
        assert case["code"].strip()
