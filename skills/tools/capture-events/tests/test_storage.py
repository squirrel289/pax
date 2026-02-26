"""Unit tests for JSONL storage and TTL cleanup."""

import json
import tempfile
import threading
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from ..event_schema import Event, EventType
from ..storage.jsonl_handler import JSONLStorage, TTLCleaner


class TestJSONLStorage(unittest.TestCase):
    """Test JSONLStorage class."""

    def setUp(self):
        """Create temporary storage file for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = str(Path(self.temp_dir) / "episodes.jsonl")
        self.storage = JSONLStorage(self.storage_path)

    def tearDown(self):
        """Clean up temporary files."""
        if Path(self.storage_path).exists():
            Path(self.storage_path).unlink()
        Path(self.temp_dir).rmdir()

    def test_append_single_event(self):
        """Test appending a single event."""
        event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "/test/file.txt"},
        )

        success = self.storage.append(event)

        self.assertTrue(success)
        self.assertTrue(Path(self.storage_path).exists())

    def test_append_multiple_events(self):
        """Test appending multiple events."""
        events = [
            Event(EventType.FILE_CREATE, "universal", {"filepath": "/test/file1.txt"}),
            Event(EventType.FILE_MODIFY, "universal", {"filepath": "/test/file2.txt"}),
            Event(EventType.FILE_DELETE, "universal", {"filepath": "/test/file3.txt"}),
        ]

        for event in events:
            self.storage.append(event)

        with open(self.storage_path, "r") as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 3)

    def test_read_all(self):
        """Test reading all events."""
        events = [
            Event(EventType.FILE_CREATE, "universal", {"filepath": "file1.txt"}),
            Event(EventType.FILE_MODIFY, "universal", {"filepath": "file2.txt"}),
        ]

        for event in events:
            self.storage.append(event)

        read_events = self.storage.read_all()

        self.assertEqual(len(read_events), 2)
        self.assertEqual(read_events[0].event_type, EventType.FILE_CREATE)
        self.assertEqual(read_events[1].event_type, EventType.FILE_MODIFY)

    def test_read_from_empty_storage(self):
        """Test reading from empty storage."""
        events = self.storage.read_all()

        self.assertEqual(len(events), 0)

    def test_read_since(self):
        """Test reading events since timestamp."""
        now = datetime.utcnow().isoformat()
        future = (datetime.utcnow() + timedelta(hours=1)).isoformat()

        event1 = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "file1.txt"},
            timestamp=now,
        )
        event2 = Event(
            EventType.FILE_MODIFY,
            "universal",
            {"filepath": "file2.txt"},
            timestamp=future,
        )

        self.storage.append(event1)
        self.storage.append(event2)

        # Read events after now (should include only future event)
        events = self.storage.read_since(now)

        # Both events should be returned since future > now
        self.assertGreaterEqual(len(events), 1)

    def test_read_by_type(self):
        """Test reading events by type."""
        events = [
            Event(EventType.FILE_CREATE, "universal", {"filepath": "file1.txt"}),
            Event(EventType.FILE_CREATE, "universal", {"filepath": "file2.txt"}),
            Event(EventType.FILE_MODIFY, "universal", {"filepath": "file3.txt"}),
        ]

        for event in events:
            self.storage.append(event)

        create_events = self.storage.read_by_type("file_create")

        self.assertEqual(len(create_events), 2)
        self.assertTrue(all(e.event_type == EventType.FILE_CREATE for e in create_events))

    def test_read_by_provider(self):
        """Test reading events by provider."""
        events = [
            Event(EventType.FILE_CREATE, "universal", {"filepath": "file1.txt"}),
            Event(EventType.FILE_CREATE, "copilot", {"filepath": "file2.txt"}),
            Event(EventType.FILE_CREATE, "universal", {"filepath": "file3.txt"}),
        ]

        for event in events:
            self.storage.append(event)

        universal_events = self.storage.read_by_provider("universal")

        self.assertEqual(len(universal_events), 2)
        self.assertTrue(all(e.provider == "universal" for e in universal_events))

    def test_count(self):
        """Test counting events."""
        for i in range(5):
            event = Event(
                EventType.FILE_CREATE,
                "universal",
                {"filepath": f"file{i}.txt"},
            )
            self.storage.append(event)

        count = self.storage.count()

        self.assertEqual(count, 5)

    def test_count_empty(self):
        """Test counting empty storage."""
        count = self.storage.count()

        self.assertEqual(count, 0)

    def test_clear(self):
        """Test clearing storage."""
        event = Event(EventType.FILE_CREATE, "universal", {"filepath": "file.txt"})
        self.storage.append(event)

        self.assertTrue(Path(self.storage_path).exists())

        success = self.storage.clear()

        self.assertTrue(success)
        self.assertFalse(Path(self.storage_path).exists())

    def test_jsonl_format(self):
        """Test that storage uses proper JSONL format."""
        event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "file.txt"},
        )
        self.storage.append(event)

        with open(self.storage_path, "r") as f:
            line = f.readline()

        data = json.loads(line)

        self.assertEqual(data["event_type"], "file_create")
        self.assertEqual(data["provider"], "universal")

    def test_concurrent_append(self):
        """Test concurrent append operations."""
        events = []

        def append_event(i):
            event = Event(
                EventType.FILE_CREATE,
                "universal",
                {"filepath": f"file{i}.txt"},
            )
            self.storage.append(event)

        threads = []
        for i in range(10):
            t = threading.Thread(target=append_event, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        count = self.storage.count()

        self.assertEqual(count, 10)


class TestTTLCleaner(unittest.TestCase):
    """Test TTLCleaner class."""

    def setUp(self):
        """Create temporary storage for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = str(Path(self.temp_dir) / "episodes.jsonl")
        self.storage = JSONLStorage(self.storage_path)
        self.cleaner = TTLCleaner(self.storage_path, ttl_days=7)

    def tearDown(self):
        """Clean up temporary files."""
        if Path(self.storage_path).exists():
            Path(self.storage_path).unlink()
        Path(self.temp_dir).rmdir()

    def test_cleanup_removes_old_events(self):
        """Test that cleanup removes old events."""
        now = datetime.utcnow()
        old_timestamp = (now - timedelta(days=8)).isoformat()
        recent_timestamp = now.isoformat()

        old_event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "old.txt"},
            timestamp=old_timestamp,
        )
        recent_event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "recent.txt"},
            timestamp=recent_timestamp,
        )

        self.storage.append(old_event)
        self.storage.append(recent_event)

        stats = self.cleaner.cleanup()

        self.assertEqual(stats["removed"], 1)
        self.assertEqual(stats["kept"], 1)

    def test_cleanup_preserves_recent_events(self):
        """Test that cleanup preserves recent events."""
        now = datetime.utcnow()
        recent1 = (now - timedelta(days=1)).isoformat()
        recent2 = (now - timedelta(days=2)).isoformat()

        event1 = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "file1.txt"},
            timestamp=recent1,
        )
        event2 = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "file2.txt"},
            timestamp=recent2,
        )

        self.storage.append(event1)
        self.storage.append(event2)

        stats = self.cleaner.cleanup()

        self.assertEqual(stats["removed"], 0)
        self.assertEqual(stats["kept"], 2)

    def test_cleanup_dry_run(self):
        """Test cleanup dry-run mode."""
        now = datetime.utcnow()
        old_timestamp = (now - timedelta(days=8)).isoformat()

        old_event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "old.txt"},
            timestamp=old_timestamp,
        )

        self.storage.append(old_event)

        stats = self.cleaner.cleanup(dry_run=True)

        self.assertEqual(stats["removed"], 1)

        # Event should still be there after dry-run
        all_events = self.storage.read_all()
        self.assertEqual(len(all_events), 1)

    def test_cleanup_empty_storage(self):
        """Test cleanup on empty storage."""
        stats = self.cleaner.cleanup()

        self.assertEqual(stats["removed"], 0)
        self.assertEqual(stats["kept"], 0)
        self.assertEqual(stats["total"], 0)

    def test_should_cleanup(self):
        """Test should_cleanup check."""
        self.assertFalse(self.cleaner.should_cleanup())

        now = datetime.utcnow()
        old_timestamp = (now - timedelta(days=8)).isoformat()

        old_event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "old.txt"},
            timestamp=old_timestamp,
        )

        self.storage.append(old_event)

        self.assertTrue(self.cleaner.should_cleanup())

    def test_custom_ttl_days(self):
        """Test cleaner with custom TTL days."""
        custom_cleaner = TTLCleaner(self.storage_path, ttl_days=1)

        now = datetime.utcnow()
        old_timestamp = (now - timedelta(days=2)).isoformat()

        old_event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "old.txt"},
            timestamp=old_timestamp,
        )

        self.storage.append(old_event)

        stats = custom_cleaner.cleanup()

        self.assertEqual(stats["removed"], 1)

    def test_cleanup_with_corrupted_lines(self):
        """Test cleanup with some corrupted event lines."""
        # Add valid event
        event = Event(
            EventType.FILE_CREATE,
            "universal",
            {"filepath": "file.txt"},
        )
        self.storage.append(event)

        # Add corrupted line
        with open(self.storage_path, "a") as f:
            f.write("invalid json line\n")

        # Cleanup should skip corrupted line and work
        stats = self.cleaner.cleanup()

        # Should have 1 valid event kept
        self.assertEqual(stats["kept"], 1)

    def test_cleanup_all_old_events(self):
        """Test cleanup when all events are old."""
        now = datetime.utcnow()
        old_timestamp = (now - timedelta(days=8)).isoformat()

        for i in range(5):
            event = Event(
                EventType.FILE_CREATE,
                "universal",
                {"filepath": f"old{i}.txt"},
                timestamp=old_timestamp,
            )
            self.storage.append(event)

        stats = self.cleaner.cleanup()

        self.assertEqual(stats["removed"], 5)
        self.assertEqual(stats["kept"], 0)

        # After cleanup, storage should be empty
        remaining = self.storage.read_all()
        self.assertEqual(len(remaining), 0)


if __name__ == "__main__":
    unittest.main()
