"""
Pytest configuration for crispr-offtarget-scanner tests.
Sets up required environment variables for testing.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set required environment variables for testing
os.environ.setdefault("AUDIT_SECRET_KEY", "test-audit-key-for-testing-only")
