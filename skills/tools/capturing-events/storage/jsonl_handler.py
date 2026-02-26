"""JSONL storage handler for episodes with TTL cleanup."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

try:
    from event_schema import Event
except ImportError:
    from ..event_schema import Event


class JSONLStorage:
    """Append-only JSONL storage for events."""

    def __init__(self, filepath: str):
        """
        Initialize JSONL storage.

        Args:
            filepath: Path to episodes.jsonl file
        """
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: Event) -> bool:
        """
        Append event to JSONL file.

        Args:
            event: Event to append

        Returns:
            True if successful

        Raises:
            IOError: If write fails
        """
        try:
            event.validate()
            json_line = event.to_json() + "\n"

            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(json_line)

            return True
        except (IOError, OSError) as e:
            raise IOError(f"Failed to append event: {e}")

    def read_all(self) -> List[Event]:
        """
        Read all events from storage.

        Returns:
            List of Event instances

        Raises:
            IOError: If read fails
        """
        if not self.filepath.exists():
            return []

        events = []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event = Event.from_json(line)
                        events.append(event)
                    except ValueError:
                        # Skip invalid lines
                        continue

            return events
        except (IOError, OSError) as e:
            raise IOError(f"Failed to read events: {e}")

    def read_since(self, since_timestamp: str) -> List[Event]:
        """
        Read events since timestamp.

        Args:
            since_timestamp: ISO 8601 timestamp

        Returns:
            List of Event instances after timestamp
        """
        all_events = self.read_all()
        return [e for e in all_events if e.timestamp >= since_timestamp]

    def read_by_type(self, event_type: str) -> List[Event]:
        """
        Read events of specific type.

        Args:
            event_type: Event type to filter

        Returns:
            List of matching Event instances
        """
        all_events = self.read_all()
        return [e for e in all_events if e.event_type.value == event_type]

    def read_by_provider(self, provider: str) -> List[Event]:
        """
        Read events from specific provider.

        Args:
            provider: Provider name to filter

        Returns:
            List of matching Event instances
        """
        all_events = self.read_all()
        return [e for e in all_events if e.provider == provider]

    def count(self) -> int:
        """
        Count events in storage.

        Returns:
            Number of events
        """
        if not self.filepath.exists():
            return 0

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return sum(1 for line in f if line.strip())
        except (IOError, OSError):
            return 0

    def clear(self) -> bool:
        """
        Clear all events from storage.

        Returns:
            True if successful
        """
        try:
            if self.filepath.exists():
                self.filepath.unlink()
            return True
        except (IOError, OSError):
            return False


class TTLCleaner:
    """TTL-based cleanup for episodic memory."""

    DEFAULT_TTL_DAYS = 7

    def __init__(self, filepath: str, ttl_days: int = DEFAULT_TTL_DAYS):
        """
        Initialize TTL cleaner.

        Args:
            filepath: Path to episodes.jsonl file
            ttl_days: Number of days to retain (default: 7)
        """
        self.storage = JSONLStorage(filepath)
        self.ttl_days = ttl_days

    def cleanup(self, dry_run: bool = False) -> dict:
        """
        Remove events older than TTL.

        Args:
            dry_run: If True, don't actually remove events

        Returns:
            Dict with cleanup stats: {"removed": int, "kept": int, "total": int}
        """
        try:
            all_events = self.storage.read_all()

            if not all_events:
                return {"removed": 0, "kept": 0, "total": 0}

            cutoff_time = datetime.utcnow() - timedelta(days=self.ttl_days)
            cutoff_timestamp = cutoff_time.isoformat()

            recent_events = []
            removed_count = 0

            for event in all_events:
                if event.timestamp >= cutoff_timestamp:
                    recent_events.append(event)
                else:
                    removed_count += 1

            if not dry_run and removed_count > 0:
                # Write-back remaining events (mark-and-sweep approach)
                self.storage.clear()
                for event in recent_events:
                    self.storage.append(event)

            return {
                "removed": removed_count,
                "kept": len(recent_events),
                "total": len(all_events),
            }

        except (IOError, OSError):
            return {"removed": 0, "kept": 0, "total": 0, "error": "Cleanup failed"}

    def should_cleanup(self) -> bool:
        """
        Check if cleanup is needed.

        Returns:
            True if storage has events older than TTL
        """
        try:
            all_events = self.storage.read_all()

            if not all_events:
                return False

            cutoff_time = datetime.utcnow() - timedelta(days=self.ttl_days)
            cutoff_timestamp = cutoff_time.isoformat()

            # Check if oldest event is past cutoff
            oldest_event = min(all_events, key=lambda e: e.timestamp)
            return oldest_event.timestamp < cutoff_timestamp

        except (IOError, OSError):
            return False
