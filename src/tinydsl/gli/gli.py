# src/tinydsl/gli/gli.py
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Optional, Union

from tinydsl.core.base_dsl import BaseDSL
from tinydsl.parser.lark_gli_parser import LarkGLIParser
from tinydsl.gli.renderers import PillowRenderer, BaseRenderer

# Support both v1 and v2 shape formats
Shape = Union[
    Tuple[str, float, float, float, str],
    Tuple[str, float, float, float, str, float, List],
]


class GlintInterpreter(BaseDSL):
    """
    GLI interpreter:
      - Parses & executes GLI via LarkGLIParser or V2 (with variables, conditionals, functions).
      - Always renders via Pillow for crisp, anti-aliased output.
      - Use version='v2' for enhanced features (variables, conditionals, functions, transforms)
    """

    def __init__(
        self,
        renderer: Optional[BaseRenderer] = None,
        accumulate: bool = False,
        version: str = "v1",  # 'v1' or 'v2'
        *,
        canvas_size: int = 768,
        supersample: int = 2,
        line_width: int = 2,
    ):
        # Choose parser version
        self._parser = LarkGLIParser(version=version)

        self.version = version
        self.shapes: List[Shape] = []
        self.accumulate = accumulate

        # Always use Pillow; allow overrides via kwargs
        self.renderer = renderer or PillowRenderer(
            canvas_size=canvas_size,
            supersample=supersample,
            line_width=line_width,
        )

    @property
    def name(self) -> str:
        """DSL identifier."""
        return "gli"

    @property
    def grammar_path(self) -> Path:
        """Path to Lark grammar file."""
        data_dir = Path(__file__).parent.parent / "data"
        return data_dir / "gli_grammar.lark"

    def parse(self, code: str) -> List[Shape]:
        """
        Parse a full GLI program into shapes. If accumulate=False (default),
        replaces the current buffer; otherwise appends.
        """
        shapes = self._parser.parse(code)
        if self.accumulate:
            self.shapes.extend(shapes)
        else:
            self.shapes = shapes
        return self.shapes

    def clear(self) -> None:
        """Drop any previously parsed shapes."""
        self.shapes = []

    def render(
        self,
        save: bool = False,
        open_after_save: bool = False,
        output_root: str = "output",
        name: str = "render",
        artifact_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Render current shapes using the Pillow renderer.
        Filenames are saved as {artifact_id}_{name}_{timestamp}.png when artifact_id is provided.
        """
        return self.renderer.render(
            self.shapes,
            save=save,
            open_after_save=open_after_save,
            output_root=output_root,
            name=name,
            artifact_id=artifact_id,
        )


if __name__ == "__main__":
    code = """
    set color red
    set size 5
    draw circle x=10 y=10
    repeat 3 {
        set color blue
        draw square x=20 + i*20 y=20
    }
    """
    gl = GlintInterpreter(canvas_size=768, supersample=2, line_width=2)
    gl.parse(code)
    gl.render(save=True, open_after_save=False, output_root="output", name="gli_demo")
