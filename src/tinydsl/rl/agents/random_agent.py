"""Random agent (baseline)."""

import numpy as np
from tinydsl.rl.agents.base_agent import BaseAgent


class RandomAgent(BaseAgent):
    """
    Random agent that selects actions uniformly.

    Useful as a baseline to compare against.
    """

    def __init__(self, action_space_size: int):
        """Initialize random agent."""
        super().__init__(action_space_size)

    def act(self, observation: np.ndarray, explore: bool = True) -> int:
        """Choose random action."""
        return np.random.randint(0, self.action_space_size)

    def learn(
        self,
        observation: np.ndarray,
        action: int,
        reward: float,
        next_observation: np.ndarray,
        done: bool
    ):
        """Random agent doesn't learn."""
        pass
