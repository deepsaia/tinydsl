"""Efficiency-based reward function."""

from typing import Any, List, Dict
from tinydsl.rl.rewards.base_reward import BaseReward


class EfficiencyReward(BaseReward):
    """
    Reward function that prioritizes both correctness and efficiency.

    Rewards:
    - +20.0 for correct output
    - Bonus for shorter programs
    - Penalty for long programs
    """

    def __init__(
        self, dsl_name: str, target_length: int = 20, length_penalty: float = 0.1
    ):
        """
        Initialize efficiency reward.

        Args:
            dsl_name: DSL name
            target_length: Target program length
            length_penalty: Penalty per token over target
        """
        self.dsl_name = dsl_name
        self.target_length = target_length
        self.length_penalty = length_penalty

    def __call__(
        self, state: List[str], action: str, result: Dict[str, Any], expected: str
    ) -> float:
        """Calculate reward based on correctness and efficiency."""
        reward = 0.0

        # Length penalty
        program_length = len(state)
        if program_length > self.target_length:
            reward += -self.length_penalty * (program_length - self.target_length)

        if result.get("error"):
            reward += -2.0
        elif result.get("success"):
            # Correct output!
            reward += 20.0

            # Efficiency bonus (shorter is better)
            if program_length < self.target_length:
                bonus = (self.target_length - program_length) * 0.5
                reward += bonus

        return reward
