"""
Gli-specific evaluator with flexible matching options.

This is a thin wrapper around BaseEvaluator configured for Gli
evaluation. Supports both exact matching and fuzzy matching for
graphics output that may vary in formatting.
"""

from tinydsl.core.evaluator import BaseEvaluator
from typing import List, Dict


class GliEvaluator(BaseEvaluator):
    """
    Evaluates Gli task outputs with configurable matching.

    Uses BaseEvaluator with either exact or fuzzy comparison for graphics
    tasks. Fuzzy matching is useful when SVG output may vary in formatting
    but should be structurally equivalent.
    """

    def __init__(
        self, benchmark_path: str, fuzzy: bool = False, threshold: float = 0.9
    ):
        """
        Initialize Gli evaluator with exact or fuzzy matching.

        Args:
            benchmark_path: Path to Gli tasks JSON file
            fuzzy: If True, use fuzzy matching instead of exact
            threshold: Similarity threshold for fuzzy matching (0.0-1.0)
        """
        if fuzzy:
            # Use fuzzy comparator for flexible graphics matching
            comparator = BaseEvaluator.fuzzy_comparator(
                threshold=threshold, return_metrics=True
            )
            super().__init__(benchmark_path, comparator=comparator)
            self.threshold = threshold
        else:
            # Use default exact matching
            super().__init__(benchmark_path)
            self.threshold = 1.0

        self.fuzzy = fuzzy

    def evaluate_output(self, task_id: str, generated_output: str) -> Dict:
        """
        Evaluate a single task output (backwards compatible API).

        Args:
            task_id: Task identifier
            generated_output: Generated output from Gli

        Returns:
            Dictionary with evaluation results
        """
        result = self.evaluate_single(task_id, generated_output)

        response = {
            "task_id": result["task_id"],
            "name": result["task_name"],
            "difficulty": result["difficulty"],
            "exact_match": result["expected"] == result["actual"],
            "status": result["status"],
            "expected": result["expected"],
            "actual": result["actual"],
        }

        # Add fuzzy metrics if available
        if self.fuzzy:
            response["similarity"] = result.get("similarity", 0.0)
            response["line_overlap"] = result.get("line_overlap", 0.0)

        return response

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
            item = {
                "task_id": detail["task_id"],
                "name": detail["task_name"],
                "difficulty": detail["difficulty"],
                "exact_match": detail["expected"] == detail["actual"],
                "status": detail["status"],
                "expected": detail["expected"],
                "actual": detail["actual"],
            }

            # Add fuzzy metrics if available
            if self.fuzzy:
                item["similarity"] = detail.get("similarity", 0.0)
                item["line_overlap"] = detail.get("line_overlap", 0.0)

            details.append(item)

        return {"accuracy": round(parent_result["accuracy"], 3), "details": details}


# Example usage:
if __name__ == "__main__":
    import json

    # Exact matching (default)
    evaluator = GliEvaluator("gli_tasks.json")

    # Or fuzzy matching for flexible comparison
    # evaluator = GliEvaluator("gli_tasks.json", fuzzy=True, threshold=0.85)

    # Example result from an LLM run
    results = [
        {"task_id": "gli_001", "output": "<circle cx='50' cy='50' r='10'/>"},
        {"task_id": "gli_002", "output": "<rect x='0' y='0' width='100' height='50'/>"},
    ]

    report = evaluator.batch_evaluate(results)
    print(json.dumps(report, indent=2))
