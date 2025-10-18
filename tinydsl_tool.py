import requests
from typing import Optional, List, Dict


class TinyDSLTool:
    """A unified client for the Glint and Lexi DSL FastAPI backend."""

    def __init__(self, base_url: str = "http://localhost:8008/api"):
        self.base_url = base_url.rstrip("/")
        # Ensure the FastAPI backend is running before using.

    # ==========================
    # 🔹 GLINT (visual DSL)
    # ==========================
    def list_examples(self, tag: Optional[str] = None):
        """List available Glint examples."""
        url = f"{self.base_url}/gli/examples"
        params = {"tag": tag} if tag else {}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def run_example(
        self, example_id: str, save: bool = True, open_after_save: bool = False
    ):
        """Run a predefined Glint example by ID."""
        url = f"{self.base_url}/gli/run_example/{example_id}"
        params = {"save": save, "open_after_save": open_after_save}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def run_code(
        self,
        code: str,
        name: Optional[str] = "agent_run",
        save: bool = True,
        open_after_save: bool = False,
    ):
        """Run arbitrary Glint DSL code."""
        url = f"{self.base_url}/gli/run"
        data = {
            "code": code,
            "name": name,
            "save": save,
            "open_after_save": open_after_save,
        }
        resp = requests.post(url, json=data)
        resp.raise_for_status()
        return resp.json()

    # ==========================
    # 🔸 LEXI (text DSL)
    # ==========================

    def run_lexi(
        self,
        code: str,
        randomness: float = 0.1,
        seed: Optional[int] = None,
    ):
        """Run arbitrary Lexi DSL code."""
        url = f"{self.base_url}/lexi/run"
        payload = {"code": code, "randomness": randomness}
        if seed is not None:
            payload["seed"] = seed
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def run_lexi_task(self, task_id: str):
        """Run a benchmark Lexi task by ID."""
        url = f"{self.base_url}/lexi/task"
        resp = requests.post(url, json={"task_id": task_id}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def eval_lexi_outputs(self, results: List[Dict[str, str]]):
        """Evaluate Lexi outputs against benchmark expected results."""
        url = f"{self.base_url}/lexi/eval"
        resp = requests.post(url, json={"results": results}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    # ==========================
    # 🧠 Memory Management
    # ==========================

    def get_memory(self):
        """Retrieve Lexi persistent memory contents."""
        url = f"{self.base_url}/lexi/memory"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def set_memory(self, key: str, value: str):
        """Set a key-value pair in Lexi memory."""
        url = f"{self.base_url}/lexi/memory/set"
        resp = requests.post(url, json={key: value})
        resp.raise_for_status()
        return resp.json()

    def clear_memory(self):
        """Clear Lexi persistent memory."""
        url = f"{self.base_url}/lexi/memory/clear"
        resp = requests.post(url)
        resp.raise_for_status()
        return resp.json()


# ==========================
# 🔧 Example Usage
# ==========================
if __name__ == "__main__":
    tool = TinyDSLTool()

    # 🖼️ Glint test
    print("🎨 Running Glint test...")
    glint_code = """
    set color orange
    repeat 6 {
        set size 5+$i
        draw circle x=$i*8 y=$i*5
    }
    """
    res = tool.run_code(glint_code, name="spiral_test")
    print("Glint output:", res)

    # 💬 Lexi test
    print("\n💬 Running Lexi test...")
    lexi_code = """
    set mood happy
    say "Hello!"
    repeat 2 {
        say "Stay awesome!"
    }
    """
    result = tool.run_lexi(lexi_code)
    print("Lexi output:", result["output"])

    # 🎯 Lexi task example
    task = tool.run_lexi_task("005")
    print("Task result:", task)

    # 🧠 Memory persistence test
    tool.set_memory("user_name", "John Arthur")
    print("Memory:", tool.get_memory())
    
    # tool.clear_memory()
    # print("Memory cleared:", tool.get_memory())
