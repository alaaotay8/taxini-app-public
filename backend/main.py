import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from app import app
__all__ = ["app"]  # This is to ignore language server warning about unused imports
