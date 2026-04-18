from fastapi import FastAPI
from pydantic import BaseModel

from agent import Agent, AgentRequest
from openrouter import OpenRouter


app = FastAPI()
agent = Agent(provider=OpenRouter())

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/health")
def health():
    return {"status": "ok"}



class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(request: ChatRequest):
    agent_message = AgentRequest(message=request.message)
    response = agent.answer(agent_message)
    return {"answer" : response}