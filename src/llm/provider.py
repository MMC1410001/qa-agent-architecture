"""LLM Provider abstraction for multiple backends."""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional

from config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096):
        """
        Initialize LLM provider.

        Args:
            model: Model name to use
            temperature: Temperature for generation (0-1)
            max_tokens: Maximum tokens in response
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate response from LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """
        Stream response from LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override

        Yields:
            Response chunks
        """
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count

        Returns:
            Token count
        """
        pass


class ClaudeProvider(LLMProvider):
    """Claude LLM Provider (Anthropic)."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-5", **kwargs):
        """
        Initialize Claude provider.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
            **kwargs: Additional arguments for parent class
        """
        super().__init__(model=model, **kwargs)
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate response from Claude."""
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=tokens,
                temperature=temp,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except Exception as e:
            logger.error("Claude generation failed", error=str(e))
            raise

    async def stream(self, prompt: str, system_prompt: Optional[str] = None, temperature: Optional[float] = None):
        """Stream response from Claude."""
        temp = temperature if temperature is not None else self.temperature

        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=temp,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error("Claude streaming failed", error=str(e))
            raise

    async def count_tokens(self, text: str) -> int:
        """Count tokens using Claude's tokenizer."""
        # Claude doesn't have a direct token counting API in async,
        # so we estimate: ~4 characters per token on average
        return len(text) // 4


class OpenAIProvider(LLMProvider):
    """OpenAI LLM Provider."""

    def __init__(self, api_key: str, model: str = "gpt-4o", **kwargs):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
            **kwargs: Additional arguments for parent class
        """
        super().__init__(model=model, **kwargs)
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                "openai package required. Install with: pip install openai"
            )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate response from OpenAI."""
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI generation failed", error=str(e))
            raise

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """Stream response from OpenAI."""
        temp = temperature if temperature is not None else self.temperature

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=self.max_tokens,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error("OpenAI streaming failed", error=str(e))
            raise

    async def count_tokens(self, text: str) -> int:
        """Count tokens using OpenAI's tokenizer."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except ImportError:
            # Fallback to estimation
            return len(text) // 4


def get_llm_provider() -> LLMProvider:
    """
    Factory function to get configured LLM provider.

    Returns:
        Configured LLM provider instance

    Raises:
        ValueError: If provider is not supported or not configured
    """
    provider_name = settings.llm.provider.lower()
    api_key = settings.llm.api_key

    if not api_key:
        raise ValueError(
            f"LLM API key not configured. Set LLM_API_KEY environment variable"
        )

    if provider_name == "claude":
        return ClaudeProvider(
            api_key=api_key,
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            max_tokens=settings.llm.max_tokens,
        )
    elif provider_name == "openai":
        return OpenAIProvider(
            api_key=api_key,
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            max_tokens=settings.llm.max_tokens,
        )
    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider_name}. "
            "Supported: claude, openai"
        )
