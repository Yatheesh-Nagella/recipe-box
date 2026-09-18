import uuid
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class RecipeStatus(str, Enum):
    want_to_try = "want_to_try"
    tried = "tried"


class TagType(str, Enum):
    cuisine = "cuisine"
    ingredient = "ingredient"


class TagCreate(BaseModel):
    name: str
    type: TagType


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: TagType


class NoteCreate(BaseModel):
    content: str


class NoteOut(BaseModel):
    id: uuid.UUID
    recipe_id: uuid.UUID
    content: str
    created_at: datetime
    edited: bool = False
    original_created_at: datetime | None = None


class RecipeCreate(BaseModel):
    title: str
    youtube_url: str | None = None
    status: RecipeStatus = RecipeStatus.want_to_try
    rating: int | None = Field(default=None, ge=1, le=5)
    cook_count: int = 0
    last_made: date | None = None


class RecipeUpdate(BaseModel):
    title: str | None = None
    youtube_url: str | None = None
    status: RecipeStatus | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    cook_count: int | None = None
    last_made: date | None = None


class RecipeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    youtube_url: str | None
    status: RecipeStatus
    rating: int | None
    cook_count: int
    last_made: date | None
    tags: list[TagOut] = []
    latest_note: str | None = None
