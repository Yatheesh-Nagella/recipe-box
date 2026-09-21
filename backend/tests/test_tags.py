import uuid


def test_create_and_list_tags(client, make_tag):
    make_tag("italian", "cuisine")
    make_tag("garlic", "ingredient")

    tags = client.get("/api/tags").json()
    assert [t["name"] for t in tags] == ["garlic", "italian"]


def test_list_tags_filtered_by_type(client, make_tag):
    make_tag("italian", "cuisine")
    make_tag("garlic", "ingredient")

    cuisines = client.get("/api/tags", params={"type": "cuisine"}).json()
    assert [t["name"] for t in cuisines] == ["italian"]


def test_duplicate_tag_name_conflicts(client, make_tag):
    make_tag("italian")
    res = client.post("/api/tags", json={"name": "italian", "type": "ingredient"})
    assert res.status_code == 409


def test_invalid_tag_type_rejected(client):
    res = client.post("/api/tags", json={"name": "x", "type": "vibe"})
    assert res.status_code == 422


def test_get_and_delete_tag(client, make_tag):
    tag = make_tag()
    assert client.get(f"/api/tags/{tag['id']}").json()["name"] == "italian"
    assert client.delete(f"/api/tags/{tag['id']}").status_code == 204
    assert client.get(f"/api/tags/{tag['id']}").status_code == 404
    assert client.get(f"/api/tags/{uuid.uuid4()}").status_code == 404


def test_attach_tag_shows_on_recipe(client, make_recipe, make_tag):
    recipe = make_recipe()
    tag = make_tag()

    res = client.post(f"/api/recipes/{recipe['id']}/tags/{tag['id']}")
    assert res.status_code == 200
    assert [t["name"] for t in res.json()["tags"]] == ["italian"]


def test_attach_is_idempotent(client, make_recipe, make_tag):
    recipe = make_recipe()
    tag = make_tag()
    client.post(f"/api/recipes/{recipe['id']}/tags/{tag['id']}")
    res = client.post(f"/api/recipes/{recipe['id']}/tags/{tag['id']}")

    assert res.status_code == 200
    assert len(res.json()["tags"]) == 1


def test_attach_unknown_tag_or_recipe_404(client, make_recipe, make_tag):
    recipe = make_recipe()
    tag = make_tag()
    assert client.post(f"/api/recipes/{recipe['id']}/tags/{uuid.uuid4()}").status_code == 404
    assert client.post(f"/api/recipes/{uuid.uuid4()}/tags/{tag['id']}").status_code == 404


def test_detach_tag(client, make_recipe, make_tag):
    recipe = make_recipe()
    tag = make_tag()
    client.post(f"/api/recipes/{recipe['id']}/tags/{tag['id']}")

    res = client.delete(f"/api/recipes/{recipe['id']}/tags/{tag['id']}")
    assert res.status_code == 200
    assert res.json()["tags"] == []


def test_deleting_a_tag_removes_it_from_recipes(client, make_recipe, make_tag):
    recipe = make_recipe()
    tag = make_tag()
    client.post(f"/api/recipes/{recipe['id']}/tags/{tag['id']}")

    client.delete(f"/api/tags/{tag['id']}")
    assert client.get(f"/api/recipes/{recipe['id']}").json()["tags"] == []
