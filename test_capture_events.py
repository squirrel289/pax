#!/usr/bin/env python3
"""Simple test runner for capture-events skill."""

import sys
sys.path.insert(0, '/Users/macos/dev/pax/skills/tools/capture-events')

# Test imports
print("Testing imports...")
try:
    from event_schema import Event, EventType, EventValidator
    print("✓ event_schema imports work")
except ImportError as e:
    print(f"✗ event_schema import failed: {e}")
    sys.exit(1)

try:
    from providers.universal import UniversalProvider
    print("✓ UniversalProvider imports work")
except ImportError as e:
    print(f"✗ UniversalProvider import failed: {e}")
    sys.exit(1)

try:
    from storage.jsonl_handler import JSONLStorage, TTLCleaner
    print("✓ JSONLStorage imports work")
except ImportError as e:
    print(f"✗ JSONLStorage import failed: {e}")
    sys.exit(1)

# Test basic functionality
print("\nTesting basic functionality...")

# Test Event creation
event = Event(EventType.FILE_CREATE, "universal", {"filepath": "test.txt"})
print(f"✓ Created event: {event}")

# Test UniversalProvider
provider = UniversalProvider()
event2 = provider.capture_file_event("file_create", "/test/file.txt")
print(f"✓ Provider captured event: {event2}")

# Test JSONLStorage (in-memory)
import tempfile
from pathlib import Path

temp_dir = tempfile.mkdtemp()
storage_path = str(Path(temp_dir) / "test.jsonl")
storage = JSONLStorage(storage_path)
storage.append(event)
print(f"✓ Stored event to {storage_path}")

events = storage.read_all()
print(f"✓ Read {len(events)} events back from storage")

# Cleanup
if Path(storage_path).exists():
    Path(storage_path).unlink()
Path(temp_dir).rmdir()

print("\n✓✓✓ All basic functionality tests passed! ✓✓✓")
