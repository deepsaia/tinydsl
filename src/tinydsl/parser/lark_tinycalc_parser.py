"""
Lark parser for TinyCalc DSL - Novel unit conversion language.
"""

import os
from typing import Dict, List, Tuple
from lark import Lark, Transformer, v_args, Token


root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(root_dir, "..", "data")
TINYCALC_GRAMMAR_PATH = os.getenv(
    "TINYCALC_GRAMMAR_PATH", os.path.join(data_dir, "tinycalc_grammar.lark")
)


@v_args(inline=True)
class TinyCalcTransformer(Transformer):
    """
    Transformer that builds a unit conversion graph and performs conversions.
    """

    def __init__(self):
        super().__init__()
        self.units: Dict[str, Dict[str, float]] = {}  # unit -> {target: factor}
        self.base_unit: str = ""
        self.output: List[str] = []

    def define_stmt(self, quantity1, unit1, quantity2, unit2):
        """
        Define a conversion: 1 flurb = 3.7 grobbles
        Stores bidirectional conversion factors.
        """
        q1, u1 = float(quantity1), str(unit1)
        q2, u2 = float(quantity2), str(unit2)

        # Forward conversion factor: u1 -> u2
        factor_forward = q2 / q1
        # Reverse conversion factor: u2 -> u1
        factor_reverse = q1 / q2

        # Initialize unit dicts if needed
        if u1 not in self.units:
            self.units[u1] = {}
        if u2 not in self.units:
            self.units[u2] = {}

        # Store bidirectional conversions
        self.units[u1][u2] = factor_forward
        self.units[u2][u1] = factor_reverse

    def set_base_stmt(self, unit):
        """Set the base unit for the system."""
        self.base_unit = str(unit)

    def convert_stmt(self, amount, from_unit, to_unit):
        """Convert X units to Y units."""
        amount = float(amount)
        from_unit = str(from_unit)
        to_unit = str(to_unit)

        result = self._convert(amount, from_unit, to_unit)
        self.output.append(f"{result} {to_unit}")

    def compute_stmt(self, expr_result, target_unit):
        """Compute an expression result in target unit."""
        # expr_result is (amount, unit) tuple from expression evaluation
        if isinstance(expr_result, tuple):
            amount, unit = expr_result
            target = str(target_unit)
            result = self._convert(amount, unit, target)
            self.output.append(f"{result} {target}")
        else:
            # Just a number, no unit
            self.output.append(f"{expr_result} {target_unit}")

    def show_stmt(self):
        """Show all defined units."""
        units_list = list(self.units.keys())
        self.output.append(f"Units: {', '.join(units_list)}")

    # Expression evaluators
    def add(self, left, right):
        """Add two quantities, converting to common unit."""
        return self._binary_op(left, right, lambda a, b: a + b)

    def sub(self, left, right):
        """Subtract two quantities."""
        return self._binary_op(left, right, lambda a, b: a - b)

    def mul(self, left, right):
        """Multiply two quantities."""
        # For now, keep the unit of the left operand
        if isinstance(left, tuple) and isinstance(right, tuple):
            amt1, unit1 = left
            amt2, unit2 = right
            # Convert right to left's unit for consistent calculation
            amt2_converted = self._convert(amt2, unit2, unit1)
            return (amt1 * amt2_converted, unit1)
        elif isinstance(left, tuple):
            amt, unit = left
            return (amt * float(right), unit)
        elif isinstance(right, tuple):
            amt, unit = right
            return (float(left) * amt, unit)
        return float(left) * float(right)

    def div(self, left, right):
        """Divide two quantities."""
        if isinstance(left, tuple) and isinstance(right, tuple):
            amt1, unit1 = left
            amt2, unit2 = right
            amt2_converted = self._convert(amt2, unit2, unit1)
            return (amt1 / amt2_converted, unit1)
        elif isinstance(left, tuple):
            amt, unit = left
            return (amt / float(right), unit)
        elif isinstance(right, tuple):
            amt, unit = right
            return (float(left) / amt, unit)
        return float(left) / float(right)

    def quantity(self, number, unit):
        """A quantity with a unit."""
        return (float(number), str(unit))

    def number(self, n):
        """Plain number without unit."""
        return float(n)

    def _binary_op(self, left, right, op):
        """Helper for binary operations with unit handling."""
        if isinstance(left, tuple) and isinstance(right, tuple):
            amt1, unit1 = left
            amt2, unit2 = right
            # Convert right to left's unit
            amt2_converted = self._convert(amt2, unit2, unit1)
            return (op(amt1, amt2_converted), unit1)
        elif isinstance(left, tuple):
            amt, unit = left
            return (op(amt, float(right)), unit)
        elif isinstance(right, tuple):
            amt, unit = right
            return (op(float(left), amt), unit)
        return op(float(left), float(right))

    def _convert(self, amount: float, from_unit: str, to_unit: str) -> float:
        """
        Convert amount from one unit to another.
        Uses BFS to find conversion path through the unit graph.
        """
        if from_unit == to_unit:
            return amount

        if from_unit not in self.units:
            raise ValueError(f"Unknown unit: {from_unit}")
        if to_unit not in self.units:
            raise ValueError(f"Unknown unit: {to_unit}")

        # BFS to find path
        visited = set()
        queue = [(from_unit, amount)]

        while queue:
            current_unit, current_amount = queue.pop(0)

            if current_unit == to_unit:
                return current_amount

            if current_unit in visited:
                continue
            visited.add(current_unit)

            # Explore neighbors
            for neighbor, factor in self.units.get(current_unit, {}).items():
                if neighbor not in visited:
                    new_amount = current_amount * factor
                    queue.append((neighbor, new_amount))

        raise ValueError(f"No conversion path from {from_unit} to {to_unit}")

    def start(self, *statements):
        return "\n".join(self.output)


class LarkTinyCalcParser:
    """Public TinyCalc parser interface."""

    def __init__(self):
        with open(TINYCALC_GRAMMAR_PATH, "r") as f:
            grammar = f.read()
        self.parser = Lark(grammar, parser="lalr", transformer=TinyCalcTransformer())

    def parse(self, code: str) -> str:
        """Parse and execute TinyCalc code, returning output."""
        try:
            return self.parser.parse(code)
        except Exception as e:
            raise ValueError(f"TinyCalc parse error: {e}")
