"""Correctness-based reward function."""

from typing import Any, List, Dict
from tinydsl.rl.rewards.base_reward import BaseReward


class CorrectnessReward(BaseReward):
    """
    Reward function based on output correctness.

    Rewards:
    - +10.0 for correct output
    - -0.1 per step (encourage efficiency)
    - -1.0 for syntax errors
    """

    def __init__(self, dsl_name: str, step_penalty: float = -0.1):
        """
        Initialize correctness reward.

        Args:
            dsl_name: DSL name (for future customization)
            step_penalty: Penalty per step
        """
        self.dsl_name = dsl_name
        self.step_penalty = step_penalty

    def __call__(
        self, state: List[str], action: str, result: Dict[str, Any], expected: str
    ) -> float:
        """Calculate reward based on correctness."""
        reward = self.step_penalty  # Base step penalty

        if result.get("error"):
            # Syntax error
            reward += -1.0
        elif result.get("success"):
            # Correct output!
            reward += 10.0
        else:
            # Partial credit for getting closer
            output = result.get("output", "")
            if output:
                # Reward partial matches
                similarity = self._calculate_similarity(output, expected)
                reward += similarity * 2.0

        return reward

    def _calculate_similarity(self, output: str, expected: str) -> float:
        """Calculate string similarity (0.0 to 1.0)."""
        if not expected:
            return 0.0

        # Simple character-level similarity
        output = output.strip()
        expected = expected.strip()

        if output == expected:
            return 1.0

        # Levenshtein-like similarity
        matches = sum(1 for a, b in zip(output, expected) if a == b)
        max_len = max(len(output), len(expected))

        return matches / max_len if max_len > 0 else 0.0
