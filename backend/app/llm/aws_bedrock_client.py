"""AWS Bedrock client for Claude"""
import httpx
from typing import Dict, Any, Optional
from app.llm.base import BaseLLMClient
from app.config import settings


class AWSBedrockClient(BaseLLMClient):
    """Client for AWS Bedrock (Claude via Bedrock) using bearer token"""

    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token or settings.AWS_BEARER_TOKEN_BEDROCK
        self.base_url = "https://bedrock-runtime.us-east-1.amazonaws.com"

        if not self.bearer_token:
            raise ValueError("AWS_BEARER_TOKEN_BEDROCK is required for Bedrock authentication")

    def invoke(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ) -> tuple[str, int, int]:
        """Invoke Claude via AWS Bedrock using bearer token"""

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
        anthropic_version = "bedrock-2023-05-31"

        try:
            # Build request body (Bedrock format)
            request_body = {
                "anthropic_version": anthropic_version,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            # Add system prompt if provided
            if system_prompt:
                request_body["system"] = system_prompt

            # Make HTTP request to Bedrock with bearer token
            url = f"{self.base_url}/model/{bedrock_model}/invoke"

            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, json=request_body, headers=headers)
                response.raise_for_status()

                result = response.json()

            # Parse response
            response_text = result["content"][0]["text"]
            prompt_tokens = result["usage"]["input_tokens"]
            response_tokens = result["usage"]["output_tokens"]

            return response_text, prompt_tokens, response_tokens

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
            raise Exception(f"AWS Bedrock API error: {e.response.status_code} - {error_detail}")
        except Exception as e:
            raise Exception(f"AWS Bedrock API error: {str(e)}")
