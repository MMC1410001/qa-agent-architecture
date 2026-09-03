"""Response parsing utilities for LLM outputs."""

import json
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar

from pydantic import BaseModel, ValidationError

from src.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class ResponseParser(ABC):
    """Abstract base class for response parsers."""

    @abstractmethod
    async def parse(self, response: str) -> Any:
        """
        Parse LLM response.

        Args:
            response: Raw LLM response text

        Returns:
            Parsed response
        """
        pass


class JSONParser(ResponseParser):
    """Parser for JSON responses."""

    def __init__(self, model: Type[BaseModel] = None):
        """
        Initialize JSON parser.

        Args:
            model: Optional Pydantic model to validate against
        """
        self.model = model

    async def parse(self, response: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from response.

        Args:
            response: Response text potentially containing JSON

        Returns:
            Parsed JSON as dictionary
        """
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Assume entire response is JSON
                json_str = response

        try:
            data = json.loads(json_str)
            logger.debug("JSON parsed successfully")

            # Validate with Pydantic model if provided
            if self.model:
                try:
                    data = self.model(**data)
                    logger.debug("Model validation successful", model=self.model.__name__)
                except ValidationError as e:
                    logger.warning(
                        "Model validation failed",
                        model=self.model.__name__,
                        error=str(e),
                    )
                    # Return raw data if validation fails
                    return data

            return data
        except json.JSONDecodeError as e:
            logger.error("JSON parsing failed", error=str(e), response=response[:200])
            raise ValueError(f"Failed to parse JSON from response: {e}")


class TextParser(ResponseParser):
    """Parser for plain text responses."""

    async def parse(self, response: str) -> str:
        """
        Parse text response.

        Args:
            response: Response text

        Returns:
            Parsed text (cleaned)
        """
        # Clean up response
        text = response.strip()
        logger.debug("Text parsed successfully", length=len(text))
        return text


class StructuredParser(ResponseParser):
    """Parser that extracts structured data from unstructured text."""

    def __init__(self, keys: list):
        """
        Initialize structured parser.

        Args:
            keys: List of keys to extract from response
        """
        self.keys = keys

    async def parse(self, response: str) -> Dict[str, str]:
        """
        Extract structured data from response.

        Args:
            response: Response text

        Returns:
            Dictionary with extracted key-value pairs
        """
        result = {}

        for key in self.keys:
            # Look for patterns like "Key: value" or "Key - value"
            pattern = rf"{key}\s*[:|\-]\s*([^\n]+)"
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                result[key] = match.group(1).strip()
            else:
                logger.warning("Key not found in response", key=key)
                result[key] = None

        logger.debug("Structured data extracted", keys=len(result))
        return result


class ListParser(ResponseParser):
    """Parser for list-based responses."""

    def __init__(self, separator: str = "\n", item_prefix: str = "-"):
        """
        Initialize list parser.

        Args:
            separator: Line separator (default newline)
            item_prefix: Prefix for list items (default dash)
        """
        self.separator = separator
        self.item_prefix = item_prefix

    async def parse(self, response: str) -> list:
        """
        Extract list items from response.

        Args:
            response: Response text

        Returns:
            List of items
        """
        items = []

        for line in response.split(self.separator):
            line = line.strip()
            if not line:
                continue

            # Remove prefix if present
            if line.startswith(self.item_prefix):
                line = line[len(self.item_prefix) :].strip()

            if line:
                items.append(line)

        logger.debug("List parsed successfully", item_count=len(items))
        return items


class CompositeParser(ResponseParser):
    """Parser that combines multiple parsers."""

    def __init__(self, parsers: Dict[str, ResponseParser]):
        """
        Initialize composite parser.

        Args:
            parsers: Dictionary of name -> parser
        """
        self.parsers = parsers

    async def parse(self, response: str) -> Dict[str, Any]:
        """
        Parse response using multiple parsers.

        Args:
            response: Response text

        Returns:
            Dictionary with parser results
        """
        results = {}

        for name, parser in self.parsers.items():
            try:
                results[name] = await parser.parse(response)
            except Exception as e:
                logger.warning("Parser failed", parser=name, error=str(e))
                results[name] = None

        return results


class ChainParser(ResponseParser):
    """Parser that chains multiple parsers in sequence."""

    def __init__(self, parsers: list):
        """
        Initialize chain parser.

        Args:
            parsers: List of parsers to apply in order
        """
        self.parsers = parsers

    async def parse(self, response: str) -> Any:
        """
        Parse response through chain of parsers.

        Args:
            response: Initial response text

        Returns:
            Final parsed result
        """
        result = response

        for parser in self.parsers:
            try:
                result = await parser.parse(result)
            except Exception as e:
                logger.error(
                    "Chain parser failed",
                    parser=parser.__class__.__name__,
                    error=str(e),
                )
                raise

        return result


# Helper function to create parsers
async def parse_response(
    response: str,
    format_type: str = "json",
    model: Type[BaseModel] = None,
) -> Any:
    """
    Convenience function to parse response.

    Args:
        response: Response text
        format_type: Format type (json, text, structured, list)
        model: Optional Pydantic model for validation

    Returns:
        Parsed response

    Raises:
        ValueError: If format_type is not supported
    """
    if format_type == "json":
        parser = JSONParser(model=model)
    elif format_type == "text":
        parser = TextParser()
    elif format_type == "list":
        parser = ListParser()
    else:
        raise ValueError(f"Unknown format type: {format_type}")

    return await parser.parse(response)
