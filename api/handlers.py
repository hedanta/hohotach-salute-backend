import httpx

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi import Depends
from fastapi.responses import JSONResponse

from api.actions import _get_or_create_user
from api.actions import _add_fav_joke
from api.actions import _get_fav_jokes
from api.actions import *
from db.dals import *
from db.session import get_db

user_router = APIRouter()

JOKE_URL = 'http://rzhunemogu.ru/RandJSON.aspx?CType=1'


@user_router.get("/get_joke_from_api", response_model=None)
async def get_joke():
    async with httpx.AsyncClient() as client:
        response = await client.get(JOKE_URL)
        content = response.text[12:-3]
        joke_item = Joke(content=content)
        joke_json = jsonable_encoder(joke_item)
        return JSONResponse(content=joke_json)


@user_router.post("/get_or_create_user", response_model=ShowUser)
async def create_user(
        user_id: str,
        db: AsyncSession = Depends(get_db)
) -> ShowUser:
    return await _get_or_create_user(user_id, db)


@user_router.post("/add_fav_joke")
async def add_fav_joke(
        content: str,
        user_id: str,
        db: AsyncSession = Depends(get_db)
):
    return await _add_fav_joke(content, user_id, db)


@user_router.get("/get_fav_jokes", response_model=List[ShowJoke])
async def get_fav_jokes(
        user_id: str,
        db: AsyncSession = Depends(get_db)
):
    return await _get_fav_jokes(user_id, db)


@user_router.delete("/delete_fav_joke")
async def delete_fav_joke(
        joke_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    fav_joke_dal = FavJokeDAL(db)
    await fav_joke_dal.delete_fav_joke(joke_id)
    print("Joke deleted successfully.")


'''
@user_router.post("/add_joke",
                  response_model=ShowJoke,
                  description='ручка не предназначена для фронта, используется в дебаге,
                     добавление анекдота в таблицу Jokes происходит через add_fav_joke')
async def add_joke(
        body: AddJoke,
        db: AsyncSession = Depends(get_db)
) -> ShowJoke:
    return await _add_joke(body, db)
'''


'''
@user_router.get("/get_joke_by_id", response_model=Union[ShowJoke, None],
                 description='тоже не для фронта')
async def get_joke(
        joke_id: UUID,
        db: AsyncSession = Depends(get_db)
) -> Union[ShowJoke, None]:
    return await _get_joke_by_id(joke_id, db)
'''
