"""Anthropic Claude client"""
from anthropic import Anthropic
from typing import Dict, Any, Optional
from app.llm.base import BaseLLMClient
from app.config import settings


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic Claude API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.client = Anthropic(api_key=self.api_key)

    def invoke(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None
    ) -> tuple[str, int, int]:
        """Invoke Claude with a prompt"""

        config = config or {}
        model = config.get("model", "claude-sonnet-4-20250514")
        max_tokens = config.get("max_tokens", 4096)
        temperature = config.get("temperature", 0.7)

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text
            prompt_tokens = response.usage.input_tokens
            response_tokens = response.usage.output_tokens

            return response_text, prompt_tokens, response_tokens

        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
