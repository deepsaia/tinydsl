import requests
from typing import Optional


class GlintDSLTool:
    """A lightweight client for the Glint DSL FastAPI backend."""

    def __init__(self, base_url: str = "http://localhost:8008/api"):
        self.base_url = base_url.rstrip("/")
        # Note: Ensure the API server is running before using this tool.
        # Ensure that the examples file is accessible by the server.

    def list_examples(self, tag: Optional[str] = None):
        """List available DSL examples."""
        url = f"{self.base_url}/examples"
        params = {"tag": tag} if tag else {}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def run_example(
        self, example_id: str, save: bool = True, open_after_save: bool = False
    ):
        """Run a saved DSL example by ID."""
        url = f"{self.base_url}/run_example/{example_id}"
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
        """Run arbitrary DSL code."""
        url = f"{self.base_url}/run"
        data = {
            "code": code,
            "name": name,
            "save": save,
            "open_after_save": open_after_save,
        }
        resp = requests.post(url, json=data)
        resp.raise_for_status()
        return resp.json()


if __name__ == "__main__":
    tool = GlintDSLTool()
    # List all examples
    examples = tool.list_examples()
    print(f"Found {len(examples)} examples")

    # Run a predefined example
    result = tool.run_example("021")  # polar spiral
    print("Generated:", result["output_path"])

    # Run custom DSL code
    code = """
    set color green
    repeat 12 {
        set size 2+$i
        draw circle x=cos($i*30)*$i*8 y=sin($i*30)*$i*8
    }
    """
    output = tool.run_code(code, name="agent_generated_spiral")
    print("Custom render saved at:", output["path"])
