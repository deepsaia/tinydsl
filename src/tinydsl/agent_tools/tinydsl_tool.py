import requests
from typing import Optional, List, Dict


class TinyDSLTool:
    """
    A unified client for all TinyDSL backends.

    Supports: Gli (graphics), Lexi (text), TinyCalc (units), TinySQL (queries)
    """

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

    def run_gli(
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
    # 🧮 TINYCALC (unit conversion DSL)
    # ==========================

    def run_tinycalc(self, code: str):
        """Run TinyCalc DSL code."""
        url = f"{self.base_url}/tinycalc/run"
        resp = requests.post(url, json={"code": code}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def run_tinycalc_task(self, task_id: str):
        """Run a benchmark TinyCalc task by ID."""
        url = f"{self.base_url}/tinycalc/task"
        resp = requests.post(url, json={"task_id": task_id}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def eval_tinycalc_outputs(self, results: List[Dict[str, str]]):
        """Evaluate TinyCalc outputs."""
        url = f"{self.base_url}/tinycalc/eval"
        resp = requests.post(url, json={"results": results}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    # ==========================
    # 🗃️ TINYSQL (query DSL)
    # ==========================

    def run_tinysql(self, code: str):
        """Run TinySQL DSL code."""
        url = f"{self.base_url}/tinysql/run"
        resp = requests.post(url, json={"code": code}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def run_tinysql_task(self, task_id: str):
        """Run a benchmark TinySQL task by ID."""
        url = f"{self.base_url}/tinysql/task"
        resp = requests.post(url, json={"task_id": task_id}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def eval_tinysql_outputs(self, results: List[Dict[str, str]]):
        """Evaluate TinySQL outputs."""
        url = f"{self.base_url}/tinysql/eval"
        resp = requests.post(url, json={"results": results}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    # ==========================
    # 🌐 Generic DSL Operations
    # ==========================

    def list_all_dsls(self):
        """List all available DSLs in the system."""
        url = f"{self.base_url.rstrip('/api')}/dsls"
        resp = requests.get(url)
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

    # 🧮 TinyCalc test
    print("\n🧮 Running TinyCalc test...")
    calc_code = """
    define 1 flurb = 3.7 grobbles
    define 1 grobble = 2.1 zepts
    convert 10 flurbs to zepts
    """
    calc_result = tool.run_tinycalc(calc_code)
    print("TinyCalc output:", calc_result["output"])

    # 🗃️ TinySQL test
    print("\n🗃️ Running TinySQL test...")
    sql_code = """
    show tables
    """
    sql_result = tool.run_tinysql(sql_code)
    print("TinySQL output:", sql_result["output"])

    # 🌐 List all DSLs
    print("\n🌐 Available DSLs:")
    dsls = tool.list_all_dsls()
    print("DSLs:", dsls)
