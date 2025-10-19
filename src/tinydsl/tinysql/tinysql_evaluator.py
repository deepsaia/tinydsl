"""
TinySQL-specific evaluator with exact matching.

This is a thin wrapper around BaseEvaluator configured for TinySQL
evaluation with exact string comparison.
"""

from tinydsl.core.evaluator import BaseEvaluator
from typing import List, Dict


class TinySQLEvaluator(BaseEvaluator):
    """
    Evaluates TinySQL task outputs with exact matching.

    Uses BaseEvaluator with default exact comparison for SQL query
    tasks where output format is predictable and standardized.
    """

    def __init__(self, benchmark_path: str):
        """
        Initialize TinySQL evaluator with exact matching.

        Args:
            benchmark_path: Path to TinySQL tasks JSON file
        """
        # Initialize with default exact matching comparator
        super().__init__(benchmark_path)

    def evaluate_output(self, task_id: str, generated_output: str) -> Dict:
        """
        Evaluate a single task output (backwards compatible API).

        Args:
            task_id: Task identifier
            generated_output: Generated output from TinySQL

        Returns:
            Dictionary with evaluation results
        """
        result = self.evaluate_single(task_id, generated_output)

        return {
            "task_id": result["task_id"],
            "name": result["task_name"],
            "difficulty": result["difficulty"],
            "exact_match": result["passed"],
            "status": result["status"],
            "expected": result["expected"],
            "actual": result["actual"],
        }

    def batch_evaluate(self, results: List[Dict[str, str]]) -> Dict:
        """
        Evaluate a batch of task outputs (backwards compatible API).

        Args:
            results: List of {"task_id": "...", "output": "..."}

        Returns:
            Dictionary with accuracy and detailed results
        """
        # Use parent's batch_evaluate
        parent_result = super().batch_evaluate(results)

        # Transform detailed results to match API
        details = []
        for detail in parent_result["details"]:
            details.append({
                "task_id": detail["task_id"],
                "name": detail["task_name"],
                "difficulty": detail["difficulty"],
                "exact_match": detail["passed"],
                "status": detail["status"],
                "expected": detail["expected"],
                "actual": detail["actual"],
            })

        return {
            "accuracy": round(parent_result["accuracy"], 3),
            "details": details
        }


# Example usage:
if __name__ == "__main__":
    import json

    evaluator = TinySQLEvaluator("tinysql_tasks.json")

    # Example result from an LLM run
    results = [
        {"task_id": "tinysql_001", "output": "SELECT * FROM users"},
        {"task_id": "tinysql_002", "output": "INSERT INTO users VALUES (1, 'Alice')"},
    ]

    report = evaluator.batch_evaluate(results)
    print(json.dumps(report, indent=2))
