"""Universal provider for workspace-only event capture."""

from datetime import datetime
from typing import Any, Dict, Optional

try:
    from event_schema import Event, EventType
except ImportError:
    from ..event_schema import Event, EventType


class FileWatcher:
    """Track file system events."""

    @staticmethod
    def capture_event(event_type: str, filepath: str) -> Dict[str, Any]:
        """
        Capture file system event.

        Args:
            event_type: "file_create", "file_modify", or "file_delete"
            filepath: Path to file

        Returns:
            Metadata dict
        """
        if event_type not in ("file_create", "file_modify", "file_delete"):
            raise ValueError(f"Unknown file event type: {event_type}")

        return {
            "filepath": filepath,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
        }


class TerminalListener:
    """Capture terminal command execution."""

    @staticmethod
    def capture_execution(command: str, output: str = "", error: str = "") -> Dict[str, Any]:
        """
        Capture terminal command execution.

        Args:
            command: Command executed
            output: Command output
            error: Error output

        Returns:
            Metadata dict
        """
        return {
            "command": command,
            "output": output[:500],  # Limit output size
            "error": error[:500],    # Limit error size
            "timestamp": datetime.utcnow().isoformat(),
        }


class DiagnosticCollector:
    """Collect VS Code diagnostic events."""

    @staticmethod
    def capture_diagnostic(
        event_type: str, filepath: str, line: int, message: str, severity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Capture diagnostic event.

        Args:
            event_type: "diagnostic_error", "diagnostic_warning", or "diagnostic_info"
            filepath: File path with diagnostic
            line: Line number (1-indexed)
            message: Diagnostic message
            severity: Optional severity override

        Returns:
            Metadata dict
        """
        if event_type not in ("diagnostic_error", "diagnostic_warning", "diagnostic_info"):
            raise ValueError(f"Unknown diagnostic event type: {event_type}")

        if severity is None:
            severity = event_type.replace("diagnostic_", "")

        return {
            "filepath": filepath,
            "line": line,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
        }


class SkillTracker:
    """Track skill invocations and completions."""

    @staticmethod
    def capture_invocation(skill_name: str, status: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Capture skill invocation event.

        Args:
            skill_name: Name of the skill
            status: Status message or skill outcome
            details: Additional details dict

        Returns:
            Metadata dict
        """
        metadata = {
            "skill_name": skill_name,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if details:
            metadata["details"] = details

        return metadata


class UniversalProvider:
    """Universal provider for workspace-only event capture (any assistant/editor)."""

    def __init__(self):
        """Initialize universal provider."""
        self.file_watcher = FileWatcher()
        self.terminal_listener = TerminalListener()
        self.diagnostic_collector = DiagnosticCollector()
        self.skill_tracker = SkillTracker()

    def capture_file_event(self, event_type: str, filepath: str) -> Event:
        """
        Capture file system event.

        Args:
            event_type: "file_create", "file_modify", or "file_delete"
            filepath: Path to file

        Returns:
            Event instance
        """
        event_type_enum = EventType(f"file_{event_type.replace('file_', '')}")
        metadata = self.file_watcher.capture_event(event_type, filepath)

        return Event(event_type_enum, "universal", metadata)

    def capture_terminal_event(
        self, event_type: str, command: str, output: str = "", error: str = ""
    ) -> Event:
        """
        Capture terminal event.

        Args:
            event_type: "terminal_execute", "terminal_output", or "terminal_error"
            command: Command executed
            output: Command output
            error: Error output

        Returns:
            Event instance
        """
        event_type_enum = EventType(event_type)
        metadata = self.terminal_listener.capture_execution(command, output, error)

        return Event(event_type_enum, "universal", metadata)

    def capture_diagnostic_event(
        self, event_type: str, filepath: str, line: int, message: str
    ) -> Event:
        """
        Capture diagnostic event.

        Args:
            event_type: "diagnostic_error", "diagnostic_warning", or "diagnostic_info"
            filepath: File path with diagnostic
            line: Line number
            message: Diagnostic message

        Returns:
            Event instance
        """
        event_type_enum = EventType(event_type)
        metadata = self.diagnostic_collector.capture_diagnostic(event_type, filepath, line, message)

        return Event(event_type_enum, "universal", metadata)

    def capture_skill_event(self, event_type: str, skill_name: str, status: str) -> Event:
        """
        Capture skill invocation event.

        Args:
            event_type: "skill_invoke", "skill_complete", or "skill_error"
            skill_name: Name of the skill
            status: Status message

        Returns:
            Event instance
        """
        event_type_enum = EventType(event_type)
        metadata = self.skill_tracker.capture_invocation(skill_name, status)

        return Event(event_type_enum, "universal", metadata)
