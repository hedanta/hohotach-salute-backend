from __future__ import annotations

import uuid

from pydantic import BaseModel


class TunedModel(BaseModel):
    class Config:
        from_attributes = True


class ShowUser(TunedModel):
    user_id: str


class CreateUser(BaseModel):
    user_id: str


class ShowJoke(BaseModel):
    joke_id: int
    content: str
    alias: str | None = None


class AddJoke(BaseModel):
    content: str
    alias: str | None = None


class FavJoke(BaseModel):
    joke_id: int
    alias: str | None = None


class ShowFavJoke(BaseModel):
    content: str
