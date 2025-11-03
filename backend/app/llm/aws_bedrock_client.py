"""AWS Bedrock client for Claude"""
from anthropic import AnthropicBedrock
from typing import Dict, Any, Optional
from app.llm.base import BaseLLMClient
from app.config import settings


class AWSBedrockClient(BaseLLMClient):
    """Client for AWS Bedrock (Claude via Bedrock)"""

    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token or settings.AWS_BEARER_TOKEN_BEDROCK

        # Initialize Anthropic Bedrock client with bearer token
        self.client = AnthropicBedrock(
            # AWS Bedrock uses bearer token for authentication
            aws_access_key=self.bearer_token,
            aws_secret_key="",  # Not needed with bearer token
            aws_region="us-east-1",  # Default region
        )

    def invoke(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ) -> tuple[str, int, int]:
        """Invoke Claude via AWS Bedrock"""

        config = config or {}

        # Map to Bedrock model IDs
        model = config.get("model", "claude-sonnet-4-20250514")

        # Convert standard model names to Bedrock model IDs
        bedrock_model_map = {
            "claude-sonnet-4-20250514": "us.anthropic.claude-sonnet-4-20250514-v1:0",
            "claude-3-5-sonnet-20241022": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            "claude-3-5-sonnet-20240620": "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
            "claude-3-opus-20240229": "anthropic.claude-3-opus-20240229-v1:0",
            "claude-3-sonnet-20240229": "anthropic.claude-3-sonnet-20240229-v1:0",
            "claude-3-haiku-20240307": "anthropic.claude-3-haiku-20240307-v1:0",
        }

        bedrock_model = bedrock_model_map.get(model, model)

        max_tokens = config.get("max_tokens", 4096)
        temperature = config.get("temperature", 0.7)

        try:
            # Build API call parameters
            api_params = {
                "model": bedrock_model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            # Add system prompt if provided
            if system_prompt:
                api_params["system"] = system_prompt

            response = self.client.messages.create(**api_params)

            response_text = response.content[0].text
            prompt_tokens = response.usage.input_tokens
            response_tokens = response.usage.output_tokens

            return response_text, prompt_tokens, response_tokens

        except Exception as e:
            raise Exception(f"AWS Bedrock API error: {str(e)}")
