import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  addNote,
  attachTag,
  deleteRecipe,
  detachTag,
  getRecipe,
  listNotes,
  listTags,
} from "../api";

export default function RecipeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState(null);
  const [notes, setNotes] = useState([]);
  const [allTags, setAllTags] = useState([]);
  const [newNote, setNewNote] = useState("");
  const [tagToAdd, setTagToAdd] = useState("");
  const [error, setError] = useState(null);

  function refresh() {
    getRecipe(id).then(setRecipe).catch((e) => setError(e.message));
    listNotes(id).then(setNotes).catch((e) => setError(e.message));
  }

  useEffect(() => {
    refresh();
    listTags().then(setAllTags).catch((e) => setError(e.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function handleAddNote(e) {
    e.preventDefault();
    if (!newNote.trim()) return;
    await addNote(id, newNote.trim());
    setNewNote("");
    refresh();
  }

  async function handleAddTag(e) {
    e.preventDefault();
    if (!tagToAdd) return;
    await attachTag(id, tagToAdd);
    setTagToAdd("");
    refresh();
  }

  async function handleRemoveTag(tagId) {
    await detachTag(id, tagId);
    refresh();
  }

  async function handleDelete() {
    if (!confirm(`Delete "${recipe.title}"? This cannot be undone.`)) return;
    await deleteRecipe(id);
    navigate("/");
  }

  if (error) return <p className="error">{error}</p>;
  if (!recipe) return <p>Loading...</p>;

  const availableTags = allTags.filter(
    (t) => !recipe.tags.some((rt) => rt.id === t.id)
  );

  return (
    <div>
      <Link to="/">&larr; Back to recipes</Link>
      <h1>{recipe.title}</h1>
      <p>
        <span className={`status status-${recipe.status}`}>{recipe.status}</span>
        {recipe.rating && <span className="rating">{"★".repeat(recipe.rating)}</span>}
        {recipe.cook_count > 0 && <span> cooked {recipe.cook_count}x</span>}
        {recipe.last_made && <span> last made {recipe.last_made}</span>}
      </p>
      {recipe.youtube_url && (
        <p>
          <a href={recipe.youtube_url} target="_blank" rel="noreferrer">
            YouTube source
          </a>
        </p>
      )}

      <div className="tags">
        {recipe.tags.map((t) => (
          <span key={t.id} className="tag">
            {t.name}
            <button onClick={() => handleRemoveTag(t.id)}>&times;</button>
          </span>
        ))}
      </div>
      <form onSubmit={handleAddTag} className="inline-form">
        <select value={tagToAdd} onChange={(e) => setTagToAdd(e.target.value)}>
          <option value="">Add a tag...</option>
          {availableTags.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name} ({t.type})
            </option>
          ))}
        </select>
        <button type="submit">Add</button>
      </form>

      <div className="actions">
        <Link className="button" to={`/recipes/${id}/edit`}>
          Edit
        </Link>
        <button onClick={handleDelete} className="danger">
          Delete
        </button>
      </div>

      <h2>Notes</h2>
      <ul className="notes">
        {notes.map((n) => (
          <li key={n.id}>
            <span className="note-date">{new Date(n.created_at).toLocaleString()}</span>
            <p>{n.content}</p>
          </li>
        ))}
        {notes.length === 0 && <p>No notes yet.</p>}
      </ul>
      <form onSubmit={handleAddNote} className="inline-form">
        <input
          type="text"
          placeholder="Add a note about this cooking attempt..."
          value={newNote}
          onChange={(e) => setNewNote(e.target.value)}
        />
        <button type="submit">Add note</button>
      </form>
    </div>
  );
}
