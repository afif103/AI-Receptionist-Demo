# --------------------------------------------------------------
# app.py  –  Streamlit + FastAPI running in the same process
# --------------------------------------------------------------
import streamlit as st
import requests
import os
from threading import Thread
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# ------------------------------------------------------------------
# 1. FastAPI backend
# ------------------------------------------------------------------
api = FastAPI()

class ChatRequest(BaseModel):
    input: str

@api.post("/chat")
async def chat(request: ChatRequest):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {"response": "Error: GROQ_API_KEY not set"}

        llm = ChatGroq(model="llama-3.1-8b-instant", api_key=api_key)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI receptionist. Greet visitors and assist with basic inquiries like checking availability."),
            ("human", "{input}"),
        ])
        chain = prompt | llm
        result = chain.invoke({"input": request.input})
        content = getattr(result, "content", str(result))
        return {"response": content}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

@api.get("/test")
def test():
    return {"status": "Backend is running"}

# ------------------------------------------------------------------
# 2. Run FastAPI in a background thread (only once)
# ------------------------------------------------------------------
def run_uvicorn():
    uvicorn.run(api, host="0.0.0.0", port=8000, log_level="error")

if not st.session_state.get("server_started", False):
    thread = Thread(target=run_uvicorn, daemon=True)
    thread.start()
    st.session_state.server_started = True
   