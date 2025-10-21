import json
import re
from pathlib import Path
from lark.tree import Tree, Token
from lark.load_grammar import load_grammar, TERMINALS, RULES

# --------------------------------------------
# Base Class: GrammarAnalyzer
# --------------------------------------------
class GrammarAnalyzer:
    """Base class for analyzing Lark grammars."""

    def __init__(self, grammar_path: str):
        self.grammar_path = Path(grammar_path)
        self.grammar_text = self.grammar_path.read_text()
        self.grammar, _ = load_grammar(
            self.grammar_text,
            "<grammar_analysis>",
            import_paths=[Path(".")],
            global_keep_all_tokens=True
        )

        # Canonical Lark rules
        self.lark_terminals = TERMINALS
        self.lark_rules = RULES

        # Analysis containers
        self.analysis = {}
        self.all_literals = set()
        self.all_regexes = set()
        self.comment_hints = []

    # ---------- Utility Methods ----------
    @staticmethod
    def extract_comment_hints(grammar_text: str):
        """Extract novelty-related comment hints (or other metadata)."""
        comments = re.findall(r"//[^\n]+", grammar_text)
        hints = [c.strip() for c in comments if re.search(r"novel|post-cutoff", c, re.IGNORECASE)]
        return hints

    def analyze(self):
        """Abstract placeholder for subclass analysis."""
        raise NotImplementedError("Subclasses must implement analyze().")

    def _load_rule_defs(self):
        """Return the rule definitions from Lark's Grammar object."""
        return getattr(self.grammar, "rule_defs", [])


# --------------------------------------------
# Subclass: GrammarNoveltyAnalyzer
# --------------------------------------------
class GrammarNoveltyAnalyzer(GrammarAnalyzer):
    """Analyzer for novelty metrics in Lark grammars."""

    DOMAIN_KEYWORDS = {
        "iteration": ["foreach", "repeat", "loop"],
        "pattern_matching": ["match", "case"],
        "error_handling": ["try", "catch", "throw", "raise"],
        "string_ops": ["concat", "split", "substring", "upper", "lower"],
        "list_ops": ["append", "list", "get", "length"],
        "functions": ["define", "func", "call", "return"],
        "memory": ["remember", "recall"],
        "graphics_transforms": ["rotate", "scale", "translate", "push", "pop"],
        "units_conversion": ["convert", "base", "flurb", "grobble", "voom"],
        "math": ["calc", "sin", "cos", "tan", "sqrt", "abs", "exp", "log", "min", "max"]
    }

    # ---------- Core Feature Extraction ----------
    def analyze_rule_features(self, rule_name: str, rule_tree: Tree):
        """Extract structural and lexical novelty metrics from a rule."""
        literals, regexes = [], []
        has_alt = has_opt = has_repeat = is_recursive = False

        def traverse(node):
            nonlocal has_alt, has_opt, has_repeat, is_recursive
            if isinstance(node, Tree):
                if node.data in ("literal", "pattern"):
                    val = node.children[0]
                    if isinstance(val, Token):
                        if node.data == "literal":
                            literals.append(val.value.strip('"'))
                        else:
                            regexes.append(val.value)
                elif node.data == "maybe":
                    has_opt = True
                elif node.data == "repeat":
                    has_repeat = True
                elif node.data == "expansions" and len(node.children) > 1:
                    has_alt = True
                elif node.data == "nonterminal":
                    child = node.children[0]
                    if isinstance(child, Token) and child.value == rule_name:
                        is_recursive = True
                for c in node.children:
                    traverse(c)

        traverse(rule_tree)
        return {
            "lexical": len(literals),
            "structural": sum([has_alt, has_opt, has_repeat]),
            "symbolic": len(regexes),
            "recursion": int(is_recursive),
            "keywords": literals,
            "regexes": regexes
        }

    # ---------- Semantic Domain Detection ----------
    def detect_semantic_domains(self, keywords):
        domains = []
        for domain, words in self.DOMAIN_KEYWORDS.items():
            if any(k in keywords for k in words):
                domains.append(domain)
        return domains

    # ---------- Main Analyzer ----------
    def analyze(self):
        rule_defs = self._load_rule_defs()
        for name, params, tree, options in rule_defs:
            features = self.analyze_rule_features(name, tree)
            features["overall"] = round(
                0.4 * features["lexical"]
                + 0.3 * features["structural"]
                + 0.2 * features["symbolic"]
                + 0.1 * features["recursion"],
                3,
            )
            self.analysis[name] = features
            self.all_literals.update(features["keywords"])
            self.all_regexes.update(features["regexes"])

        # Summaries
        recursives = sum(v["recursion"] for v in self.analysis.values())
        avg_lex = round(sum(v["lexical"] for v in self.analysis.values()) / len(self.analysis), 3)
        avg_struct = round(sum(v["structural"] for v in self.analysis.values()) / len(self.analysis), 3)
        avg_symb = round(sum(v["symbolic"] for v in self.analysis.values()) / len(self.analysis), 3)
        avg_overall = round(sum(v["overall"] for v in self.analysis.values()) / len(self.analysis), 3)

        # Metadata
        self.comment_hints = self.extract_comment_hints(self.grammar_text)
        self.domains = self.detect_semantic_domains(self.all_literals)

        return {
            "summary": {
                "num_rules_analyzed": len(self.analysis),
                "num_keywords": len(self.all_literals),
                "num_regex_tokens": len(self.all_regexes),
                "lexical_novelty": avg_lex,
                "structural_novelty": avg_struct,
                "symbolic_novelty": avg_symb,
                "recursive_rules": recursives,
                "detected_domains": self.domains,
                "grammar_novelty_index": avg_overall,
                "comment_hints": self.comment_hints,
                "total_lark_rules": len(self.lark_rules),
                "total_lark_terminals": len(self.lark_terminals),
            },
            "rules": self.analysis,
            "keywords": sorted(self.all_literals),
            "regex_tokens": sorted(self.all_regexes)
        }

    # ---------- Pretty Reporting ----------
    def print_report(self, result):
        s = result["summary"]
        print(f"\n=== Grammar Novelty Index Report: {self.grammar_path.name} ===")
        print(f"📜 Rules (analyzed / Lark): {s['num_rules_analyzed']} / {s['total_lark_rules']}")
        print(f"🔤 Keywords: {s['num_keywords']}")
        print(f"⚙️ Regex Tokens: {s['num_regex_tokens']}")
        print(f"🧩 Lexical Novelty: {s['lexical_novelty']}")
        print(f"🏗️ Structural Novelty: {s['structural_novelty']}")
        print(f"🔣 Symbolic Novelty: {s['symbolic_novelty']}")
        print(f"🔁 Recursive Rules: {s['recursive_rules']}")
        print(f"🌐 Domains Detected: {', '.join(s['detected_domains']) or 'None'}")
        print(f"⭐ Grammar Novelty Index (GNI): {s['grammar_novelty_index']}")
        print(f"📘 Lark terminals tracked: {s['total_lark_terminals']}\n")

        if s["comment_hints"]:
            print("🧠 Novelty hints in comments:")
            for c in s["comment_hints"]:
                print(f"   - {c}")
            print("")

        top_rules = sorted(result["rules"].items(), key=lambda kv: kv[1]["overall"], reverse=True)[:5]
        print("Top 5 Most Novel Rules:")
        for name, scores in top_rules:
            print(f"  • {name:20} → {scores}")


# --------------------------------------------
# Runner
# --------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compute Grammar Novelty Index (GNI) for any Lark grammar.")
    parser.add_argument("grammar", help="Path to .lark grammar file")
    args = parser.parse_args()

    analyzer = GrammarNoveltyAnalyzer(args.grammar)
    result = analyzer.analyze()
    analyzer.print_report(result)

    out_path = Path(args.grammar).with_suffix(".gni.json")
    out_path.write_text(json.dumps(result, indent=2))
    print(f"\n📁 Saved detailed JSON report to {out_path}")
