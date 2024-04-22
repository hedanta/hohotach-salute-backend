from __future__ import annotations

from pydantic import BaseModel

class TunedModel(BaseModel):
    class Config:
        from_attributes = True


class ShowUser(TunedModel):
    user_id: int
    name: str


class CreateUser(BaseModel):
    user_id: int
    name: str


class ShowJoke(BaseModel):
    joke_id: int
    content: str
    alias: str


class ShowApiJoke(BaseModel):
    content: str


class AddJoke(BaseModel):
    content: str
    alias: str


class AddFavJoke(BaseModel):
    jokeBody: AddJoke
    user: CreateUser


class FavJoke(BaseModel):
    user_id: int
    joke_id: int
