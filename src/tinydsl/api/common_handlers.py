"""
Common API handlers for DSL endpoints.

This module provides reusable handlers for standard DSL operations:
- run: Execute arbitrary DSL code
- task: Run predefined benchmark tasks
- eval: Batch evaluate task outputs
- ast: Parse code and return AST

Each DSL can use these handlers while customizing DSL-specific behavior.
"""

from typing import Any, Callable, Dict, Optional, Type
from fastapi import HTTPException
from tinydsl.parser.ast_parser import LarkASTParser
from tinydsl.core.logging_config import get_logger
import json


class DSLHandler:
    """
    Generic handler for DSL API endpoints.

    Provides standard implementations for run, task, and eval endpoints
    while allowing DSL-specific customization.
    """

    def __init__(
        self,
        dsl_class: Type,
        evaluator_class: Type,
        tasks_path: str,
        dsl_name: str,
        grammar_path: Optional[str] = None,
    ):
        """
        Initialize DSL handler.

        Args:
            dsl_class: DSL interpreter class (e.g., LexiInterpreter)
            evaluator_class: Evaluator class (e.g., LexiEvaluator)
            tasks_path: Path to tasks JSON file
            dsl_name: Name of DSL for logging/responses
            grammar_path: Path to Lark grammar file (for AST parsing)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.dsl_class = dsl_class
        self.evaluator_class = evaluator_class
        self.tasks_path = tasks_path
        self.dsl_name = dsl_name
        self.grammar_path = grammar_path

        self.logger.debug(f"Initializing DSLHandler for {dsl_name}")

        # Initialize AST parser if grammar path provided
        self.ast_parser = None
        if grammar_path:
            try:
                self.ast_parser = LarkASTParser(grammar_path)
                self.logger.debug(f"AST parser initialized for {dsl_name}")
            except Exception as e:
                self.logger.warning(
                    f"Could not initialize AST parser for {dsl_name}: {e}"
                )

    def handle_run(
        self,
        code: str,
        dsl_kwargs: Optional[Dict[str, Any]] = None,
        process_output: Optional[Callable[[Any, Any], Dict]] = None,
    ) -> Dict:
        """
        Handle /run endpoint - execute arbitrary DSL code.

        Args:
            code: DSL code string to execute
            dsl_kwargs: Optional kwargs to pass to DSL constructor
            process_output: Optional function to process output before returning
                           Signature: (dsl_instance, output) -> response_dict

        Returns:
            Response dictionary with status and output

        Raises:
            HTTPException: If execution fails
        """
        # Skip verbose logging for very short code (likely RL exploration)
        # RL agents often generate random short snippets (< 50 chars)
        is_exploration = len(code.strip()) < 50

        if not is_exploration:
            self.logger.info(
                f"Executing {self.dsl_name} code (length: {len(code)} chars)"
            )

        try:
            # Create DSL instance with optional kwargs
            dsl_kwargs = dsl_kwargs or {}
            dsl = self.dsl_class(**dsl_kwargs)

            # Execute code
            if not is_exploration:
                self.logger.debug(f"Parsing {self.dsl_name} code")
            dsl.parse(code)

            if not is_exploration:
                self.logger.debug(f"Rendering {self.dsl_name} output")
            output = dsl.render()

            # Process output if custom processor provided
            if process_output:
                if not is_exploration:
                    self.logger.debug("Using custom output processor")
                result = process_output(dsl, output)
            else:
                result = {"status": "ok", "output": output}

            if not is_exploration:
                self.logger.success(f"Successfully executed {self.dsl_name} code")
            return result

        except Exception as e:
            # Log at debug level for exploration (RL agent trying invalid syntax)
            # Log at error level for real user requests
            if is_exploration:
                self.logger.debug(f"Exploration attempt failed: {e}")
            else:
                self.logger.error(f"Failed to execute {self.dsl_name} code: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    def handle_task(
        self,
        task_id: str,
        dsl_kwargs: Optional[Dict[str, Any]] = None,
        process_output: Optional[Callable[[Any, Any, Dict], Dict]] = None,
    ) -> Dict:
        """
        Handle /task endpoint - run predefined benchmark task.

        Args:
            task_id: Task identifier
            dsl_kwargs: Optional kwargs to pass to DSL constructor
            process_output: Optional function to process output
                           Signature: (dsl_instance, output, task) -> response_dict

        Returns:
            Response dictionary with task results

        Raises:
            HTTPException: If task not found or execution fails
        """
        try:
            # Load tasks
            with open(self.tasks_path, "r") as f:
                tasks = json.load(f)

            # Find task
            task = next((t for t in tasks if t["id"] == task_id), None)
            if not task:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

            # Create DSL instance
            dsl_kwargs = dsl_kwargs or {}
            dsl = self.dsl_class(**dsl_kwargs)

            # Execute task code
            dsl.parse(task["code"])
            output = dsl.render()

            # Process output if custom processor provided
            if process_output:
                return process_output(dsl, output, task)

            # Default response
            return {
                "status": "ok",
                "task_id": task["id"],
                "task_name": task.get("name", ""),
                "output": output,
                "expected_output": task.get("expected_output", ""),
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def handle_eval(self, results: list[dict]) -> Dict:
        """
        Handle /eval endpoint - evaluate multiple task outputs.

        Args:
            results: List of {"task_id": "...", "output": "..."}

        Returns:
            Evaluation report with accuracy and details

        Raises:
            HTTPException: If evaluation fails
        """
        try:
            # Create evaluator
            evaluator = self.evaluator_class(self.tasks_path)

            # Batch evaluate
            report = evaluator.batch_evaluate(results)

            # Return standardized response
            return {
                "status": "ok",
                "summary": {
                    "accuracy": report.get("accuracy", 0.0),
                    "passed": report.get("passed", 0),
                    "total": report.get("total", 0),
                },
                "details": report.get("details", []),
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def load_tasks(self) -> list[dict]:
        """
        Load tasks from JSON file.

        Returns:
            List of task dictionaries

        Raises:
            HTTPException: If tasks file cannot be loaded
        """
        try:
            with open(self.tasks_path, "r") as f:
                return json.load(f)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to load tasks: {str(e)}"
            )

    def handle_ast(
        self,
        code: str,
        include_pretty: bool = True,
        include_dot: bool = False,
    ) -> Dict:
        """
        Handle /ast endpoint - parse code and return AST.

        Args:
            code: DSL source code
            include_pretty: Include human-readable pretty print
            include_dot: Include Graphviz DOT format

        Returns:
            Dictionary with AST data

        Raises:
            HTTPException: If AST parsing not available or parsing fails
        """
        if not self.ast_parser:
            raise HTTPException(
                status_code=501, detail=f"AST parsing not available for {self.dsl_name}"
            )

        try:
            tree = self.ast_parser.parse_tree(code)
            payload = {
                "status": "ok",
                "tree": self.ast_parser.tree_to_dict(tree),
            }
            if include_pretty:
                payload["pretty"] = self.ast_parser.tree_pretty(tree)
            if include_dot:
                payload["dot"] = self.ast_parser.tree_to_dot(tree)
            return payload
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"AST parse error: {e}")


# Utility functions for common operations


def standard_run_response(output: Any) -> Dict:
    """Create standard response for /run endpoint."""
    return {"status": "ok", "output": output}


def standard_task_response(task: Dict, output: Any) -> Dict:
    """Create standard response for /task endpoint."""
    return {
        "status": "ok",
        "task_id": task["id"],
        "task_name": task.get("name", ""),
        "output": output,
        "expected_output": task.get("expected_output", ""),
    }


def standard_eval_response(report: Dict) -> Dict:
    """Create standard response for /eval endpoint."""
    return {
        "status": "ok",
        "summary": {
            "accuracy": report.get("accuracy", 0.0),
            "passed": report.get("passed", 0),
            "total": report.get("total", 0),
        },
        "details": report.get("details", []),
    }
