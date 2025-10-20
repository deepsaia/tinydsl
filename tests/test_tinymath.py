"""Tests for TinyMath DSL."""

import pytest
from tinydsl.tinymath.tinymath import TinyMathInterpreter


class TestTinyMath:
    """Test TinyMath DSL."""

    def test_tinymath_initialization(self):
        """Test TinyMath initializes correctly."""
        math_interp = TinyMathInterpreter()
        assert math_interp.name == "tinymath"

    def test_simple_addition(self):
        """Test basic addition."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("2 + 3")
        output = math_interp.render()
        assert "5.0" in output

    def test_multiplication(self):
        """Test multiplication."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("4 * 5")
        output = math_interp.render()
        assert "20.0" in output

    def test_division(self):
        """Test division."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("20 / 4")
        output = math_interp.render()
        assert "5.0" in output

    def test_subtraction(self):
        """Test subtraction."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("10 - 3")
        output = math_interp.render()
        assert "7.0" in output

    def test_operator_precedence(self):
        """Test order of operations."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("2 + 3 * 4")
        output = math_interp.render()
        assert "14.0" in output

    def test_parentheses(self):
        """Test parentheses override precedence."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("(2 + 3) * 4")
        output = math_interp.render()
        assert "20.0" in output

    def test_variable_assignment(self):
        """Test variable assignment."""
        math_interp = TinyMathInterpreter()
        code = "x = 10\nx"
        math_interp.parse(code)
        output = math_interp.render()
        assert "x = 10.0" in output
        assert "10.0" in output

    def test_variable_arithmetic(self):
        """Test arithmetic with variables."""
        math_interp = TinyMathInterpreter()
        code = "x = 5\ny = 3\nx + y"
        math_interp.parse(code)
        output = math_interp.render()
        assert "8.0" in output

    def test_sqrt_function(self):
        """Test square root function."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("sqrt(16)")
        output = math_interp.render()
        assert "4.0" in output

    def test_power_operator(self):
        """Test exponentiation operator."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("2 ^ 8")
        output = math_interp.render()
        assert "256.0" in output

    def test_abs_function(self):
        """Test absolute value function."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("abs(-10)")
        output = math_interp.render()
        assert "10.0" in output

    def test_max_function(self):
        """Test max function."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("max(3, 7, 2, 9, 1)")
        output = math_interp.render()
        assert "9.0" in output

    def test_min_function(self):
        """Test min function."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("min(8, 3, 12, 1, 5)")
        output = math_interp.render()
        assert "1.0" in output

    def test_floor_function(self):
        """Test floor function."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("floor(3.7)")
        output = math_interp.render()
        assert "3" in output

    def test_ceil_function(self):
        """Test ceil function."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("ceil(3.2)")
        output = math_interp.render()
        assert "4" in output

    def test_modulo(self):
        """Test modulo operator."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("17 % 5")
        output = math_interp.render()
        assert "2.0" in output

    def test_negative_numbers(self):
        """Test negative unary operator."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("-5 + 10")
        output = math_interp.render()
        assert "5.0" in output

    def test_complex_expression(self):
        """Test complex multi-operation expression."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("(10 + 5) * 2 - 3")
        output = math_interp.render()
        assert "27.0" in output

    def test_pythagorean_theorem(self):
        """Test Pythagorean theorem calculation."""
        math_interp = TinyMathInterpreter()
        code = "a = 3\nb = 4\nsqrt(a^2 + b^2)"
        math_interp.parse(code)
        output = math_interp.render()
        assert "5.0" in output

    def test_sin_function(self):
        """Test sine function."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("sin(0)")
        output = math_interp.render()
        assert "0.0" in output

    def test_cos_function(self):
        """Test cosine function."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("cos(0)")
        output = math_interp.render()
        assert "1.0" in output

    def test_comparison_equal(self):
        """Test equality comparison."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("5 == 5")
        output = math_interp.render()
        assert "1.0" in output

    def test_comparison_less_than(self):
        """Test less than comparison."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("3 < 7")
        output = math_interp.render()
        assert "1.0" in output

    def test_comparison_greater_than(self):
        """Test greater than comparison."""
        math_interp = TinyMathInterpreter()
        math_interp.parse("10 > 5")
        output = math_interp.render()
        assert "1.0" in output

    def test_show_variable(self):
        """Test show statement."""
        math_interp = TinyMathInterpreter()
        code = "x = 42\nshow x"
        math_interp.parse(code)
        output = math_interp.render()
        assert "x = 42.0" in output

    def test_invalid_syntax(self):
        """Test error handling for invalid syntax."""
        math_interp = TinyMathInterpreter()
        with pytest.raises(ValueError):
            math_interp.parse("2 +")  # Incomplete expression

    def test_undefined_variable(self):
        """Test error handling for undefined variable."""
        math_interp = TinyMathInterpreter()
        with pytest.raises(ValueError):
            math_interp.parse("undefined_var + 5")

    def test_division_by_zero(self):
        """Test error handling for division by zero."""
        math_interp = TinyMathInterpreter()
        with pytest.raises(ValueError):
            math_interp.parse("10 / 0")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
