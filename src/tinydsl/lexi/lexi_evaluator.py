"""
Lexi-specific evaluator with fuzzy matching.

This is a thin wrapper around BaseEvaluator configured for text-based
evaluation with similarity scoring. Maintains backwards compatibility
with existing code while using the unified evaluation framework.
"""

from tinydsl.core.evaluator import BaseEvaluator
from typing import List, Dict


class LexiEvaluator(BaseEvaluator):
    """
    Evaluates Lexi task outputs with fuzzy matching.

    Uses BaseEvaluator with fuzzy comparison for better handling
    of text generation tasks where exact matches are too strict.
    """

    def __init__(self, benchmark_path: str, threshold: float = 0.8):
        """
        Initialize Lexi evaluator with fuzzy matching.

        Args:
            benchmark_path: Path to Lexi tasks JSON file
            threshold: Similarity threshold for passing (0.0-1.0)
        """
        # Initialize with fuzzy comparator that returns metrics
        comparator = BaseEvaluator.fuzzy_comparator(
            threshold=threshold, return_metrics=True
        )
        super().__init__(benchmark_path, comparator=comparator)
        self.threshold = threshold

    def evaluate_output(self, task_id: str, generated_output: str) -> Dict:
        """
        Evaluate a single task output (backwards compatible API).

        Args:
            task_id: Task identifier
            generated_output: Generated output from Lexi

        Returns:
            Dictionary with evaluation results including similarity metrics
        """
        result = self.evaluate_single(task_id, generated_output)

        # Transform to match legacy LexiEvaluator API
        return {
            "task_id": result["task_id"],
            "name": result["task_name"],
            "difficulty": result["difficulty"],
            "similarity": result.get("similarity", 0.0),
            "line_overlap": result.get("line_overlap", 0.0),
            "exact_match": result["expected"] == result["actual"],
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

        # Transform detailed results to match legacy API
        details = []
        for detail in parent_result["details"]:
            details.append(
                {
                    "task_id": detail["task_id"],
                    "name": detail["task_name"],
                    "difficulty": detail["difficulty"],
                    "similarity": detail.get("similarity", 0.0),
                    "line_overlap": detail.get("line_overlap", 0.0),
                    "exact_match": detail["expected"] == detail["actual"],
                    "status": detail["status"],
                    "expected": detail["expected"],
                    "actual": detail["actual"],
                }
            )

        return {"accuracy": round(parent_result["accuracy"], 3), "details": details}


# Example usage:
if __name__ == "__main__":
    import json

    evaluator = LexiEvaluator("lexi_tasks.json")

    # Example result from an LLM run
    results = [
        {"task_id": "lexi_task_002", "output": "You look great today!"},
        {"task_id": "lexi_task_003", "output": "Echo\nEcho\nEcho"},
    ]

    report = evaluator.batch_evaluate(results)
    print(json.dumps(report, indent=2))
