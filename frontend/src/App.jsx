import { Link, Route, Routes } from "react-router-dom";
import RecipeDetail from "./pages/RecipeDetail";
import RecipeForm from "./pages/RecipeForm";
import RecipeList from "./pages/RecipeList";
import Tags from "./pages/Tags";

export default function App() {
  return (
    <div className="app">
      <header>
        <Link to="/" className="brand">
          recipe-box
        </Link>
        <nav>
          <Link to="/tags">Tags</Link>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<RecipeList />} />
          <Route path="/recipes/new" element={<RecipeForm />} />
          <Route path="/recipes/:id" element={<RecipeDetail />} />
          <Route path="/recipes/:id/edit" element={<RecipeForm />} />
          <Route path="/tags" element={<Tags />} />
        </Routes>
      </main>
    </div>
  );
}
