"""Detection-rate eval: 12 snippets, each with one seeded bug.

    ollama pull qwen2.5-coder:7b && ollama serve      # in another terminal
    pip install -r requirements.txt
    python -m eval.run_eval

A case counts as detected if any reported issue mentions one of the case's keywords.
The category check reports whether the model also labeled the issue correctly.
Also reports per-review latency. Results are written to eval/results.json.
"""

import asyncio
import json
import statistics
import time
from pathlib import Path

from app.reviewer import MODEL_NAME, review_code

CASES = sorted(Path(__file__).parent.joinpath("cases").glob("*.json"))


def matches(issue: dict, keywords: list[str]) -> bool:
    text = f"{issue['description']} {issue['suggestion']}".lower()
    return any(k in text for k in keywords)


async def main():
    rows, latencies = [], []
    for path in CASES:
        case = json.loads(path.read_text())
        start = time.perf_counter()
        review = await review_code(case["code"], case["language"])
        latencies.append(time.perf_counter() - start)
        hits = [i for i in review["issues"] if matches(i, case["keywords"])]
        rows.append(
            {
                "case": case["name"],
                "detected": bool(hits),
                "category_correct": any(i["category"] == case["expected_category"] for i in hits),
                "issues_reported": len(review["issues"]),
                "seconds": round(latencies[-1], 1),
            }
        )
        print(f"{'PASS' if hits else 'MISS'}  {case['name']:<20} {latencies[-1]:5.1f}s  {len(review['issues'])} issues")

    detected = sum(r["detected"] for r in rows)
    labeled = sum(r["category_correct"] for r in rows)
    summary = {
        "model": MODEL_NAME,
        "cases": len(rows),
        "detected": detected,
        "detection_rate": round(detected / len(rows), 3),
        "category_accuracy_on_detected": round(labeled / detected, 3) if detected else 0,
        "median_seconds_per_review": round(statistics.median(latencies), 1),
        "results": rows,
    }
    Path(__file__).parent.joinpath("results.json").write_text(json.dumps(summary, indent=2))
    print(
        f"\nDetected {detected}/{len(rows)} seeded bugs ({100 * detected / len(rows):.0f}%), "
        f"correct category on {labeled}/{detected}, median {summary['median_seconds_per_review']}s per review"
    )


if __name__ == "__main__":
    asyncio.run(main())
