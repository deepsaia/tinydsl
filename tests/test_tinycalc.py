"""Tests for TinyCalc DSL."""
import pytest
from tinydsl.tinycalc.tinycalc import TinyCalcInterpreter


class TestTinyCalc:
    """Test TinyCalc DSL."""

    def test_tinycalc_initialization(self):
        """Test TinyCalc initializes correctly."""
        calc = TinyCalcInterpreter()
        assert calc.name == "tinycalc"

    def test_simple_conversion(self, sample_tinycalc_code):
        """Test simple unit conversion."""
        calc = TinyCalcInterpreter()
        result = calc.execute(sample_tinycalc_code)
        assert "grobble" in result

    def test_define_and_convert(self):
        """Test defining units and converting."""
        calc = TinyCalcInterpreter()
        code = """
define 1 flurb = 3 zept
convert 2 flurb to zept
"""
        result = calc.execute(code)
        assert "6.0 zept" in result

    def test_chained_conversion(self):
        """Test multi-hop conversion."""
        calc = TinyCalcInterpreter()
        code = """
define 1 flurb = 2 grobble
define 1 grobble = 3 zept
convert 1 flurb to zept
"""
        result = calc.execute(code)
        assert "6.0 zept" in result

    def test_arithmetic_in_conversion(self):
        """Test arithmetic operations in conversion."""
        calc = TinyCalcInterpreter()
        code = """
define 1 flurb = 5 grobble
compute 2 * 3 flurb in grobble
"""
        result = calc.execute(code)
        assert "grobble" in result

    def test_invalid_syntax(self):
        """Test handling of invalid syntax."""
        calc = TinyCalcInterpreter()
        code = "invalid syntax here"
        try:
            result = calc.execute(code)
            # If it returns a result, check for error message
            assert "error" in result.lower()
        except (ValueError, Exception) as e:
            # Or it should raise an error
            assert "error" in str(e).lower() or "unexpected" in str(e).lower()
