# CodeGuard AI - Local AI Code Reviewer

An intelligent, fully local AI-powered code review assistant built with FastAPI and Ollama.

Paste any code snippet and get instant professional feedback on bugs, security issues, performance, style, and refactoring suggestions.

## ✨ Key Features
- Runs completely locally using Ollama (no data leaves your machine)
- Uses strong open-source coding model (Qwen2.5-Coder)
- Structured JSON review output
- Clean, modern web interface
- Prompt engineering for high-quality, consistent reviews

## 🛠 Tech Stack
- FastAPI (Python)
- Ollama + Qwen2.5-Coder (local LLM)
- Tailwind CSS + Jinja2
- httpx for async API calls

## 🚀 How to Run

1. Install Ollama → https://ollama.com
2. Pull the model:
   ```bash
   ollama pull qwen2.5-coder:7b