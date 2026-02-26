"""Capture-events skill for continuous feedback loop."""

__version__ = "0.1.0"
__all__ = ["Event", "EventType", "ProviderFacade", "JSONLStorage"]

from .event_schema import Event, EventType
from .providers.facade import ProviderFacade
from .storage.jsonl_handler import JSONLStorage
