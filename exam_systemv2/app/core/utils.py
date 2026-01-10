"""Utility functions for common operations."""
import json
from typing import Any, Optional, List, Dict
from datetime import datetime, timezone


def safe_json_loads(json_str: Optional[str], default: Any = None) -> Any:
    """Safely parse JSON string with fallback."""
    if json_str is None:
        return default
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError, AttributeError):
        return default if default is not None else json_str


def normalize_datetime_to_utc_naive(dt: Optional[datetime]) -> Optional[datetime]:
    """Normalize datetime to UTC naive datetime for database storage."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Already naive, assume UTC
        return dt
    # Convert to UTC and make naive
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def normalize_datetime_to_utc_aware(dt: Optional[datetime]) -> Optional[datetime]:
    """Normalize datetime to UTC timezone-aware for comparison."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Naive datetime - assume UTC
        return dt.replace(tzinfo=timezone.utc)
    # Already timezone-aware, convert to UTC
    return dt.astimezone(timezone.utc)


def parse_form_datetime(datetime_str: Optional[str]) -> Optional[datetime]:
    """Parse datetime string from form and normalize to UTC naive."""
    if not datetime_str:
        return None
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return normalize_datetime_to_utc_naive(dt)
    except (ValueError, AttributeError) as e:
        import logging
        logging.getLogger(__name__).warning(f"Invalid datetime format: {datetime_str}, error: {str(e)}")
        return None


def ensure_list(value: Any) -> List:
    """Ensure value is a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def safe_get(d: Dict, key: str, default: Any = None) -> Any:
    """Safely get value from dict with fallback."""
    if not isinstance(d, dict):
        return default
    return d.get(key, default)

