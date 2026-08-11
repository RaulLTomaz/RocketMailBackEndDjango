import os
from pathlib import Path

os.environ.setdefault("PYTHON_ENV", "test")
_env_test = Path(__file__).resolve().parent.parent / ".env.test"
if _env_test.exists():
    from dotenv import load_dotenv

    load_dotenv(_env_test, override=False)

if not os.getenv("DATABASE_URL") and os.getenv("DATABASE_URL_TEST"):
    os.environ["DATABASE_URL"] = os.environ["DATABASE_URL_TEST"]

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client(db):
    return APIClient()
