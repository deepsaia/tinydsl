# src/tinydsl/gli/renderers.py
from __future__ import annotations
import os
import datetime
import re
from typing import List, Tuple, Literal, Optional

# shape tuple: (shape, x, y, size, color)
Shape = Tuple[str, float, float, float, str]

def _slug(s: str) -> str:
    s = s.strip()
    # allow alnum, dash, underscore; collapse spaces to underscore
    s = re.sub(r"\s+", "_", s)
    return re.sub(r"[^A-Za-z0-9_\-]+", "", s)

def _build_filename(artifact_id: Optional[str], name: Optional[str]) -> str:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    parts = []
    if artifact_id:
        parts.append(_slug(artifact_id))
    if name:
        parts.append(_slug(name))
    parts.append(ts)
    return "_".join(parts) + ".png"


class BaseRenderer:
    #pylint: disable=too-few-public-methods, unused-argument
    def render(
        self,
        shapes: List[Shape],
        save: bool = False,
        open_after_save: bool = False,
        output_root: str = "output",
        name: str = "render",
        artifact_id: Optional[str] = None,
    ) -> Optional[str]:
        raise NotImplementedError

class MatplotlibRenderer(BaseRenderer):
    def __init__(self, dpi: int = 300):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        self.plt = plt
        self.dpi = dpi

    def render(self, shapes, save=False, open_after_save=False, output_root="output", name="render", artifact_id: Optional[str] = None,) -> Optional[str]:
        plt = self.plt
        fig, ax = plt.subplots()
        for shape, x, y, size, color in shapes:
            if shape == "circle":
                ax.add_patch(plt.Circle((x, y), size, color=color, fill=False))
            elif shape == "square":
                ax.add_patch(plt.Rectangle((x - size/2, y - size/2), size, size, color=color, fill=False))
            elif shape == "line":
                ax.plot([x, x+size], [y, y], color=color)
        ax.set_aspect("equal")
        ax.autoscale()
        plt.axis("off")

        if save:
            os.makedirs(output_root, exist_ok=True)
            fname = _build_filename(artifact_id, name)  # << use new pattern
            path = os.path.join(output_root, fname)
            plt.savefig(path, bbox_inches="tight", dpi=self.dpi)
            plt.close(fig)
            if open_after_save:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(path)}")
            return path
        else:
            plt.show()
            return None

class PillowRenderer(BaseRenderer):
    """
    Crisp output via supersampling.
    Logical coords are same as matplotlib path (so no DSL change).
    """
    def __init__(self, canvas_size: int = 512, bg="white", line_width: int = 2, supersample: int = 2):
        from PIL import Image, ImageDraw, ImageOps
        self.Image = Image
        self.ImageDraw = ImageDraw
        self.ImageOps = ImageOps
        self.canvas_size = canvas_size
        self.bg = bg
        self.line_width = line_width
        self.supersample = supersample

    def _bounds(self, shapes: List[Shape]):
        # compute min/max to auto-fit like mpl.autoscale
        xs, ys = [], []
        for s, x, y, size, _ in shapes:
            if s == "circle":
                xs += [x - size, x + size]
                ys += [y - size, y + size]
            elif s == "square":
                xs += [x - size/2, x + size/2]
                ys += [y - size/2, y + size/2]
            elif s == "line":
                xs += [x, x + size]
                ys += [y, y]
        if not xs:
            return (0, 0, 1, 1)
        pad = 5
        return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)

    def render(self, shapes, save=False, open_after_save=False, output_root="output", name="render", artifact_id: Optional[str] = None,) -> Optional[str]:
        if not shapes:
            # create blank canvas
            w = h = self.canvas_size
            img = self.Image.new("RGB", (w, h), self.bg)
        else:
            xmin, ymin, xmax, ymax = self._bounds(shapes)
            width = xmax - xmin
            height = ymax - ymin
            # maintain aspect and target size
            target = self.canvas_size
            scale = (target / max(width, height)) * self.supersample
            w = max(1, int(width * scale))
            h = max(1, int(height * scale))
            img = self.Image.new("RGB", (w, h), self.bg)
            draw = self.ImageDraw.Draw(img)

            def tx(x): return int((x - xmin) * scale)
            def ty(y): 
                # flip y to match mpl typical Cartesian notion
                return int((ymax - y) * scale)

            lw = max(1, int(self.line_width * self.supersample))

            for shape, x, y, size, color in shapes:
                if shape == "circle":
                    r = size * scale
                    bbox = [tx(x) - r, ty(y) - r, tx(x) + r, ty(y) + r]
                    draw.ellipse(bbox, outline=color, width=lw)
                elif shape == "square":
                    half = (size/2) * scale
                    bbox = [tx(x)-half, ty(y)-half, tx(x)+half, ty(y)+half]
                    draw.rectangle(bbox, outline=color, width=lw)
                elif shape == "line":
                    draw.line([(tx(x), ty(y)), (tx(x+size), ty(y))], fill=color, width=lw)

            # downsample for anti-aliased crispness
            if self.supersample > 1:
                img = img.resize((int(w/self.supersample), int(h/self.supersample)), self.Image.LANCZOS)

        if save:
            os.makedirs(output_root, exist_ok=True)
            fname = _build_filename(artifact_id, name)
            path = os.path.join(output_root, fname)
            img.save(path, format="PNG")
            if open_after_save:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(path)}")
            return path
        else:
            # For CLI use you could show(); API should always save.
            return None
