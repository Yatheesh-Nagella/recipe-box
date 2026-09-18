import { useEffect, useState } from "react";
import { attachTag, createTag, detachTag, listTags } from "../api";

// If recipeId is set, add/remove call the API immediately (edit mode).
// If recipeId is null, tags are only tracked locally until the caller
// attaches them after creating the recipe (new-recipe mode).
export default function TagPicker({ recipeId, tags, onChange }) {
  const [allTags, setAllTags] = useState([]);
  const [pickId, setPickId] = useState("");
  const [newName, setNewName] = useState("");
  const [newType, setNewType] = useState("cuisine");
  const [error, setError] = useState(null);

  useEffect(() => {
    listTags().then(setAllTags).catch((e) => setError(e.message));
  }, []);

  const available = allTags.filter((t) => !tags.some((rt) => rt.id === t.id));

  async function addExisting() {
    if (!pickId) return;
    const tag = allTags.find((t) => t.id === pickId);
    try {
      if (recipeId) await attachTag(recipeId, tag.id);
      onChange([...tags, tag]);
      setPickId("");
    } catch (err) {
      setError(err.message);
    }
  }

  async function createAndAdd(e) {
    e.preventDefault();
    if (!newName.trim()) return;
    try {
      const tag = await createTag({ name: newName.trim(), type: newType });
      setAllTags((prev) => [...prev, tag]);
      if (recipeId) await attachTag(recipeId, tag.id);
      onChange([...tags, tag]);
      setNewName("");
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove(tag) {
    try {
      if (recipeId) await detachTag(recipeId, tag.id);
      onChange(tags.filter((t) => t.id !== tag.id));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="tag-picker">
      {tags.length > 0 && (
        <div className="tags">
          {tags.map((t) => (
            <span key={t.id} className="tag">
              {t.name}
              <button type="button" onClick={() => remove(t)}>
                &times;
              </button>
            </span>
          ))}
        </div>
      )}
      {error && <p className="error">{error}</p>}
      <div className="tag-picker-controls">
        <select value={pickId} onChange={(e) => setPickId(e.target.value)}>
          <option value="">Add existing tag...</option>
          {available.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name} ({t.type})
            </option>
          ))}
        </select>
        <button type="button" onClick={addExisting} disabled={!pickId}>
          Add
        </button>
      </div>
      <div className="tag-picker-controls">
        <input
          type="text"
          placeholder="New tag name"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
        />
        <select value={newType} onChange={(e) => setNewType(e.target.value)}>
          <option value="cuisine">Cuisine</option>
          <option value="ingredient">Ingredient</option>
        </select>
        <button type="button" onClick={createAndAdd} disabled={!newName.trim()}>
          Create + add
        </button>
      </div>
    </div>
  );
}
