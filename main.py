from fastapi import FastAPI

from app.agent import Agent, AgentRequest
from app.models import ChatRequest, ChatResponse
from app.openrouter import OpenRouter


app = FastAPI()
agent = Agent(provider=OpenRouter())

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    agent_message = AgentRequest(message=request.message)
    response = agent.answer(agent_message)
    return ChatResponse(answer=response)
