"""Azure OpenAI client"""
from openai import AzureOpenAI
from typing import Dict, Any, Optional
from app.llm.base import BaseLLMClient
from app.config import settings


class AzureOpenAIClient(BaseLLMClient):
    """Client for Azure OpenAI API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_version: Optional[str] = None,
        deployment: Optional[str] = None
    ):
        self.api_key = api_key or settings.AZURE_OPENAI_API_KEY
        self.endpoint = endpoint or settings.AZURE_OPENAI_ENDPOINT
        self.api_version = api_version or settings.AZURE_OPENAI_API_VERSION
        self.deployment = deployment or settings.AZURE_OPENAI_DEPLOYMENT

        self.client = AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.endpoint,
            api_version=self.api_version
        )

    def invoke(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ) -> tuple[str, int, int]:
        """Invoke Azure OpenAI with a prompt"""

        config = config or {}
        # Use deployment from config or default
        deployment = config.get("model", self.deployment)
        max_tokens = config.get("max_tokens", 4096)
        temperature = config.get("temperature", 0.7)

        try:
            # Build messages array
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=deployment,  # This is the deployment name in Azure
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            response_text = response.choices[0].message.content
            prompt_tokens = response.usage.prompt_tokens
            response_tokens = response.usage.completion_tokens

            return response_text, prompt_tokens, response_tokens

        except Exception as e:
            raise Exception(f"Azure OpenAI API error: {str(e)}")
