"""RL training utilities."""

from typing import Dict, Any, Optional, List
from tinydsl.rl.envs.dsl_env import DSLEnv
from tinydsl.rl.agents.base_agent import BaseAgent
import time
import json
from pathlib import Path


class RLTrainer:
    """
    Trainer for RL agents on DSL environments.

    Handles training loops, logging, checkpointing, and evaluation.
    """

    def __init__(
        self,
        env: DSLEnv,
        agent: BaseAgent,
        log_dir: Optional[str] = None
    ):
        """
        Initialize trainer.

        Args:
            env: DSL environment
            agent: RL agent
            log_dir: Directory for logs and checkpoints
        """
        self.env = env
        self.agent = agent
        self.log_dir = Path(log_dir) if log_dir else Path("output/rl_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.episode_rewards: List[float] = []
        self.episode_lengths: List[int] = []
        self.success_rate: List[float] = []

    def train(
        self,
        num_episodes: int,
        eval_every: int = 100,
        save_every: int = 500,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Train agent for specified number of episodes.

        Args:
            num_episodes: Number of training episodes
            eval_every: Evaluate every N episodes
            save_every: Save checkpoint every N episodes
            verbose: Print progress

        Returns:
            Training statistics
        """
        if verbose:
            print(f"🏋️ Training on {self.env.dsl_name} task {self.env.task_id}")
            print(f"📊 Episodes: {num_episodes}")
            print(f"🎯 Target: {self.env.expected_output}\n")

        start_time = time.time()

        for episode in range(1, num_episodes + 1):
            # Run episode
            episode_reward, episode_length, success = self._run_episode()

            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(episode_length)
            self.success_rate.append(1.0 if success else 0.0)

            # Decay exploration (if applicable)
            if hasattr(self.agent, 'decay_epsilon'):
                self.agent.decay_epsilon()

            # Logging
            if verbose and episode % eval_every == 0:
                avg_reward = sum(self.episode_rewards[-eval_every:]) / eval_every
                avg_length = sum(self.episode_lengths[-eval_every:]) / eval_every
                success_rate = sum(self.success_rate[-eval_every:]) / eval_every
                epsilon = getattr(self.agent, 'epsilon', None)

                print(f"Episode {episode}/{num_episodes}")
                print(f"  Avg Reward: {avg_reward:.2f}")
                print(f"  Avg Length: {avg_length:.1f}")
                print(f"  Success Rate: {success_rate:.2%}")
                if epsilon is not None:
                    print(f"  Epsilon: {epsilon:.3f}")
                print()

            # Checkpointing
            if episode % save_every == 0:
                self._save_checkpoint(episode)

        elapsed = time.time() - start_time

        # Final evaluation
        final_eval = self.evaluate(n_episodes=10)

        stats = {
            "total_episodes": num_episodes,
            "elapsed_seconds": elapsed,
            "final_avg_reward": sum(self.episode_rewards[-100:]) / min(100, len(self.episode_rewards)),
            "final_success_rate": sum(self.success_rate[-100:]) / min(100, len(self.success_rate)),
            "evaluation": final_eval
        }

        # Save training curve
        self._save_training_curve()

        if verbose:
            print("✅ Training complete!")
            print(f"⏱️ Time: {elapsed:.1f}s")
            print(f"🎯 Final success rate: {stats['final_success_rate']:.2%}")

        return stats

    def _run_episode(self) -> tuple:
        """Run a single episode."""
        observation = self.env.reset()
        done = False
        episode_reward = 0.0
        episode_length = 0

        while not done:
            # Agent acts
            action = self.agent.act(observation, explore=True)

            # Environment steps
            next_observation, reward, done, info = self.env.step(action)

            # Agent learns
            self.agent.learn(observation, action, reward, next_observation, done)

            episode_reward += reward
            episode_length += 1
            observation = next_observation

        success = info.get("result", {}).get("success", False)

        return episode_reward, episode_length, success

    def evaluate(self, n_episodes: int = 10) -> Dict[str, Any]:
        """
        Evaluate agent performance.

        Args:
            n_episodes: Number of evaluation episodes

        Returns:
            Evaluation statistics
        """
        rewards = []
        lengths = []
        successes = []

        for _ in range(n_episodes):
            observation = self.env.reset()
            done = False
            episode_reward = 0.0
            episode_length = 0

            while not done:
                # No exploration during evaluation
                action = self.agent.act(observation, explore=False)
                observation, reward, done, info = self.env.step(action)
                episode_reward += reward
                episode_length += 1

            rewards.append(episode_reward)
            lengths.append(episode_length)
            successes.append(1.0 if info.get("result", {}).get("success", False) else 0.0)

        return {
            "avg_reward": sum(rewards) / len(rewards),
            "avg_length": sum(lengths) / len(lengths),
            "success_rate": sum(successes) / len(successes),
            "n_episodes": n_episodes
        }

    def _save_checkpoint(self, episode: int):
        """Save agent checkpoint."""
        checkpoint_path = self.log_dir / f"checkpoint_ep{episode}.npy"
        self.agent.save(str(checkpoint_path))

    def _save_training_curve(self):
        """Save training curve data."""
        data = {
            "episode_rewards": self.episode_rewards,
            "episode_lengths": self.episode_lengths,
            "success_rate": self.success_rate
        }

        curve_path = self.log_dir / "training_curve.json"
        with open(curve_path, "w") as f:
            json.dump(data, f, indent=2)
