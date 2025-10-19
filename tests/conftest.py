"""Pytest configuration and fixtures."""
import pytest
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_tinycalc_code():
    """Sample TinyCalc code for testing."""
    return """
define 1 flurb = 2 grobble
convert 5 flurb to grobble
"""


@pytest.fixture
def sample_gli_v1_code():
    """Sample Gli V1 code for testing."""
    return """
set color red
set size 10
draw circle x=50 y=50
"""


@pytest.fixture
def sample_gli_v2_code():
    """Sample Gli V2 code for testing."""
    return """
var x = 100
set color blue
draw circle x=x y=50
"""


@pytest.fixture
def sample_lexi_v1_code():
    """Sample Lexi V1 code for testing."""
    return """
say "Hello"
say "World"
"""


@pytest.fixture
def sample_lexi_v2_code():
    """Sample Lexi V2 code for testing."""
    return """
set name "Alice"
upper name as result
length result as len
"""
