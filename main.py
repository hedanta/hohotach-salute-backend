import uuid

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter
from pydantic import BaseModel
from sqlalchemy import Column, String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/db"

# for async interaction with db
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()


# region: database models


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)


# endregion

# region: data access layer


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, name: str) -> User:
        new_user = User(name=name)
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user


# endregion

# region: API models


class TunedModel(BaseModel):
    class Config:
        from_attributes = True


class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str


class CreateUser(BaseModel):
    name: str


class ShowJoke(TunedModel):
    content: str


# endregion


app = FastAPI(title="hohotach")

JOKE_URL = 'http://rzhunemogu.ru/RandJSON.aspx?CType=1'

user_router = APIRouter()


async def _create_new_user(body: CreateUser) -> ShowUser:
    async with async_session() as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(name=body.name)
            return ShowUser(user_id=user.user_id, name=user.name)


@user_router.post("/", response_model=ShowUser)
async def create_user(body: CreateUser) -> ShowUser:
    return await _create_new_user(body=body)


@user_router.get("/joke", response_model=ShowJoke)
async def get_joke() -> ShowJoke:
    async with httpx.AsyncClient() as client:
        response = await client.get(JOKE_URL)
        joke = response.json(strict=False)  # \r\n
        content = joke['content']
        return ShowJoke(content=content)


main_api_router = APIRouter()

main_api_router.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
