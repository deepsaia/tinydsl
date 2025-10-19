"""
TinySQL Interpreter - Simple Query DSL
"""

from pathlib import Path
from typing import Any
import json

from tinydsl.core.base_dsl import BaseDSL
from tinydsl.parser.lark_tinysql_parser import LarkTinySQLParser


class TinySQLInterpreter(BaseDSL):
    """
    TinySQL DSL interpreter for data queries.

    Example:
        load table users from "users.json"
        filter users where age > 25
        select name, email
        sort by age desc
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parser = LarkTinySQLParser()
        self.output = ""

    @property
    def name(self) -> str:
        return "tinysql"

    @property
    def grammar_path(self) -> Path:
        root = Path(__file__).parent.parent / "data"
        return root / "tinysql_grammar.lark"

    def parse(self, code: str) -> Any:
        """Parse and execute TinySQL code."""
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
        self.parser = LarkTinySQLParser()

    def get_examples(self):
        """Load TinySQL examples from JSON."""
        examples_path = self.grammar_path.parent / "tinysql_examples.json"
        if examples_path.exists():
            with open(examples_path) as f:
                return json.load(f)
        return []

    def get_tasks(self):
        """Load TinySQL tasks from JSON."""
        tasks_path = self.grammar_path.parent / "tinysql_tasks.json"
        if tasks_path.exists():
            with open(tasks_path) as f:
                return json.load(f)
        return []
