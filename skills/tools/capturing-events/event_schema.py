"""Event schema definition and validation for capture-events skill."""

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class EventType(str, Enum):
    """Types of events captured by the skill."""

    # File system events
    FILE_CREATE = "file_create"
    FILE_MODIFY = "file_modify"
    FILE_DELETE = "file_delete"

    # Terminal events
    TERMINAL_EXECUTE = "terminal_execute"
    TERMINAL_OUTPUT = "terminal_output"
    TERMINAL_ERROR = "terminal_error"

    # Diagnostic events
    DIAGNOSTIC_ERROR = "diagnostic_error"
    DIAGNOSTIC_WARNING = "diagnostic_warning"
    DIAGNOSTIC_INFO = "diagnostic_info"

    # Skill invocation events
    SKILL_INVOKE = "skill_invoke"
    SKILL_COMPLETE = "skill_complete"
    SKILL_ERROR = "skill_error"


class Event:
    """Standardized event for workspace signal capture."""

    def __init__(
        self,
        event_type: EventType,
        provider: str,
        metadata: Dict[str, Any],
        timestamp: Optional[str] = None,
    ):
        """
        Initialize an event.

        Args:
            event_type: Type of event (must be EventType enum value)
            provider: Source provider (e.g., "universal", "copilot", "cursor")
            metadata: Event-specific metadata dict
            timestamp: ISO 8601 timestamp (auto-generated if not provided)

        Raises:
            TypeError: If event_type is not EventType or metadata is not dict
            ValueError: If metadata is missing required fields for event type
        """
        if not isinstance(event_type, EventType):
            raise TypeError(
                f"event_type must be EventType, got {type(event_type).__name__}"
            )

        if not isinstance(metadata, dict):
            raise TypeError(f"metadata must be dict, got {type(metadata).__name__}")

        if not isinstance(provider, str):
            raise TypeError(f"provider must be str, got {type(provider).__name__}")

        self.event_type = event_type
        self.provider = provider
        self.metadata = metadata
        self.timestamp = timestamp or datetime.utcnow().isoformat()

    def validate(self) -> bool:
        """
        Validate event has all required fields.

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        required_fields = {"event_type", "provider", "timestamp", "metadata"}
        provided_fields = {"event_type", "provider", "timestamp", "metadata"}

        if not issubclass(type(self.event_type), EventType):
            raise ValueError("event_type must be EventType enum value")

        if not self.provider:
            raise ValueError("provider cannot be empty")

        if not self.timestamp:
            raise ValueError("timestamp cannot be empty")

        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be dict")

        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary.

        Returns:
            Dict with event data
        """
        return {
            "event_type": self.event_type.value,
            "provider": self.provider,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """
        Convert event to JSON string.

        Returns:
            JSON-encoded event
        """
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Event":
        """
        Create event from dictionary.

        Args:
            data: Dict with event data

        Returns:
            Event instance

        Raises:
            ValueError: If data is invalid
        """
        try:
            event_type = EventType(data["event_type"])
            provider = data["provider"]
            timestamp = data["timestamp"]
            metadata = data["metadata"]
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")

        event = Event(event_type, provider, metadata, timestamp)
        event.validate()
        return event

    @staticmethod
    def from_json(json_str: str) -> "Event":
        """
        Create event from JSON string.

        Args:
            json_str: JSON-encoded event

        Returns:
            Event instance

        Raises:
            ValueError: If JSON is invalid
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        return Event.from_dict(data)

    def __repr__(self) -> str:
        """String representation of event."""
        return (
            f"Event(type={self.event_type.value}, "
            f"provider={self.provider}, "
            f"timestamp={self.timestamp})"
        )

    def __eq__(self, other: Any) -> bool:
        """Check equality with another event."""
        if not isinstance(other, Event):
            return False

        return (
            self.event_type == other.event_type
            and self.provider == other.provider
            and self.timestamp == other.timestamp
            and self.metadata == other.metadata
        )


class EventValidator:
    """Validator for event schema."""

    @staticmethod
    def validate_event(event: Event) -> Dict[str, Any]:
        """
        Validate an event and return validation result.

        Args:
            event: Event to validate

        Returns:
            Dict with validation result: {"valid": bool, "errors": list}
        """
        errors = []

        try:
            if not isinstance(event.event_type, EventType):
                errors.append("event_type must be EventType enum")

            if not isinstance(event.provider, str) or not event.provider:
                errors.append("provider must be non-empty string")

            if not isinstance(event.timestamp, str) or not event.timestamp:
                errors.append("timestamp must be non-empty string")

            if not isinstance(event.metadata, dict):
                errors.append("metadata must be dict")

            event.validate()

        except ValueError as e:
            errors.append(str(e))

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_json_line(line: str) -> Dict[str, Any]:
        """
        Validate a JSON line as an event.

        Args:
            line: JSON string to validate

        Returns:
            Dict with validation result and Event if valid
        """
        try:
            event = Event.from_json(line)
            return {"valid": True, "errors": [], "event": event}
        except (json.JSONDecodeError, ValueError) as e:
            return {"valid": False, "errors": [str(e)], "event": None}
