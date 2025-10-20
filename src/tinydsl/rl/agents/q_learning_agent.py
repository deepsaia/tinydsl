"""Q-Learning agent with function approximation."""

import numpy as np
from tinydsl.rl.agents.base_agent import BaseAgent


class QLearningAgent(BaseAgent):
    """
    Q-Learning agent with linear function approximation.

    Uses epsilon-greedy exploration and Q-learning updates.
    """

    def __init__(
        self,
        action_space_size: int,
        state_size: int = 100,
        learning_rate: float = 0.001,
        gamma: float = 0.99,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
    ):
        """
        Initialize Q-learning agent.

        Args:
            action_space_size: Number of actions
            state_size: Observation dimension
            learning_rate: Learning rate for Q-updates
            gamma: Discount factor
            epsilon: Initial exploration rate
            epsilon_decay: Epsilon decay per episode
            epsilon_min: Minimum epsilon
        """
        super().__init__(action_space_size)
        self.state_size = state_size
        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Q-function: linear weights
        self.weights = np.random.randn(state_size, action_space_size) * 0.01

    def act(self, observation: np.ndarray, explore: bool = True) -> int:
        """Epsilon-greedy action selection."""
        if explore and np.random.random() < self.epsilon:
            return np.random.randint(0, self.action_space_size)

        # Greedy action
        q_values = observation @ self.weights
        return int(np.argmax(q_values))

    def learn(
        self,
        observation: np.ndarray,
        action: int,
        reward: float,
        next_observation: np.ndarray,
        done: bool,
    ):
        """Q-learning update."""
        # Current Q-value
        q_current = observation @ self.weights[:, action]

        # Target Q-value
        if done:
            q_target = reward
        else:
            q_next_max = np.max(next_observation @ self.weights)
            q_target = reward + self.gamma * q_next_max

        # TD error
        td_error = q_target - q_current

        # Gradient update
        self.weights[:, action] += self.lr * td_error * observation

    def decay_epsilon(self):
        """Decay exploration rate."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, filepath: str):
        """Save weights."""
        np.save(filepath, self.weights)

    def load(self, filepath: str):
        """Load weights."""
        self.weights = np.load(filepath)
