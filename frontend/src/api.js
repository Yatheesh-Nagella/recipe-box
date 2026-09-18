const BASE = `${import.meta.env.BASE_URL.replace(/\/$/, "")}/api`;

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export function listRecipes({ status, tag, q } = {}) {
  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (tag) params.set("tag", tag);
  if (q) params.set("q", q);
  const qs = params.toString();
  return request(`/recipes${qs ? `?${qs}` : ""}`);
}

export function getRecipe(id) {
  return request(`/recipes/${id}`);
}

export function createRecipe(data) {
  return request("/recipes", { method: "POST", body: JSON.stringify(data) });
}

export function updateRecipe(id, data) {
  return request(`/recipes/${id}`, { method: "PATCH", body: JSON.stringify(data) });
}

export function deleteRecipe(id) {
  return request(`/recipes/${id}`, { method: "DELETE" });
}

export function attachTag(recipeId, tagId) {
  return request(`/recipes/${recipeId}/tags/${tagId}`, { method: "POST" });
}

export function detachTag(recipeId, tagId) {
  return request(`/recipes/${recipeId}/tags/${tagId}`, { method: "DELETE" });
}

export function listTags(type) {
  const qs = type ? `?type=${type}` : "";
  return request(`/tags${qs}`);
}

export function createTag(data) {
  return request("/tags", { method: "POST", body: JSON.stringify(data) });
}

export function listNotes(recipeId) {
  return request(`/recipes/${recipeId}/notes`);
}

export function addNote(recipeId, content) {
  return request(`/recipes/${recipeId}/notes`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export function editNote(recipeId, noteId, content) {
  return request(`/recipes/${recipeId}/notes/${noteId}/edit`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export function getNoteHistory(recipeId, noteId) {
  return request(`/recipes/${recipeId}/notes/${noteId}/history`);
}
