from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from rag_chatbot.chatbot import RagChatbot
from rag_chatbot.config import get_settings


app = FastAPI(title="Simple RAG Chatbot", version="0.1.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class Source(BaseModel):
    id: str
    source: str
    title: str
    section: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> dict:
    try:
        bot = RagChatbot(get_settings())
        return bot.chat(request.message)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
