"""
Unified Lark parser for Lexi DSL supporting both v1 (basic) and v2 (enhanced) features.

V1 features:
- say, set, remember, recall
- if/repeat blocks
- task definitions

V2 features (additional):
- String operations (concat, split, substring, length, upper, lower)
- Lists/Arrays (create, append, get, length)
- Foreach loops
- Pattern matching
- Error handling (try/catch)
"""

import os
import math
from typing import Any, List
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
    """
    Unified transformer supporting both v1 and v2 features.
    V2 features (strings, lists, pattern matching) are active when using v2 grammar.
    """

    def __init__(self, memory=None, context=None, version='v1'):
        self.memory = memory or LexiMemoryStore()
        self.context = context or {}
        self.output = []
        self.math_parser = LarkMathParser()
        self.version = version

    # ========== V1 & V2: Core Primitives ==========

    def say_stmt(self, text):
        self.output.append(str(text).strip('"'))

    def set_stmt(self, name, value):
        name = str(name)
        if isinstance(value, (int, float)):
            self.context[name] = value
        elif isinstance(value, list):
            self.context[name] = value
        else:
            try:
                self.context[name] = self.math_parser.parse_expression(str(value), self.context)
            except Exception:
                self.context[name] = str(value)

    def remember_stmt(self, name, value):
        name = str(name)
        if isinstance(value, (int, float, list)):
            self.memory.set(name, value)
        else:
            try:
                self.memory.set(name, self.math_parser.parse_expression(str(value), self.context))
            except Exception:
                self.memory.set(name, str(value))

    def recall_stmt(self, name):
        val = self.memory.get(str(name), f"[undefined:{name}]")
        if isinstance(val, list):
            self.output.append(str(val))
        else:
            self.output.append(str(val))

    # ========== V1 & V2: Control Flow ==========

    def if_block(self, cond_name, cond_value, block, else_block=None):
        """Conditional execution (v1 and v2, v2 adds else support)."""
        cond_name, cond_value = str(cond_name), str(cond_value)
        if str(self.context.get(cond_name)) == cond_value:
            for stmt in block:
                pass
        elif else_block and self.version == 'v2':
            for stmt in else_block:
                pass

    def repeat_block(self, count, block):
        count = int(count)
        for i in range(count):
            self.context["i"] = i
            for stmt in block:
                pass

    def block(self, *stmts):
        return stmts

    # ========== V1 & V2: Tasks ==========

    def task_def(self, name, block):
        self.context[f"task_{name}"] = block

    def call_stmt(self, name):
        task = self.context.get(f"task_{name}")
        if task:
            for stmt in task:
                pass
        else:
            self.output.append(f"[Unknown task: {name}]")

    # ========== V2 Only: String Operations ==========

    def str_concat(self, name1, name2, result_name):
        """Concatenate two string variables (v2)."""
        val1 = str(self.context.get(str(name1), ""))
        val2 = str(self.context.get(str(name2), ""))
        self.context[str(result_name)] = val1 + val2

    def str_split(self, name, delimiter, result_name):
        """Split string by delimiter into list (v2)."""
        val = str(self.context.get(str(name), ""))
        delim = str(delimiter).strip('"')
        self.context[str(result_name)] = val.split(delim)

    def str_substring(self, name, start, end, result_name):
        """Extract substring (v2)."""
        val = str(self.context.get(str(name), ""))
        s, e = int(start), int(end)
        self.context[str(result_name)] = val[s:e]

    def length_op(self, name, result_name):
        """Universal length operation for strings and lists (v2)."""
        val = self.context.get(str(name))
        if isinstance(val, list):
            self.context[str(result_name)] = len(val)
        else:
            # Treat as string
            self.context[str(result_name)] = len(str(val)) if val else 0

    def str_length(self, name, result_name):
        """Get string length (v2) - redirects to length_op."""
        self.length_op(name, result_name)

    def str_upper(self, name, result_name):
        """Convert string to uppercase (v2)."""
        val = str(self.context.get(str(name), ""))
        self.context[str(result_name)] = val.upper()

    def str_lower(self, name, result_name):
        """Convert string to lowercase (v2)."""
        val = str(self.context.get(str(name), ""))
        self.context[str(result_name)] = val.lower()

    # ========== V2 Only: List Operations ==========

    def list_create(self, name, values):
        """Create a list (v2)."""
        self.context[str(name)] = list(values)

    def list_append(self, name, value):
        """Append to list (v2)."""
        lst = self.context.get(str(name), [])
        if not isinstance(lst, list):
            lst = [lst]
        val = value if isinstance(value, (int, float)) else str(value).strip('"')
        lst.append(val)
        self.context[str(name)] = lst

    def list_get(self, name, index, result_name):
        """Get list element by index (v2)."""
        lst = self.context.get(str(name), [])
        idx = int(index)
        if isinstance(lst, list) and 0 <= idx < len(lst):
            self.context[str(result_name)] = lst[idx]
        else:
            self.context[str(result_name)] = None

    def list_length(self, name, result_name):
        """Get list length (v2) - redirects to length_op."""
        self.length_op(name, result_name)

    def value_list(self, *values):
        """Parse list literal values (v2)."""
        return [v if isinstance(v, (int, float)) else str(v).strip('"') for v in values]

    # ========== V2 Only: Foreach Loop ==========

    def foreach_block(self, var_name, list_name, block):
        """Foreach loop (v2)."""
        var_name = str(var_name)
        lst = self.context.get(str(list_name), [])
        if isinstance(lst, list):
            for item in lst:
                self.context[var_name] = item
                for stmt in block:
                    pass

    # ========== V2 Only: Pattern Matching ==========

    def match_block(self, name, *cases):
        """Pattern matching (v2)."""
        val = self.context.get(str(name))
        for case_val, case_block in cases:
            case_val_str = str(case_val).strip('"')
            if str(val) == case_val_str:
                for stmt in case_block:
                    pass
                break

    def match_case(self, value, block):
        """Match case (v2)."""
        return (value, block)

    # ========== V2 Only: Error Handling ==========

    def try_block(self, try_block, error_var, catch_block):
        """Try-catch error handling (v2)."""
        try:
            for stmt in try_block:
                pass
        except Exception as e:
            self.context[str(error_var)] = str(e)
            for stmt in catch_block:
                pass

    # ========== V1 & V2: Math Operations ==========

    def math_call(self, value):
        return float(value)

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

    def assign_value(self, v):
        return v

    def plain_string(self, s):
        txt = str(s)
        return txt[1:-1] if len(txt) >= 2 and txt[0] == txt[-1] and txt[0] in ('"', "'") else txt

    def plain_number(self, n):
        return float(n)

    def plain_name(self, n):
        return str(n)

    # ========== Tree Traversal ==========

    def start(self, *stmts):
        if self.version == 'v2':
            return "\n".join(self.output)
        return self.output


class LarkLexiParser:
    """
    Unified Lark parser for Lexi DSL supporting both v1 and v2.

    Args:
        version: 'v1' for basic features, 'v2' for enhanced features
    """

    def __init__(self, version: str = 'v1'):
        self.version = version

        # Load unified grammar (supports both v1 and v2 features)
        with open(LEXI_GRAMMAR_PATH) as f:
            grammar = f.read()

        self.parser = Lark(
            grammar,
            parser="lalr",
            transformer=LexiTransformer(version=version)
        )

    def parse(self, code: str):
        try:
            result = self.parser.parse(code)
            if self.version == 'v2':
                # V2 returns string from start()
                return result
            else:
                # V1 returns list from start()
                return "\n".join(result)
        except Exception as e:
            raise ValueError(f"Lexi parse error: {e}")


class LarkLexiASTParser:
    """
    A plain-parser (no Transformer) for Lexi, used to return the AST.
    Produces a Lark Tree; helper methods convert it to dict/pretty/DOT.
    Supports both v1 and v2 grammars.
    """

    def __init__(self, version: str = 'v1'):
        self.version = version

        # Load unified grammar (supports both v1 and v2 features)
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


# Backward compatibility aliases
LexiTransformerV2 = LexiTransformer
LarkLexiParserV2 = LarkLexiParser  # Can use LarkLexiParser(version='v2') instead
