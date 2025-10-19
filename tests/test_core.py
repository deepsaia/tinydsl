"""Tests for core framework components."""
import pytest
from tinydsl.core.base_dsl import BaseDSL
from tinydsl.core.dsl_registry import DSLRegistry
from tinydsl.core.memory import InMemoryStore, JSONFileMemory
from tinydsl.core.evaluator import BaseEvaluator


class TestBaseDSL:
    """Test BaseDSL abstract class."""

    def test_base_dsl_is_abstract(self):
        """Test that BaseDSL cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseDSL()


class TestDSLRegistry:
    """Test DSL registry."""

    def test_registry_initialization(self):
        """Test registry initializes with empty registry."""
        registry = DSLRegistry()
        assert len(registry.list_dsls()) == 0

    def test_register_dsl(self):
        """Test registering a DSL."""
        from tinydsl.tinycalc.tinycalc import TinyCalcInterpreter

        registry = DSLRegistry()
        registry.register("tinycalc", TinyCalcInterpreter)
        assert "tinycalc" in registry.list_dsls()

    def test_get_dsl(self):
        """Test retrieving a registered DSL."""
        from tinydsl.tinycalc.tinycalc import TinyCalcInterpreter

        registry = DSLRegistry()
        registry.register("tinycalc", TinyCalcInterpreter)
        dsl_class = registry.get("tinycalc")
        assert dsl_class == TinyCalcInterpreter

    def test_get_nonexistent_dsl(self):
        """Test getting a DSL that doesn't exist."""
        registry = DSLRegistry()
        dsl = registry.get("nonexistent")
        assert dsl is None


class TestMemory:
    """Test memory implementations."""

    def test_in_memory_store(self):
        """Test InMemoryStore."""
        store = InMemoryStore()

        # Test set and get
        store.set("key1", "value1")
        assert store.get("key1") == "value1"

        # Test default value
        assert store.get("nonexistent", "default") == "default"

        # Test delete
        store.delete("key1")
        assert store.get("key1") is None

    def test_json_file_memory(self, tmp_path):
        """Test JSONFileMemory."""
        file_path = tmp_path / "test_memory.json"
        store = JSONFileMemory(str(file_path))

        # Test set and get
        store.set("key1", "value1")
        assert store.get("key1") == "value1"

        # Test persistence
        store2 = JSONFileMemory(str(file_path))
        assert store2.get("key1") == "value1"

        # Test clear
        store2.clear()
        assert store2.get("key1") is None


class TestEvaluator:
    """Test DSL evaluator."""

    def test_evaluator_initialization(self, tmp_path):
        """Test evaluator initializes correctly."""
        import json

        # Create a temporary tasks file
        tasks_file = tmp_path / "test_tasks.json"
        tasks = [
            {
                "id": "test_001",
                "name": "Test Task",
                "code": "test code",
                "expected_output": "test output",
                "difficulty": "easy"
            }
        ]
        with open(tasks_file, "w") as f:
            json.dump(tasks, f)

        evaluator = BaseEvaluator(str(tasks_file))
        assert len(evaluator.tasks) == 1

    def test_evaluate_single_task(self, tmp_path):
        """Test evaluating a single task."""
        import json

        # Create a temporary tasks file
        tasks_file = tmp_path / "test_tasks.json"
        tasks = [
            {
                "id": "test_001",
                "name": "Convert Task",
                "code": "define 1 flurb = 2 grobble\nconvert 1 flurb to grobble",
                "expected_output": "2.0 grobble",
                "difficulty": "easy"
            }
        ]
        with open(tasks_file, "w") as f:
            json.dump(tasks, f)

        evaluator = BaseEvaluator(str(tasks_file))
        result = evaluator.evaluate_single("test_001", "2.0 grobble")

        assert result["task_id"] == "test_001"
        assert result["passed"] is True
        assert result["status"] == "pass"
