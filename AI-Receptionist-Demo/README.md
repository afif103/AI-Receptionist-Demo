# AI Receptionist Demo Project

A demo AI receptionist MVP using Python, LangChain chain, and Groq LLM.

## Setup

1. Create virtual environment: `python -m venv .venv`
2. Activate: `.venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Set API key: Add `GROQ_API_KEY=your_key_here` to `config/.env`

## Run

- Backend: `uvicorn backend.main:app --reload`
- Frontend: `streamlit run frontend/app.py`

## Features

- Basic chat with AI receptionist
- Greetings and availability checks
- Error handling and logging

## Project Structure

- backend/: FastAPI backend with LangChain
- frontend/: Streamlit UI
- tools/: Placeholder for custom tools
- config/: Environment config
- memory/: Project memory for demo
- demo_summary.txt: Demo overview

## Demo

This is a demo project showcasing multi-agent workflow. For full features, expand with Chroma DB and LangGraph.