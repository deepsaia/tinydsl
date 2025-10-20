"""
Test contamination checking across all DSLs.
"""

from datetime import datetime
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.check_contamination import check_dsl_contamination


def test_all_dsls():
    """Test contamination checking for all DSLs."""
    dsl_dir = Path(__file__).parent.parent / "src" / "tinydsl" / "data"

    # Model cutoff (example)
    model_cutoff = datetime(2025, 1, 1)

    dsls = [
        {
            "name": "tinycalc",
            "grammar": "tinycalc_grammar.lark",
            "examples": "tinycalc_examples.json",
            "created": datetime(2024, 10, 18),
        },
        {
            "name": "lexi",
            "grammar": "lexi_grammar.lark",
            "examples": "lexi_examples.json",
            "created": datetime(2024, 10, 18),
        },
        {
            "name": "gli",
            "grammar": "gli_grammar.lark",
            "examples": "gli_examples.json",
            "created": datetime(2024, 10, 18),
        },
        {
            "name": "tinysql",
            "grammar": "tinysql_grammar.lark",
            "examples": "tinysql_examples.json",
            "created": datetime(2024, 10, 18),
        },
        {
            "name": "tinymath",
            "grammar": "tinymath_grammar.lark",
            "examples": "tinymath_examples.json",
            "created": datetime(2024, 10, 18),
        },
    ]

    print("=" * 80)
    print("CONTAMINATION CHECK - ALL DSLs")
    print("=" * 80)

    for dsl in dsls:
        print(f"\n{'='*40}")
        print(f"Testing: {dsl['name'].upper()}")
        print(f"{'='*40}")

        try:
            report = check_dsl_contamination(
                dsl_name=dsl["name"],
                grammar_path=dsl_dir / dsl["grammar"],
                examples_path=dsl_dir / dsl["examples"],
                creation_date=dsl["created"],
                model_cutoff=model_cutoff,
            )

            print(f"\n📊 Results for {dsl['name']}:")
            print(f"  Post-cutoff: {report['post_cutoff']}")
            print(f"  Novel: {report['verdict']['novel']}")
            print(f"  Confidence: {report['verdict']['confidence']}")

            uniqueness = report["uniqueness"]
            print(f"  Unique identifiers found: {uniqueness['count']}")
            print(f"  Identifiers: {uniqueness['novel_identifiers']}")

            if "declared_by_category" in uniqueness:
                print(
                    f"  Categories: {list(uniqueness['declared_by_category'].keys())}"
                )

            if "novel_features" in uniqueness and uniqueness["novel_features"]:
                print(f"  Novel features: {uniqueness['novel_features']}")

        except Exception as e:
            print(f"❌ Error checking {dsl['name']}: {e}")

    print(f"\n{'='*80}")
    print("✅ All contamination checks completed")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_all_dsls()
