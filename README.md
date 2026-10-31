# CodeGuard AI: Local AI Code Reviewer

A fully local, AI-powered code review assistant built with FastAPI and Ollama.

Paste a code snippet and get structured feedback on bugs, security issues, performance, and maintainability. Each finding includes a severity, a line number, and a suggested fix. The model runs on your machine, so your code never leaves it.

## Key Features

- **Runs entirely locally** on Ollama with Qwen2.5-Coder. No API keys, and no code is sent to a third party.
- **Structured, validated output.** Ollama's JSON mode constrains the response to JSON. The response is parsed, any invalid fields are corrected to fit the schema, and issues are sorted by severity.
- **Line-referenced findings.** The prompt numbers each line of code, so issues point to specific lines.
- **Safe rendering.** Model output is HTML-escaped before display, which prevents XSS from model text.
- **Clear errors.** The app returns a clear error when Ollama is down or the response is malformed, instead of failing silently.
- **Evaluation set:** 12 snippets with seeded bugs across Python, Java, and JavaScript. The eval script measures detection rate and latency.
- **CI:** GitHub Actions runs Ruff (lint and format checks), pytest with Ollama mocked, a smoke test, and the Docker build.

## Tech Stack

FastAPI · Ollama + Qwen2.5-Coder · httpx (async) · Jinja2 + Tailwind CSS · pytest · Ruff · GitHub Actions · Docker Compose

## Run Locally

```bash
ollama pull qwen2.5-coder:7b          # once
ollama serve                          # if not already running
pip install -r requirements.txt
uvicorn app.main:app --reload         # open http://localhost:8000
```

Or with Docker (this runs Ollama in a container too):

```bash
docker compose up --build
docker compose exec ollama ollama pull qwen2.5-coder:7b
```

| Env var | Default |
|---|---|
| `OLLAMA_URL` | `http://localhost:11434` |
| `CODEGUARD_MODEL` | `qwen2.5-coder:7b` |
| `CODEGUARD_TIMEOUT` | `180` (seconds) |

## API

```bash
curl -X POST http://localhost:8000/review \
  -F 'language=Python' -F 'code=def avg(xs): return sum(xs) / len(xs)'
```

```json
{
  "status": "success",
  "review": {
    "score": 6,
    "summary": "...",
    "issues": [{"severity": "high", "category": "bug", "line": 1, "description": "...", "suggestion": "..."}],
    "refactored_code": "..."
  },
  "model_used": "qwen2.5-coder:7b"
}
```

## Evaluation

```bash
python -m eval.run_eval
```

The eval runs 12 seeded-bug cases from `eval/cases/`. They cover SQL injection, a hardcoded secret, `eval` on user input, XSS through `innerHTML`, a mutable default argument, an off-by-one error, division by zero, an exception swallowed by a bare `except`, an O(n²) lookup, a Java resource leak, Java `==` string comparison, and a missing `await`.

For each case it reports whether the bug was detected, whether the category was correct, and how long the review took. Results are saved to `eval/results.json`. Record your results here, with the model and hardware you used.

## Tests

```bash
pip install pytest && pytest -q
```

## Project Structure

```text
app/
  parsing.py    prompt builder + JSON extraction/validation (no network deps)
  reviewer.py   Ollama client
  main.py       FastAPI app (/, /review, /health)
  templates/    web UI
eval/           seeded-bug cases + detection-rate script
tests/          pytest suite
.github/        CI
```
