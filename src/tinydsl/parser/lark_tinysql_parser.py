"""
Lark parser for TinySQL DSL - Simple query language.
"""

import os
import json
from typing import Dict, List, Any
from lark import Lark, Transformer, v_args, Token


root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(root_dir, "..", "data")
TINYSQL_GRAMMAR_PATH = os.getenv(
    "TINYSQL_GRAMMAR_PATH", os.path.join(data_dir, "tinysql_grammar.lark")
)


@v_args(inline=True)
class TinySQLTransformer(Transformer):
    """
    Transformer that executes SQL-like operations on in-memory tables.
    """

    def __init__(self):
        super().__init__()
        self.tables: Dict[str, List[Dict[str, Any]]] = {}
        self.current_table: str = ""
        self.current_data: List[Dict[str, Any]] = []
        self.output: List[str] = []

    def load_stmt(self, name, filepath):
        """Load a JSON table from file."""
        table_name = str(name)
        file_path = str(filepath)[1:-1]  # Remove quotes

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                self.tables[table_name] = data
                self.current_table = table_name
                self.current_data = data
                self.output.append(f"Loaded {len(data)} rows into {table_name}")
        except Exception as e:
            self.output.append(f"Error loading {file_path}: {e}")

    def filter_stmt(self, table_name, field, op, val):
        """Filter rows where field matches condition."""
        table_name = str(table_name)
        field = str(field)
        op = str(op)

        if table_name not in self.tables:
            self.output.append(f"Error: Table {table_name} not found")
            return

        # Get value
        if hasattr(val, "value"):
            value = val.value
            # Remove quotes from strings
            if value.startswith('"') or value.startswith("'"):
                value = value[1:-1]
            # Try to convert to number
            try:
                value = float(value)
            except:
                pass
        else:
            value = str(val)

        # Filter logic
        filtered = []
        for row in self.tables[table_name]:
            row_val = row.get(field)
            if row_val is None:
                continue

            match = False
            if op == "=":
                match = row_val == value
            elif op == ">":
                match = row_val > value
            elif op == "<":
                match = row_val < value
            elif op == ">=":
                match = row_val >= value
            elif op == "<=":
                match = row_val <= value
            elif op == "!=":
                match = row_val != value

            if match:
                filtered.append(row)

        self.current_data = filtered
        self.output.append(f"Filtered to {len(filtered)} rows")

    def select_stmt(self, names):
        """Select specific columns."""
        if isinstance(names, list):
            fields = [str(n) for n in names]
        else:
            fields = [str(names)]

        selected = []
        for row in self.current_data:
            new_row = {field: row.get(field) for field in fields if field in row}
            selected.append(new_row)

        self.current_data = selected
        # Output the selected data as JSON
        self.output.append(json.dumps(selected, indent=2))

    def sort_stmt(self, field, order=None):
        """Sort by field."""
        field = str(field)
        reverse = str(order) == "desc" if order else False

        try:
            self.current_data = sorted(
                self.current_data,
                key=lambda x: x.get(field, 0),
                reverse=reverse
            )
            self.output.append(f"Sorted by {field} {'desc' if reverse else 'asc'}")
        except Exception as e:
            self.output.append(f"Error sorting: {e}")

    def limit_stmt(self, n):
        """Limit number of rows."""
        n = int(n)
        self.current_data = self.current_data[:n]
        self.output.append(f"Limited to {n} rows")

    def show_stmt(self):
        """Show all table names."""
        tables = list(self.tables.keys())
        self.output.append(f"Tables: {', '.join(tables)}")

    def join_stmt(self, other_table, left_key, right_key):
        """Simple inner join (placeholder)."""
        self.output.append(f"Join not fully implemented yet")

    def name_list(self, *names):
        """List of field names."""
        return [str(n) for n in names]

    def value(self, v):
        """A value (string, number, or name)."""
        return v

    def start(self, *statements):
        return "\n".join(self.output)


class LarkTinySQLParser:
    """Public TinySQL parser interface."""

    def __init__(self):
        with open(TINYSQL_GRAMMAR_PATH, "r") as f:
            grammar = f.read()
        self.parser = Lark(grammar, parser="lalr", transformer=TinySQLTransformer())

    def parse(self, code: str) -> str:
        """Parse and execute TinySQL code."""
        try:
            return self.parser.parse(code)
        except Exception as e:
            raise ValueError(f"TinySQL parse error: {e}")
