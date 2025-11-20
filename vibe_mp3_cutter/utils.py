"""Utility functions."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def validate_source(source: str) -> str:
    """
    Validate input source (URL or file path).

    Args:
        source: Source to validate

    Returns:
        Validated source

    Raises:
        ValueError: If source is invalid
    """
    source = source.strip()

    # Check if it's a URL
    if source.startswith(("http://", "https://", "youtube.com", "youtu.be")):
        if "youtube.com" in source or "youtu.be" in source:
            return source
        raise ValueError(f"Only YouTube URLs supported, got: {source}")

    # Check if it's a file
    path = Path(source).expanduser()
    if path.exists() and path.is_file():
        return str(path)

    raise ValueError(f"Invalid source: {source} (not a valid YouTube URL or file path)")


def format_duration(seconds: Optional[float]) -> str:
    """
    Format duration in seconds to human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds is None:
        return "unknown"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def get_output_path(input_path: Path, suffix: str = "_processed") -> Path:
    """
    Generate output path based on input path.

    Args:
        input_path: Input file path
        suffix: Suffix to add before extension

    Returns:
        Output file path
    """
    return input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"
