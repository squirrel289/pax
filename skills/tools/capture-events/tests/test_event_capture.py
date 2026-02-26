"""Unit tests for event capture logic."""

import json
import unittest
from datetime import datetime

from ..event_schema import Event, EventType, EventValidator
from ..providers.universal import (
    UniversalProvider,
    FileWatcher,
    TerminalListener,
    DiagnosticCollector,
    SkillTracker,
)


class TestEventType(unittest.TestCase):
    """Test EventType enum."""

    def test_file_events(self):
        """Test file event types."""
        self.assertEqual(EventType.FILE_CREATE.value, "file_create")
        self.assertEqual(EventType.FILE_MODIFY.value, "file_modify")
        self.assertEqual(EventType.FILE_DELETE.value, "file_delete")

    def test_terminal_events(self):
        """Test terminal event types."""
        self.assertEqual(EventType.TERMINAL_EXECUTE.value, "terminal_execute")
        self.assertEqual(EventType.TERMINAL_OUTPUT.value, "terminal_output")
        self.assertEqual(EventType.TERMINAL_ERROR.value, "terminal_error")

    def test_diagnostic_events(self):
        """Test diagnostic event types."""
        self.assertEqual(EventType.DIAGNOSTIC_ERROR.value, "diagnostic_error")
        self.assertEqual(EventType.DIAGNOSTIC_WARNING.value, "diagnostic_warning")
        self.assertEqual(EventType.DIAGNOSTIC_INFO.value, "diagnostic_info")

    def test_skill_events(self):
        """Test skill event types."""
        self.assertEqual(EventType.SKILL_INVOKE.value, "skill_invoke")
        self.assertEqual(EventType.SKILL_COMPLETE.value, "skill_complete")
        self.assertEqual(EventType.SKILL_ERROR.value, "skill_error")


class TestEvent(unittest.TestCase):
    """Test Event class."""

    def test_create_valid_event(self):
        """Test creating valid event."""
        event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "/test/file.txt"},
        )

        self.assertEqual(event.event_type, EventType.FILE_CREATE)
        self.assertEqual(event.provider, "universal")
        self.assertIsNotNone(event.timestamp)
        self.assertEqual(event.metadata["filepath"], "/test/file.txt")

    def test_event_with_explicit_timestamp(self):
        """Test event with explicit timestamp."""
        timestamp = "2026-02-26T10:30:00"
        event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "/test/file.txt"},
            timestamp=timestamp,
        )

        self.assertEqual(event.timestamp, timestamp)

    def test_invalid_event_type(self):
        """Test creating event with invalid type."""
        with self.assertRaises(TypeError):
            Event("invalid", "universal", {})

    def test_invalid_provider(self):
        """Test creating event with invalid provider."""
        with self.assertRaises(TypeError):
            Event(EventType.FILE_CREATE, 123, {})

    def test_invalid_metadata(self):
        """Test creating event with invalid metadata."""
        with self.assertRaises(TypeError):
            Event(EventType.FILE_CREATE, "universal", "not_a_dict")

    def test_event_validation(self):
        """Test event validation."""
        event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "/test/file.txt"},
        )

        self.assertTrue(event.validate())

    def test_event_to_dict(self):
        """Test event to dict conversion."""
        event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "/test/file.txt"},
            timestamp="2026-02-26T10:30:00",
        )

        event_dict = event.to_dict()

        self.assertEqual(event_dict["event_type"], "file_create")
        self.assertEqual(event_dict["provider"], "universal")
        self.assertEqual(event_dict["timestamp"], "2026-02-26T10:30:00")
        self.assertEqual(event_dict["metadata"]["filepath"], "/test/file.txt")

    def test_event_to_json(self):
        """Test event to JSON conversion."""
        event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "/test/file.txt"},
            timestamp="2026-02-26T10:30:00",
        )

        json_str = event.to_json()
        data = json.loads(json_str)

        self.assertEqual(data["event_type"], "file_create")
        self.assertEqual(data["provider"], "universal")

    def test_event_from_dict(self):
        """Test creating event from dict."""
        data = {
            "event_type": "file_create",
            "provider": "universal",
            "timestamp": "2026-02-26T10:30:00",
            "metadata": {"filepath": "/test/file.txt"},
        }

        event = Event.from_dict(data)

        self.assertEqual(event.event_type, EventType.FILE_CREATE)
        self.assertEqual(event.provider, "universal")
        self.assertEqual(event.timestamp, "2026-02-26T10:30:00")

    def test_event_from_json(self):
        """Test creating event from JSON."""
        json_str = (
            '{"event_type": "file_create", "provider": "universal", '
            '"timestamp": "2026-02-26T10:30:00", "metadata": {"filepath": "/test/file.txt"}}'
        )

        event = Event.from_json(json_str)

        self.assertEqual(event.event_type, EventType.FILE_CREATE)
        self.assertEqual(event.provider, "universal")

    def test_event_equality(self):
        """Test event equality."""
        event1 = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "/test/file.txt"},
            timestamp="2026-02-26T10:30:00",
        )

        event2 = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "/test/file.txt"},
            timestamp="2026-02-26T10:30:00",
        )

        self.assertEqual(event1, event2)


class TestFileWatcher(unittest.TestCase):
    """Test FileWatcher class."""

    def test_capture_create_event(self):
        """Test capturing file create event."""
        metadata = FileWatcher.capture_event("file_create", "/test/file.txt")

        self.assertEqual(metadata["filepath"], "/test/file.txt")
        self.assertEqual(metadata["event_type"], "file_create")
        self.assertIn("timestamp", metadata)

    def test_capture_modify_event(self):
        """Test capturing file modify event."""
        metadata = FileWatcher.capture_event("file_modify", "/test/file.txt")

        self.assertEqual(metadata["event_type"], "file_modify")

    def test_capture_delete_event(self):
        """Test capturing file delete event."""
        metadata = FileWatcher.capture_event("file_delete", "/test/file.txt")

        self.assertEqual(metadata["event_type"], "file_delete")

    def test_invalid_event_type(self):
        """Test invalid event type."""
        with self.assertRaises(ValueError):
            FileWatcher.capture_event("invalid", "/test/file.txt")


class TestTerminalListener(unittest.TestCase):
    """Test TerminalListener class."""

    def test_capture_execution(self):
        """Test capturing terminal execution."""
        metadata = TerminalListener.capture_execution(
            "ls -la",
            output="file1.txt file2.txt",
            error="",
        )

        self.assertEqual(metadata["command"], "ls -la")
        self.assertEqual(metadata["output"], "file1.txt file2.txt")
        self.assertEqual(metadata["error"], "")
        self.assertIn("timestamp", metadata)

    def test_output_truncation(self):
        """Test that large output is truncated."""
        large_output = "x" * 1000
        metadata = TerminalListener.capture_execution("cmd", output=large_output)

        self.assertEqual(len(metadata["output"]), 500)


class TestDiagnosticCollector(unittest.TestCase):
    """Test DiagnosticCollector class."""

    def test_capture_error(self):
        """Test capturing error diagnostic."""
        metadata = DiagnosticCollector.capture_diagnostic(
            "diagnostic_error",
            "/test/file.py",
            10,
            "Type error: expected str",
        )

        self.assertEqual(metadata["filepath"], "/test/file.py")
        self.assertEqual(metadata["line"], 10)
        self.assertEqual(metadata["message"], "Type error: expected str")
        self.assertEqual(metadata["severity"], "error")

    def test_capture_warning(self):
        """Test capturing warning diagnostic."""
        metadata = DiagnosticCollector.capture_diagnostic(
            "diagnostic_warning",
            "/test/file.py",
            20,
            "Unused variable",
        )

        self.assertEqual(metadata["severity"], "warning")

    def test_capture_info(self):
        """Test capturing info diagnostic."""
        metadata = DiagnosticCollector.capture_diagnostic(
            "diagnostic_info",
            "/test/file.py",
            30,
            "Hint: use type hints",
        )

        self.assertEqual(metadata["severity"], "info")


class TestSkillTracker(unittest.TestCase):
    """Test SkillTracker class."""

    def test_capture_invocation(self):
        """Test capturing skill invocation."""
        metadata = SkillTracker.capture_invocation("my-skill", "start")

        self.assertEqual(metadata["skill_name"], "my-skill")
        self.assertEqual(metadata["status"], "start")
        self.assertIn("timestamp", metadata)

    def test_capture_with_details(self):
        """Test capturing with details."""
        details = {"duration": 5.2, "success": True}
        metadata = SkillTracker.capture_invocation("my-skill", "complete", details)

        self.assertEqual(metadata["details"], details)


class TestUniversalProvider(unittest.TestCase):
    """Test UniversalProvider class."""

    def setUp(self):
        """Set up test provider."""
        self.provider = UniversalProvider()

    def test_capture_file_event(self):
        """Test capturing file event."""
        event = self.provider.capture_file_event("file_create", "/test/file.txt")

        self.assertEqual(event.event_type, EventType.FILE_CREATE)
        self.assertEqual(event.provider, "universal")
        self.assertEqual(event.metadata["filepath"], "/test/file.txt")

    def test_capture_terminal_event(self):
        """Test capturing terminal event."""
        event = self.provider.capture_terminal_event(
            "terminal_execute",
            "ls -la",
            "file.txt",
            "",
        )

        self.assertEqual(event.event_type, EventType.TERMINAL_EXECUTE)
        self.assertEqual(event.provider, "universal")
        self.assertEqual(event.metadata["command"], "ls -la")

    def test_capture_diagnostic_event(self):
        """Test capturing diagnostic event."""
        event = self.provider.capture_diagnostic_event(
            "diagnostic_error",
            "/test/file.py",
            10,
            "Error message",
        )

        self.assertEqual(event.event_type, EventType.DIAGNOSTIC_ERROR)
        self.assertEqual(event.provider, "universal")
        self.assertEqual(event.metadata["line"], 10)

    def test_capture_skill_event(self):
        """Test capturing skill event."""
        event = self.provider.capture_skill_event(
            "skill_invoke",
            "test-skill",
            "running",
        )

        self.assertEqual(event.event_type, EventType.SKILL_INVOKE)
        self.assertEqual(event.provider, "universal")
        self.assertEqual(event.metadata["skill_name"], "test-skill")


class TestEventValidator(unittest.TestCase):
    """Test EventValidator class."""

    def test_validate_valid_event(self):
        """Test validating valid event."""
        event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "/test/file.txt"},
        )

        result = EventValidator.validate_event(event)

        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)

    def test_validate_invalid_provider(self):
        """Test validating event with invalid provider."""
        event = Event(EventType.FILE_CREATE, "", {})

        result = EventValidator.validate_event(event)

        self.assertFalse(result["valid"])
        self.assertTrue(len(result["errors"]) > 0)

    def test_validate_json_line(self):
        """Test validating JSON line."""
        json_line = (
            '{"event_type": "file_create", "provider": "universal", '
            '"timestamp": "2026-02-26T10:30:00", "metadata": {}}'
        )

        result = EventValidator.validate_json_line(json_line)

        self.assertTrue(result["valid"])
        self.assertIsNotNone(result["event"])

    def test_validate_invalid_json_line(self):
        """Test validating invalid JSON line."""
        result = EventValidator.validate_json_line("invalid json")

        self.assertFalse(result["valid"])
        self.assertIsNone(result["event"])


if __name__ == "__main__":
    unittest.main()
