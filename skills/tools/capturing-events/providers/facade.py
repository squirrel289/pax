"""Provider facade for assistant-agnostic event capture."""

import os
import sys
from typing import Optional

try:
    from universal import UniversalProvider
except ImportError:
    from .universal import UniversalProvider


class ProviderDetector:
    """Detect which provider/assistant is available."""

    @staticmethod
    def detect() -> str:
        """
        Detect active provider.

        Returns:
            Provider name: "copilot", "codex", "cursor", or "universal" (default)
        """
        # Check for GitHub Copilot in VS Code environment
        if "GITHUB_COPILOT_AGENT" in os.environ:
            return "copilot"

        # Check for Codex (OpenAI API key)
        if "OPENAI_API_KEY" in os.environ:
            return "codex"

        # Check for Cursor editor environment
        if "CURSOR" in os.environ or "CURSOR_PATH" in os.environ:
            return "cursor"

        # Check for VS Code environment (Copilot fallback)
        if "TERM_PROGRAM" in os.environ and "vscode" in os.environ.get(
            "TERM_PROGRAM", ""
        ).lower():
            return "copilot"

        # Default to universal (workspace-only) provider
        return "universal"


class ProviderFacade:
    """Facade for provider-agnostic event capture."""

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize provider facade.

        Args:
            provider: Explicit provider name or None to auto-detect.
                     Valid values: "universal", "copilot", "codex", "cursor"
        """
        if provider is None:
            provider = ProviderDetector.detect()

        self.provider_name = provider
        self._provider = self._create_provider(provider)

    def _create_provider(self, provider: str):
        """
        Create provider instance.

        Args:
            provider: Provider name

        Returns:
            Provider instance

        Raises:
            ValueError: If provider is unknown
        """
        if provider == "universal":
            return UniversalProvider()
        elif provider == "copilot":
            # TODO: Implement Copilot provider (wi-004)
            return UniversalProvider()  # Fall back to universal
        elif provider == "codex":
            # TODO: Implement Codex provider (wi-004)
            return UniversalProvider()  # Fall back to universal
        elif provider == "cursor":
            # TODO: Implement Cursor provider (wi-004)
            return UniversalProvider()  # Fall back to universal
        else:
            raise ValueError(
                f"Unknown provider: {provider}. "
                'Valid options: "universal", "copilot", "codex", "cursor"'
            )

    def capture_file_event(self, event_type: str, filepath: str) -> dict:
        """
        Capture file system event.

        Args:
            event_type: "file_create", "file_modify", or "file_delete"
            filepath: Path to file

        Returns:
            Event dict
        """
        return self._provider.capture_file_event(event_type, filepath)

    def capture_terminal_event(
        self, event_type: str, command: str, output: str = "", error: str = ""
    ) -> dict:
        """
        Capture terminal event.

        Args:
            event_type: "terminal_execute", "terminal_output", or "terminal_error"
            command: Command executed
            output: Command output (if any)
            error: Error output (if any)

        Returns:
            Event dict
        """
        return self._provider.capture_terminal_event(event_type, command, output, error)

    def capture_diagnostic_event(
        self, event_type: str, file: str, line: int, message: str
    ) -> dict:
        """
        Capture diagnostic event.

        Args:
            event_type: "diagnostic_error", "diagnostic_warning", or "diagnostic_info"
            file: File path with diagnostic
            line: Line number
            message: Diagnostic message

        Returns:
            Event dict
        """
        return self._provider.capture_diagnostic_event(event_type, file, line, message)

    def capture_skill_event(self, event_type: str, skill_name: str, status: str) -> dict:
        """
        Capture skill invocation event.

        Args:
            event_type: "skill_invoke", "skill_complete", or "skill_error"
            skill_name: Name of the skill
            status: Status message

        Returns:
            Event dict
        """
        return self._provider.capture_skill_event(event_type, skill_name, status)
