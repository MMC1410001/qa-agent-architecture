"""Helper utilities for QA-OS."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TypeVar

import yaml
from pathlib import Path

T = TypeVar("T")


def load_yaml(file_path: str) -> Dict[str, Any]:
    """
    Load YAML configuration file.

    Args:
        file_path: Path to YAML file

    Returns:
        Parsed YAML content as dictionary
    """
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON content as dictionary
    """
    with open(file_path, "r") as f:
        return json.load(f)


def save_json(data: Dict[str, Any], file_path: str, indent: int = 2) -> None:
    """
    Save data to JSON file.

    Args:
        data: Data to save
        file_path: Path to save file
        indent: JSON indentation level
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=indent, default=str)


def chunks(lst: List[T], n: int) -> List[List[T]]:
    """
    Split list into chunks of size n.

    Args:
        lst: List to split
        n: Chunk size

    Returns:
        List of chunks
    """
    return [lst[i : i + n] for i in range(0, len(lst), n)]


async def async_retry(
    func,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for each retry
        exceptions: Exceptions to catch and retry

    Returns:
        Result of function call
    """
    last_exception = None
    current_delay = delay

    for attempt in range(max_attempts):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_attempts - 1:
                await asyncio.sleep(current_delay)
                current_delay *= backoff

    raise last_exception


def parse_duration(duration_str: str) -> timedelta:
    """
    Parse duration string to timedelta.

    Supports formats like:
    - 5s (5 seconds)
    - 10m (10 minutes)
    - 2h (2 hours)
    - 1d (1 day)

    Args:
        duration_str: Duration string

    Returns:
        Timedelta object
    """
    duration_str = duration_str.strip().lower()
    multipliers = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
    }

    for suffix, multiplier in multipliers.items():
        if duration_str.endswith(suffix):
            value = float(duration_str[:-1])
            return timedelta(seconds=value * multiplier)

    raise ValueError(f"Invalid duration format: {duration_str}")


def format_duration(td: timedelta) -> str:
    """
    Format timedelta to human-readable string.

    Args:
        td: Timedelta object

    Returns:
        Formatted duration string
    """
    total_seconds = int(td.total_seconds())

    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        return f"{total_seconds // 60}m {total_seconds % 60}s"
    elif total_seconds < 86400:
        return f"{total_seconds // 3600}h {(total_seconds % 3600) // 60}m"
    else:
        return f"{total_seconds // 86400}d {(total_seconds % 86400) // 3600}h"


def generate_test_id(prefix: str = "TEST") -> str:
    """
    Generate a unique test ID.

    Args:
        prefix: ID prefix

    Returns:
        Unique test ID
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}-{timestamp}"


def sanitize_name(name: str, replace_char: str = "_") -> str:
    """
    Sanitize name for use in identifiers.

    Replaces spaces and special characters with specified character.

    Args:
        name: Name to sanitize
        replace_char: Character to replace invalid chars with

    Returns:
        Sanitized name
    """
    import re

    # Replace spaces and special chars
    sanitized = re.sub(r"[^\w\-]", replace_char, name)
    # Remove consecutive replacements
    sanitized = re.sub(rf"{replace_char}+", replace_char, sanitized)
    # Remove leading/trailing replacements
    sanitized = sanitized.strip(replace_char)
    return sanitized


def merge_dicts(base: Dict, updates: Dict) -> Dict:
    """
    Recursively merge update dict into base dict.

    Args:
        base: Base dictionary
        updates: Dictionary with updates

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def get_nested(obj: Dict, path: str, default: Any = None) -> Any:
    """
    Get nested value from dictionary using dot notation.

    Args:
        obj: Dictionary
        path: Dot-separated path (e.g., 'a.b.c')
        default: Default value if path not found

    Returns:
        Value at path or default
    """
    keys = path.split(".")
    result = obj

    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default

    return result


def set_nested(obj: Dict, path: str, value: Any) -> Dict:
    """
    Set nested value in dictionary using dot notation.

    Args:
        obj: Dictionary
        path: Dot-separated path (e.g., 'a.b.c')
        value: Value to set

    Returns:
        Modified dictionary
    """
    keys = path.split(".")
    current = obj

    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value
    return obj
