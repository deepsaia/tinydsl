import json
import difflib
from typing import List, Dict

class LexiEvaluator:
    """Evaluates Lexi task outputs against expected results."""

    def __init__(self, benchmark_path: str):
        with open(benchmark_path, "r") as f:
            self.tasks = json.load(f)

    def evaluate_output(self, task_id: str, generated_output: str) -> Dict:
        """Compare model output to expected output with similarity scoring."""
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            raise ValueError(f"Task {task_id} not found in benchmark.")

        expected = task["expected_output"].strip()
        actual = generated_output.strip()

        # Normalize and compute similarity
        expected_lines = expected.splitlines()
        actual_lines = actual.splitlines()
        matcher = difflib.SequenceMatcher(None, expected, actual)
        similarity = matcher.ratio()

        # Scoring metrics
        exact_match = expected == actual
        line_overlap = len(set(expected_lines) & set(actual_lines)) / max(1, len(expected_lines))
        pass_fail = "pass" if similarity > 0.8 or line_overlap > 0.8 else "fail"

        return {
            "task_id": task_id,
            "name": task["name"],
            "difficulty": task["difficulty"],
            "similarity": round(similarity, 3),
            "line_overlap": round(line_overlap, 3),
            "status": pass_fail,
            "expected": expected,
            "actual": actual,
        }

    def batch_evaluate(self, results: List[Dict[str, str]]) -> Dict:
        """Evaluate a batch of task outputs."""
        report = [self.evaluate_output(r["task_id"], r["output"]) for r in results]
        accuracy = sum(r["status"] == "pass" for r in report) / len(report)
        return {"accuracy": round(accuracy, 3), "details": report}

# Example usage:
if __name__ == "__main__":
    evaluator = LexiEvaluator("lexi_tasks.json")

    # Example result from an LLM run
    results = [
        {"task_id": "lexi_task_002", "output": "You look great today!"},
        {"task_id": "lexi_task_003", "output": "Echo\nEcho\nEcho"},
    ]

    report = evaluator.batch_evaluate(results)
    print(json.dumps(report, indent=2))