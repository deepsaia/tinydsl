"""Evaluator for TinyMath DSL tasks."""

from pathlib import Path
from tinydsl.core.evaluator import BaseEvaluator


class TinyMathEvaluator(BaseEvaluator):
    """
    Evaluator for TinyMath DSL.

    Compares numerical outputs with tolerance for floating point.
    """

    def __init__(self, tasks_path: str, tolerance: float = 0.0001):
        """
        Initialize TinyMath evaluator.

        Args:
            tasks_path: Path to tasks JSON file
            tolerance: Floating point comparison tolerance
        """
        super().__init__(tasks_path)
        self.tolerance = tolerance

    def compare_output(self, generated: str, expected: str) -> bool:
        """
        Compare TinyMath outputs with numerical tolerance.

        Args:
            generated: Generated output from TinyMath
            expected: Expected output

        Returns:
            True if outputs match within tolerance
        """
        # Clean whitespace
        generated = generated.strip()
        expected = expected.strip()

        # Try exact match first
        if generated == expected:
            return True

        # Try numerical comparison for each line
        gen_lines = generated.split("\n")
        exp_lines = expected.split("\n")

        if len(gen_lines) != len(exp_lines):
            return False

        for gen_line, exp_line in zip(gen_lines, exp_lines):
            gen_line = gen_line.strip()
            exp_line = exp_line.strip()

            # Try exact match
            if gen_line == exp_line:
                continue

            # Try to extract numbers and compare with tolerance
            try:
                # Handle "x = 5.0" format
                if "=" in gen_line and "=" in exp_line:
                    gen_val = float(gen_line.split("=")[-1].strip())
                    exp_val = float(exp_line.split("=")[-1].strip())
                else:
                    gen_val = float(gen_line)
                    exp_val = float(exp_line)

                if abs(gen_val - exp_val) > self.tolerance:
                    return False
            except (ValueError, IndexError):
                # Not a number, use exact match
                if gen_line != exp_line:
                    return False

        return True


if __name__ == "__main__":
    # Test evaluator
    data_dir = Path(__file__).parent.parent / "data"
    tasks_path = data_dir / "tinymath_tasks.json"

    evaluator = TinyMathEvaluator(str(tasks_path))

    # Test cases
    print("Testing TinyMath evaluator...")

    # Exact match
    assert evaluator.compare_output("15.0", "15.0")
    assert evaluator.compare_output("x = 5.0", "x = 5.0")

    # Numerical tolerance
    assert evaluator.compare_output("3.14159", "3.14159")
    assert evaluator.compare_output("2.9999999", "3.0")

    # Multi-line
    assert evaluator.compare_output("x = 5.0\n10.0", "x = 5.0\n10.0")

    # Mismatch
    assert not evaluator.compare_output("5.0", "6.0")
    assert not evaluator.compare_output("x = 5.0", "x = 6.0")

    print("✓ All evaluator tests passed!")
