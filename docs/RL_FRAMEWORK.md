# TinyDSL RL/ES Framework

**Reinforcement Learning and Evolution Strategies for Domain-Specific Languages**

---

## Overview

TinyDSL now includes a complete RL/ES framework that treats each DSL as a learning environment. This enables:

- **RL Research**: Use DSLs as testbeds for RL algorithms
- **Sample Efficiency Studies**: Measure how quickly agents learn novel languages
- **Curriculum Learning**: Train on progressively harder tasks
- **Transfer Learning**: Test if knowledge transfers across tasks
- **Algorithm Comparison**: Benchmark different RL approaches

---

## Architecture

```
tinydsl/rl/
├── envs/              # DSL environments
│   └── dsl_env.py    # Gym-style wrapper for any DSL
├── agents/            # RL algorithms
│   ├── random_agent.py          # Baseline
│   ├── q_learning_agent.py      # Q-learning
│   └── policy_gradient_agent.py # REINFORCE
├── rewards/           # Reward functions
│   ├── correctness_reward.py    # Output correctness
│   └── efficiency_reward.py     # Correctness + efficiency
└── utils/             # Training utilities
    ├── trainer.py     # Training loop
    └── evaluator.py   # Evaluation metrics
```

---

## Quick Start

### 1. Train a Simple Agent

```python
from tinydsl.rl.envs import make_env
from tinydsl.rl.agents import QLearningAgent
from tinydsl.rl.utils import RLTrainer

# Create environment
env = make_env('tinycalc', '001', max_steps=30)

# Create agent
agent = QLearningAgent(
    action_space_size=env.action_space_size,
    learning_rate=0.01,
    epsilon=0.3
)

# Train
trainer = RLTrainer(env, agent)
stats = trainer.train(num_episodes=2000)

print(f"Success rate: {stats['final_success_rate']:.2%}")
```

### 2. Run Example Scripts

```bash
# Simple training example
python examples/rl_simple_example.py

# Compare multiple agents
python examples/rl_compare_agents.py

# Curriculum learning
python examples/rl_curriculum_learning.py
```

---

## DSL as RL Environment

### State Representation
- **Current program**: Sequence of DSL tokens
- **Progress**: Step count / max steps
- **Context**: Variables, execution state

### Action Space
- **Vocabulary**: Valid DSL tokens (keywords, operators, values)
- **Action**: Select next token to append to program
- **Size**: ~20-50 tokens per DSL

### Reward Signal
- **Correctness**: +10.0 for matching expected output
- **Step penalty**: -0.1 per step (encourages efficiency)
- **Error penalty**: -1.0 for syntax errors
- **Partial credit**: Reward for getting closer to correct output

### Episode Termination
- **Success**: Correct output produced
- **Max steps**: Reached maximum program length
- **Newline**: Program completed (heuristic)

---

## Available Agents

### 1. RandomAgent (Baseline)
```python
from tinydsl.rl.agents import RandomAgent

agent = RandomAgent(action_space_size)
```
- Selects actions uniformly at random
- Useful baseline for comparison

### 2. QLearningAgent
```python
from tinydsl.rl.agents import QLearningAgent

agent = QLearningAgent(
    action_space_size=env.action_space_size,
    learning_rate=0.01,
    gamma=0.99,
    epsilon=0.3,
    epsilon_decay=0.995
)
```
- Linear function approximation
- Epsilon-greedy exploration
- Q-learning updates with TD(0)

### 3. PolicyGradientAgent (REINFORCE)
```python
from tinydsl.rl.agents import PolicyGradientAgent

agent = PolicyGradientAgent(
    action_space_size=env.action_space_size,
    learning_rate=0.001,
    gamma=0.99
)
```
- Stochastic policy
- Monte Carlo policy gradient
- Baseline normalization

---

## Reward Functions

### CorrectnessReward (Default)
```python
from tinydsl.rl.rewards import CorrectnessReward

reward_fn = CorrectnessReward(dsl_name='tinycalc', step_penalty=-0.1)
```
- **+10.0**: Correct output
- **-0.1**: Per step
- **-1.0**: Syntax error
- **Partial credit**: Based on string similarity

### EfficiencyReward
```python
from tinydsl.rl.rewards import EfficiencyReward

reward_fn = EfficiencyReward(
    dsl_name='tinycalc',
    target_length=20,
    length_penalty=0.1
)
```
- **+20.0**: Correct output
- **Bonus**: For shorter programs
- **Penalty**: For exceeding target length

### Custom Reward
```python
class MyReward(BaseReward):
    def __call__(self, state, action, result, expected):
        # Your custom logic
        if result['success']:
            return 100.0
        return -1.0

env = make_env('tinycalc', '001', reward_fn=MyReward())
```

---

## Training & Evaluation

### Training Loop

```python
from tinydsl.rl.utils import RLTrainer

trainer = RLTrainer(env, agent, log_dir='output/rl_logs/experiment1')

stats = trainer.train(
    num_episodes=5000,
    eval_every=500,      # Evaluate every N episodes
    save_every=1000,     # Save checkpoint every N episodes
    verbose=True
)
```

**Returns**:
```python
{
    "total_episodes": 5000,
    "elapsed_seconds": 120.5,
    "final_avg_reward": 8.2,
    "final_success_rate": 0.75,
    "evaluation": {...}
}
```

### Evaluation

```python
from tinydsl.rl.utils import RLEvaluator

evaluator = RLEvaluator()

# Evaluate single agent
results = evaluator.evaluate_agent(agent, env, n_episodes=100)
print(f"Success rate: {results['success_rate']:.2%}")

# Compare multiple agents
agents = {
    "Random": random_agent,
    "Q-Learning": qlearning_agent,
    "Policy Gradient": pg_agent
}
comparison = evaluator.compare_agents(agents, env, n_episodes=100)
```

---

## Advanced Usage

### Curriculum Learning

Train on progressively harder tasks:

```python
from tinydsl.rl.envs import make_env
from tinydsl.rl.agents import QLearningAgent
from tinydsl.rl.utils import RLTrainer

# Task sequence: easy -> hard
tasks = ["001", "002", "003", "004", "005"]

# Create agent
env = make_env('tinycalc', tasks[0])
agent = QLearningAgent(action_space_size=env.action_space_size)

# Train on each task sequentially
for task_id in tasks:
    env = make_env('tinycalc', task_id)
    trainer = RLTrainer(env, agent)
    stats = trainer.train(num_episodes=1000)
    print(f"Task {task_id}: {stats['final_success_rate']:.2%}")
```

### Transfer Learning

Evaluate transfer across DSLs:

```python
# Train on TinyCalc
env_train = make_env('tinycalc', '001')
agent = QLearningAgent(action_space_size=env_train.action_space_size)
trainer = RLTrainer(env_train, agent)
trainer.train(num_episodes=2000)

# Test on different task
env_test = make_env('tinycalc', '005')
eval_result = trainer.evaluate(n_episodes=50)
print(f"Transfer success: {eval_result['success_rate']:.2%}")
```

### Multi-Task Learning

Train agent on multiple tasks simultaneously:

```python
tasks = ['001', '002', '003']
envs = [make_env('tinycalc', tid) for tid in tasks]

agent = QLearningAgent(action_space_size=envs[0].action_space_size)

for episode in range(10000):
    # Sample task
    env = envs[episode % len(envs)]

    # Run episode
    obs = env.reset()
    done = False
    while not done:
        action = agent.act(obs)
        next_obs, reward, done, info = env.step(action)
        agent.learn(obs, action, reward, next_obs, done)
        obs = next_obs
```

---

## Supported DSLs

All TinyDSL languages work as RL environments:

| DSL | Action Space | Typical Tasks | Difficulty |
|-----|--------------|---------------|------------|
| **TinyCalc** | ~25 tokens | Unit conversion | Medium |
| **Lexi** | ~30 tokens | Text generation | Easy |
| **Gli** | ~35 tokens | Graphics | Hard |
| **TinySQL** | ~20 tokens | Queries | Medium |

---

## Experiment Examples

### Example 1: Baseline Comparison

```python
# Compare Random vs Q-Learning
agents = {
    "Random": RandomAgent(env.action_space_size),
    "Q-Learning": QLearningAgent(env.action_space_size)
}

for name, agent in agents.items():
    trainer = RLTrainer(env, agent)
    stats = trainer.train(num_episodes=2000)
    print(f"{name}: {stats['final_success_rate']:.2%}")
```

**Expected Output**:
```
Random: 2.5%
Q-Learning: 68.3%
```

### Example 2: Sample Efficiency

```python
# Measure episodes to 80% success
agent = QLearningAgent(env.action_space_size)
trainer = RLTrainer(env, agent)

for episode in range(10000):
    stats = trainer.train(num_episodes=1, verbose=False)
    if stats['final_success_rate'] >= 0.8:
        print(f"Reached 80% after {episode} episodes")
        break
```

### Example 3: Curriculum vs Direct

```python
# Curriculum: 001 -> 002 -> 003
agent_curriculum = train_with_curriculum(['001', '002', '003'])

# Direct: train only on 003
agent_direct = train_on_single_task('003')

# Compare on task 003
eval_curriculum = evaluate(agent_curriculum, '003')
eval_direct = evaluate(agent_direct, '003')

print(f"Curriculum: {eval_curriculum['success_rate']:.2%}")
print(f"Direct: {eval_direct['success_rate']:.2%}")
```

---

## Integration with KAIT Protocol

Combine RL with KAIT evaluation:

```python
from tinydsl.agent_tools import KAITAgent
from tinydsl.rl.agents import QLearningAgent

# Train RL agent
rl_agent = train_rl_agent('tinycalc', '001')

# Use with KAIT
kait = KAITAgent('tinycalc')
kait.run_baseline(['001', '002', '003'])

# RL agent generates code
# KAIT evaluates acquisition and transfer
```

---

## Performance Tips

### 1. Hyperparameter Tuning

**Q-Learning**:
- `learning_rate`: 0.001 - 0.01
- `epsilon`: 0.1 - 0.5 (higher for complex tasks)
- `gamma`: 0.95 - 0.99

**Policy Gradient**:
- `learning_rate`: 0.0001 - 0.001 (lower than Q-learning)
- `gamma`: 0.95 - 0.99

### 2. Environment Configuration

- `max_steps`: 20-50 (shorter for simple tasks)
- `reward_fn`: Use `EfficiencyReward` for shorter programs

### 3. Training Tips

- **Warm-up**: Train on easier tasks first
- **Curriculum**: Use progressive difficulty
- **Checkpointing**: Save every 500-1000 episodes
- **Evaluation**: Evaluate frequently to track progress

---

## Future Extensions

### 1. Advanced Algorithms

- **PPO**: Proximal Policy Optimization
- **A3C**: Asynchronous Advantage Actor-Critic
- **SAC**: Soft Actor-Critic

### 2. Evolution Strategies

- **CMA-ES**: Covariance Matrix Adaptation
- **OpenAI ES**: Evolution Strategies for RL
- **Genetic Programming**: Evolve DSL programs directly

### 3. Meta-Learning

- **MAML**: Model-Agnostic Meta-Learning
- **Reptile**: First-order meta-learning
- **Multi-task**: Learn across all DSLs simultaneously

---

## Citation

If you use TinyDSL's RL framework in research:

```bibtex
@software{tinydsl_rl,
  title = {TinyDSL RL Framework},
  author = {TinyDSL Contributors},
  year = {2025},
  url = {https://github.com/deepsaia/tinydsl}
}
```

---

## References

- **KAIT Protocol**: Knowledge Acquisition & Inter-task Transfer
- **Chollet's ARC**: On the Measure of Intelligence (arxiv:1911.01547)
- **Curriculum Learning**: Bengio et al.
- **REINFORCE**: Williams, 1992
- **Q-Learning**: Watkins & Dayan, 1992

---

## Support

For questions or issues:
- GitHub Issues: https://github.com/deepsaia/tinydsl/issues
- Examples: See `examples/rl_*.py`
- Documentation: This file

Happy experimenting! 🚀
