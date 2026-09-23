from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from database import engine

# The suite truncates every table between tests, so refuse to run against
# anything that isn't clearly a throwaway test database.
if not (engine.url.database or "").endswith("_test"):
    raise RuntimeError(
        f"Refusing to run tests against database {engine.url.database!r}; "
        "point DATABASE_URL at a database whose name ends in '_test'."
    )

from main import app  # noqa: E402


@pytest.fixture(scope="session")
def alembic_cfg():
    return Config(str(Path(__file__).resolve().parent.parent / "alembic.ini"))


@pytest.fixture(scope="session", autouse=True)
def migrated_schema(alembic_cfg):
    # Build the schema the same way production does, so migrations are tested too.
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(autouse=True)
def clean_db():
    yield
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE notes, recipe_tags, tags, recipes CASCADE"))


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def make_recipe(client):
    def _make(**overrides):
        payload = {"title": "Test Dish", **overrides}
        res = client.post("/api/recipes", json=payload)
        assert res.status_code == 201, res.text
        return res.json()

    return _make


@pytest.fixture
def make_tag(client):
    def _make(name="italian", type="cuisine"):
        res = client.post("/api/tags", json={"name": name, "type": type})
        assert res.status_code == 201, res.text
        return res.json()

    return _make
