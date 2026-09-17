from fastapi import FastAPI

import models
from database import Base, engine
from routers import notes, recipes, tags

app = FastAPI(title="recipe-box")

Base.metadata.create_all(bind=engine)

app.include_router(recipes.router)
app.include_router(tags.router)
app.include_router(notes.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
