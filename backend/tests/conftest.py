import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from database import engine

# The suite truncates every table between tests, so refuse to run against
# anything that isn't clearly a throwaway test database. This must run before
# importing main, whose import-time create_all would already touch the DB.
if not (engine.url.database or "").endswith("_test"):
    raise RuntimeError(
        f"Refusing to run tests against database {engine.url.database!r}; "
        "point DATABASE_URL at a database whose name ends in '_test'."
    )

from main import app  # noqa: E402


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
