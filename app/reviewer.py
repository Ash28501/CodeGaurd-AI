import httpx
import json
from typing import Dict

# Best practical model for code review in 2026 (change if you pull a bigger one)
MODEL_NAME = "qwen2.5-coder:7b"   # Fast & very good for review
# MODEL_NAME = "deepseek-coder-v2:16b"  # Better quality (needs more RAM/GPU)

OLLAMA_URL = "http://localhost:11434/api/chat"

async def review_code(code: str, language: str = "Python") -> Dict:
    prompt = f"""You are a strict, senior software engineer (10+ years experience) performing a professional code review.

Review the following {language} code and return **only** valid JSON (no extra text).

Code:
```{language.lower()}
{code}"