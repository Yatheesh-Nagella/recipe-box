import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createTag, deleteTag, listTags } from "../api";

export default function Tags() {
  const [tags, setTags] = useState([]);
  const [name, setName] = useState("");
  const [type, setType] = useState("cuisine");
  const [error, setError] = useState(null);

  function refresh() {
    listTags().then(setTags).catch((e) => setError(e.message));
  }

  useEffect(refresh, []);

  async function handleCreate(e) {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      await createTag({ name: name.trim(), type });
      setName("");
      refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    await deleteTag(id);
    refresh();
  }

  return (
    <div>
      <Link to="/">&larr; Back to recipes</Link>
      <h1>Tags</h1>
      {error && <p className="error">{error}</p>}

      <form onSubmit={handleCreate} className="inline-form">
        <input
          type="text"
          placeholder="Tag name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="cuisine">Cuisine</option>
          <option value="ingredient">Ingredient</option>
        </select>
        <button type="submit">Add tag</button>
      </form>

      <ul className="tag-list">
        {tags.map((t) => (
          <li key={t.id}>
            {t.name} <span className="tag-type">({t.type})</span>
            <button onClick={() => handleDelete(t.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
