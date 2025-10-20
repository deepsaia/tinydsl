"""Pytest configuration and fixtures."""

import pytest
import sys
import os
import shutil
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session", autouse=True)
def setup_memory_directory():
    """Create memory directory before tests and cleanup in CI after tests."""
    # Get project root (parent of tests directory)
    project_root = Path(__file__).parent.parent
    memory_dir = project_root / "memory"

    # Ensure memory directory exists
    memory_dir.mkdir(exist_ok=True)

    # Create empty lexi_memory.json if it doesn't exist
    lexi_memory_file = memory_dir / "lexi_memory.json"
    if not lexi_memory_file.exists():
        lexi_memory_file.write_text("{}")

    yield

    # Cleanup only in CI environment (GitHub Actions)
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        if memory_dir.exists():
            shutil.rmtree(memory_dir)


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
