"""Tests for RL framework."""
import pytest
import numpy as np
from tinydsl.rl.envs import make_env
from tinydsl.rl.envs.dsl_env import DSLEnv
from tinydsl.rl.agents import RandomAgent, QLearningAgent, PolicyGradientAgent
from tinydsl.rl.rewards import CorrectnessReward, EfficiencyReward
from tinydsl.rl.utils import RLTrainer, RLEvaluator


# ====================
# Unit Tests
# ====================

class TestRLEnvironment:
    """Test RL environment."""

    def test_make_env(self):
        """Test creating an environment."""
        env = make_env('tinycalc', '001', max_steps=10)
        assert env is not None
        assert env.max_steps == 10

    def test_env_reset(self):
        """Test environment reset."""
        env = make_env('tinycalc', '001', max_steps=10)
        obs = env.reset()
        assert obs is not None
        assert isinstance(obs, np.ndarray)

    def test_env_initialization(self):
        """Test environment initialization."""
        env = DSLEnv("tinycalc", "001", max_steps=20)
        assert env.dsl_name == "tinycalc"
        assert env.task_id == "001"
        assert env.max_steps == 20
        assert env.action_space_size > 0
        assert len(env.vocabulary) > 0

    def test_env_vocabulary(self):
        """Test vocabulary generation for different DSLs."""
        # TinyCalc
        env = DSLEnv("tinycalc", "001")
        assert "define" in env.vocabulary
        assert "convert" in env.vocabulary

        # Lexi
        env = DSLEnv("lexi", "001")
        assert "say" in env.vocabulary
        assert "remember" in env.vocabulary

        # Gli
        env = DSLEnv("gli", "001")
        assert "draw" in env.vocabulary
        assert "circle" in env.vocabulary

        # TinySQL
        env = DSLEnv("tinysql", "001")
        assert "select" in env.vocabulary
        assert "from" in env.vocabulary

    def test_env_render(self):
        """Test environment render."""
        env = make_env('tinycalc', '001', max_steps=10)
        env.reset()
        rendered = env.render()
        assert isinstance(rendered, str)
        assert "Step" in rendered

    def test_env_action_mask(self):
        """Test action mask generation."""
        env = make_env('tinycalc', '001', max_steps=10)
        env.reset()
        mask = env.get_action_mask()
        assert isinstance(mask, np.ndarray)
        assert len(mask) == env.action_space_size


class TestRLAgents:
    """Test RL agents."""

    def test_random_agent(self):
        """Test random agent."""
        agent = RandomAgent(action_space_size=10)
        obs = np.random.rand(100)
        action = agent.act(obs)
        assert 0 <= action < 10

    def test_q_learning_agent(self):
        """Test Q-learning agent."""
        agent = QLearningAgent(
            action_space_size=10,
            learning_rate=0.01,
            epsilon=0.3
        )

        obs = np.random.rand(100)
        action = agent.act(obs)
        assert 0 <= action < 10

        # Test learning
        next_obs = np.random.rand(100)
        agent.learn(obs, action, 1.0, next_obs, False)

    def test_policy_gradient_agent(self):
        """Test policy gradient agent."""
        agent = PolicyGradientAgent(
            action_space_size=10,
            learning_rate=0.001
        )

        obs = np.random.rand(100)
        action = agent.act(obs)
        assert 0 <= action < 10

        # Test learning (PolicyGradientAgent uses learn() not store_transition())
        next_obs = np.random.rand(100)
        agent.learn(obs, action, 1.0, next_obs, done=False)

        # Test episode completion
        agent.learn(next_obs, action, 1.0, next_obs, done=True)

    def test_epsilon_decay(self):
        """Test epsilon decay in Q-learning agent."""
        agent = QLearningAgent(
            action_space_size=10,
            epsilon=0.5,
            epsilon_decay=0.9
        )

        initial_epsilon = agent.epsilon
        agent.decay_epsilon()
        assert agent.epsilon < initial_epsilon


class TestRewardFunctions:
    """Test reward functions."""

    def test_correctness_reward(self):
        """Test correctness reward function."""
        reward_fn = CorrectnessReward(dsl_name='tinycalc')

        # Test success
        result = {'success': True, 'output': '5.0 grobble'}
        reward = reward_fn([], 'token', result, '5.0 grobble')
        assert reward > 0

        # Test failure
        result = {'success': False, 'error': 'Parse error'}
        reward = reward_fn([], 'token', result, '5.0 grobble')
        assert reward < 0

    def test_correctness_reward_similarity(self):
        """Test partial reward based on similarity."""
        reward_fn = CorrectnessReward(dsl_name='tinycalc')

        # Partial match
        result = {'success': False, 'output': '14.0'}
        reward = reward_fn([], 'convert', result, '14.0 grobble')
        assert reward > -1.0  # Better than error, worse than success
        assert reward < 10.0

    def test_efficiency_reward(self):
        """Test efficiency reward function."""
        reward_fn = EfficiencyReward(
            dsl_name='tinycalc',
            target_length=10
        )

        # Test success with short program
        result = {'success': True, 'output': '5.0 grobble'}
        state = ['token'] * 5
        reward = reward_fn(state, 'token', result, '5.0 grobble')
        assert reward > 0


class TestRLTrainer:
    """Test RL trainer."""

    def test_trainer_initialization(self):
        """Test trainer initializes correctly."""
        env = make_env('tinycalc', '001', max_steps=10)
        agent = RandomAgent(env.action_space_size)
        trainer = RLTrainer(env, agent)
        assert trainer.env == env
        assert trainer.agent == agent

    def test_trainer_short_training(self):
        """Test short training run."""
        env = make_env('tinycalc', '001', max_steps=10)
        agent = RandomAgent(env.action_space_size)
        trainer = RLTrainer(env, agent)

        # Train for just 5 episodes
        stats = trainer.train(num_episodes=5, verbose=False)

        assert 'total_episodes' in stats
        assert stats['total_episodes'] == 5
        assert 'final_avg_reward' in stats
        assert 'final_success_rate' in stats


class TestRLEvaluator:
    """Test RL evaluator."""

    def test_evaluator_initialization(self):
        """Test evaluator initializes correctly."""
        evaluator = RLEvaluator()
        assert evaluator is not None

    def test_evaluate_agent(self):
        """Test evaluating an agent."""
        env = make_env('tinycalc', '001', max_steps=10)
        agent = RandomAgent(env.action_space_size)
        evaluator = RLEvaluator()

        results = evaluator.evaluate_agent(agent, env, n_episodes=3)

        assert 'success_rate' in results
        assert 'avg_reward' in results
        assert 'avg_length' in results
        assert 0 <= results['success_rate'] <= 1

    def test_compare_agents(self):
        """Test comparing multiple agents."""
        env = make_env('tinycalc', '001', max_steps=10)
        agent1 = RandomAgent(env.action_space_size)
        agent2 = RandomAgent(env.action_space_size)

        agents = {"agent1": agent1, "agent2": agent2}
        evaluator = RLEvaluator()

        results = evaluator.compare_agents(agents, env, n_episodes=3)

        assert len(results) == 2
        assert "agent1" in results
        assert "agent2" in results


# ====================
# Integration Tests (Require Server)
# ====================

@pytest.mark.integration
@pytest.mark.requires_server
class TestRLEnvironmentIntegration:
    """Integration tests for RL environment with real server."""

    def test_env_step_execution(self):
        """Test environment step with actual DSL execution."""
        env = make_env('tinycalc', '001', max_steps=10)
        env.reset()

        # Take first action
        action = 0  # First token in vocabulary
        obs, reward, done, info = env.step(action)

        # Verify step interface
        assert isinstance(obs, np.ndarray)
        assert isinstance(reward, (int, float))
        assert isinstance(done, bool)
        assert isinstance(info, dict)

        # Verify info contents
        assert "current_code" in info
        assert "result" in info
        assert "expected" in info
        assert "step" in info

    def test_env_episode_flow(self):
        """Test full episode flow."""
        env = make_env('tinycalc', '001', max_steps=20)
        obs = env.reset()

        done = False
        steps = 0
        total_reward = 0

        while not done and steps < 20:
            action = np.random.randint(0, env.action_space_size)
            obs, reward, done, info = env.step(action)
            total_reward += reward
            steps += 1

        # Episode should terminate
        assert steps <= 20
        assert isinstance(total_reward, (int, float))

    def test_env_with_correctness_reward(self):
        """Test environment with CorrectnessReward."""
        reward_fn = CorrectnessReward("tinycalc")
        env = DSLEnv("tinycalc", "001", reward_fn=reward_fn, max_steps=10)

        obs = env.reset()
        action = 0
        obs, reward, done, info = env.step(action)

        # Reward should be a float
        assert isinstance(reward, (int, float))

    def test_env_multiple_dsls(self):
        """Test environment creation for all DSLs."""
        dsls = ["tinycalc", "lexi", "gli", "tinysql"]

        for dsl in dsls:
            env = make_env(dsl, "001", max_steps=10)
            assert env.dsl_name == dsl
            assert env.action_space_size > 0

            # Test reset works
            obs = env.reset()
            assert isinstance(obs, np.ndarray)

    def test_env_integration_with_client(self):
        """Test environment uses GenericDSLClient correctly."""
        from tinydsl.agent_tools.generic_dsl_client import GenericDSLClient

        # Create client
        client = GenericDSLClient()

        # Test client works
        result = client.run("tinycalc", "define 1 flurb = 3.5 grobble\nconvert 4 flurb to grobble")
        assert result.get("status") == "ok"

        # Create environment that uses same client internally
        env = DSLEnv("tinycalc", "001")
        assert env.dsl_name == "tinycalc"


@pytest.mark.integration
@pytest.mark.requires_server
class TestRLTrainerIntegration:
    """Integration tests for RL trainer with real environment."""

    def test_train_random_agent(self):
        """Test training a random agent on real environment."""
        env = make_env('tinycalc', '001', max_steps=15)
        agent = RandomAgent(env.action_space_size)
        trainer = RLTrainer(env, agent)

        # Short training run
        stats = trainer.train(num_episodes=10, verbose=False)

        assert stats['total_episodes'] == 10
        assert 'final_avg_reward' in stats
        assert 'final_success_rate' in stats
        assert 0 <= stats['final_success_rate'] <= 1

    def test_train_q_learning_agent(self):
        """Test training a Q-learning agent."""
        env = make_env('tinycalc', '001', max_steps=15)
        agent = QLearningAgent(
            action_space_size=env.action_space_size,
            learning_rate=0.01,
            epsilon=0.3
        )
        trainer = RLTrainer(env, agent)

        # Short training run
        stats = trainer.train(num_episodes=10, verbose=False)

        assert stats['total_episodes'] == 10
        assert isinstance(stats['final_avg_reward'], (int, float))


# ====================
# Test Runner
# ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
