"""RL evaluation utilities."""

from typing import Dict, Any, List
from tinydsl.rl.envs.dsl_env import DSLEnv
from tinydsl.rl.agents.base_agent import BaseAgent
import numpy as np


class RLEvaluator:
    """
    Evaluator for RL agents on DSL tasks.

    Provides comprehensive evaluation metrics for comparing agents.
    """

    def __init__(self):
        """Initialize evaluator."""
        pass

    def evaluate_agent(
        self, agent: BaseAgent, env: DSLEnv, n_episodes: int = 100
    ) -> Dict[str, Any]:
        """
        Evaluate agent comprehensively.

        Args:
            agent: RL agent to evaluate
            env: Environment
            n_episodes: Number of episodes

        Returns:
            Detailed evaluation metrics
        """
        rewards = []
        lengths = []
        successes = []
        programs = []

        for _ in range(n_episodes):
            observation = env.reset()
            done = False
            episode_reward = 0.0
            episode_length = 0

            while not done:
                action = agent.act(observation, explore=False)
                observation, reward, done, info = env.step(action)
                episode_reward += reward
                episode_length += 1

            rewards.append(episode_reward)
            lengths.append(episode_length)
            success = info.get("result", {}).get("success", False)
            successes.append(1.0 if success else 0.0)
            programs.append(info.get("current_code", ""))

        return {
            "avg_reward": np.mean(rewards),
            "std_reward": np.std(rewards),
            "avg_length": np.mean(lengths),
            "std_length": np.std(lengths),
            "success_rate": np.mean(successes),
            "n_episodes": n_episodes,
            "sample_programs": programs[:5],  # First 5 programs
        }

    def compare_agents(
        self, agents: Dict[str, BaseAgent], env: DSLEnv, n_episodes: int = 100
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple agents.

        Args:
            agents: Dict of {name: agent}
            env: Environment
            n_episodes: Episodes per agent

        Returns:
            Comparison results
        """
        results = {}

        for name, agent in agents.items():
            print(f"Evaluating {name}...")
            results[name] = self.evaluate_agent(agent, env, n_episodes)

        return results

    def compute_sample_efficiency(
        self, training_curves: List[List[float]]
    ) -> Dict[str, float]:
        """
        Compute sample efficiency metrics.

        Args:
            training_curves: List of reward curves

        Returns:
            Efficiency metrics
        """
        # Area under curve
        aucs = [np.trapz(curve) for curve in training_curves]

        # Episodes to threshold (e.g., 80% success)
        threshold = 0.8
        episodes_to_threshold = []
        for curve in training_curves:
            for i, val in enumerate(curve):
                if val >= threshold:
                    episodes_to_threshold.append(i)
                    break
            else:
                episodes_to_threshold.append(len(curve))

        return {
            "mean_auc": np.mean(aucs),
            "mean_episodes_to_threshold": np.mean(episodes_to_threshold),
            "convergence_rate": (
                1.0 / np.mean(episodes_to_threshold) if episodes_to_threshold else 0.0
            ),
        }
