import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { attachTag, createRecipe, getRecipe, updateRecipe } from "../api";
import TagPicker from "../components/TagPicker";

const EMPTY = {
  title: "",
  youtube_url: "",
  status: "want_to_try",
  rating: "",
  cook_count: 0,
  last_made: "",
};

export default function RecipeForm() {
  const { id } = useParams();
  const editing = Boolean(id);
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY);
  const [tags, setTags] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!editing) return;
    getRecipe(id).then((r) => {
      setForm({
        title: r.title,
        youtube_url: r.youtube_url || "",
        status: r.status,
        rating: r.rating ?? "",
        cook_count: r.cook_count,
        last_made: r.last_made || "",
      });
      setTags(r.tags);
    });
  }, [id, editing]);

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const payload = {
      title: form.title,
      youtube_url: form.youtube_url || null,
      status: form.status,
      rating: form.rating === "" ? null : Number(form.rating),
      cook_count: Number(form.cook_count),
      last_made: form.last_made || null,
    };
    try {
      const saved = editing
        ? await updateRecipe(id, payload)
        : await createRecipe(payload);
      if (!editing) {
        // tags were only picked locally until the recipe existed
        for (const tag of tags) {
          await attachTag(saved.id, tag.id);
        }
      }
      navigate(`/recipes/${saved.id}`);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <Link to="/">&larr; Back to recipes</Link>
      <h1>{editing ? "Edit recipe" : "New recipe"}</h1>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleSubmit} className="recipe-form">
        <label>
          Title
          <input
            required
            value={form.title}
            onChange={(e) => set("title", e.target.value)}
          />
        </label>
        <label>
          YouTube URL
          <input
            value={form.youtube_url}
            onChange={(e) => set("youtube_url", e.target.value)}
          />
        </label>
        <label>
          Status
          <select value={form.status} onChange={(e) => set("status", e.target.value)}>
            <option value="want_to_try">Want to try</option>
            <option value="tried">Tried</option>
          </select>
        </label>
        <label>
          Rating (1-5)
          <input
            type="number"
            min="1"
            max="5"
            value={form.rating}
            onChange={(e) => set("rating", e.target.value)}
          />
        </label>
        <label>
          Cook count
          <input
            type="number"
            min="0"
            value={form.cook_count}
            onChange={(e) => set("cook_count", e.target.value)}
          />
        </label>
        <label>
          Last made
          <input
            type="date"
            value={form.last_made}
            onChange={(e) => set("last_made", e.target.value)}
          />
        </label>
        <label>
          Tags
          <TagPicker recipeId={editing ? id : null} tags={tags} onChange={setTags} />
        </label>
        <button type="submit">{editing ? "Save changes" : "Create recipe"}</button>
      </form>
    </div>
  );
}
