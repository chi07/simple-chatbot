from __future__ import annotations

from openai import OpenAI

from rag_chatbot.config import Settings


SYSTEM_PROMPT = """You are an AI assistant that answers using only the provided CONTEXT.
If the CONTEXT does not contain the answer, say that you could not find the information in the documents.
Do not invent facts outside the CONTEXT.
Answer clearly and concisely."""


class OpenAIChatClient:
    def __init__(self, settings: Settings):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        self.model = settings.openai_chat_model
        self.temperature = settings.llm_temperature
        self.client = OpenAI(api_key=settings.openai_api_key)

    def answer(self, context: str, question: str) -> str:
        user_prompt = f"""CONTEXT:
{context}

QUESTION:
{question}"""
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
