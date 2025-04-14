import sys
import os

# Determine the repository root (where conftest.py lives)
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
# Add the "src" folder (which contains riksbank_mcp) to Python's module search path
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
