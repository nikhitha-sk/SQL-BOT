import os
import tempfile

# Use a throwaway data folder so tests never touch the real databases.
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="sqlbot-test-")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
