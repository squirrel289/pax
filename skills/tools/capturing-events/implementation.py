"""Capture-events skill implementation with CLI entry point."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from event_schema import Event, EventType
from providers.facade import ProviderFacade
from storage.jsonl_handler import JSONLStorage, TTLCleaner


def get_storage_path() -> str:
    """
    Get path to episodes.jsonl.

    Returns:
        Path to episodes.jsonl in .vscode/pax-memory/
    """
    # Try to find .vscode/pax-memory from current directory or parent
    current = Path.cwd()

    while current != current.parent:
        vscode_memory = current / ".vscode" / "pax-memory"
        if vscode_memory.exists():
            return str(vscode_memory / "episodes.jsonl")

        current = current.parent

    # Default to .vscode/pax-memory/episodes.jsonl from workspace root
    workspace_root = Path.cwd()
    return str(workspace_root / ".vscode" / "pax-memory" / "episodes.jsonl")


class CaptureEventsSkill:
    """Capture-events skill for continuous feedback loop."""

    def __init__(self, storage_path: Optional[str] = None, provider: Optional[str] = None):
        """
        Initialize capture-events skill.

        Args:
            storage_path: Path to episodes.jsonl (auto-detect if None)
            provider: Provider name or None to auto-detect
        """
        self.storage_path = storage_path or get_storage_path()
        self.storage = JSONLStorage(self.storage_path)
        self.cleaner = TTLCleaner(self.storage_path)
        self.facade = ProviderFacade(provider)

    def capture_file(self, event_type: str, filepath: str) -> dict:
        """
        Capture file event and store.

        Args:
            event_type: "create", "modify", or "delete"
            filepath: File path

        Returns:
            Result dict
        """
        try:
            full_event_type = f"file_{event_type}"
            event = self.facade._provider.capture_file_event(full_event_type, filepath)
            self.storage.append(event)

            return {
                "success": True,
                "event_type": full_event_type,
                "filepath": filepath,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def capture_terminal(
        self, command: str, output: str = "", error: str = ""
    ) -> dict:
        """
        Capture terminal event and store.

        Args:
            command: Command executed
            output: Command output
            error: Error output

        Returns:
            Result dict
        """
        try:
            event = self.facade._provider.capture_terminal_event(
                "terminal_execute", command, output, error
            )
            self.storage.append(event)

            return {
                "success": True,
                "event_type": "terminal_execute",
                "command": command,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def capture_diagnostic(
        self, filepath: str, line: int, message: str, severity: str = "error"
    ) -> dict:
        """
        Capture diagnostic event and store.

        Args:
            filepath: File with diagnostic
            line: Line number
            message: Diagnostic message
            severity: "error", "warning", or "info"

        Returns:
            Result dict
        """
        try:
            event_type = f"diagnostic_{severity}"
            event = self.facade._provider.capture_diagnostic_event(
                event_type, filepath, line, message
            )
            self.storage.append(event)

            return {
                "success": True,
                "event_type": event_type,
                "filepath": filepath,
                "line": line,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def capture_skill(self, skill_name: str, event_type: str, status: str) -> dict:
        """
        Capture skill event and store.

        Args:
            skill_name: Name of the skill
            event_type: "invoke", "complete", or "error"
            status: Status message

        Returns:
            Result dict
        """
        try:
            full_event_type = f"skill_{event_type}"
            event = self.facade._provider.capture_skill_event(full_event_type, skill_name, status)
            self.storage.append(event)

            return {
                "success": True,
                "event_type": full_event_type,
                "skill_name": skill_name,
                "status": status,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cleanup(self, dry_run: bool = False) -> dict:
        """
        Run TTL cleanup.

        Args:
            dry_run: If True, don't actually delete

        Returns:
            Cleanup statistics
        """
        return self.cleaner.cleanup(dry_run=dry_run)

    def read_all(self) -> dict:
        """
        Read all stored events.

        Returns:
            Dict with events list and count
        """
        try:
            events = self.storage.read_all()
            return {
                "success": True,
                "count": len(events),
                "events": [e.to_dict() for e in events],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_by_type(self, event_type: str) -> dict:
        """
        Read events of specific type.

        Args:
            event_type: Event type to filter

        Returns:
            Dict with matching events
        """
        try:
            events = self.storage.read_by_type(event_type)
            return {
                "success": True,
                "event_type": event_type,
                "count": len(events),
                "events": [e.to_dict() for e in events],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stats(self) -> dict:
        """
        Get storage statistics.

        Returns:
            Dict with stats
        """
        try:
            all_events = self.storage.read_all()
            event_types = {}
            providers = {}

            for event in all_events:
                event_types[event.event_type.value] = (
                    event_types.get(event.event_type.value, 0) + 1
                )
                providers[event.provider] = providers.get(event.provider, 0) + 1

            return {
                "success": True,
                "total_events": len(all_events),
                "event_types": event_types,
                "providers": providers,
                "storage_path": self.storage_path,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    """CLI entry point for capture-events skill."""
    parser = argparse.ArgumentParser(
        description="Capture-events skill for continuous feedback loop"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # File capture command
    file_parser = subparsers.add_parser("file", help="Capture file event")
    file_parser.add_argument(
        "type", choices=["create", "modify", "delete"], help="File event type"
    )
    file_parser.add_argument("filepath", help="Path to file")

    # Terminal capture command
    term_parser = subparsers.add_parser("terminal", help="Capture terminal event")
    term_parser.add_argument("command", help="Command executed")
    term_parser.add_argument("--output", default="", help="Command output")
    term_parser.add_argument("--error", default="", help="Error output")

    # Diagnostic capture command
    diag_parser = subparsers.add_parser("diagnostic", help="Capture diagnostic event")
    diag_parser.add_argument("filepath", help="File with diagnostic")
    diag_parser.add_argument("--line", type=int, default=1, help="Line number")
    diag_parser.add_argument("--message", required=True, help="Diagnostic message")
    diag_parser.add_argument(
        "--severity", choices=["error", "warning", "info"], default="error"
    )

    # Skill capture command
    skill_parser = subparsers.add_parser("skill", help="Capture skill event")
    skill_parser.add_argument("name", help="Skill name")
    skill_parser.add_argument(
        "type", choices=["invoke", "complete", "error"], help="Skill event type"
    )
    skill_parser.add_argument("--status", required=True, help="Status message")

    # Read commands
    read_parser = subparsers.add_parser("read", help="Read stored events")
    read_parser.add_argument(
        "--type", help="Filter by event type"
    )

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Run TTL cleanup")
    cleanup_parser.add_argument("--dry-run", action="store_true", help="Don't actually delete")

    # Stats command
    subparsers.add_parser("stats", help="Show storage statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    skill = CaptureEventsSkill()

    # Execute command
    if args.command == "file":
        result = skill.capture_file(args.type, args.filepath)
    elif args.command == "terminal":
        result = skill.capture_terminal(args.command, args.output, args.error)
    elif args.command == "diagnostic":
        result = skill.capture_diagnostic(
            args.filepath, args.line, args.message, args.severity
        )
    elif args.command == "skill":
        result = skill.capture_skill(args.name, args.type, args.status)
    elif args.command == "read":
        if args.type:
            result = skill.read_by_type(args.type)
        else:
            result = skill.read_all()
    elif args.command == "cleanup":
        result = skill.cleanup(dry_run=args.dry_run)
    elif args.command == "stats":
        result = skill.stats()
    else:
        parser.print_help()
        sys.exit(1)

    # Output result
    print(json.dumps(result, indent=2))

    if not result.get("success", True):
        sys.exit(1)


if __name__ == "__main__":
    main()
