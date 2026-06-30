import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("BACKEND_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("BACKEND_DATABASE_URL", "sqlite:///./test_shared.db")
