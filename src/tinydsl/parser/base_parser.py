from abc import ABC, abstractmethod

class BaseParser(ABC):
    """Abstract base class for all parsers in TinyDSL."""

    @abstractmethod
    def parse_expression(self, expr: str, context: dict | None = None):
        """Parse and evaluate a mathematical or symbolic expression."""
        pass

    @abstractmethod
    def sanitize(self, expr: str) -> str:
        """Optional sanitization for DSL expressions."""
        pass
