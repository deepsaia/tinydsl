import os
import math
from lark import Lark, Transformer, v_args, Tree, Token
from tinydsl.lexi.lexi_memory import LexiMemoryStore
from tinydsl.parser.lark_math_parser import LarkMathParser

root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(root_dir, "..", "data")
LEXI_GRAMMAR_PATH = os.getenv(
    "LEXI_GRAMMAR_PATH", os.path.join(data_dir, "lexi_grammar.lark")
)

@v_args(inline=True)
class LexiTransformer(Transformer):
    """Transformer that executes Lexi DSL instructions during parsing."""

    def __init__(self, memory=None, context=None):
        self.memory = memory or LexiMemoryStore()
        self.context = context or {}
        self.output = []
        self.math_parser = LarkMathParser()

    # --- Core primitives (unchanged) ---
    def say_stmt(self, text):
        self.output.append(str(text).strip('"'))

    def set_stmt(self, name, value):
        name = str(name)
        if isinstance(value, (int, float)):
            self.context[name] = value
        else:
            # Back-compat: still try your existing LarkMathParser on plain strings
            try:
                self.context[name] = self.math_parser.parse_expression(str(value), self.context)
            except Exception:
                self.context[name] = str(value)

    def remember_stmt(self, name, value):
        name = str(name)
        if isinstance(value, (int, float)):
            self.memory.set(name, value)
        else:
            # Back-compat
            try:
                self.memory.set(name, self.math_parser.parse_expression(str(value), self.context))
            except Exception:
                self.memory.set(name, str(value))

    def recall_stmt(self, name):
        val = self.memory.get(str(name), f"[undefined:{name}]")
        self.output.append(str(val))

    # --- Control flow (unchanged) ---
    def if_block(self, cond_name, cond_value, block):
        cond_name, cond_value = str(cond_name), str(cond_value)
        if str(self.context.get(cond_name)) == cond_value:
            for stmt in block:
                pass

    def repeat_block(self, count, block):
        count = int(count)
        for i in range(count):
            self.context["i"] = i
            for stmt in block:
                pass

    def block(self, *stmts):
        return stmts

    # --- Tasks (unchanged) ---
    def task_def(self, name, block):
        self.context[f"task_{name}"] = block

    def call_stmt(self, name):
        task = self.context.get(f"task_{name}")
        if task:
            for stmt in task:
                pass
        else:
            self.output.append(f"[Unknown task: {name}]")

    def start(self, *stmts):
        return self.output

    # ------------------------------------------------------------------
    # NEW: calc(...) branch — evaluate math deterministically
    # ------------------------------------------------------------------
    def math_call(self, value):
        # 'value' is the evaluated float returned by the math subtree below
        return float(value)

    # Leaf math nodes (scoped only within calc(...))
    def m_number(self, n):
        return float(n)

    def m_var(self, name):
        k = str(name)
        if k in self.context:
            try:
                return float(self.context[k])
            except Exception:
                raise ValueError(f"Variable '{k}' is not numeric: {self.context[k]!r}")
        raise ValueError(f"Unknown variable '{k}' in calc(...)")

    def m_neg(self, x):
        return -float(x)

    def m_func(self, func_name, value):
        fn = str(func_name)
        safe_funcs = {m: getattr(math, m) for m in dir(math) if not m.startswith("_")}
        if fn not in safe_funcs:
            raise ValueError(f"Unsupported function '{fn}'")
        return float(safe_funcs[fn](float(value)))

    def add(self, a, b): return float(a) + float(b)
    def sub(self, a, b): return float(a) - float(b)
    def mul(self, a, b): return float(a) * float(b)
    def div(self, a, b): return float(a) / float(b)
    def pow(self, a, b): return float(a) ** float(b)

    # stringify wrappers for plain values
    def assign_value(self, v):
        # pass-through wrapper so downstream sees a plain value
        return v

    def plain_string(self, s):
        # s is an ESCAPED_STRING token like '"blue"'
        txt = str(s)
        return txt[1:-1] if len(txt) >= 2 and txt[0] == txt[-1] and txt[0] in ('"', "'") else txt

    def plain_number(self, n):
        return float(n)

    def plain_name(self, n):
        # keep as bare identifier string (existing behavior)
        return str(n)


class LarkLexiParser:
    """Main Lark parser for Lexi DSL with unambiguous inline math via calc(...)."""

    def __init__(self):
        with open(LEXI_GRAMMAR_PATH) as f:
            grammar = f.read()
        self.parser = Lark(grammar, parser="lalr", transformer=LexiTransformer())

    def parse(self, code: str):
        try:
            return "\n".join(self.parser.parse(code))
        except Exception as e:
            raise ValueError(f"Lexi parse error: {e}")


class LarkLexiASTParser:
    """
    A plain-parser (no Transformer) for Lexi, used to return the AST.
    Produces a Lark Tree; helper methods convert it to dict/pretty/DOT.
    """

    def __init__(self):
        with open(LEXI_GRAMMAR_PATH, "r") as f:
            grammar = f.read()
        # No transformer: we want the raw Tree
        self.parser = Lark(grammar, parser="lalr")

    def parse_tree(self, code: str) -> Tree:
        return self.parser.parse(code)

    # --------- Utilities to export the AST ----------
    @staticmethod
    def tree_to_dict(node):
        if isinstance(node, Tree):
            return {
                "type": str(node.data),
                "children": [LarkLexiASTParser.tree_to_dict(c) for c in node.children],
            }
        elif isinstance(node, Token):
            return {"type": "token", "terminal": node.type, "value": str(node)}
        else:
            return {"type": "literal", "value": repr(node)}

    @staticmethod
    def tree_pretty(node: Tree) -> str:
        # Human-readable, like Lark's .pretty()
        return node.pretty()

    @staticmethod
    def tree_to_dot(node: Tree) -> str:
        """
        Minimal Graphviz DOT (no external deps). You can pipe to dot -Tpng later.
        """
        lines = ["digraph G {", '  node [shape=box, fontname="Courier"];']
        counter = {"i": 0}

        def nid():
            counter["i"] += 1
            return f"n{counter['i']}"

        def esc(s: str) -> str:
            return s.replace("\\", "\\\\").replace('"', '\\"')

        def walk(n):
            my_id = nid()
            if isinstance(n, Tree):
                label = f"{n.data}"
            elif isinstance(n, Token):
                label = f"{n.type}\\n{n.value}"
            else:
                label = f"{type(n).__name__}\\n{n}"
            lines.append(f'  {my_id} [label="{esc(label)}"];')
            if isinstance(n, Tree):
                for c in n.children:
                    cid = walk(c)
                    lines.append(f"  {my_id} -> {cid};")
            return my_id

        walk(node)
        lines.append("}")
        return "\n".join(lines)