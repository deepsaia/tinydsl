"""
Abstract memory interface for DSLs.

Provides persistent storage abstraction for DSLs that need to
maintain state across invocations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
import os
from pathlib import Path


class BaseMemory(ABC):
    """Abstract base class for DSL memory/state storage."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from memory."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Store a value in memory."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove a key from memory."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all memory."""
        pass

    @abstractmethod
    def keys(self) -> list:
        """Get all keys in memory."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Export memory as dictionary."""
        pass

    def __contains__(self, key: str) -> bool:
        """Check if key exists in memory."""
        return key in self.keys()

    def __getitem__(self, key: str) -> Any:
        """Dictionary-style access."""
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Dictionary-style assignment."""
        self.set(key, value)


class InMemoryStore(BaseMemory):
    """Simple in-memory storage (non-persistent)."""

    def __init__(self):
        self._store: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def delete(self, key: str) -> None:
        if key in self._store:
            del self._store[key]

    def clear(self) -> None:
        self._store.clear()

    def keys(self) -> list:
        return list(self._store.keys())

    def to_dict(self) -> Dict[str, Any]:
        return self._store.copy()

    def __repr__(self) -> str:
        return f"<InMemoryStore: {len(self._store)} keys>"


class JSONFileMemory(BaseMemory):
    """
    Persistent memory backed by JSON file.

    This is what LexiMemoryStore implements - extracted as base class.
    """

    def __init__(self, filepath: Optional[str] = None, auto_save: bool = True):
        """
        Initialize JSON-backed memory.

        Args:
            filepath: Path to JSON file (default: output/memory.json)
            auto_save: Whether to save after each modification
        """
        if filepath is None:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            filepath = str(output_dir / "memory.json")

        self.filepath = Path(filepath)
        self.auto_save = auto_save
        self._store: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load memory from file."""
        if self.filepath.exists():
            try:
                with open(self.filepath, "r") as f:
                    self._store = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._store = {}

    def _save(self) -> None:
        """Save memory to file."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w") as f:
            json.dump(self._store, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value
        if self.auto_save:
            self._save()

    def delete(self, key: str) -> None:
        if key in self._store:
            del self._store[key]
            if self.auto_save:
                self._save()

    def clear(self) -> None:
        self._store.clear()
        if self.auto_save:
            self._save()

    def keys(self) -> list:
        return list(self._store.keys())

    def to_dict(self) -> Dict[str, Any]:
        return self._store.copy()

    def load(self) -> Dict[str, Any]:
        """Reload from disk and return current state."""
        self._load()
        return self.to_dict()

    def save(self) -> None:
        """Explicitly save to disk."""
        self._save()

    def __repr__(self) -> str:
        return f"<JSONFileMemory: {self.filepath}, {len(self._store)} keys>"
