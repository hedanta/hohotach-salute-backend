from typing import Union
from typing import Generator

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import select
from sqlalchemy import delete

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/db"

# for async interaction with db
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    execution_options={"isolation_level": "AUTOCOMMIT"}
)

async_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def get_db() -> Generator:
    """Dependency for getting async session"""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()


# region: database models


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    name = Column(String, nullable=False)


class Joke(Base):
    __tablename__ = "jokes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey("users.user_id"), nullable=False)
    content = Column(String, nullable=False)


# endregion

# region: data access layer


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self,
        user_id: int,
        name: str
    ) -> User:
        new_user = User(
            user_id=user_id,
            name=name
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user


class JokeDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add_joke(
        self,
        user_id: int,
        content: str
    ) -> Joke:
        joke = Joke(
            user_id=user_id,
            content=content
        )
        self.db_session.add(joke)
        await self.db_session.flush()
        return joke

    async def delete_joke(self, user_id: int):
        query = (
            delete(Joke).where(Joke.user_id == user_id)
        )
        res = await self.db_session.execute(query)

    async def get_joke_by_id(self, user_id: int) -> Union[Joke, None]:
        query = select(Joke).where(Joke.user_id == user_id)
        res = await self.db_session.execute(query)
        joke_row = res.fetchone()
        if joke_row is not None:
            return joke_row[0]


# endregion

# region: API models

class TunedModel(BaseModel):
    class Config:
        from_attributes = True


class ShowUser(TunedModel):
    user_id: int
    name: str


class CreateUser(BaseModel):
    user_id: int
    name: str


class ShowJoke(TunedModel):
    content: str


class ShowFavJoke(BaseModel):
    user_id: int
    content: str


class AddJoke(BaseModel):
    user_id: int
    content: str


# endregion


app = FastAPI(title="hohotach")

JOKE_URL = 'http://rzhunemogu.ru/RandJSON.aspx?CType=1'

user_router = APIRouter()


async def _create_new_user(body: CreateUser, session) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user(
            user_id=body.user_id,
            name=body.name)
        return ShowUser(user_id=user.user_id, name=user.name)


async def _add_fav_joke(body: AddJoke, session) -> ShowFavJoke:
    async with session.begin():
        joke_dal = JokeDAL(session)
        joke = await joke_dal.add_joke(user_id=body.user_id, content=body.content)
        return ShowFavJoke(user_id=joke.user_id, content=joke.content)


async def _delete_fav_joke(user_id, session):
    async with session.begin():
        joke_dal = JokeDAL(session)
        return await joke_dal.delete_joke(user_id=user_id)


async def _get_fav_joke(user_id, session) -> Union[Joke, None]:
    async with session.begin():
        joke_dal = JokeDAL(session)
        joke = await joke_dal.get_joke_by_id(user_id=user_id)
        if joke is not None:
            return joke


@user_router.post("/", response_model=ShowUser)
async def create_user(
    body: CreateUser,
    db: AsyncSession = Depends(get_db)
) -> ShowUser:
    return await _create_new_user(body, db)


@user_router.get("/joke", response_model=ShowJoke)
async def get_joke() -> ShowJoke:
    async with httpx.AsyncClient() as client:
        response = await client.get(JOKE_URL)
        joke = response.json(strict=False)  # \r\n
        content = joke['content']
        return ShowJoke(content=content)


@user_router.post("/favourites", response_model=ShowFavJoke)
async def add_fav_joke(
    body: AddJoke,
    db: AsyncSession = Depends(get_db)
) -> ShowFavJoke:
    return await _add_fav_joke(body, db)


@user_router.get("/favourites")
async def get_fav_joke(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> ShowJoke:
    joke = await _get_fav_joke(user_id, db)
    if joke is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} has no favourite jokes."
        )
    return ShowJoke(content=joke.content)


@user_router.delete("/favourites")
async def delete_fav_joke(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    #    return await _delete_fav_joke(user_id, db)
    return await _delete_fav_joke(user_id, db)


main_api_router = APIRouter()

main_api_router.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
