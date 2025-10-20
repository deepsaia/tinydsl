"""Base reward function interface."""

from abc import ABC, abstractmethod
from typing import Any, List, Dict


class BaseReward(ABC):
    """Abstract base class for reward functions."""

    @abstractmethod
    def __call__(
        self, state: List[str], action: str, result: Dict[str, Any], expected: str
    ) -> float:
        """
        Calculate reward for a state-action-result triple.

        Args:
            state: Current program tokens
            action: Token just added
            result: Execution result
            expected: Expected output

        Returns:
            Reward value
        """
        pass
