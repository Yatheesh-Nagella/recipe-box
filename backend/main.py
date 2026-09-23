from fastapi import FastAPI

from routers import notes, recipes, tags

app = FastAPI(title="recipe-box")

app.include_router(recipes.router)
app.include_router(tags.router)
app.include_router(notes.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
