"""
Curriculum Learning example: Train agent on progressively harder tasks.

This demonstrates:
- Training on easy tasks first
- Gradually increasing difficulty
- Transfer learning across tasks
"""

from tinydsl.rl.envs import make_env
from tinydsl.rl.agents import QLearningAgent
from tinydsl.rl.utils import RLTrainer, RLEvaluator
from typing import List


def curriculum_learning(
    dsl_name="tinycalc",
    task_sequence: List[str] = None
):
    """
    Train agent using curriculum learning.

    Args:
        dsl_name: DSL to use
        task_sequence: Ordered list of task IDs (easy -> hard)
    """
    if task_sequence is None:
        # Default curriculum for TinyCalc
        task_sequence = ["001", "002", "003", "004", "005"]

    print(f"📚 Curriculum Learning on {dsl_name}")
    print(f"   Task sequence: {' -> '.join(task_sequence)}\n")

    # Create agent
    env = make_env(dsl_name, task_sequence[0], max_steps=30)
    agent = QLearningAgent(
        action_space_size=env.action_space_size,
        learning_rate=0.01,
        epsilon=0.5  # Higher exploration for curriculum
    )

    results = []

    for i, task_id in enumerate(task_sequence):
        print(f"\n{'='*60}")
        print(f"Stage {i+1}/{len(task_sequence)}: Task {task_id}")
        print('='*60)

        # Create environment for current task
        env = make_env(dsl_name, task_id, max_steps=30)

        # Create trainer
        trainer = RLTrainer(
            env=env,
            agent=agent,  # Same agent, continues learning
            log_dir=f"output/rl_curriculum/{dsl_name}/stage_{i+1}_task_{task_id}"
        )

        # Train on this task
        stats = trainer.train(
            num_episodes=1000,
            eval_every=200,
            save_every=500,
            verbose=True
        )

        results.append({
            "task_id": task_id,
            "stage": i + 1,
            "stats": stats
        })

        print(f"\n✅ Stage {i+1} complete")
        print(f"   Success rate: {stats['final_success_rate']:.2%}")

    # Final evaluation on all tasks
    print(f"\n{'='*60}")
    print("FINAL EVALUATION ON ALL TASKS")
    print('='*60)

    evaluator = RLEvaluator()

    for task_id in task_sequence:
        env = make_env(dsl_name, task_id, max_steps=30)
        eval_result = evaluator.evaluate_agent(agent, env, n_episodes=20)

        print(f"\nTask {task_id}:")
        print(f"  Success Rate: {eval_result['success_rate']:.2%}")
        print(f"  Avg Reward: {eval_result['avg_reward']:.2f}")

    return results, agent


def compare_curriculum_vs_single_task(dsl_name="tinycalc"):
    """
    Compare curriculum learning vs training on hardest task directly.
    """
    print("🔬 Comparing Curriculum Learning vs Direct Training\n")

    task_sequence = ["001", "002", "003", "004", "005"]
    hard_task = "005"

    # Curriculum agent
    print("Training with curriculum...")
    curriculum_results, curriculum_agent = curriculum_learning(dsl_name, task_sequence)

    # Direct training agent
    print("\n\nTraining directly on hard task...")
    env = make_env(dsl_name, hard_task, max_steps=30)
    direct_agent = QLearningAgent(
        action_space_size=env.action_space_size,
        learning_rate=0.01,
        epsilon=0.5
    )

    trainer = RLTrainer(env, direct_agent, log_dir="output/rl_direct/tinycalc_005")
    direct_stats = trainer.train(num_episodes=5000, eval_every=1000, verbose=True)

    # Compare
    print(f"\n{'='*60}")
    print("COMPARISON")
    print('='*60)

    # Evaluate both on hard task
    evaluator = RLEvaluator()
    env = make_env(dsl_name, hard_task, max_steps=30)

    curriculum_eval = evaluator.evaluate_agent(curriculum_agent, env, n_episodes=50)
    direct_eval = evaluator.evaluate_agent(direct_agent, env, n_episodes=50)

    print(f"\nCurriculum Learning on task {hard_task}:")
    print(f"  Success Rate: {curriculum_eval['success_rate']:.2%}")
    print(f"  Avg Reward: {curriculum_eval['avg_reward']:.2f}")

    print(f"\nDirect Training on task {hard_task}:")
    print(f"  Success Rate: {direct_eval['success_rate']:.2%}")
    print(f"  Avg Reward: {direct_eval['avg_reward']:.2f}")

    if curriculum_eval['success_rate'] > direct_eval['success_rate']:
        print("\n🏆 Curriculum learning wins!")
    else:
        print("\n🏆 Direct training wins!")

    return curriculum_eval, direct_eval


if __name__ == "__main__":
    # Example 1: Basic curriculum learning
    print("EXAMPLE 1: Basic Curriculum Learning")
    print("="*60)
    curriculum_learning("tinycalc", ["001", "002", "003"])

    print("\n\n")

    # Example 2: Curriculum vs Direct comparison
    print("EXAMPLE 2: Curriculum vs Direct Training")
    print("="*60)
    compare_curriculum_vs_single_task("tinycalc")
