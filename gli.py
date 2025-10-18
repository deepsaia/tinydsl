import math
import re
import os
import datetime
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


class GlintInterpreter:
    """Enhanced TinyDSL interpreter with repeat indexing and expression parsing."""

    def __init__(self):
        self.color = "black"
        self.size = 10
        self.shapes = []

    def parse(self, code: str, repeat_index: int = 0):
        """Parse and execute the TinyDSL code."""
        lines = [line.strip() for line in code.splitlines() if line.strip()]
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("set"):
                _, param, value = line.split(maxsplit=2)
                value = self._eval_expr(value, repeat_index)
                if param == "size":
                    self.size = float(value)
                else:
                    setattr(self, param, value)
            elif line.startswith("draw"):
                _, shape, *params = line.split()
                expr_text = " ".join(params)
                matches = re.findall(r"(\w+)=([-\w+*/.$()]+)", expr_text)
                kwargs = {
                    k: float(self._eval_expr(v, repeat_index)) for k, v in matches
                }
                self.draw(shape, **kwargs)
            elif line.startswith("repeat"):
                count = int(line.split()[1])
                block = []
                i += 1
                while i < len(lines) and not lines[i].startswith("}"):
                    block.append(lines[i])
                    i += 1
                block_code = "\n".join(block)
                for idx in range(count):
                    self.parse(block_code, repeat_index=idx)
            i += 1

    def _eval_expr(self, expr: str, i: int):
        """Safely evaluate numeric expressions supporting $i and math functions."""
        expr = expr.replace("$i", str(i))

        # Allowlisted safe functions and constants from math
        safe_env = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "pi": math.pi,
            "e": math.e,
            "abs": abs,
            "min": min,
            "max": max,
        }

        try:
            return eval(expr, {"__builtins__": {}}, safe_env)
        except Exception:
            # fallback for non-numeric values like color strings
            return expr

    def draw(self, shape, **kwargs):
        x, y = kwargs.get("x", 0), kwargs.get("y", 0)
        self.shapes.append((shape, x, y, self.size, self.color))

    def render(
        self, save=False, open_after_save=False, output_root="outputs", name="render"
    ):
        fig, ax = plt.subplots()
        for shape, x, y, size, color in self.shapes:
            if shape == "circle":
                ax.add_patch(plt.Circle((x, y), size, color=color, fill=False))
            elif shape == "square":
                ax.add_patch(
                    plt.Rectangle(
                        (x - size / 2, y - size / 2),
                        size,
                        size,
                        color=color,
                        fill=False,
                    )
                )
            elif shape == "line":
                ax.plot([x, x + size], [y, y], color=color)
        ax.set_aspect("equal")
        ax.autoscale()
        plt.axis("off")

        if save:
            os.makedirs(output_root, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(output_root, f"{name}_{timestamp}.png")
            plt.savefig(file_path, bbox_inches="tight", dpi=300)
            plt.close(fig)
            if open_after_save:
                import webbrowser

                webbrowser.open(f"file://{os.path.abspath(file_path)}")
            return file_path
        else:
            plt.show()


if __name__ == "__main__":
    # Example usage (standalone mode)
    code = """
    set color red
    set size 5
    draw circle x=10 y=10
    repeat 3 {
        set color blue
        draw square x=20+$i*20 y=20
    }
    """
    gl = GlintInterpreter()
    gl.parse(code)
    gl.render()
