import { Link, Route, Routes } from "react-router-dom";
import RecipeDetail from "./pages/RecipeDetail";
import RecipeForm from "./pages/RecipeForm";
import RecipeList from "./pages/RecipeList";
import { useTheme } from "./useTheme";

export default function App() {
  const [theme, toggleTheme] = useTheme();

  return (
    <div className="app">
      <header>
        <Link to="/" className="brand">
          recipe-box
        </Link>
        <nav>
          <button onClick={toggleTheme} aria-label="Toggle dark mode">
            {theme === "dark" ? "Light mode" : "Dark mode"}
          </button>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<RecipeList />} />
          <Route path="/recipes/new" element={<RecipeForm />} />
          <Route path="/recipes/:id" element={<RecipeDetail />} />
          <Route path="/recipes/:id/edit" element={<RecipeForm />} />
        </Routes>
      </main>
    </div>
  );
}
