# src/tinydsl/parser/lark_gli_parser.py
"""
Unified Gli Parser supporting both v1 (basic) and v2 (enhanced) features.

V1 features:
- set color/size
- draw shapes
- repeat blocks

V2 features (additional):
- Variables (var x = value)
- Conditionals (if/elif/else)
- User-defined functions (define func(params) { ... })
- Transforms (rotate, scale, translate, push/pop)
"""
from __future__ import annotations
import os
import math
from typing import Callable, Dict, List, Tuple, Any
from copy import deepcopy

from lark import Lark, Transformer, v_args, Tree, Token
from tinydsl.parser.lark_math_parser import LarkMathParser

# Shape: (shape_name, x, y, size, color) for v1
#        (shape_name, x, y, size, color, rotation, transform_matrix) for v2
Shape = Tuple[str, float, float, float, str, ...]

_root = os.path.dirname(os.path.abspath(__file__))
_data = os.path.join(_root, "..", "data")
GLI_GRAMMAR_PATH = os.getenv(
    "GLI_GRAMMAR_PATH", os.path.join(_data, "gli_grammar.lark")
)

_MATH_CHARS = set("+-*/^()")
_MATH_FUNCS = ("sin(", "cos(", "tan(", "sqrt(", "abs(", "min(", "max(", "exp(", "log(")


def _looks_math(s: str) -> bool:
    s = s.strip()
    return (
        any(c in s for c in _MATH_CHARS)
        or any(f in s for f in _MATH_FUNCS)
        or "calc(" in s
        or "i" == s
        or s.startswith("i")
        and any(ch in s for ch in "+-*/^)")
    )


def _unquote(s: str) -> str:
    return s[1:-1] if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'") else s


@v_args(inline=True)
class _GLICompiler(Transformer):
    """
    Unified Gli compiler supporting both v1 and v2 features.
    V2 features (variables, functions, transforms) are active when using v2 grammar.
    """

    def __init__(self, version: str = "v1"):
        super().__init__()
        self.version = version
        self.shapes: List[Shape] = []
        self.context: Dict[str, Any] = {"color": "black", "size": 10.0}
        self.math = LarkMathParser()
        self.i: int = 0
        self.program: List[Callable[[], None]] = []

        # V2 features
        self.variables: Dict[str, Any] = {}  # User-defined variables
        self.functions: Dict[str, Callable] = {}  # User-defined functions
        self.transform_stack: List[Dict[str, float]] = []  # Transformation stack
        self.current_transform = {
            "rotation": 0.0,
            "scale_x": 1.0,
            "scale_y": 1.0,
            "tx": 0.0,
            "ty": 0.0,
        }

    # ========== Common Token/Value Handlers ==========

    def VALUE(self, tok: Token):
        return str(tok)

    def assign_value(self, v):
        return v

    def value(self, v):
        return v

    def plain_string(self, s):
        txt = str(s)
        return (
            txt[1:-1]
            if len(txt) >= 2 and txt[0] == txt[-1] and txt[0] in ("'", '"')
            else txt
        )

    def plain_number(self, n):
        return float(n)

    def plain_name(self, n):
        return str(n)

    def v_number(self, n):
        return float(n)

    def v_name(self, n):
        return str(n)

    def v_math(self, v):
        return float(v)

    def param(self, k, v):
        return (str(k), v)

    def _math_ctx(self):
        """Math context with constants and variables."""
        ctx = {"pi": math.pi, "e": math.e, "i": self.i}
        if self.version == "v2":
            ctx.update(self.variables)
        return ctx

    def _eval_value(self, raw: str) -> Any:
        """Evaluate a value (supports variables, math, literals)."""
        s = raw.strip()
        s = _unquote(s)
        s = s.replace("$i", "i")

        # Check if it's a variable reference (v2 only)
        if self.version == "v2" and s in self.variables:
            return self.variables[s]

        # Math evaluation
        if s.startswith("calc(") and s.endswith(")"):
            inner = s[5:-1].strip()
            return float(self.math.parse_expression(inner, self._math_ctx()))
        if _looks_math(s):
            try:
                return float(self.math.parse_expression(s, self._math_ctx()))
            except Exception:
                pass
        try:
            return float(s)
        except Exception:
            return s  # literal string (e.g., color)

    # ========== V1 & V2: Set/Draw/Repeat ==========

    def set_stmt(self, name: Token, value: Any):
        """Set context variable (color, size)."""
        key = str(name)

        def _op():
            val = value
            if isinstance(val, str):
                val = self._eval_value(val)
            if key == "size":
                try:
                    self.context["size"] = float(val)
                except Exception:
                    pass
            else:
                self.context[key] = val

        self.program.append(_op)
        return _op

    def draw_stmt(self, shape: Token, args: dict | None = None):
        """Draw a shape at x, y."""
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

                # Apply transforms (v2 only)
                if self.version == "v2":
                    tx = self.current_transform["tx"]
                    ty = self.current_transform["ty"]
                    rot = self.current_transform["rotation"]
                    sx = self.current_transform["scale_x"]
                    sy = self.current_transform["scale_y"]

                    # Apply translation and scaling
                    xf = xf * sx + tx
                    yf = yf * sy + ty

            except Exception:
                raise ValueError(
                    f"x/y must be numeric after evaluation, got x={raw_x!r}, y={raw_y!r}"
                )

            size = float(self.context.get("size", 10.0))
            color = str(self.context.get("color", "black"))

            if self.version == "v2":
                # V2 shape format with transforms
                rot = self.current_transform["rotation"]
                sx = self.current_transform["scale_x"]
                sy = self.current_transform["scale_y"]
                tx = self.current_transform["tx"]
                ty = self.current_transform["ty"]
                transform = [rot, sx, sy, tx, ty]
                self.shapes.append((shape_name, xf, yf, size, color, rot, transform))
            else:
                # V1 shape format (simple)
                self.shapes.append((shape_name, xf, yf, size, color))

        self.program.append(_op)
        return _op

    def draw_args(self, *params: Tuple[str, str]):
        return dict(params)

    def repeat_block(self, n: Token, block_ops):
        """Repeat block n times, setting self.i at each iteration."""
        count = int(n)

        # Convert to list if not already
        if not isinstance(block_ops, list):
            block_ops = [block_ops] if block_ops else []

        # Remove operations that were added to self.program during block processing
        # (they will be executed by the repeat, so shouldn't also be in main program)
        for op in block_ops:
            if op in self.program:
                self.program.remove(op)

        def _repeat():
            for idx in range(count):
                self.i = idx
                for op in block_ops:
                    if callable(op):
                        op()

        self.program.append(_repeat)
        return _repeat

    # ========== V2 Only: Variables ==========

    def var_stmt(self, name: Token, value: Any):
        """Variable assignment (v2)."""
        key = str(name)

        def _op():
            val = value
            if isinstance(val, str):
                val = self._eval_value(val)
            self.variables[key] = val

        self.program.append(_op)
        return _op

    # ========== V2 Only: Conditionals ==========

    def if_block(
        self, name: Token, op: Token, value: Any, block: List, else_block: List = None
    ):
        """Conditional execution (v2)."""
        name = str(name)
        op = str(op)

        # Remove block operations from program (they'll be executed conditionally)
        for stmt in block:
            if stmt in self.program:
                self.program.remove(stmt)
        if else_block:
            for stmt in else_block:
                if stmt in self.program:
                    self.program.remove(stmt)

        def _op():
            # Get variable or context value
            left = self.variables.get(name, self.context.get(name))
            right = value if not isinstance(value, str) else self._eval_value(value)

            match = False
            if op in ("is", "=="):
                match = left == right
            elif op == ">":
                match = left > right
            elif op == "<":
                match = left < right
            elif op == ">=":
                match = left >= right
            elif op == "<=":
                match = left <= right
            elif op == "!=":
                match = left != right

            if match:
                for stmt in block:
                    if callable(stmt):
                        stmt()
            elif else_block:
                for stmt in else_block:
                    if callable(stmt):
                        stmt()

        self.program.append(_op)
        return _op

    # ========== V2 Only: Functions ==========

    def func_def(self, name: Token, params: List[str], block: List):
        """Define a function (v2)."""
        func_name = str(name)
        param_names = params if params else []

        # Remove block operations from program (they'll be executed when function is called)
        for stmt in block:
            if stmt in self.program:
                self.program.remove(stmt)

        def func(*args):
            # Save current variables
            saved_vars = self.variables.copy()
            # Bind arguments to parameters
            for param_name, arg in zip(param_names, args):
                self.variables[param_name] = arg
            # Execute function body
            for stmt in block:
                if callable(stmt):
                    stmt()
            # Restore variables
            self.variables = saved_vars

        self.functions[func_name] = func

        def _op():
            pass  # Function definition doesn't execute immediately

        self.program.append(_op)
        return _op

    def call_stmt(self, name: Token, args: List[Any] = None):
        """Call a function (v2)."""
        func_name = str(name)
        arg_values = args if args else []

        def _op():
            if func_name in self.functions:
                # Evaluate arguments
                evaled_args = []
                for arg in arg_values:
                    if isinstance(arg, str):
                        evaled_args.append(self._eval_value(arg))
                    else:
                        evaled_args.append(arg)
                self.functions[func_name](*evaled_args)

        self.program.append(_op)
        return _op

    def param_list(self, *names):
        return [str(n) for n in names]

    def arg_list(self, *args):
        return list(args)

    # ========== V2 Only: Transforms ==========

    def transform_stmt(self, *args):
        # Will be handled by specific transform methods
        pass

    def rotate(self, angle: Any):
        """Rotate transform (v2)."""

        def _op():
            val = angle if not isinstance(angle, str) else self._eval_value(angle)
            self.current_transform["rotation"] += float(val)

        self.program.append(_op)
        return _op

    def scale(self, sx: Any, sy: Any = None):
        """Scale transform (v2)."""

        def _op():
            scale_x = sx if not isinstance(sx, str) else self._eval_value(sx)
            scale_y = (
                sy
                if sy and not isinstance(sy, str)
                else (self._eval_value(sy) if sy else scale_x)
            )
            self.current_transform["scale_x"] *= float(scale_x)
            self.current_transform["scale_y"] *= float(scale_y)

        self.program.append(_op)
        return _op

    def translate(self, tx: Any, ty: Any):
        """Translate transform (v2)."""

        def _op():
            t_x = tx if not isinstance(tx, str) else self._eval_value(tx)
            t_y = ty if not isinstance(ty, str) else self._eval_value(ty)
            self.current_transform["tx"] += float(t_x)
            self.current_transform["ty"] += float(t_y)

        self.program.append(_op)
        return _op

    def push(self):
        """Push transform state (v2)."""

        def _op():
            self.transform_stack.append(deepcopy(self.current_transform))

        self.program.append(_op)
        return _op

    def pop(self):
        """Pop transform state (v2)."""

        def _op():
            if self.transform_stack:
                self.current_transform = self.transform_stack.pop()

        self.program.append(_op)
        return _op

    # ========== Tree Traversal ==========

    def statement(self, stmt):
        """Pass through statement content."""
        return stmt

    def start(self, *stmts):
        for op in self.program:
            if callable(op):
                op()
        return self.shapes

    def block(self, *stmts):
        """Collect block statements into a list."""
        return list(stmts)


class LarkGLIParser:
    """
    Unified GLI parser interface supporting both v1 and v2.

    Args:
        version: 'v1' for basic features, 'v2' for enhanced features
    """

    def __init__(self, version: str = "v1"):
        self.version = version

        # Load unified grammar (supports both v1 and v2 features)
        with open(GLI_GRAMMAR_PATH, "r") as f:
            grammar = f.read()

        self._parser = Lark(grammar, parser="lalr")

    def parse(self, code: str) -> List[Shape]:
        tree: Tree = self._parser.parse(code)
        compiler = _GLICompiler(version=self.version)
        shapes: List[Shape] = compiler.transform(tree)
        return shapes


# Backward compatibility aliases
LarkGLIParserV2 = LarkGLIParser  # Can use LarkGLIParser(version='v2') instead
