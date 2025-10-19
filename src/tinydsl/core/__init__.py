"""
TinyDSL Core Framework

Common abstractions, registry, and utilities for building DSLs.
"""

from tinydsl.core.base_dsl import BaseDSL
from tinydsl.core.dsl_registry import DSLRegistry
from tinydsl.core.evaluator import BaseEvaluator
from tinydsl.core.memory import BaseMemory

__all__ = ["BaseDSL", "DSLRegistry", "BaseEvaluator", "BaseMemory"]
