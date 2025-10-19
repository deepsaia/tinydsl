"""Tests for Gli DSL."""
import pytest
from tinydsl.gli.gli import GlintInterpreter


class TestGliV1:
    """Test Gli V1 features."""

    def test_gli_v1_initialization(self):
        """Test Gli V1 initializes correctly."""
        gli = GlintInterpreter(version='v1')
        assert gli.version == 'v1'

    def test_basic_shape(self, sample_gli_v1_code):
        """Test basic shape drawing."""
        gli = GlintInterpreter(version='v1')
        shapes = gli.parse(sample_gli_v1_code)
        assert len(shapes) >= 1
        assert shapes[0][0] == "circle"  # shape name

    def test_set_color(self):
        """Test setting color."""
        gli = GlintInterpreter(version='v1')
        code = "set color red\ndraw circle x=50 y=50"
        shapes = gli.parse(code)
        assert shapes[0][4] == "red"  # color

    def test_set_size(self):
        """Test setting size."""
        gli = GlintInterpreter(version='v1')
        code = "set size 20\ndraw square x=10 y=10"
        shapes = gli.parse(code)
        assert shapes[0][3] == 20.0  # size

    def test_repeat_block(self):
        """Test repeat block."""
        gli = GlintInterpreter(version='v1')
        code = "repeat 3 {\ndraw circle x=10 y=10\n}"
        shapes = gli.parse(code)
        assert len(shapes) == 3

    def test_math_expressions(self):
        """Test math in coordinates."""
        gli = GlintInterpreter(version='v1')
        code = "draw circle x=10+5 y=20*2"
        shapes = gli.parse(code)
        assert shapes[0][1] == 15.0  # x
        assert shapes[0][2] == 40.0  # y


class TestGliV2:
    """Test Gli V2 features."""

    def test_gli_v2_initialization(self):
        """Test Gli V2 initializes correctly."""
        gli = GlintInterpreter(version='v2')
        assert gli.version == 'v2'

    def test_variables(self, sample_gli_v2_code):
        """Test variable assignment and usage."""
        gli = GlintInterpreter(version='v2')
        shapes = gli.parse(sample_gli_v2_code)
        assert len(shapes) >= 1

    def test_conditionals(self):
        """Test if-else conditionals."""
        gli = GlintInterpreter(version='v2')
        code = """
var x = 50
if x > 40 {
    draw circle x=x y=50
}
"""
        shapes = gli.parse(code)
        assert len(shapes) == 1

    def test_functions(self):
        """Test function definition and call."""
        gli = GlintInterpreter(version='v2')
        code = """
define drawCircle(x, y) {
    draw circle x=x y=y
}
call drawCircle(50, 50)
"""
        shapes = gli.parse(code)
        assert len(shapes) >= 1

    def test_transforms(self):
        """Test transform operations."""
        gli = GlintInterpreter(version='v2')
        code = """
rotate 45
draw circle x=50 y=50
"""
        shapes = gli.parse(code)
        # V2 shapes have transform data
        assert len(shapes[0]) == 7  # includes rotation and transform matrix
