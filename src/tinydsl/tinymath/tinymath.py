"""
TinyMath Interpreter - General-purpose arithmetic DSL

Supports variables, functions, and mathematical expressions.
"""

from pathlib import Path
from typing import Any
import json

from tinydsl.core.base_dsl import BaseDSL
from tinydsl.parser.lark_tinymath_parser import LarkTinyMathParser


class TinyMathInterpreter(BaseDSL):
    """
    TinyMath DSL interpreter for general arithmetic.

    Example:
        x = 5
        y = 10
        x + y
        # Output: 15.0

        sqrt(16)
        # Output: 4.0

        sin(3.14159 / 2)
        # Output: 1.0
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parser = LarkTinyMathParser()
        self.output = ""

    @property
    def name(self) -> str:
        return "tinymath"

    @property
    def grammar_path(self) -> Path:
        root = Path(__file__).parent.parent / "data"
        return root / "tinymath_grammar.lark"

    def parse(self, code: str) -> Any:
        """Parse and execute TinyMath code."""
        self.output = self.parser.parse(code)
        self._parsed = True
        return self.output

    def render(self) -> str:
        """Return the execution output."""
        if not self._parsed:
            raise RuntimeError("Must call parse() before render()")
        return self.output

    def reset(self) -> None:
        """Reset interpreter state."""
        super().reset()
        self.output = ""
        self.parser = LarkTinyMathParser()

    def get_examples(self):
        """Load TinyMath examples from JSON."""
        examples_path = self.grammar_path.parent / "tinymath_examples.json"
        if examples_path.exists():
            with open(examples_path) as f:
                return json.load(f)
        return []

    def get_tasks(self):
        """Load TinyMath tasks from JSON."""
        tasks_path = self.grammar_path.parent / "tinymath_tasks.json"
        if tasks_path.exists():
            with open(tasks_path) as f:
                return json.load(f)
        return []


if __name__ == "__main__":
    # Demo TinyMath
    code = """
    # Variable assignments
    x = 5
    y = 10

    # Arithmetic
    x + y
    x * y

    # Functions
    sqrt(16)
    sin(0)
    max(1, 2, 3, 4, 5)

    # Complex expressions
    (x + y) * 2
    """

    math_interp = TinyMathInterpreter()
    math_interp.parse(code)
    print("TinyMath Output:")
    print(math_interp.render())
