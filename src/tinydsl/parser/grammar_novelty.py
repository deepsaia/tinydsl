import re
import json
from pathlib import Path
from collections import defaultdict

def analyze_grammar(grammar_text):
    """Analyze a single grammar file for novelty and structural complexity."""
    # Basic regex patterns
    rule_pattern = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:", re.MULTILINE)
    literal_pattern = re.compile(r'"([^"]+)"')
    regex_pattern = re.compile(r"/([^/]+)/")
    comment_pattern = re.compile(r"//\s*(.*)")
    alt_pattern = re.compile(r"\|")
    opt_pattern = re.compile(r"\[.*?\]")
    group_pattern = re.compile(r"\(.*?\)")
    brace_pattern = re.compile(r"\{.*?\}")

    # Extract components
    rules = rule_pattern.findall(grammar_text)
    literals = literal_pattern.findall(grammar_text)
    regexes = regex_pattern.findall(grammar_text)
    comments = comment_pattern.findall(grammar_text)

    # Rule-by-rule analysis
    rule_data = {}
    for rule_match in rule_pattern.finditer(grammar_text):
        name = rule_match.group(1)
        start = rule_match.end()
        end = grammar_text.find("\n\n", start)
        rhs = grammar_text[start:end].strip() if end != -1 else grammar_text[start:].strip()

        alts = len(alt_pattern.findall(rhs))
        opts = len(opt_pattern.findall(rhs))
        groups = len(group_pattern.findall(rhs))
        braces = len(brace_pattern.findall(rhs))
        literals_in_rule = len(literal_pattern.findall(rhs))
        regexes_in_rule = len(regex_pattern.findall(rhs))

        # Heuristic "novelty" score
        novelty = (0.2 * literals_in_rule +
                   0.3 * alts +
                   0.3 * opts +
                   0.2 * (groups + braces))
        complexity = alts + opts + groups + braces + literals_in_rule + regexes_in_rule

        rule_data[name] = {
            "alts": alts,
            "opts": opts,
            "groups": groups,
            "braces": braces,
            "literals": literals_in_rule,
            "regexes": regexes_in_rule,
            "complexity_score": complexity,
            "novelty_score": round(novelty, 2)
        }

    # Top-level metrics
    summary = {
        "num_rules": len(rules),
        "num_literals": len(literals),
        "num_regexes": len(regexes),
        "avg_rule_complexity": round(sum(v["complexity_score"] for v in rule_data.values()) / (len(rule_data) or 1), 2),
        "explicit_novelty_mentions": [c for c in comments if "novel" in c.lower() or "post-cutoff" in c.lower()],
    }

    return {
        "rules": rule_data,
        "literals": sorted(set(literals)),
        "regexes": sorted(set(regexes)),
        "comments": comments,
        "summary": summary,
    }


def print_summary(analysis):
    print("\n=== Grammar Feature Summary ===")
    s = analysis["summary"]
    print(f"📜 Rules: {s['num_rules']}")
    print(f"🔤 Literals: {s['num_literals']}")
    print(f"⚙️ Regex tokens: {s['num_regexes']}")
    print(f"🧩 Avg. rule complexity: {s['avg_rule_complexity']}")
    if s["explicit_novelty_mentions"]:
        print("\n🧠 Novelty hints in comments:")
        for c in s["explicit_novelty_mentions"]:
            print(f"   - {c}")

    print("\n🧮 Top 5 potentially novel rules:")
    ranked = sorted(analysis["rules"].items(), key=lambda kv: kv[1]["novelty_score"], reverse=True)
    for name, stats in ranked[:5]:
        print(f"   • {name:20}  novelty={stats['novelty_score']}  complexity={stats['complexity_score']}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Analyze a single Lark grammar for novelty and complexity.")
    parser.add_argument("grammar", help="Path to grammar file (.lark)")
    args = parser.parse_args()

    grammar_text = Path(args.grammar).read_text()
    analysis = analyze_grammar(grammar_text)
    print_summary(analysis)

    out_path = Path(args.grammar).with_suffix(".novelty.json")
    out_path.write_text(json.dumps(analysis, indent=2))
    print(f"\n📁 Detailed report saved to {out_path}")
