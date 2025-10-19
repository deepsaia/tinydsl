# src/tinydsl/parser/lark_gli_parser.py
from __future__ import annotations
import os, math
from typing import Callable, Dict, List, Tuple, Any

from lark import Lark, Transformer, v_args, Tree, Token
from tinydsl.parser.lark_math_parser import LarkMathParser

# (shape, x, y, size, color)
Shape = Tuple[str, float, float, float, str]

# Path to grammar
_root = os.path.dirname(os.path.abspath(__file__))
_data = os.path.join(_root, "..", "data")
GLI_GRAMMAR_PATH = os.getenv("GLI_GRAMMAR_PATH", os.path.join(_data, "gli_grammar.lark"))

# Heuristic to decide if a VALUE looks like a math expression
_MATH_CHARS = set("+-*/^()")
_MATH_FUNCS = ("sin(", "cos(", "tan(", "sqrt(", "abs(", "min(", "max(", "exp(", "log(")


def _looks_math(s: str) -> bool:
    s = s.strip()
    return (
        any(c in s for c in _MATH_CHARS)
        or any(f in s for f in _MATH_FUNCS)
        or "calc(" in s
        or "i" == s  # allow bare i
        or s.startswith("i") and any(ch in s for ch in "+-*/^)")  # i*..., i+...
    )


def _unquote(s: str) -> str:
    return s[1:-1] if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'") else s


@v_args(inline=True)
class _GLICompiler(Transformer):
    """
    Compiles the parse tree into a list of callables (imperative program).
    We then execute those callables with the current loop index `i`.
    """

    def __init__(self):
        super().__init__()
        self.shapes: List[Shape] = []
        self.context: Dict[str, Any] = {"color": "black", "size": 10.0}
        self.math = LarkMathParser()
        self.i: int = 0  # loop index set at runtime
        self.program: List[Callable[[], None]] = []

    # ---------- Helpers ----------

    # --- make value nodes return real values (no Tree objects) ---
    def VALUE(self, tok: Token):
        # always a plain string, e.g. "purple", "5+$i*5", "calc(...)", "50"
        return str(tok)

    def assign_value(self, v):
        # pass-through wrapper from grammar -> always a plain Python value, not a Tree
        return v

    def value(self, v):
        # pass-through for draw params
        return v

    # plain assignment values (used if you later expand grammar to allow explicit STRING/NUMBER/NAME)
    def plain_string(self, s):
        txt = str(s)
        return txt[1:-1] if len(txt) >= 2 and txt[0] == txt[-1] and txt[0] in ("'", '"') else txt
    def plain_number(self, n): return float(n)
    def plain_name(self, n):   return str(n)

    # draw param values (typed already when possible)
    def v_number(self, n): return float(n)
    def v_name(self, n):   return str(n)   # keep as identifier; we’ll eval later
    def v_math(self, v):   return float(v) # already numeric

    # --- keep values typed; do NOT re-stringify v here ---
    def param(self, k, v):
        # (remove the duplicate param method that returns str(v))
        return (str(k), v)

    def _eval_value(self, raw: str) -> Any:
        s = raw.strip()
        s = _unquote(s)
        s = s.replace("$i", "i")
        if s.startswith("calc(") and s.endswith(")"):
            inner = s[5:-1].strip()
            return float(self.math.parse_expression(inner, {"i": self.i, **self._math_ctx()}))
        if _looks_math(s):
            try:
                return float(self.math.parse_expression(s, {"i": self.i, **self._math_ctx()}))
            except Exception:
                pass
        try:
            return float(s)
        except Exception:
            return s  # literal (e.g., color)

    # set_stmt: allow numeric or string; size must be numeric
    def set_stmt(self, name: Token, value: Any):
        key = str(name)

        def _op():
            val = value
            if isinstance(val, str):
                val = self._eval_value(val)
            if key == "size":
                try:
                    self.context["size"] = float(val)
                except Exception:
                    # ignore invalid non-numeric size
                    pass
            else:
                self.context[key] = val

        self.program.append(_op)
        return _op

    # draw_stmt: evaluate x/y if they’re strings; pass floats through
    def draw_stmt(self, shape: Token, args: dict | None = None):
        shape_name = str(shape)
        args = args or {}
        raw_x = args.get("x", 0)
        raw_y = args.get("y", 0)

        def _coerce(v):
            if isinstance(v, (int, float)):
                return float(v)
            return float(self._eval_value(str(v)))

        def _op():
            try:
                xf = _coerce(raw_x)
                yf = _coerce(raw_y)
            except Exception:
                raise ValueError(f"x/y must be numeric after evaluation, got x={raw_x!r}, y={raw_y!r}")
            size = float(self.context.get("size", 10.0))
            color = str(self.context.get("color", "black"))
            self.shapes.append((shape_name, xf, yf, size, color))

        self.program.append(_op)
        return _op

    # draw_args: param+
    def draw_args(self, *params: Tuple[str, str]):
        return dict(params)

    # param: NAME "=" value
    def param(self, k: Token, v: Any):
        return (str(k), str(v))

    def repeat_block(self, n: Token, block_ops: List[Callable[[], None]]):
        """Repeat block n times, setting self.i at each iteration."""
        count = int(n)

        def _repeat():
            for idx in range(count):
                self.i = idx
                for op in block_ops:
                    if callable(op):
                        op()
        self.program.append(_repeat)
        return _repeat

    # start: statement+
    def start(self, *stmts):
        for op in self.program:
            if callable(op):
                op()
        return self.shapes

    # block: "{" statement+ "}"
    def block(self, *stmts):
        # each stmt is a callable we already appended to program; block returns its own list for reuse
        return list(stmts)


class LarkGLIParser:
    """Public GLI parser interface: parse(code) -> List[Shape]"""

    def __init__(self):
        with open(GLI_GRAMMAR_PATH, "r") as f:
            grammar = f.read()
        # Parse to a Tree, then compile to callables via Transformer
        self._parser = Lark(grammar, parser="lalr")

    def parse(self, code: str) -> List[Shape]:
        tree: Tree = self._parser.parse(code)
        compiler = _GLICompiler()
        shapes: List[Shape] = compiler.transform(tree)
        return shapes
