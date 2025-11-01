"""DeepSeek AI client"""
from openai import OpenAI
from typing import Dict, Any, Optional
from app.llm.base import BaseLLMClient
from app.config import settings


class DeepSeekClient(BaseLLMClient):
    """Client for DeepSeek AI API (OpenAI-compatible)"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.base_url = base_url or settings.DEEPSEEK_BASE_URL
        self.model = model or settings.DEEPSEEK_MODEL

        # DeepSeek API is OpenAI-compatible
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def invoke(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None
    ) -> tuple[str, int, int]:
        """Invoke DeepSeek with a prompt"""

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

            message = response.choices[0].message

            # DeepSeek Reasoner has both content and reasoning_content fields
            response_text = message.content or ""

            # If there's reasoning_content, combine it with the response
            # This helps with debugging and provides full context
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                if response_text:
                    # Both exist: combine them
                    response_text = f"[Reasoning]\n{message.reasoning_content}\n\n[Response]\n{response_text}"
                else:
                    # Only reasoning exists: use it as response
                    response_text = message.reasoning_content

            prompt_tokens = response.usage.prompt_tokens
            response_tokens = response.usage.completion_tokens

            return response_text, prompt_tokens, response_tokens

        except Exception as e:
            raise Exception(f"DeepSeek API error: {str(e)}")
