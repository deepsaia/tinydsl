"""Base agent interface."""

from abc import ABC, abstractmethod
import numpy as np


class BaseAgent(ABC):
    """Abstract base class for RL agents."""

    def __init__(self, action_space_size: int):
        """
        Initialize agent.

        Args:
            action_space_size: Number of possible actions
        """
        self.action_space_size = action_space_size

    @abstractmethod
    def act(self, observation: np.ndarray, explore: bool = True) -> int:
        """
        Choose an action given an observation.

        Args:
            observation: Current state observation
            explore: Whether to explore (vs exploit)

        Returns:
            Action index
        """
        pass

    @abstractmethod
    def learn(
        self,
        observation: np.ndarray,
        action: int,
        reward: float,
        next_observation: np.ndarray,
        done: bool,
    ):
        """
        Update agent based on experience.

        Args:
            observation: Current state
            action: Action taken
            reward: Reward received
            next_observation: Next state
            done: Whether episode ended
        """
        pass

    def save(self, filepath: str):
        """Save agent parameters."""
        pass

    def load(self, filepath: str):
        """Load agent parameters."""
        pass
