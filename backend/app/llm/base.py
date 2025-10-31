"""Base LLM client interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseLLMClient(ABC):
    """Base class for LLM clients"""

    @abstractmethod
    def invoke(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None
    ) -> tuple[str, int, int]:
        """
        Invoke the LLM with a prompt

        Returns:
            tuple: (response_text, prompt_tokens, response_tokens)
        """
        pass
