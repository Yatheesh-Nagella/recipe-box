import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  addNote,
  deleteRecipe,
  editNote,
  getNoteHistory,
  getRecipe,
  listNotes,
} from "../api";

function NoteItem({ recipeId, note, onSaved }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(note.content);
  const [history, setHistory] = useState(null);
  const [error, setError] = useState(null);

  async function save() {
    if (!draft.trim()) return;
    try {
      const updated = await editNote(recipeId, note.id, draft.trim());
      onSaved(updated);
      setEditing(false);
    } catch (err) {
      setError(err.message);
    }
  }

  async function toggleHistory() {
    if (history) {
      setHistory(null);
      return;
    }
    try {
      const past = await getNoteHistory(recipeId, note.id);
      setHistory(past.slice(0, -1)); // everything before the current version
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <li>
      <div className="note-meta">
        <span className="note-date">{new Date(note.created_at).toLocaleString()}</span>
        {note.edited && <span className="note-edited">edited</span>}
      </div>
      {error && <p className="error">{error}</p>}
      {editing ? (
        <div className="note-edit">
          <input value={draft} onChange={(e) => setDraft(e.target.value)} />
          <button onClick={save}>Save</button>
          <button onClick={() => setEditing(false)}>Cancel</button>
        </div>
      ) : (
        <p>{note.content}</p>
      )}
      <div className="note-actions">
        {!editing && (
          <button onClick={() => setEditing(true)} className="link-button">
            Edit
          </button>
        )}
        {note.edited && (
          <button onClick={toggleHistory} className="link-button">
            {history ? "Hide history" : "View history"}
          </button>
        )}
      </div>
      {history && (
        <ul className="note-history">
          {history.map((h) => (
            <li key={h.id}>
              <span className="note-date">{new Date(h.created_at).toLocaleString()}</span>
              <p>{h.content}</p>
            </li>
          ))}
        </ul>
      )}
    </li>
  );
}

export default function RecipeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState(null);
  const [notes, setNotes] = useState([]);
  const [newNote, setNewNote] = useState("");
  const [error, setError] = useState(null);

  function refresh() {
    getRecipe(id).then(setRecipe).catch((e) => setError(e.message));
    listNotes(id).then(setNotes).catch((e) => setError(e.message));
  }

  useEffect(refresh, [id]);

  async function handleAddNote(e) {
    e.preventDefault();
    if (!newNote.trim()) return;
    const created = await addNote(id, newNote.trim());
    setNotes((prev) => [...prev, created]);
    setNewNote("");
  }

  function handleNoteSaved() {
    // editing swaps the note for a new head with a new id, so refetch
    // rather than trying to patch it into place by index/id.
    listNotes(id).then(setNotes).catch((e) => setError(e.message));
  }

  async function handleDelete() {
    if (!confirm(`Delete "${recipe.title}"? This cannot be undone.`)) return;
    await deleteRecipe(id);
    navigate("/");
  }

  if (error) return <p className="error">{error}</p>;
  if (!recipe) return <p>Loading...</p>;

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

      {recipe.tags.length > 0 && (
        <div className="tags">
          {recipe.tags.map((t) => (
            <span key={t.id} className="tag">
              {t.name}
            </span>
          ))}
        </div>
      )}

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
          <NoteItem key={n.id} recipeId={id} note={n} onSaved={handleNoteSaved} />
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
