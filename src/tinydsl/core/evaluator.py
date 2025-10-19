"""
Generic evaluator for DSL task benchmarks.

Provides a reusable framework for:
- Loading task definitions from JSON
- Running tasks through a DSL interpreter
- Comparing outputs against expected results
- Generating accuracy reports
- Fuzzy matching for text-based DSLs
"""

from typing import List, Dict, Any, Callable, Optional, Tuple
import json
from pathlib import Path
import difflib


class BaseEvaluator:
    """
    Generic task evaluator for DSL benchmarks.

    Loads tasks from JSON and evaluates interpreter outputs
    against expected results.
    """

    def __init__(
        self,
        tasks_path: str,
        comparator: Optional[Callable[[str, str], bool]] = None
    ):
        """
        Initialize evaluator.

        Args:
            tasks_path: Path to JSON file with task definitions
            comparator: Custom comparison function(actual, expected) -> bool
                       Defaults to exact string match
        """
        self.tasks_path = Path(tasks_path)
        self.tasks: List[Dict[str, Any]] = []
        self._load_tasks()
        self.comparator = comparator or self._default_comparator

    def _load_tasks(self) -> None:
        """Load tasks from JSON file."""
        if self.tasks_path.exists():
            with open(self.tasks_path, "r") as f:
                self.tasks = json.load(f)

    def _default_comparator(self, actual: str, expected: str) -> bool:
        """Default exact string comparison."""
        return str(actual).strip() == str(expected).strip()

    @staticmethod
    def fuzzy_comparator(
        threshold: float = 0.8,
        return_metrics: bool = False
    ) -> Callable:
        """
        Create a fuzzy string comparator using sequence matching.

        Args:
            threshold: Similarity threshold (0.0-1.0) for passing
            return_metrics: If True, returns (bool, dict) with similarity metrics

        Returns:
            Comparator function

        Example:
            evaluator = BaseEvaluator(
                "tasks.json",
                comparator=BaseEvaluator.fuzzy_comparator(threshold=0.85)
            )
        """
        def comparator(actual: str, expected: str) -> bool:
            actual_clean = str(actual).strip()
            expected_clean = str(expected).strip()

            # Sequence similarity
            matcher = difflib.SequenceMatcher(None, expected_clean, actual_clean)
            similarity = matcher.ratio()

            # Line overlap for multi-line text
            expected_lines = expected_clean.splitlines()
            actual_lines = actual_clean.splitlines()
            line_overlap = 0.0
            if expected_lines:
                matching_lines = set(expected_lines) & set(actual_lines)
                line_overlap = len(matching_lines) / len(expected_lines)

            # Pass if either metric exceeds threshold
            passed = similarity >= threshold or line_overlap >= threshold

            if return_metrics:
                return passed, {
                    "similarity": round(similarity, 3),
                    "line_overlap": round(line_overlap, 3),
                    "threshold": threshold
                }
            return passed

        return comparator

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID."""
        return next((t for t in self.tasks if t["id"] == task_id), None)

    def get_tasks_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """Filter tasks by difficulty level."""
        return [t for t in self.tasks if t.get("difficulty") == difficulty]

    def get_tasks_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Filter tasks by tag."""
        return [t for t in self.tasks if tag in t.get("tags", [])]

    def evaluate_single(self, task_id: str, actual_output: str) -> Dict[str, Any]:
        """
        Evaluate a single task result.

        Args:
            task_id: Task identifier
            actual_output: Generated output from DSL

        Returns:
            Dictionary with evaluation results
        """
        task = self.get_task(task_id)
        if not task:
            return {
                "task_id": task_id,
                "status": "error",
                "message": "Task not found",
                "passed": False
            }

        expected = task.get("expected_output", "")

        # Comparator might return bool or (bool, dict) tuple
        comparison_result = self.comparator(actual_output, expected)
        if isinstance(comparison_result, tuple):
            passed, metrics = comparison_result
        else:
            passed = comparison_result
            metrics = {}

        result = {
            "task_id": task_id,
            "task_name": task.get("name", ""),
            "difficulty": task.get("difficulty", "unknown"),
            "status": "pass" if passed else "fail",
            "passed": passed,
            "expected": expected,
            "actual": actual_output,
            "match": passed
        }

        # Add any additional metrics from the comparator
        if metrics:
            result.update(metrics)

        return result

    def batch_evaluate(self, results: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Evaluate multiple task results.

        Args:
            results: List of {"task_id": "...", "output": "..."}

        Returns:
            Report with accuracy and per-task details
        """
        details = []
        for result in results:
            task_id = result.get("task_id")
            output = result.get("output", "")
            evaluation = self.evaluate_single(task_id, output)
            details.append(evaluation)

        total = len(details)
        passed = sum(1 for d in details if d["passed"])
        accuracy = passed / total if total > 0 else 0.0

        # Breakdown by difficulty
        by_difficulty = {}
        for detail in details:
            diff = detail.get("difficulty", "unknown")
            if diff not in by_difficulty:
                by_difficulty[diff] = {"total": 0, "passed": 0}
            by_difficulty[diff]["total"] += 1
            if detail["passed"]:
                by_difficulty[diff]["passed"] += 1

        for diff in by_difficulty:
            stats = by_difficulty[diff]
            stats["accuracy"] = stats["passed"] / stats["total"]

        return {
            "accuracy": accuracy,
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "by_difficulty": by_difficulty,
            "details": details
        }

    def run_all_tasks(
        self,
        executor: Callable[[str], str],
        difficulty: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run all tasks through an executor function.

        Args:
            executor: Function that takes DSL code and returns output
            difficulty: Filter by difficulty (optional)
            limit: Maximum number of tasks to run (optional)

        Returns:
            Full evaluation report
        """
        tasks = self.tasks
        if difficulty:
            tasks = self.get_tasks_by_difficulty(difficulty)
        if limit:
            tasks = tasks[:limit]

        results = []
        for task in tasks:
            try:
                output = executor(task["code"])
                results.append({
                    "task_id": task["id"],
                    "output": output
                })
            except Exception as e:
                results.append({
                    "task_id": task["id"],
                    "output": f"[ERROR: {str(e)}]"
                })

        return self.batch_evaluate(results)

    def __repr__(self) -> str:
        return f"<BaseEvaluator: {len(self.tasks)} tasks from {self.tasks_path.name}>"
