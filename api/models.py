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
    content: str
    id: int
    alias: str
    category_id: int | None = None


class AddJoke(BaseModel):
    content: str
    alias: str
    category_id: int | None = None

class AddFavJoke(BaseModel):
    jokeBody : AddJoke
    user: CreateUser

class FavJoke(BaseModel):
    user_id: int
    joke_id: int
