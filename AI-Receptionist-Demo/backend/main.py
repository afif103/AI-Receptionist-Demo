from fastapi import FastAPI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv('config/.env')

app = FastAPI()

class ChatRequest(BaseModel):
    input: str

@app.post("/chat")
def chat(request: ChatRequest):
    print(f"Received input: {request.input}")
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Error: GROQ_API_KEY not set")
            return {"response": "Error: GROQ_API_KEY not set in environment."}
        print("API key found")
        # LLM
        llm = ChatGroq(model="llama-3.1-8b-instant", api_key=api_key)
        print("LLM initialized")
        # Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI receptionist. Greet visitors and assist with basic inquiries like checking availability."),
            ("human", "{input}"),
        ])
        # Chain
        chain = prompt | llm
        print("Chain created")
        response = chain.invoke({"input": request.input})
        print(f"Response type: {type(response)}, content: {getattr(response, 'content', 'no content')}")
        content = response.content if hasattr(response, 'content') else str(response)
        return {"response": content}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {"response": f"Error: {str(e)}"}

@app.get("/test")
def test():
    return {"status": "Backend is running"}