from lark import Lark, Transformer
import math
from tinydsl.parser.base_parser import BaseParser


class MathTransformer(Transformer):
    """Transforms parsed tree into evaluated numeric result."""

    def __init__(self, context=None):
        self.context = context or {}

    def number(self, n):
        return float(n[0])

    def var(self, name):
        name = str(name[0])
        if name in self.context:
            return float(self.context[name])
        raise ValueError(f"Unknown variable: {name}")

    def add(self, args):
        return args[0] + args[1]

    def sub(self, args):
        return args[0] - args[1]

    def mul(self, args):
        return args[0] * args[1]

    def div(self, args):
        return args[0] / args[1]

    def pow(self, args):
        return args[0] ** args[1]

    def neg(self, args):
        return -args[0]

    def func(self, args):
        func_name = args[0]
        val = args[1]
        safe_funcs = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        if func_name in safe_funcs:
            return safe_funcs[func_name](val)
        raise ValueError(f"Unknown function: {func_name}")


# Grammar for mathematical expressions with variables and math functions
GRAMMAR = r"""
    ?start: expr
    ?expr: expr "+" term   -> add
         | expr "-" term   -> sub
         | term
    ?term: term "*" pow    -> mul
         | term "/" pow    -> div
         | pow
    ?pow: factor "^" pow   -> pow
         | factor
    ?factor: NUMBER        -> number
           | "-" factor    -> neg
           | NAME          -> var
           | FUNC "(" expr ")" -> func
           | "(" expr ")"
    FUNC: /(sin|cos|tan|sqrt|abs|min|max|exp|log)/
    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE
    %ignore WS_INLINE
"""


class LarkMathParser(BaseParser):
    """Reusable Lark-based mathematical expression parser."""

    def __init__(self):
        self.parser = Lark(GRAMMAR, parser="lalr")

    def sanitize(self, expr: str) -> str:
        return expr.strip().replace("$", "")

    def parse_expression(self, expr: str, context: dict | None = None):
        try:
            tree = self.parser.parse(expr)
            return MathTransformer(context).transform(tree)
        except Exception as e:
            raise ValueError(f"Failed to parse expression '{expr}': {e}")
