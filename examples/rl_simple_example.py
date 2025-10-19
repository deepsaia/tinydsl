"""
Simple RL example: Train an agent to solve a TinyCalc task.

This demonstrates the basic workflow:
1. Create environment
2. Create agent
3. Train
4. Evaluate
"""

from tinydsl.rl.envs import make_env
from tinydsl.rl.agents import RandomAgent, QLearningAgent, PolicyGradientAgent
from tinydsl.rl.utils import RLTrainer


def train_agent_on_task(dsl_name="tinycalc", task_id="001", agent_type="qlearning"):
    """
    Train an RL agent on a single task.

    Args:
        dsl_name: DSL to use
        task_id: Task identifier
        agent_type: 'random', 'qlearning', or 'pg'
    """
    print(f"🎮 Training {agent_type} agent on {dsl_name} task {task_id}\n")

    # Create environment
    env = make_env(dsl_name, task_id, max_steps=30)

    # Create agent
    if agent_type == "random":
        agent = RandomAgent(env.action_space_size)
        num_episodes = 100
    elif agent_type == "qlearning":
        agent = QLearningAgent(
            action_space_size=env.action_space_size,
            learning_rate=0.01,
            epsilon=0.3
        )
        num_episodes = 2000
    elif agent_type == "pg":
        agent = PolicyGradientAgent(
            action_space_size=env.action_space_size,
            learning_rate=0.001
        )
        num_episodes = 5000
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

    # Create trainer
    trainer = RLTrainer(env, agent, log_dir=f"output/rl_logs/{dsl_name}_{task_id}_{agent_type}")

    # Train
    stats = trainer.train(
        num_episodes=num_episodes,
        eval_every=max(num_episodes // 10, 1),
        save_every=max(num_episodes // 5, 1),
        verbose=True
    )

    print("\n📊 Final Statistics:")
    print(f"  Success Rate: {stats['final_success_rate']:.2%}")
    print(f"  Avg Reward: {stats['final_avg_reward']:.2f}")
    print(f"  Training Time: {stats['elapsed_seconds']:.1f}s")

    # Evaluate
    print("\n🧪 Final Evaluation (10 episodes):")
    eval_stats = stats['evaluation']
    print(f"  Success Rate: {eval_stats['success_rate']:.2%}")
    print(f"  Avg Reward: {eval_stats['avg_reward']:.2f}")
    print(f"  Avg Length: {eval_stats['avg_length']:.1f}")

    return stats


if __name__ == "__main__":
    # Example 1: Random baseline
    print("=" * 60)
    print("EXAMPLE 1: Random Agent (Baseline)")
    print("=" * 60)
    train_agent_on_task("tinycalc", "001", "random")

    print("\n\n")

    # Example 2: Q-Learning
    print("=" * 60)
    print("EXAMPLE 2: Q-Learning Agent")
    print("=" * 60)
    train_agent_on_task("tinycalc", "001", "qlearning")

    print("\n\n")

    # Example 3: Policy Gradient
    print("=" * 60)
    print("EXAMPLE 3: Policy Gradient Agent")
    print("=" * 60)
    train_agent_on_task("tinycalc", "001", "pg")
