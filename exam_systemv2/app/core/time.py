from datetime import datetime, timezone
from typing import Protocol


class TimeProvider(Protocol):
    """Interface for time operations to enable testing and determinism."""
    
    def now(self) -> datetime:
        """Get current datetime."""
        ...


class SystemTimeProvider:
    """Default time provider using system time."""
    
    def now(self) -> datetime:
        """Get current UTC datetime with fallback for ZoneInfo issues."""
        try:
            from zoneinfo import ZoneInfo
            return datetime.now(ZoneInfo("UTC"))
        except (ImportError, ValueError, Exception):
            # Fallback to timezone.utc if ZoneInfo fails
            return datetime.now(timezone.utc)


# Default instance
time_provider: TimeProvider = SystemTimeProvider()

