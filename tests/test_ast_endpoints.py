#!/usr/bin/env python3
"""
Quick test script to verify AST endpoints work for all DSLs.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from tinydsl.api.common_handlers import DSLHandler
from tinydsl.tinycalc.tinycalc import TinyCalcInterpreter
from tinydsl.tinycalc.tinycalc_evaluator import TinyCalcEvaluator
from tinydsl.tinysql.tinysql import TinySQLInterpreter
from tinydsl.tinysql.tinysql_evaluator import TinySQLEvaluator
from tinydsl.lexi.lexi import LexiInterpreter
from tinydsl.lexi.lexi_evaluator import LexiEvaluator
from tinydsl.gli.gli import GlintInterpreter
from tinydsl.gli.gli_evaluator import GliEvaluator

data_dir = os.path.join(os.path.dirname(__file__), "src", "tinydsl", "data")

def test_dsl_ast(dsl_name, dsl_class, evaluator_class, tasks_path, grammar_path, test_code):
    """Test AST parsing for a DSL."""
    print(f"\n{'='*60}")
    print(f"Testing {dsl_name} AST endpoint")
    print(f"{'='*60}")

    try:
        # Initialize handler with grammar path
        handler = DSLHandler(
            dsl_class=dsl_class,
            evaluator_class=evaluator_class,
            tasks_path=tasks_path,
            dsl_name=dsl_name,
            grammar_path=grammar_path,
        )

        # Test AST parsing
        result = handler.handle_ast(
            code=test_code,
            include_pretty=True,
            include_dot=False,
        )

        print(f"✓ {dsl_name} handler initialized successfully")
        print(f"✓ AST parsing works for {dsl_name}")
        print(f"✓ Result keys: {list(result.keys())}")
        print(f"✓ AST tree type: {result['tree'].get('type', 'N/A')}")
        if 'pretty' in result:
            print(f"✓ Pretty print available (length: {len(result['pretty'])} chars)")

        return True

    except Exception as e:
        print(f"✗ Error testing {dsl_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("Testing AST endpoints for all DSLs...")

    results = []

    # Test TinyCalc
    results.append(test_dsl_ast(
        dsl_name="tinycalc",
        dsl_class=TinyCalcInterpreter,
        evaluator_class=TinyCalcEvaluator,
        tasks_path=os.path.join(data_dir, "tinycalc_tasks.json"),
        grammar_path=os.path.join(data_dir, "tinycalc_grammar.lark"),
        test_code="define 1 flurb = 3.5 grobbles\nconvert 4 flurbs to grobbles",
    ))

    # Test TinySQL
    results.append(test_dsl_ast(
        dsl_name="tinysql",
        dsl_class=TinySQLInterpreter,
        evaluator_class=TinySQLEvaluator,
        tasks_path=os.path.join(data_dir, "tinysql_tasks.json"),
        grammar_path=os.path.join(data_dir, "tinysql_grammar.lark"),
        test_code='load table test from "test.json"\nshow tables',
    ))

    # Test Lexi
    results.append(test_dsl_ast(
        dsl_name="lexi",
        dsl_class=LexiInterpreter,
        evaluator_class=LexiEvaluator,
        tasks_path=os.path.join(data_dir, "lexi_tasks.json"),
        grammar_path=os.path.join(data_dir, "lexi_grammar.lark"),
        test_code='say "Hello world!"',
    ))

    # Test Gli
    results.append(test_dsl_ast(
        dsl_name="gli",
        dsl_class=GlintInterpreter,
        evaluator_class=GliEvaluator,
        tasks_path=os.path.join(data_dir, "gli_tasks.json"),
        grammar_path=os.path.join(data_dir, "gli_grammar.lark"),
        test_code="set color red\nset size 10\ndraw circle x=50 y=50",
    ))

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary: {sum(results)}/{len(results)} DSLs passed")
    print(f"{'='*60}")

    if all(results):
        print("✓ All AST endpoints working correctly!")
        return 0
    else:
        print("✗ Some AST endpoints failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
