import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from routers.notes import current_notes

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


def _get_recipe_or_404(recipe_id: uuid.UUID, db: Session) -> models.Recipe:
    recipe = db.get(models.Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


def _with_latest_note(db: Session, recipe: models.Recipe) -> models.Recipe:
    notes = current_notes(db, recipe.id)
    recipe.latest_note = notes[-1].content if notes else None
    return recipe


@router.post("", response_model=schemas.RecipeOut, status_code=201)
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = models.Recipe(**recipe.model_dump(exclude={"status"}), status=recipe.status.value)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return _with_latest_note(db, db_recipe)


@router.get("", response_model=list[schemas.RecipeOut])
def list_recipes(
    status: schemas.RecipeStatus | None = None,
    tag: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(models.Recipe)
    if status is not None:
        query = query.where(models.Recipe.status == status.value)
    if tag is not None:
        query = query.join(models.Recipe.tags).where(models.Tag.name == tag)
    if q is not None:
        query = query.where(models.Recipe.title.ilike(f"%{q}%"))
    recipes = db.scalars(query.order_by(models.Recipe.title)).unique().all()
    return [_with_latest_note(db, r) for r in recipes]


@router.get("/{recipe_id}", response_model=schemas.RecipeOut)
def get_recipe(recipe_id: uuid.UUID, db: Session = Depends(get_db)):
    return _with_latest_note(db, _get_recipe_or_404(recipe_id, db))


@router.patch("/{recipe_id}", response_model=schemas.RecipeOut)
def update_recipe(recipe_id: uuid.UUID, update: schemas.RecipeUpdate, db: Session = Depends(get_db)):
    db_recipe = _get_recipe_or_404(recipe_id, db)
    updates = update.model_dump(exclude_unset=True)
    if "status" in updates:
        updates["status"] = updates["status"].value
    for field, value in updates.items():
        setattr(db_recipe, field, value)
    db.commit()
    db.refresh(db_recipe)
    return _with_latest_note(db, db_recipe)


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: uuid.UUID, db: Session = Depends(get_db)):
    db_recipe = _get_recipe_or_404(recipe_id, db)
    db.delete(db_recipe)
    db.commit()


@router.post("/{recipe_id}/tags/{tag_id}", response_model=schemas.RecipeOut)
def attach_tag(recipe_id: uuid.UUID, tag_id: uuid.UUID, db: Session = Depends(get_db)):
    db_recipe = _get_recipe_or_404(recipe_id, db)
    db_tag = db.get(models.Tag, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if db_tag not in db_recipe.tags:
        db_recipe.tags.append(db_tag)
        db.commit()
        db.refresh(db_recipe)
    return _with_latest_note(db, db_recipe)


@router.delete("/{recipe_id}/tags/{tag_id}", response_model=schemas.RecipeOut)
def detach_tag(recipe_id: uuid.UUID, tag_id: uuid.UUID, db: Session = Depends(get_db)):
    db_recipe = _get_recipe_or_404(recipe_id, db)
    db_tag = db.get(models.Tag, tag_id)
    if db_tag and db_tag in db_recipe.tags:
        db_recipe.tags.remove(db_tag)
        db.commit()
        db.refresh(db_recipe)
    return _with_latest_note(db, db_recipe)
