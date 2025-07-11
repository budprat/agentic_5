# ABOUTME: This file marks the tests directory as a Python package
# ABOUTME: Contains test configuration and shared test utilities

import pytest
from pathlib import Path
import sys

# Add src to path for imports in tests
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))