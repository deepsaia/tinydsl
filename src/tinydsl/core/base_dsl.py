"""
Abstract base class for all TinyDSL implementations.

This provides a standard interface that all DSLs must implement,
enabling plugin architecture and uniform agent integration.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pathlib import Path


class BaseDSL(ABC):
    """
    Base class for all DSL interpreters in TinyDSL.

    All DSLs must implement:
    - parse(): Parse DSL code into internal representation
    - render(): Execute/render the parsed program
    - grammar_path: Path to Lark grammar file
    - name: Unique DSL identifier
    """

    def __init__(self, **kwargs):
        """Initialize DSL with optional configuration."""
        self.config = kwargs
        self.context: Dict[str, Any] = {}
        self._parsed = False

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this DSL (e.g., 'gli', 'lexi', 'tinycalc')."""
        pass

    @property
    @abstractmethod
    def grammar_path(self) -> Path:
        """Path to the Lark grammar file for this DSL."""
        pass

    @abstractmethod
    def parse(self, code: str) -> Any:
        """
        Parse DSL code into internal representation.

        Args:
            code: DSL source code as string

        Returns:
            Parsed representation (AST, shape list, output, etc.)
        """
        pass

    @abstractmethod
    def render(self) -> Any:
        """
        Execute/render the parsed program.

        Returns:
            Output appropriate to the DSL (image path, text, query result, etc.)
        """
        pass

    def reset(self) -> None:
        """Reset DSL state (context, memory, etc.)."""
        self.context = {}
        self._parsed = False

    def get_context(self) -> Dict[str, Any]:
        """Get current execution context."""
        return self.context.copy()

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set execution context."""
        self.context = context.copy()

    # Optional methods with default implementations
    def validate(self, code: str) -> bool:
        """
        Validate DSL code without executing.

        Returns:
            True if code is syntactically valid
        """
        try:
            self.parse(code)
            return True
        except Exception:
            return False

    def get_examples(self) -> List[Dict[str, Any]]:
        """
        Get example programs for this DSL.

        Returns:
            List of example dictionaries with 'code', 'description', etc.
        """
        return []

    def get_tasks(self) -> List[Dict[str, Any]]:
        """
        Get benchmark tasks for this DSL.

        Returns:
            List of task dictionaries with 'id', 'code', 'expected_output', etc.
        """
        return []

    def execute(self, code: str) -> Any:
        """
        Convenience method: parse and render in one call.

        Args:
            code: DSL source code as string

        Returns:
            Rendered output from the DSL
        """
        self.parse(code)
        return self.render()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}'>"
