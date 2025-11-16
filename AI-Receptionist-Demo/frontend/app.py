import streamlit as st
import requests

st.title("AI Receptionist MVP")

st.write("Chat with the AI receptionist below.")

user_input = st.text_input("Your message:")

if st.button("Send"):
    if user_input:
        try:
            response = requests.post("http://localhost:8000/chat", json={"input": user_input})
            st.write("Receptionist:", response.json()["response"])
        except Exception as e:
            st.write("Error:", str(e))
    else:
        st.write("Please enter a message.")