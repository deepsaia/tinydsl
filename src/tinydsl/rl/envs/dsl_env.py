"""
DSL Environment for Reinforcement Learning

Wraps any TinyDSL as an RL environment compatible with standard interfaces.
"""

from typing import Any, Dict, Tuple, Optional, List
import numpy as np


class DSLEnv:
    """
    Generic RL environment for any TinyDSL.

    State: Current DSL program (sequence of tokens/commands)
    Actions: DSL commands (vocabulary of valid tokens)
    Rewards: Task-specific (correctness, efficiency, etc.)

    Compatible with OpenAI Gym-style interface.
    """

    def __init__(
        self,
        dsl_name: str,
        task_id: str,
        reward_fn: Optional[callable] = None,
        max_steps: int = 50,
        vocabulary: Optional[List[str]] = None,
    ):
        """
        Initialize DSL environment.

        Args:
            dsl_name: Name of DSL ('tinycalc', 'lexi', etc.)
            task_id: Task identifier
            reward_fn: Custom reward function (state, action, result) -> float
            max_steps: Maximum steps per episode
            vocabulary: List of valid tokens (auto-generated if None)
        """
        self.dsl_name = dsl_name
        self.task_id = task_id
        self.max_steps = max_steps
        self.current_step = 0

        # Get task definition
        self.task = self._load_task(task_id)
        self.expected_output = self.task.get("expected_output", "")

        # Build vocabulary (action space)
        if vocabulary is None:
            self.vocabulary = self._build_vocabulary()
        else:
            self.vocabulary = vocabulary

        self.action_space_size = len(self.vocabulary)

        # Current program state
        self.program = []
        self.done = False

        # Reward function
        if reward_fn is None:
            from tinydsl.rl.rewards.correctness_reward import CorrectnessReward

            self.reward_fn = CorrectnessReward(dsl_name)
        else:
            self.reward_fn = reward_fn

    def _load_task(self, task_id: str) -> Dict[str, Any]:
        """Load task from JSON."""
        import json
        from pathlib import Path

        # Find task file
        data_dir = Path(__file__).parent.parent.parent / "data"
        task_file = data_dir / f"{self.dsl_name}_tasks.json"

        if task_file.exists():
            with open(task_file) as f:
                tasks = json.load(f)
                task = next((t for t in tasks if t["id"] == task_id), None)
                if task:
                    return task

        # Fallback
        return {
            "id": task_id,
            "code": "",
            "expected_output": "",
            "description": f"Task {task_id}",
        }

    def _build_vocabulary(self) -> List[str]:
        """Build vocabulary from DSL grammar."""
        # DSL-specific vocabularies
        vocabs = {
            "tinycalc": [
                "define",
                "convert",
                "compute",
                "show",
                "base",
                "1",
                "2",
                "3",
                "5",
                "10",
                "flurb",
                "grobble",
                "zept",
                "quib",
                "voom",
                "=",
                "+",
                "-",
                "*",
                "/",
                "to",
                "in",
                "units",
                "\n",
            ],
            "lexi": [
                "say",
                "set",
                "remember",
                "recall",
                "repeat",
                "if",
                "is",
                "task",
                "call",
                "calc",
                "happy",
                "sad",
                "excited",
                '"Hello"',
                '"world"',
                '"Hi"',
                "{",
                "}",
                "\n",
            ],
            "gli": [
                "set",
                "draw",
                "repeat",
                "var",
                "define",
                "call",
                "color",
                "size",
                "circle",
                "square",
                "line",
                "red",
                "blue",
                "green",
                "orange",
                "x=",
                "y=",
                "cos",
                "sin",
                "$i",
                "{",
                "}",
                "\n",
            ],
            "tinysql": [
                "load",
                "table",
                "from",
                "filter",
                "where",
                "select",
                "sort",
                "by",
                "asc",
                "desc",
                "limit",
                "show",
                "tables",
                ">",
                "<",
                "=",
                "\n",
            ],
        }

        return vocabs.get(self.dsl_name, ["token"])

    def reset(self) -> np.ndarray:
        """
        Reset environment to initial state.

        Returns:
            Initial observation
        """
        self.program = []
        self.current_step = 0
        self.done = False
        return self._get_observation()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Take a step in the environment.

        Args:
            action: Index into vocabulary

        Returns:
            (observation, reward, done, info)
        """
        if self.done:
            raise RuntimeError("Episode is done. Call reset().")

        # Convert action to token
        token = self.vocabulary[action]
        self.program.append(token)
        self.current_step += 1

        # Check if done
        code = "".join(self.program)
        result = self._execute_program(code)

        # Calculate reward
        reward = self.reward_fn(
            state=self.program,
            action=token,
            result=result,
            expected=self.expected_output,
        )

        # Episode termination
        self.done = (
            self.current_step >= self.max_steps
            or result.get("success", False)
            or "\n" in token
            and len(self.program) > 10
        )

        observation = self._get_observation()

        info = {
            "current_code": code,
            "result": result,
            "expected": self.expected_output,
            "step": self.current_step,
        }

        return observation, reward, self.done, info

    def _execute_program(self, code: str) -> Dict[str, Any]:
        """Execute DSL program and return result."""
        try:
            # Use GenericDSLClient to execute
            from tinydsl.agent_tools.generic_dsl_client import GenericDSLClient

            client = GenericDSLClient()

            result = client.run(self.dsl_name, code)
            output = result.get("output", "")

            return {
                "success": output.strip() == self.expected_output.strip(),
                "output": output,
                "error": None,
            }
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}

    def _get_observation(self) -> np.ndarray:
        """
        Get current observation (state representation).

        Returns:
            Numpy array representing current state
        """
        # Simple one-hot encoding of last N tokens
        obs_size = 100  # Fixed observation size

        # One-hot encode program tokens
        obs = np.zeros(obs_size)

        for i, token in enumerate(self.program[-10:]):  # Last 10 tokens
            if token in self.vocabulary:
                token_idx = self.vocabulary.index(token)
                obs[i * 10 + (token_idx % 10)] = 1.0

        # Add metadata
        obs[-5] = self.current_step / self.max_steps  # Progress
        obs[-4] = len(self.program) / self.max_steps  # Program length
        obs[-3] = float(self.done)  # Done flag

        return obs

    def render(self) -> str:
        """Render current state as string."""
        code = "".join(self.program)
        return f"Step {self.current_step}/{self.max_steps}\n{code}"

    def get_action_mask(self) -> np.ndarray:
        """
        Get mask of valid actions in current state.

        Returns:
            Binary mask (1 = valid, 0 = invalid)
        """
        # For now, all actions are valid
        # Could add grammar-based constraints
        return np.ones(self.action_space_size)


def make_env(dsl_name: str, task_id: str, **kwargs) -> DSLEnv:
    """
    Factory function to create DSL environment.

    Args:
        dsl_name: DSL name
        task_id: Task identifier
        **kwargs: Additional arguments for DSLEnv

    Returns:
        Initialized environment
    """
    return DSLEnv(dsl_name, task_id, **kwargs)
