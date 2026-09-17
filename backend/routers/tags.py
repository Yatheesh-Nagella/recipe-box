import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.post("", response_model=schemas.TagOut, status_code=201)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(models.Tag).where(models.Tag.name == tag.name))
    if existing:
        raise HTTPException(status_code=409, detail="Tag with this name already exists")
    db_tag = models.Tag(name=tag.name, type=tag.type.value)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.get("", response_model=list[schemas.TagOut])
def list_tags(type: schemas.TagType | None = None, db: Session = Depends(get_db)):
    query = select(models.Tag)
    if type is not None:
        query = query.where(models.Tag.type == type.value)
    return db.scalars(query.order_by(models.Tag.name)).all()


@router.get("/{tag_id}", response_model=schemas.TagOut)
def get_tag(tag_id: uuid.UUID, db: Session = Depends(get_db)):
    tag = db.get(models.Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: uuid.UUID, db: Session = Depends(get_db)):
    tag = db.get(models.Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()
