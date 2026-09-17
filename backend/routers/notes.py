import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/recipes/{recipe_id}/notes", tags=["notes"])


def _get_recipe_or_404(recipe_id: uuid.UUID, db: Session) -> models.Recipe:
    recipe = db.get(models.Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("", response_model=schemas.NoteOut, status_code=201)
def add_note(recipe_id: uuid.UUID, note: schemas.NoteCreate, db: Session = Depends(get_db)):
    _get_recipe_or_404(recipe_id, db)
    db_note = models.Note(recipe_id=recipe_id, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.get("", response_model=list[schemas.NoteOut])
def list_notes(recipe_id: uuid.UUID, db: Session = Depends(get_db)):
    _get_recipe_or_404(recipe_id, db)
    query = (
        select(models.Note)
        .where(models.Note.recipe_id == recipe_id)
        .order_by(models.Note.created_at)
    )
    return db.scalars(query).all()
