"""Policy Gradient (REINFORCE) agent."""

import numpy as np
from typing import List, Tuple
from tinydsl.rl.agents.base_agent import BaseAgent


class PolicyGradientAgent(BaseAgent):
    """
    Policy Gradient (REINFORCE) agent.

    Learns a stochastic policy using Monte Carlo policy gradient.
    """

    def __init__(
        self,
        action_space_size: int,
        state_size: int = 100,
        learning_rate: float = 0.001,
        gamma: float = 0.99
    ):
        """
        Initialize policy gradient agent.

        Args:
            action_space_size: Number of actions
            state_size: Observation dimension
            learning_rate: Learning rate
            gamma: Discount factor
        """
        super().__init__(action_space_size)
        self.state_size = state_size
        self.lr = learning_rate
        self.gamma = gamma

        # Policy parameters (logits)
        self.theta = np.random.randn(state_size, action_space_size) * 0.01

        # Episode buffer
        self.episode_buffer: List[Tuple] = []

    def act(self, observation: np.ndarray, explore: bool = True) -> int:
        """Sample action from policy."""
        logits = observation @ self.theta
        # Softmax
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)

        # Sample action
        action = np.random.choice(self.action_space_size, p=probs)
        return int(action)

    def learn(
        self,
        observation: np.ndarray,
        action: int,
        reward: float,
        next_observation: np.ndarray,
        done: bool
    ):
        """Store experience in buffer."""
        self.episode_buffer.append((observation, action, reward))

        if done:
            self._update_policy()
            self.episode_buffer = []

    def _update_policy(self):
        """Update policy using REINFORCE algorithm."""
        if not self.episode_buffer:
            return

        # Calculate discounted returns
        returns = []
        G = 0.0
        for _, _, reward in reversed(self.episode_buffer):
            G = reward + self.gamma * G
            returns.insert(0, G)

        returns = np.array(returns)
        # Normalize returns
        if len(returns) > 1:
            returns = (returns - np.mean(returns)) / (np.std(returns) + 1e-8)

        # Policy gradient update
        for (observation, action, _), G in zip(self.episode_buffer, returns):
            # Compute softmax probabilities
            logits = observation @ self.theta
            exp_logits = np.exp(logits - np.max(logits))
            probs = exp_logits / np.sum(exp_logits)

            # Gradient: dlog(pi)/dtheta = (e_a - pi) where e_a is one-hot
            grad = -probs
            grad[action] += 1.0

            # Update: theta += lr * G * grad * observation
            self.theta += self.lr * G * np.outer(observation, grad)

    def save(self, filepath: str):
        """Save policy parameters."""
        np.save(filepath, self.theta)

    def load(self, filepath: str):
        """Load policy parameters."""
        self.theta = np.load(filepath)
