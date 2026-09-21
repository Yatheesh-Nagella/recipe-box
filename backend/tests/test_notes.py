import uuid


def add_note(client, recipe_id, content):
    res = client.post(f"/api/recipes/{recipe_id}/notes", json={"content": content})
    assert res.status_code == 201, res.text
    return res.json()


def edit_note(client, recipe_id, note_id, content):
    return client.post(
        f"/api/recipes/{recipe_id}/notes/{note_id}/edit", json={"content": content}
    )


def test_add_and_list_notes(client, make_recipe):
    recipe = make_recipe()
    add_note(client, recipe["id"], "first")
    add_note(client, recipe["id"], "second")

    notes = client.get(f"/api/recipes/{recipe['id']}/notes").json()
    assert [n["content"] for n in notes] == ["first", "second"]
    assert all(n["edited"] is False for n in notes)
    assert all(n["original_created_at"] is None for n in notes)


def test_notes_for_missing_recipe_404(client):
    missing = uuid.uuid4()
    assert client.get(f"/api/recipes/{missing}/notes").status_code == 404
    res = client.post(f"/api/recipes/{missing}/notes", json={"content": "x"})
    assert res.status_code == 404


def test_edit_creates_new_head_and_preserves_original_timestamp(client, make_recipe):
    recipe = make_recipe()
    original = add_note(client, recipe["id"], "draft")

    res = edit_note(client, recipe["id"], original["id"], "final")
    assert res.status_code == 200
    edited = res.json()

    assert edited["id"] != original["id"]
    assert edited["content"] == "final"
    assert edited["edited"] is True
    assert edited["original_created_at"] == original["created_at"]


def test_list_shows_only_current_version_after_edit(client, make_recipe):
    recipe = make_recipe()
    original = add_note(client, recipe["id"], "draft")
    edit_note(client, recipe["id"], original["id"], "final")

    notes = client.get(f"/api/recipes/{recipe['id']}/notes").json()
    assert [n["content"] for n in notes] == ["final"]
    assert notes[0]["edited"] is True


def test_editing_an_older_note_keeps_its_position(client, make_recipe):
    recipe = make_recipe()
    first = add_note(client, recipe["id"], "first")
    add_note(client, recipe["id"], "second")

    edit_note(client, recipe["id"], first["id"], "first, corrected")

    notes = client.get(f"/api/recipes/{recipe['id']}/notes").json()
    assert [n["content"] for n in notes] == ["first, corrected", "second"]


def test_latest_note_is_last_posted_not_last_edited(client, make_recipe):
    recipe = make_recipe()
    first = add_note(client, recipe["id"], "first")
    add_note(client, recipe["id"], "second")

    edit_note(client, recipe["id"], first["id"], "first, corrected")

    assert client.get(f"/api/recipes/{recipe['id']}").json()["latest_note"] == "second"
    assert client.get("/api/recipes").json()[0]["latest_note"] == "second"


def test_editing_a_superseded_note_is_rejected(client, make_recipe):
    recipe = make_recipe()
    original = add_note(client, recipe["id"], "draft")
    assert edit_note(client, recipe["id"], original["id"], "v2").status_code == 200

    res = edit_note(client, recipe["id"], original["id"], "stale")
    assert res.status_code == 409


def test_edit_missing_note_404(client, make_recipe):
    recipe = make_recipe()
    res = edit_note(client, recipe["id"], uuid.uuid4(), "x")
    assert res.status_code == 404


def test_cannot_edit_a_note_through_a_different_recipe(client, make_recipe):
    recipe_a = make_recipe(title="A")
    recipe_b = make_recipe(title="B")
    note = add_note(client, recipe_a["id"], "belongs to A")

    res = edit_note(client, recipe_b["id"], note["id"], "hijack")
    assert res.status_code == 404
    unchanged = client.get(f"/api/recipes/{recipe_a['id']}/notes").json()
    assert [n["content"] for n in unchanged] == ["belongs to A"]


def test_history_returns_full_chain_oldest_first(client, make_recipe):
    recipe = make_recipe()
    v1 = add_note(client, recipe["id"], "v1")
    v2 = edit_note(client, recipe["id"], v1["id"], "v2").json()
    v3 = edit_note(client, recipe["id"], v2["id"], "v3").json()

    history = client.get(f"/api/recipes/{recipe['id']}/notes/{v3['id']}/history").json()
    assert [n["content"] for n in history] == ["v1", "v2", "v3"]

    current = client.get(f"/api/recipes/{recipe['id']}/notes").json()
    assert [n["content"] for n in current] == ["v3"]
    assert current[0]["original_created_at"] == v1["created_at"]


def test_superseded_content_is_never_modified(client, make_recipe):
    recipe = make_recipe()
    v1 = add_note(client, recipe["id"], "original wording")
    v2 = edit_note(client, recipe["id"], v1["id"], "new wording").json()

    history = client.get(f"/api/recipes/{recipe['id']}/notes/{v2['id']}/history").json()
    assert history[0]["id"] == v1["id"]
    assert history[0]["content"] == "original wording"
    assert history[0]["created_at"] == v1["created_at"]


def test_latest_note_on_recipe_reflects_edits(client, make_recipe):
    recipe = make_recipe()
    assert client.get(f"/api/recipes/{recipe['id']}").json()["latest_note"] is None

    note = add_note(client, recipe["id"], "draft")
    assert client.get(f"/api/recipes/{recipe['id']}").json()["latest_note"] == "draft"

    edit_note(client, recipe["id"], note["id"], "final")
    assert client.get(f"/api/recipes/{recipe['id']}").json()["latest_note"] == "final"


def test_deleting_recipe_removes_its_notes(client, make_recipe):
    recipe = make_recipe()
    note = add_note(client, recipe["id"], "v1")
    edit_note(client, recipe["id"], note["id"], "v2")

    assert client.delete(f"/api/recipes/{recipe['id']}").status_code == 204
    assert client.get(f"/api/recipes/{recipe['id']}/notes").status_code == 404
