"""
Compare multiple RL agents on the same task.

This demonstrates:
- Training multiple agents
- Comparing performance
- Visualizing results
"""

from tinydsl.rl.envs import make_env
from tinydsl.rl.agents import RandomAgent, QLearningAgent, PolicyGradientAgent
from tinydsl.rl.utils import RLTrainer
from typing import Dict, Any


def compare_agents_on_task(dsl_name="tinycalc", task_id="001"):
    """
    Compare different RL agents on the same task.

    Args:
        dsl_name: DSL to use
        task_id: Task identifier
    """
    print(f"🔬 Comparing agents on {dsl_name} task {task_id}\n")

    # Environment
    env = make_env(dsl_name, task_id, max_steps=30)

    # Agents to compare
    agents = {
        "Random": RandomAgent(env.action_space_size),
        "Q-Learning": QLearningAgent(
            action_space_size=env.action_space_size, learning_rate=0.01, epsilon=0.3
        ),
        "Policy Gradient": PolicyGradientAgent(
            action_space_size=env.action_space_size, learning_rate=0.001
        ),
    }

    # Training configurations
    training_configs = {"Random": 100, "Q-Learning": 2000, "Policy Gradient": 3000}

    # Train each agent
    results: Dict[str, Any] = {}

    for name, agent in agents.items():
        print(f"\n{'='*60}")
        print(f"Training {name}")
        print("=" * 60)

        trainer = RLTrainer(
            env=make_env(dsl_name, task_id, max_steps=30),
            agent=agent,
            log_dir=f"output/rl_comparison/{dsl_name}_{task_id}/{name.replace(' ', '_').lower()}",
        )

        stats = trainer.train(
            num_episodes=training_configs[name],
            eval_every=max(training_configs[name] // 5, 1),
            save_every=max(training_configs[name] // 2, 1),
            verbose=False,  # Less verbose for comparison
        )

        results[name] = stats

        print(f"✅ {name} trained")
        print(f"   Final success rate: {stats['final_success_rate']:.2%}")
        print(f"   Final avg reward: {stats['final_avg_reward']:.2f}")

    # Compare results
    print(f"\n{'='*60}")
    print("COMPARISON RESULTS")
    print("=" * 60)
    print(f"{'Agent':<20} {'Success Rate':<15} {'Avg Reward':<15} {'Time (s)':<10}")
    print("-" * 60)

    for name, stats in results.items():
        print(
            f"{name:<20} "
            f"{stats['final_success_rate']:>12.2%}   "
            f"{stats['final_avg_reward']:>12.2f}   "
            f"{stats['elapsed_seconds']:>8.1f}"
        )

    # Determine winner
    print("\n🏆 Winner (by success rate):")
    winner = max(results.items(), key=lambda x: x[1]["final_success_rate"])
    print(f"   {winner[0]} with {winner[1]['final_success_rate']:.2%} success rate")

    return results


if __name__ == "__main__":
    # Compare agents on a TinyCalc task
    results = compare_agents_on_task("tinycalc", "001")

    # Save comparison report
    import json
    from pathlib import Path

    output_dir = Path("output/rl_comparison")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "comparison_report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Comparison report saved to {report_path}")
