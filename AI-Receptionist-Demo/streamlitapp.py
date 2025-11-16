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
import pandas as pd

# ========================================
# 1. Load Secrets (Safe & Hidden)
# ========================================
try:
    ADMIN_USERNAME = st.secrets["ADMIN_USERNAME"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
    EMPLOYEE_USERNAME = st.secrets["EMPLOYEE_USERNAME"]
    EMPLOYEE_PASSWORD = st.secrets["EMPLOYEE_PASSWORD"]
except:
    st.error("Missing secrets! Add ADMIN_USERNAME, ADMIN_PASSWORD, etc. in secrets.toml")
    st.stop()

# Define users from secrets
USERS = {
    ADMIN_USERNAME: {"password": ADMIN_PASSWORD, "role": "admin"},
    EMPLOYEE_USERNAME: {"password": EMPLOYEE_PASSWORD, "role": "employee"}
}

# ========================================
# 2. FastAPI Backend
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
# 3. Run FastAPI in Background
# ========================================
def run_server():
    config = uvicorn.Config(api, host="0.0.0.0", port=8000, log_level="error")
    server = uvicorn.Server(config)
    server.run()

if "server_started" not in st.session_state:
    st.session_state.server_started = True
    thread = Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(3)

# ========================================
# 4. Login System (Credentials from secrets)
# ========================================
if "user" not in st.session_state:
    st.title("AI Receptionist - Login")
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username")
    with col2:
        password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.user = username
            st.session_state.role = USERS[username]["role"]
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

# ========================================
# 5. Main App UI
# ========================================
BACKEND_URL = "http://127.0.0.1:8000"
st.title("AI Receptionist MVP")
st.write(f"Logged in as: **{st.session_state.user}** ({st.session_state.role})")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.spinner("Thinking..."):
        try:
            resp = requests.post(f"{BACKEND_URL}/chat", json={"input": user_input}, timeout=30)
            resp.raise_for_status()
            ai_response = resp.json()["response"]
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            with st.chat_message("assistant"):
                st.write(ai_response)
        except Exception as e:
            st.error(f"Error: {e}")

# ========================================
# 6. Admin-Only: Lead History
# ========================================
if st.session_state.role == "admin":
    st.divider()
    st.subheader("Lead History (Admin Only)")

    if "leads" not in st.session_state:
        st.session_state.leads = []

    # Save new lead
    if user_input and len(st.session_state.messages) >= 2:
        last_user_msg = st.session_state.messages[-2]["content"]
        last_ai_msg = st.session_state.messages[-1]["content"]
        if not st.session_state.leads or st.session_state.leads[-1]["message"] != last_user_msg:
            st.session_state.leads.append({
                "time": time.strftime("%H:%M"),
                "message": last_user_msg,
                "response": last_ai_msg
            })

    if st.session_state.leads:
        df = pd.DataFrame(st.session_state.leads)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No leads yet.")
