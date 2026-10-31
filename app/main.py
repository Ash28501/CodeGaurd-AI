from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .reviewer import MODEL_NAME, ReviewError, review_code

app = FastAPI(title="CodeGuard AI - Local Code Reviewer")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/review")
async def review(code: str = Form(...), language: str = Form("Python")):
    try:
        result = await review_code(code, language)
    except ReviewError as exc:
        raise HTTPException(status_code=502 if "Ollama" in str(exc) or "JSON" in str(exc) else 400, detail=str(exc)) from exc
    return {"status": "success", "review": result, "language": language, "model_used": MODEL_NAME}
