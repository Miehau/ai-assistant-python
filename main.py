import logging

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from app.agent import Agent, AgentRequest
from app.config import load_config
from app.models import ChatRequest, ChatResponse
from app.openrouter import OpenRouterProvider
from app.tools.horoscope import HoroscopeTool


app = FastAPI()
config = load_config()
agent = Agent(provider=OpenRouterProvider(config.openrouter), tools=[HoroscopeTool()])
logging.basicConfig(level=logging.INFO)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    agent_message = AgentRequest(message=request.message)
    response = await agent.answer(agent_message)
    return ChatResponse(answer=response)


@app.post("/chat_async")
async def chat_async(request: ChatRequest):
    agent_request = AgentRequest(message=request.message)
    return StreamingResponse(
        agent.answer_async(agent_request),
        media_type="text/plain"
    )