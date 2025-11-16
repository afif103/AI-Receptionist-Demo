# app.py
import streamlit as st
import requests
import os
from threading import Thread
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import time

# ========================================
# 1. FastAPI Backend
# ========================================
api = FastAPI()

class ChatRequest(BaseModel):
    input: str

@api.post("/chat")
async def chat(request: ChatRequest):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {"response": "Error: GROQ_API_KEY missing"}

        llm = ChatGroq(model="llama-3.1-8b-instant", api_key=api_key)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI receptionist. Greet visitors and assist with basic inquiries."),
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
    return {"status": "Backend is running!"}

# ========================================
# 2. Run FastAPI in Background (Robust)
# ========================================
def run_server():
    config = uvicorn.Config(api, host="0.0.0.0", port=8000, log_level="error")
    server = uvicorn.Server(config)
    server.run()

# Start server only once
if "server_started" not in st.session_state:
    st.session_state.server_started = True
    thread = Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(3)  # Give server time to bind

# ========================================
# 3. Streamlit UI
# ========================================
st.title("AI Receptionist MVP")
st.write("Chat with the AI receptionist below.")

# Use 127.0.0.1 (not localhost) — works in Streamlit Cloud
BACKEND_URL = "http://127.0.0.1:8000"

# Optional: Show backend status
with st.expander("Backend Status"):
    try:
        test_resp = requests.get(f"{BACKEND_URL}/test", timeout=5)
        if test_resp.status_code == 200:
            st.success("Backend connected: " + test_resp.json()["status"])
        else:
            st.warning(f"Backend responded: {test_resp.status_code}")
    except:
        st.error("Backend not responding yet. Retrying...")

user_input = st.text_input("Your message:")
if st.button("Send"):
    if user_input.strip():
        with st.spinner("Thinking..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"input": user_input},
                    timeout=30
                )
                resp.raise_for_status()
                st.success("Receptionist: " + resp.json()["response"])
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")
    else:
        st.info("Please type a message.")
