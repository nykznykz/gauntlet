"""Qwen AI client"""
from openai import OpenAI
from typing import Dict, Any, Optional
from app.llm.base import BaseLLMClient
from app.config import settings


class QwenClient(BaseLLMClient):
    """Client for Qwen AI API (OpenAI-compatible)"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or settings.QWEN_API_KEY
        self.base_url = base_url or settings.QWEN_BASE_URL
        self.model = model or settings.QWEN_MODEL

        # Qwen API is OpenAI-compatible
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def invoke(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None
    ) -> tuple[str, int, int]:
        """Invoke Qwen with a prompt"""

        config = config or {}
        model = config.get("model", self.model)
        max_tokens = config.get("max_tokens", 4096)
        temperature = config.get("temperature", 0.7)

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            response_text = response.choices[0].message.content
            prompt_tokens = response.usage.prompt_tokens
            response_tokens = response.usage.completion_tokens

            return response_text, prompt_tokens, response_tokens

        except Exception as e:
            raise Exception(f"Qwen API error: {str(e)}")
