"""
LLM provider abstraction supporting OpenAI, Anthropic, and Google Generative AI.
This isolates provider-specific client code and presents a unified async API.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import asyncio

from config import settings


class LLMClient:
    """Unified asynchronous LLM client with minimal surface area."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = (provider or settings.llm_provider).lower()
        self.model = model or settings.llm_model

        if self.provider == "openai":
            from openai import AsyncOpenAI  # lazy import

            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif self.provider == "anthropic":
            from anthropic import AsyncAnthropic

            self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        elif self.provider == "google":
            import google.generativeai as genai

            genai.configure(api_key=settings.google_api_key)
            self._client = genai
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.1, max_tokens: int = 2000) -> str:
        """Send a chat-style request and return text content."""
        if self.provider == "openai":
            resp = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content

        if self.provider == "anthropic":
            resp = await self._client.messages.create(
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=messages,
            )
            return resp.content[0].text

        if self.provider == "google":
            # Simple wrapper using the new GenerativeModel API
            model = self._client.GenerativeModel(self.model)
            # Convert messages to a single prompt
            prompt = "\n".join([m.get("content", "") for m in messages])
            resp = await asyncio.get_running_loop().run_in_executor(None, lambda: model.generate_content(prompt))
            return getattr(resp, "text", "") or ""

        raise RuntimeError("Unsupported provider path")


class EmbeddingClient:
    """Embeddings abstraction for vector stores."""

    def __init__(self, provider: Optional[str] = None, embedding_model: Optional[str] = None):
        self.provider = (provider or settings.llm_provider).lower()
        self.embedding_model = embedding_model or settings.embedding_model

        if self.provider == "openai":
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif self.provider == "google":
            import google.generativeai as genai

            genai.configure(api_key=settings.google_api_key)
            self._client = genai
        else:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def embed(self, texts: List[str]) -> List[List[float]]:
        if self.provider == "openai":
            resp = await self._client.embeddings.create(model=settings.embedding_model, input=texts)
            return [d.embedding for d in resp.data]

        if self.provider == "google":
            model = self._client.GenerativeModel("text-embedding-004")
            loop = asyncio.get_running_loop()
            # The Google SDK does not provide a batch async embedding helper; simulate
            def _embed_one(t: str):
                return model.embed_content(t).embedding

            return await asyncio.gather(*[loop.run_in_executor(None, _embed_one, t) for t in texts])

        # Fallback to OpenAI
        resp = await self._client.embeddings.create(model=settings.embedding_model, input=texts)
        return [d.embedding for d in resp.data]


