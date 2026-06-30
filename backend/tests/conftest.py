import os
import sys

# Add the backend/ directory (for `from app...` style imports if used) and the
# workspace root (for `from backend.app...` style imports used in the tests)
# to sys.path. Pytest's default rootdir makes only one of these discoverable,
# so we add both explicitly to keep tests runnable regardless of invocation.
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_TESTS_DIR)
_WORKSPACE_ROOT = os.path.dirname(_BACKEND_DIR)
for _p in (_BACKEND_DIR, _WORKSPACE_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

os.environ.setdefault("BACKEND_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("BACKEND_DATABASE_URL", "sqlite:///./test_shared.db")
