"""Tests for all DSL evaluators."""
import pytest
import json
import tempfile
from pathlib import Path

from tinydsl.core.evaluator import BaseEvaluator
from tinydsl.lexi.lexi_evaluator import LexiEvaluator
from tinydsl.tinycalc.tinycalc_evaluator import TinyCalcEvaluator
from tinydsl.tinysql.tinysql_evaluator import TinySQLEvaluator
from tinydsl.gli.gli_evaluator import GliEvaluator


@pytest.fixture
def sample_tasks_file():
    """Create a temporary tasks file for testing."""
    tasks = [
        {
            "id": "test_001",
            "name": "Test Task 1",
            "code": "test code",
            "expected_output": "test output",
            "difficulty": "easy",
            "tags": ["basic"]
        },
        {
            "id": "test_002",
            "name": "Test Task 2",
            "code": "test code 2",
            "expected_output": "test output 2",
            "difficulty": "medium",
            "tags": ["intermediate"]
        }
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(tasks, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink()


class TestBaseEvaluator:
    """Test BaseEvaluator functionality."""

    def test_base_evaluator_exact_match(self, sample_tasks_file):
        """Test BaseEvaluator with exact matching."""
        evaluator = BaseEvaluator(sample_tasks_file)
        result = evaluator.evaluate_single("test_001", "test output")
        assert result["passed"] is True
        assert result["status"] == "pass"

    def test_base_evaluator_mismatch(self, sample_tasks_file):
        """Test BaseEvaluator with non-matching output."""
        evaluator = BaseEvaluator(sample_tasks_file)
        result = evaluator.evaluate_single("test_001", "wrong output")
        assert result["passed"] is False
        assert result["status"] == "fail"

    def test_base_evaluator_fuzzy_match(self, sample_tasks_file):
        """Test BaseEvaluator with fuzzy matching."""
        evaluator = BaseEvaluator(
            sample_tasks_file,
            comparator=BaseEvaluator.fuzzy_comparator(threshold=0.8, return_metrics=True)
        )
        result = evaluator.evaluate_single("test_001", "test output!")
        assert result["passed"] is True
        assert "similarity" in result

    def test_base_evaluator_batch(self, sample_tasks_file):
        """Test batch evaluation."""
        evaluator = BaseEvaluator(sample_tasks_file)
        results = [
            {"task_id": "test_001", "output": "test output"},
            {"task_id": "test_002", "output": "test output 2"}
        ]
        report = evaluator.batch_evaluate(results)
        assert report["accuracy"] == 1.0
        assert report["total"] == 2
        assert report["passed"] == 2

    def test_get_task(self, sample_tasks_file):
        """Test getting a task by ID."""
        evaluator = BaseEvaluator(sample_tasks_file)
        task = evaluator.get_task("test_001")
        assert task is not None
        assert task["name"] == "Test Task 1"

    def test_get_tasks_by_difficulty(self, sample_tasks_file):
        """Test filtering tasks by difficulty."""
        evaluator = BaseEvaluator(sample_tasks_file)
        easy_tasks = evaluator.get_tasks_by_difficulty("easy")
        assert len(easy_tasks) == 1
        assert easy_tasks[0]["id"] == "test_001"

    def test_get_tasks_by_tag(self, sample_tasks_file):
        """Test filtering tasks by tag."""
        evaluator = BaseEvaluator(sample_tasks_file)
        basic_tasks = evaluator.get_tasks_by_tag("basic")
        assert len(basic_tasks) == 1
        assert basic_tasks[0]["id"] == "test_001"


class TestLexiEvaluator:
    """Test LexiEvaluator functionality."""

    def test_lexi_evaluator_initialization(self, sample_tasks_file):
        """Test LexiEvaluator initializes correctly."""
        evaluator = LexiEvaluator(sample_tasks_file)
        assert evaluator.threshold == 0.8

    def test_lexi_evaluator_custom_threshold(self, sample_tasks_file):
        """Test LexiEvaluator with custom threshold."""
        evaluator = LexiEvaluator(sample_tasks_file, threshold=0.9)
        assert evaluator.threshold == 0.9

    def test_lexi_evaluator_output(self, sample_tasks_file):
        """Test evaluate_output method."""
        evaluator = LexiEvaluator(sample_tasks_file)
        result = evaluator.evaluate_output("test_001", "test output")
        assert result["status"] == "pass"
        assert "similarity" in result
        assert "line_overlap" in result

    def test_lexi_batch_evaluate(self, sample_tasks_file):
        """Test batch evaluation."""
        evaluator = LexiEvaluator(sample_tasks_file)
        results = [
            {"task_id": "test_001", "output": "test output"},
            {"task_id": "test_002", "output": "test output 2"}
        ]
        report = evaluator.batch_evaluate(results)
        assert report["accuracy"] == 1.0
        assert len(report["details"]) == 2


class TestTinyCalcEvaluator:
    """Test TinyCalcEvaluator functionality."""

    def test_tinycalc_evaluator_initialization(self, sample_tasks_file):
        """Test TinyCalcEvaluator initializes correctly."""
        evaluator = TinyCalcEvaluator(sample_tasks_file)
        assert evaluator is not None

    def test_tinycalc_evaluator_output(self, sample_tasks_file):
        """Test evaluate_output method."""
        evaluator = TinyCalcEvaluator(sample_tasks_file)
        result = evaluator.evaluate_output("test_001", "test output")
        assert result["status"] == "pass"
        assert result["exact_match"] is True

    def test_tinycalc_batch_evaluate(self, sample_tasks_file):
        """Test batch evaluation."""
        evaluator = TinyCalcEvaluator(sample_tasks_file)
        results = [
            {"task_id": "test_001", "output": "test output"},
            {"task_id": "test_002", "output": "test output 2"}
        ]
        report = evaluator.batch_evaluate(results)
        assert report["accuracy"] == 1.0
        assert len(report["details"]) == 2


class TestTinySQLEvaluator:
    """Test TinySQLEvaluator functionality."""

    def test_tinysql_evaluator_initialization(self, sample_tasks_file):
        """Test TinySQLEvaluator initializes correctly."""
        evaluator = TinySQLEvaluator(sample_tasks_file)
        assert evaluator is not None

    def test_tinysql_evaluator_output(self, sample_tasks_file):
        """Test evaluate_output method."""
        evaluator = TinySQLEvaluator(sample_tasks_file)
        result = evaluator.evaluate_output("test_001", "test output")
        assert result["status"] == "pass"
        assert result["exact_match"] is True

    def test_tinysql_batch_evaluate(self, sample_tasks_file):
        """Test batch evaluation."""
        evaluator = TinySQLEvaluator(sample_tasks_file)
        results = [
            {"task_id": "test_001", "output": "test output"},
            {"task_id": "test_002", "output": "test output 2"}
        ]
        report = evaluator.batch_evaluate(results)
        assert report["accuracy"] == 1.0
        assert len(report["details"]) == 2


class TestGliEvaluator:
    """Test GliEvaluator functionality."""

    def test_gli_evaluator_initialization(self, sample_tasks_file):
        """Test GliEvaluator initializes correctly."""
        evaluator = GliEvaluator(sample_tasks_file)
        assert evaluator is not None
        assert evaluator.fuzzy is False

    def test_gli_evaluator_fuzzy_mode(self, sample_tasks_file):
        """Test GliEvaluator with fuzzy matching."""
        evaluator = GliEvaluator(sample_tasks_file, fuzzy=True, threshold=0.9)
        assert evaluator.fuzzy is True
        assert evaluator.threshold == 0.9

    def test_gli_evaluator_output_exact(self, sample_tasks_file):
        """Test evaluate_output with exact matching."""
        evaluator = GliEvaluator(sample_tasks_file)
        result = evaluator.evaluate_output("test_001", "test output")
        assert result["status"] == "pass"
        assert result["exact_match"] is True

    def test_gli_evaluator_output_fuzzy(self, sample_tasks_file):
        """Test evaluate_output with fuzzy matching."""
        evaluator = GliEvaluator(sample_tasks_file, fuzzy=True)
        result = evaluator.evaluate_output("test_001", "test output!")
        assert result["status"] == "pass"
        assert "similarity" in result
        assert "line_overlap" in result

    def test_gli_batch_evaluate(self, sample_tasks_file):
        """Test batch evaluation."""
        evaluator = GliEvaluator(sample_tasks_file)
        results = [
            {"task_id": "test_001", "output": "test output"},
            {"task_id": "test_002", "output": "test output 2"}
        ]
        report = evaluator.batch_evaluate(results)
        assert report["accuracy"] == 1.0
        assert len(report["details"]) == 2


class TestFuzzyComparator:
    """Test fuzzy comparator functionality."""

    def test_fuzzy_exact_match(self):
        """Test fuzzy comparator with exact match."""
        comparator = BaseEvaluator.fuzzy_comparator(threshold=0.8, return_metrics=True)
        passed, metrics = comparator("hello world", "hello world")
        assert passed is True
        assert metrics["similarity"] == 1.0

    def test_fuzzy_close_match(self):
        """Test fuzzy comparator with close match."""
        comparator = BaseEvaluator.fuzzy_comparator(threshold=0.8, return_metrics=True)
        passed, metrics = comparator("hello world!", "hello world")
        assert passed is True
        assert metrics["similarity"] > 0.8

    def test_fuzzy_no_match(self):
        """Test fuzzy comparator with no match."""
        comparator = BaseEvaluator.fuzzy_comparator(threshold=0.8, return_metrics=True)
        passed, metrics = comparator("completely different", "hello world")
        assert passed is False
        assert metrics["similarity"] < 0.8

    def test_fuzzy_multiline_match(self):
        """Test fuzzy comparator with multiline text."""
        comparator = BaseEvaluator.fuzzy_comparator(threshold=0.8, return_metrics=True)
        text1 = "line 1\nline 2\nline 3"
        text2 = "line 1\nline 2\nline 3"
        passed, metrics = comparator(text1, text2)
        assert passed is True
        assert metrics["line_overlap"] == 1.0
