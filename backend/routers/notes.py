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


def _get_note_or_404(recipe_id: uuid.UUID, note_id: uuid.UUID, db: Session) -> models.Note:
    note = db.get(models.Note, note_id)
    if not note or note.recipe_id != recipe_id:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


def _find_predecessor(db: Session, note_id: uuid.UUID) -> models.Note | None:
    return db.scalar(select(models.Note).where(models.Note.superseded_by_id == note_id))


def _to_out(note: models.Note, edited: bool, original_created_at) -> schemas.NoteOut:
    return schemas.NoteOut(
        id=note.id,
        recipe_id=note.recipe_id,
        content=note.content,
        created_at=note.created_at,
        edited=edited,
        original_created_at=original_created_at,
    )


def _enrich(db: Session, note: models.Note) -> schemas.NoteOut:
    original = note
    predecessor = _find_predecessor(db, note.id)
    edited = predecessor is not None
    while predecessor is not None:
        original = predecessor
        predecessor = _find_predecessor(db, predecessor.id)
    return _to_out(note, edited, original.created_at if edited else None)


def current_notes(db: Session, recipe_id: uuid.UUID) -> list[schemas.NoteOut]:
    """Current (non-superseded) notes in the order they were first posted.

    An edit is a new row, so its own created_at is the edit time; sorting on it
    would push an edited note below newer ones. Order by the chain's original
    timestamp instead.
    """
    heads = db.scalars(
        select(models.Note).where(
            models.Note.recipe_id == recipe_id, models.Note.superseded_by_id.is_(None)
        )
    ).all()
    notes = [_enrich(db, n) for n in heads]
    notes.sort(key=lambda n: n.original_created_at or n.created_at)
    return notes


@router.post("", response_model=schemas.NoteOut, status_code=201)
def add_note(recipe_id: uuid.UUID, note: schemas.NoteCreate, db: Session = Depends(get_db)):
    _get_recipe_or_404(recipe_id, db)
    db_note = models.Note(recipe_id=recipe_id, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return _to_out(db_note, edited=False, original_created_at=None)


@router.get("", response_model=list[schemas.NoteOut])
def list_notes(recipe_id: uuid.UUID, db: Session = Depends(get_db)):
    _get_recipe_or_404(recipe_id, db)
    return current_notes(db, recipe_id)


@router.post("/{note_id}/edit", response_model=schemas.NoteOut)
def edit_note(
    recipe_id: uuid.UUID, note_id: uuid.UUID, note: schemas.NoteCreate, db: Session = Depends(get_db)
):
    old = _get_note_or_404(recipe_id, note_id, db)
    if old.superseded_by_id is not None:
        raise HTTPException(
            status_code=409, detail="Note has already been edited; edit the latest version instead"
        )
    new_note = models.Note(recipe_id=recipe_id, content=note.content)
    db.add(new_note)
    db.flush()
    old.superseded_by_id = new_note.id
    db.commit()
    db.refresh(new_note)
    return _enrich(db, new_note)


@router.get("/{note_id}/history", response_model=list[schemas.NoteOut])
def note_history(recipe_id: uuid.UUID, note_id: uuid.UUID, db: Session = Depends(get_db)):
    head = _get_note_or_404(recipe_id, note_id, db)
    chain = [head]
    predecessor = _find_predecessor(db, head.id)
    while predecessor is not None:
        chain.append(predecessor)
        predecessor = _find_predecessor(db, predecessor.id)
    chain.reverse()
    return [_to_out(n, edited=False, original_created_at=None) for n in chain]
