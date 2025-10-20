"""
TinyCalc Interpreter - Novel Unit Conversion DSL

Demonstrates BaseDSL implementation with a post-cutoff knowledge domain.
"""

from pathlib import Path
from typing import Any
import json

from tinydsl.core.base_dsl import BaseDSL
from tinydsl.parser.lark_tinycalc_parser import LarkTinyCalcParser


class TinyCalcInterpreter(BaseDSL):
    """
    TinyCalc DSL interpreter for novel unit conversions.

    Example:
        define 1 flurb = 3.7 grobbles
        define 1 grobble = 2.1 zepts
        convert 10 flurbs to zepts
        # Output: 77.7 zepts
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parser = LarkTinyCalcParser()
        self.output = ""

    @property
    def name(self) -> str:
        return "tinycalc"

    @property
    def grammar_path(self) -> Path:
        root = Path(__file__).parent.parent / "data"
        return root / "tinycalc_grammar.lark"

    def parse(self, code: str) -> Any:
        """Parse and execute TinyCalc code."""
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
        self.parser = LarkTinyCalcParser()

    def get_examples(self):
        """Load TinyCalc examples from JSON."""
        examples_path = self.grammar_path.parent / "tinycalc_examples.json"
        if examples_path.exists():
            with open(examples_path) as f:
                return json.load(f)
        return []

    def get_tasks(self):
        """Load TinyCalc tasks from JSON."""
        tasks_path = self.grammar_path.parent / "tinycalc_tasks.json"
        if tasks_path.exists():
            with open(tasks_path) as f:
                return json.load(f)
        return []


if __name__ == "__main__":
    # Demo TinyCalc
    code = """
    define 1 flurb = 3.7 grobbles
    define 1 grobble = 2.1 zepts
    convert 10 flurbs to zepts
    compute 5 flurbs + 2 grobbles in zepts
    """

    calc = TinyCalcInterpreter()
    calc.parse(code)
    print(calc.render())
