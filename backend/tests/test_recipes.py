import uuid


def test_create_recipe_defaults(client):
    res = client.post("/api/recipes", json={"title": "Pasta"})
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "Pasta"
    assert body["status"] == "want_to_try"
    assert body["cook_count"] == 0
    assert body["rating"] is None
    assert body["tags"] == []
    assert body["latest_note"] is None


def test_create_recipe_validation(client):
    assert client.post("/api/recipes", json={}).status_code == 422
    too_high = client.post("/api/recipes", json={"title": "x", "rating": 6})
    assert too_high.status_code == 422
    bad_status = client.post("/api/recipes", json={"title": "x", "status": "maybe"})
    assert bad_status.status_code == 422


def test_get_recipe_and_404(client, make_recipe):
    recipe = make_recipe(title="Soup")
    assert client.get(f"/api/recipes/{recipe['id']}").json()["title"] == "Soup"
    assert client.get(f"/api/recipes/{uuid.uuid4()}").status_code == 404


def test_patch_only_changes_supplied_fields(client, make_recipe):
    recipe = make_recipe(title="Curry", rating=3, youtube_url="https://example.com")

    res = client.patch(f"/api/recipes/{recipe['id']}", json={"status": "tried", "cook_count": 2})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "tried"
    assert body["cook_count"] == 2
    assert body["title"] == "Curry"
    assert body["rating"] == 3
    assert body["youtube_url"] == "https://example.com"


def test_patch_can_clear_a_field(client, make_recipe):
    recipe = make_recipe(rating=4)
    res = client.patch(f"/api/recipes/{recipe['id']}", json={"rating": None})
    assert res.json()["rating"] is None


def test_delete_recipe(client, make_recipe):
    recipe = make_recipe()
    assert client.delete(f"/api/recipes/{recipe['id']}").status_code == 204
    assert client.get(f"/api/recipes/{recipe['id']}").status_code == 404
    assert client.delete(f"/api/recipes/{recipe['id']}").status_code == 404


def test_list_filters_by_status(client, make_recipe):
    make_recipe(title="A", status="tried")
    make_recipe(title="B", status="want_to_try")

    tried = client.get("/api/recipes", params={"status": "tried"}).json()
    assert [r["title"] for r in tried] == ["A"]


def test_list_search_is_case_insensitive_substring(client, make_recipe):
    make_recipe(title="Kaju Paneer Pulav")
    make_recipe(title="Tacos")

    found = client.get("/api/recipes", params={"q": "paneer"}).json()
    assert [r["title"] for r in found] == ["Kaju Paneer Pulav"]


def test_list_filters_by_tag_name(client, make_recipe, make_tag):
    italian = make_tag("italian")
    pasta = make_recipe(title="Pasta")
    make_recipe(title="Tacos")
    client.post(f"/api/recipes/{pasta['id']}/tags/{italian['id']}")

    found = client.get("/api/recipes", params={"tag": "italian"}).json()
    assert [r["title"] for r in found] == ["Pasta"]


def test_list_is_sorted_by_title(client, make_recipe):
    for title in ["Charlie", "Alpha", "Bravo"]:
        make_recipe(title=title)
    titles = [r["title"] for r in client.get("/api/recipes").json()]
    assert titles == ["Alpha", "Bravo", "Charlie"]


def test_list_includes_latest_note(client, make_recipe):
    recipe = make_recipe()
    client.post(f"/api/recipes/{recipe['id']}/notes", json={"content": "less salt"})

    listed = client.get("/api/recipes").json()
    assert listed[0]["latest_note"] == "less salt"
