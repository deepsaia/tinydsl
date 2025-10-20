"""Lark parser for TinyMath DSL."""

import math
from pathlib import Path
from lark import Lark, Transformer
from typing import Dict


class TinyMathTransformer(Transformer):
    """Transform TinyMath parse tree into evaluated results."""

    def __init__(self):
        super().__init__()
        self.variables: Dict[str, float] = {}
        self.results = []

    def number(self, args):
        """Convert number token to float."""
        return float(args[0])

    def var(self, args):
        """Retrieve variable value."""
        name = str(args[0])
        if name not in self.variables:
            raise ValueError(f"Undefined variable: {name}")
        return self.variables[name]

    def assignment(self, args):
        """Assign value to variable."""
        name = str(args[0])
        value = args[1]
        self.variables[name] = value
        self.results.append(f"{name} = {value}")
        return value

    def show_stmt(self, args):
        """Show variable value."""
        name = str(args[0])
        if name not in self.variables:
            raise ValueError(f"Undefined variable: {name}")
        value = self.variables[name]
        self.results.append(f"{name} = {value}")
        return value

    def add(self, args):
        """Addition."""
        return args[0] + args[1]

    def sub(self, args):
        """Subtraction."""
        return args[0] - args[1]

    def mul(self, args):
        """Multiplication."""
        return args[0] * args[1]

    def div(self, args):
        """Division."""
        if args[1] == 0:
            raise ValueError("Division by zero")
        return args[0] / args[1]

    def mod(self, args):
        """Modulo."""
        return args[0] % args[1]

    def pow(self, args):
        """Exponentiation."""
        return args[0] ** args[1]

    def neg(self, args):
        """Negation."""
        return -args[0]

    def pos(self, args):
        """Positive (unary plus)."""
        return +args[0]

    def eq(self, args):
        """Equality comparison."""
        return 1.0 if args[0] == args[1] else 0.0

    def neq(self, args):
        """Inequality comparison."""
        return 1.0 if args[0] != args[1] else 0.0

    def lt(self, args):
        """Less than."""
        return 1.0 if args[0] < args[1] else 0.0

    def lte(self, args):
        """Less than or equal."""
        return 1.0 if args[0] <= args[1] else 0.0

    def gt(self, args):
        """Greater than."""
        return 1.0 if args[0] > args[1] else 0.0

    def gte(self, args):
        """Greater than or equal."""
        return 1.0 if args[0] >= args[1] else 0.0

    def function_call(self, args):
        """Call built-in function."""
        func_name = str(args[0])
        # args[1] is the arguments list (or None if no args)
        func_args = args[1] if len(args) > 1 and args[1] is not None else []

        # Built-in functions
        functions = {
            "sin": lambda x: math.sin(x),
            "cos": lambda x: math.cos(x),
            "tan": lambda x: math.tan(x),
            "asin": lambda x: math.asin(x),
            "acos": lambda x: math.acos(x),
            "atan": lambda x: math.atan(x),
            "sqrt": lambda x: math.sqrt(x),
            "abs": lambda x: abs(x),
            "log": lambda x: math.log(x),
            "log10": lambda x: math.log10(x),
            "exp": lambda x: math.exp(x),
            "floor": lambda x: math.floor(x),
            "ceil": lambda x: math.ceil(x),
            "round": lambda x: round(x),
            "min": lambda *args: min(args),
            "max": lambda *args: max(args),
            "pow": lambda x, y: x**y,
        }

        if func_name not in functions:
            raise ValueError(f"Unknown function: {func_name}")

        try:
            result = functions[func_name](*func_args)
            return result
        except Exception as e:
            raise ValueError(f"Error calling {func_name}: {e}")

    def arguments(self, args):
        """Collect function arguments as a flat list."""
        return list(args)

    def statement(self, args):
        """Process statement and collect result."""
        if len(args) > 0:
            result = args[0]
            # If it's an expression result (not assignment/show), add it
            if not isinstance(result, str) and result is not None:
                self.results.append(str(result))
            return result
        return None


class LarkTinyMathParser:
    """Lark-based parser for TinyMath DSL."""

    def __init__(self):
        grammar_path = Path(__file__).parent.parent / "data" / "tinymath_grammar.lark"
        with open(grammar_path, "r") as f:
            self.grammar = f.read()

        self.parser = Lark(
            self.grammar, parser="lalr", transformer=TinyMathTransformer()
        )

    def parse(self, code: str) -> str:
        """
        Parse and execute TinyMath code.

        Args:
            code: TinyMath source code

        Returns:
            Output as string (one result per line)

        Raises:
            ValueError: On syntax or runtime errors
        """
        try:
            transformer = TinyMathTransformer()
            tree = Lark(self.grammar, parser="lalr").parse(code)

            # Transform tree with fresh transformer
            transformer.transform(tree)

            # Return results
            if transformer.results:
                return "\n".join(transformer.results)
            else:
                return ""

        except Exception as e:
            raise ValueError(f"TinyMath parse error: {e}")


if __name__ == "__main__":
    # Test the parser
    parser = LarkTinyMathParser()

    test_code = """
    x = 5
    y = 10
    x + y
    x * y
    sqrt(16)
    sin(0)
    max(1, 2, 3)
    """

    result = parser.parse(test_code)
    print("TinyMath output:")
    print(result)
