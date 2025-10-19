"""
Generic DSL client that works with any registered DSL.

Provides a unified interface for interacting with all TinyDSL backends.
"""

import requests
from typing import Optional, List, Dict, Any


class GenericDSLClient:
    """
    Generic client for any TinyDSL backend.

    Automatically works with all registered DSLs without needing DSL-specific methods.
    """

    def __init__(self, base_url: str = "http://localhost:8008/api"):
        self.base_url = base_url.rstrip("/")
        self._available_dsls = None

    def list_dsls(self) -> List[str]:
        """Get list of available DSLs from the server."""
        if self._available_dsls is None:
            url = f"{self.base_url.rstrip('/api')}/dsls"
            resp = requests.get(url)
            resp.raise_for_status()
            self._available_dsls = resp.json().get("dsls", [])
        return self._available_dsls

    def run(self, dsl_name: str, code: str, **kwargs) -> Dict[str, Any]:
        """
        Run code for any DSL.

        Args:
            dsl_name: Name of the DSL (e.g., 'gli', 'lexi', 'tinycalc', 'tinysql')
            code: DSL code to execute
            **kwargs: Additional parameters (e.g., save=True for gli)

        Returns:
            Response dict with output
        """
        url = f"{self.base_url}/{dsl_name}/run"
        payload = {"code": code, **kwargs}
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def run_task(self, dsl_name: str, task_id: str) -> Dict[str, Any]:
        """
        Run a benchmark task for any DSL.

        Args:
            dsl_name: Name of the DSL
            task_id: Task identifier

        Returns:
            Response dict with task results
        """
        url = f"{self.base_url}/{dsl_name}/task"
        resp = requests.post(url, json={"task_id": task_id}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def evaluate(self, dsl_name: str, results: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Evaluate multiple outputs for any DSL.

        Args:
            dsl_name: Name of the DSL
            results: List of {"task_id": "...", "output": "..."}

        Returns:
            Evaluation report with accuracy metrics
        """
        url = f"{self.base_url}/{dsl_name}/eval"
        resp = requests.post(url, json={"results": results}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_examples(self, dsl_name: str, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get examples for a DSL.

        Args:
            dsl_name: Name of the DSL
            tag: Optional tag filter

        Returns:
            List of example dicts
        """
        url = f"{self.base_url}/{dsl_name}/examples"
        params = {"tag": tag} if tag else {}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get("examples", [])

    def run_all_tasks(
        self,
        dsl_name: str,
        task_ids: Optional[List[str]] = None,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run multiple tasks and return combined results.

        Args:
            dsl_name: Name of the DSL
            task_ids: Specific task IDs to run (if None, runs all)
            difficulty: Filter by difficulty (easy/medium/hard)

        Returns:
            Dict with results and summary
        """
        results = []

        # If task_ids not specified, we'd need to fetch them from the server
        # For now, assume task_ids are provided
        if task_ids is None:
            raise ValueError("task_ids must be provided or implement task discovery")

        for task_id in task_ids:
            try:
                result = self.run_task(dsl_name, task_id)
                results.append({
                    "task_id": task_id,
                    "output": result.get("generated_output", "")
                })
            except Exception as e:
                results.append({
                    "task_id": task_id,
                    "output": f"[ERROR: {str(e)}]"
                })

        # Evaluate all results
        eval_result = self.evaluate(dsl_name, results)

        return {
            "dsl": dsl_name,
            "total_tasks": len(results),
            "results": results,
            "evaluation": eval_result
        }


class DSLTester:
    """Helper class for testing DSLs with specific scenarios."""

    def __init__(self, client: GenericDSLClient):
        self.client = client

    def test_dsl_basic(self, dsl_name: str, test_code: str) -> bool:
        """
        Test if a DSL can execute basic code.

        Args:
            dsl_name: DSL to test
            test_code: Simple test code

        Returns:
            True if execution succeeded
        """
        try:
            result = self.client.run(dsl_name, test_code)
            return result.get("status") == "ok"
        except Exception:
            return False

    def benchmark_dsl(
        self,
        dsl_name: str,
        task_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Run benchmark suite for a DSL.

        Args:
            dsl_name: DSL to benchmark
            task_ids: Task IDs to run

        Returns:
            Benchmark report with timing and accuracy
        """
        import time

        start_time = time.time()
        results = self.client.run_all_tasks(dsl_name, task_ids)
        elapsed = time.time() - start_time

        return {
            "dsl": dsl_name,
            "tasks_run": results["total_tasks"],
            "accuracy": results["evaluation"].get("summary", {}).get("accuracy", 0.0),
            "elapsed_seconds": elapsed,
            "tasks_per_second": results["total_tasks"] / elapsed if elapsed > 0 else 0
        }


if __name__ == "__main__":
    # Example usage
    client = GenericDSLClient()

    print("🌐 Available DSLs:", client.list_dsls())

    # Test TinyCalc
    print("\n🧮 Testing TinyCalc...")
    result = client.run("tinycalc", "define 1 flurb = 5 zepts\nconvert 10 flurbs to zepts")
    print("Output:", result.get("output"))

    # Test Lexi
    print("\n💬 Testing Lexi...")
    result = client.run("lexi", "say \"Hello from generic client!\"")
    print("Output:", result.get("output"))

    # Run a task
    print("\n🎯 Running TinyCalc task...")
    result = client.run_task("tinycalc", "001")
    print("Task result:", result)
