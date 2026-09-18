import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listRecipes, listTags } from "../api";

export default function RecipeList() {
  const [recipes, setRecipes] = useState([]);
  const [tags, setTags] = useState([]);
  const [status, setStatus] = useState("");
  const [tag, setTag] = useState("");
  const [q, setQ] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    listTags().then(setTags).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    const handle = setTimeout(() => {
      listRecipes({ status, tag, q })
        .then(setRecipes)
        .catch((e) => setError(e.message));
    }, 200);
    return () => clearTimeout(handle);
  }, [status, tag, q]);

  return (
    <div>
      <div className="toolbar">
        <input
          type="text"
          placeholder="Search title..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All statuses</option>
          <option value="want_to_try">Want to try</option>
          <option value="tried">Tried</option>
        </select>
        <select value={tag} onChange={(e) => setTag(e.target.value)}>
          <option value="">All tags</option>
          {tags.map((t) => (
            <option key={t.id} value={t.name}>
              {t.name} ({t.type})
            </option>
          ))}
        </select>
        <Link className="button" to="/recipes/new">
          + New recipe
        </Link>
      </div>

      {error && <p className="error">{error}</p>}

      <ul className="recipe-list">
        {recipes.map((r) => (
          <li key={r.id}>
            <Link to={`/recipes/${r.id}`} className="recipe-card">
              <div className="recipe-card-top">
                <strong>{r.title}</strong>
                {r.rating && <span className="rating">{"★".repeat(r.rating)}</span>}
              </div>
              <div className="recipe-card-meta">
                <span className={`status status-${r.status}`}>{r.status}</span>
                {r.tags.map((t) => (
                  <span key={t.id} className="tag">
                    {t.name}
                  </span>
                ))}
              </div>
              {r.latest_note && <p className="recipe-card-note">&ldquo;{r.latest_note}&rdquo;</p>}
              {r.last_made && <span className="recipe-card-date">last made {r.last_made}</span>}
            </Link>
          </li>
        ))}
        {recipes.length === 0 && <p>No recipes found.</p>}
      </ul>
    </div>
  );
}
