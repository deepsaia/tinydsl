"""
Generic AST parser for all Lark-based DSLs.

Provides common functionality to:
- Parse DSL code into a Lark Tree
- Convert Tree to JSON-serializable dict
- Generate human-readable pretty print
- Generate Graphviz DOT format

This module is DSL-agnostic and works with any Lark grammar.
"""

from lark import Lark, Tree, Token
from typing import Any, Dict


class LarkASTParser:
    """
    Generic AST parser for Lark grammars.

    Produces raw Lark Tree without transformation.
    Provides utilities to export AST in various formats.
    """

    def __init__(self, grammar_path: str):
        """
        Initialize AST parser with a grammar file.

        Args:
            grammar_path: Path to Lark grammar file (.lark)
        """
        self.grammar_path = grammar_path

        # Load grammar
        with open(grammar_path, "r") as f:
            grammar = f.read()

        # No transformer: we want the raw Tree
        self.parser = Lark(grammar, parser="lalr")

    def parse_tree(self, code: str) -> Tree:
        """
        Parse DSL code into a Lark Tree.

        Args:
            code: DSL source code string

        Returns:
            Lark Tree (AST)

        Raises:
            Exception: If parsing fails
        """
        return self.parser.parse(code)

    # --------- Utilities to export the AST ----------

    @staticmethod
    def tree_to_dict(node: Any) -> Dict:
        """
        Convert Lark Tree to JSON-serializable dictionary.

        Args:
            node: Tree, Token, or literal value

        Returns:
            Dictionary representation of the AST
        """
        if isinstance(node, Tree):
            return {
                "type": str(node.data),
                "children": [LarkASTParser.tree_to_dict(c) for c in node.children],
            }
        elif isinstance(node, Token):
            return {"type": "token", "terminal": node.type, "value": str(node)}
        else:
            return {"type": "literal", "value": repr(node)}

    @staticmethod
    def tree_pretty(node: Tree) -> str:
        """
        Get human-readable tree representation.

        Args:
            node: Lark Tree

        Returns:
            Pretty-printed string representation
        """
        return node.pretty()

    @staticmethod
    def tree_to_dot(node: Tree) -> str:
        """
        Generate Graphviz DOT format for visualization.

        The output can be rendered with:
            dot -Tpng output.dot -o tree.png

        Args:
            node: Lark Tree

        Returns:
            DOT format string
        """
        lines = ["digraph G {", '  node [shape=box, fontname="Courier"];']
        counter = {"i": 0}

        def nid():
            counter["i"] += 1
            return f"n{counter['i']}"

        def esc(s: str) -> str:
            """Escape special characters for DOT format."""
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


def create_ast_parser(grammar_path: str) -> LarkASTParser:
    """
    Factory function to create an AST parser for a DSL.

    Args:
        grammar_path: Path to Lark grammar file

    Returns:
        LarkASTParser instance
    """
    return LarkASTParser(grammar_path)
