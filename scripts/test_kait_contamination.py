"""
Test KAIT agent with integrated contamination checking.
"""

from datetime import datetime
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tinydsl.agent_tools.kait_agent import KAITAgent


def test_kait_with_contamination():
    """Test KAIT agent initialization with contamination checking."""
    print("=" * 80)
    print("Testing KAIT Agent with Contamination Checking")
    print("=" * 80)

    dsls = ["tinycalc", "lexi", "gli", "tinysql", "tinymath"]

    for dsl_name in dsls:
        print(f"\n{'='*40}")
        print(f"Testing: {dsl_name.upper()}")
        print(f"{'='*40}")

        try:
            # Initialize KAIT agent with contamination checking
            agent = KAITAgent(
                dsl_name=dsl_name,
                check_contamination=True,
                creation_date=datetime(2024, 10, 18),
                model_cutoff=datetime(2025, 1, 1),
            )

            # Check if contamination report was generated
            if agent.contamination_report:
                print("\n✅ Contamination report generated")
                print(f"   Novel: {agent.contamination_report['verdict']['novel']}")
                print(f"   Post-cutoff: {agent.contamination_report['post_cutoff']}")
                print(
                    f"   Identifiers: {agent.contamination_report['uniqueness']['count']}"
                )

                # Show categories if available
                if "declared_by_category" in agent.contamination_report["uniqueness"]:
                    categories = agent.contamination_report["uniqueness"][
                        "declared_by_category"
                    ]
                    for cat, identifiers in categories.items():
                        print(f"   {cat}: {', '.join(identifiers[:5])}")
            else:
                print("⚠️  No contamination report generated")

        except Exception as e:
            print(f"❌ Error testing {dsl_name}: {e}")

    print(f"\n{'='*80}")
    print("✅ All KAIT agent tests completed")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_kait_with_contamination()
