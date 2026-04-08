
### 3. app/main.py

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .reviewer import review_code

app = FastAPI(title="CodeGuard AI - Local Code Reviewer")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/review")
async def review(code: str = Form(...), language: str = Form("Python")):
    review_result = await review_code(code, language)
    return {
        "status": "success",
        "review": review_result,
        "language": language,
        "model_used": MODEL_NAME
    }