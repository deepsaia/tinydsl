"""Tests for Lexi DSL."""

import pytest
from tinydsl.lexi.lexi import LexiInterpreter


class TestLexiV1:
    """Test Lexi V1 features."""

    def test_lexi_v1_initialization(self):
        """Test Lexi V1 initializes correctly."""
        lexi = LexiInterpreter(version="v1")
        assert lexi.version == "v1"

    def test_say_statement(self, sample_lexi_v1_code):
        """Test say statement."""
        lexi = LexiInterpreter(version="v1")
        lexi.parse(sample_lexi_v1_code)
        output = lexi.render()
        assert "Hello" in output
        assert "World" in output

    def test_set_statement(self):
        """Test set statement."""
        lexi = LexiInterpreter(version="v1")
        code = 'set name "Alice"'
        lexi.parse(code)
        # Should execute without error
        assert lexi.render() is not None

    def test_remember_and_recall(self):
        """Test remember and recall."""
        lexi = LexiInterpreter(version="v1")
        code = """
remember name = "Alice"
recall name
"""
        lexi.parse(code)
        output = lexi.render()
        assert "Alice" in output

    def test_if_block(self):
        """Test if conditional."""
        lexi = LexiInterpreter(version="v1")
        code = """
set mood "happy"
if mood is happy {
    say "I'm happy!"
}
"""
        lexi.parse(code)
        output = lexi.render()
        assert "happy" in output.lower()

    def test_repeat_block(self):
        """Test repeat loop."""
        lexi = LexiInterpreter(version="v1")
        code = """
repeat 3 {
    say "Hello"
}
"""
        lexi.parse(code)
        output = lexi.render()
        # Check that "Hello" appears in output (Lexi may format differently)
        assert "Hello" in output
        assert output is not None

    def test_task_definition_and_call(self):
        """Test task definition and calling."""
        lexi = LexiInterpreter(version="v1")
        code = """
task greet {
    say "Hello!"
}
call greet
"""
        lexi.parse(code)
        output = lexi.render()
        assert "Hello!" in output


class TestLexiV2:
    """Test Lexi V2 features."""

    def test_lexi_v2_initialization(self):
        """Test Lexi V2 initializes correctly."""
        lexi = LexiInterpreter(version="v2")
        assert lexi.version == "v2"

    def test_string_operations(self, sample_lexi_v2_code):
        """Test string operations."""
        lexi = LexiInterpreter(version="v2")
        lexi.parse(sample_lexi_v2_code)
        # Should execute without error
        assert lexi.render() is not None

    def test_upper_operation(self):
        """Test upper case operation."""
        lexi = LexiInterpreter(version="v2")
        code = """
set name "alice"
upper name as result
"""
        lexi.parse(code)
        # Should not raise error
        assert True

    def test_length_operation(self):
        """Test length operation."""
        lexi = LexiInterpreter(version="v2")
        code = """
set text "Hello"
length text as len
"""
        lexi.parse(code)
        # Should not raise error
        assert True

    def test_list_operations(self):
        """Test list creation and operations."""
        lexi = LexiInterpreter(version="v2")
        code = """
list items = ["a", "b", "c"]
get items 0 as first
"""
        lexi.parse(code)
        # Should not raise error
        assert True

    @pytest.mark.skip(reason="foreach loop not yet implemented in Lexi V2 grammar")
    def test_foreach_loop(self):
        """Test foreach loop."""
        lexi = LexiInterpreter(version="v2")
        code = """
list items = ["a", "b", "c"]
foreach item in items {
    say item
}
"""
        lexi.parse(code)
        # Should not raise error
        assert True
