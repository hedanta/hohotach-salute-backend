from fastapi import APIRouter
from .models import AddFavJoke, AddJoke, CreateUser, FavJoke, ShowJoke, ShowUser
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from db.dals import *
from db.session import get_db
from fastapi import Query

import httpx

user_router = APIRouter()

JOKE_URL = 'http://rzhunemogu.ru/RandJSON.aspx?CType=1'

# TODO: по хорошему приватные методы нужно перетащить в отдельный файл, а здесь оставить только хендлеы 
 
# ручка не предназначена для фронта, используется в дебаге
async def _get_or_create_user(body: CreateUser, session) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_or_create_user(
            user_id=body.user_id,
            name=body.name)
        return ShowUser(user_id=user.id, name=user.username)
    
@user_router.post("/get_or_create_user", response_model=ShowUser)
async def create_user(
    body: CreateUser,
    db: AsyncSession = Depends(get_db)
) -> ShowUser:
    return await _get_or_create_user(body, db)

# 
# Аналогично с методом _get_joke_by_id
async def _add_joke(body: AddJoke, session) -> ShowJoke:
    async with session.begin():
        joke_dal = JokeDAL(session)
        print(f"hui: {body.category_id}")
        joke = await joke_dal.add_joke(content =body.content, alias=body.alias, category_id=body.category_id)
        return ShowJoke(content=joke.content, 
                            id=joke.id,
                            alias = joke.alias,
                            category_id=joke.category_id)
    
@user_router.post("/add_joke",
                   response_model=ShowJoke,
                   description= '''ручка не предназначена для фронта, используется в дебаге,
                     добавление анекдота в таблицу Jokes происходит через add_fav_joke''')
async def add_joke(
    body: AddJoke,
    db: AsyncSession = Depends(get_db)
) -> ShowJoke:
    return await _add_joke(body, db)


async def _get_joke_by_id(id: int, session) -> Union[ShowJoke, None]:
    async with session.begin():
        joke_dal = JokeDAL(session)
        joke = await joke_dal.get_joke_by_id(joke_id=id)
        if joke:
            print(joke.content, joke.id, joke.alias, joke.category_id)
            return ShowJoke(content=joke.content, 
                                id=joke.id,
                                alias = joke.alias,
                                category_id=joke.category_id)
    
@user_router.get("/get_joke_by_id", response_model=Union[ShowJoke, None],
                 description= 'тоже не для фронта')
async def get_joke(
    id: int,
    db: AsyncSession = Depends(get_db)
) -> Union[ShowJoke, None]:
    return await _get_joke_by_id(id, db)
     

async def _add_fav_joke(body: AddFavJoke, session) -> FavJoke:
    user = body.user
    joke = body.jokeBody

    user = await _get_or_create_user(user, session)
    joke = await _add_joke(joke, session)
    
    async with session.begin():
        fav_joke_dal = FavJokeDAL(session)
        fav_joke = await fav_joke_dal.add_fav_joke(user.user_id, joke.id)
        
        return FavJoke(user_id = fav_joke.user_id, joke_id = fav_joke.joke_id)

@user_router.post("/add_fav_joke", response_model=FavJoke)
async def add_fav_joke(
    body: AddFavJoke,
    db: AsyncSession = Depends(get_db)
) -> ShowJoke:
    return await _add_fav_joke(body, db)       
        
# здесь я уже задолбался делать эти приватные методы, поэтому будет без них   
@user_router.get("/get_fav_joke", response_model = List[ShowJoke])
async def get_fav_joke(id: int,
                        db: AsyncSession = Depends(get_db)):
    fav_joke_dal = FavJokeDAL(db)
    jokes = await fav_joke_dal.get_fav_joke(id)

    showjokes_list = []
    for joke in jokes:
        showjokes_list.append(ShowJoke(content = joke.content, 
                                    id = joke.id,
                                    alias = joke.alias,
                                    category_id= joke.category_id))
    return showjokes_list


@user_router.get("/get_joke_from_api", response_model=ShowJoke)
async def get_joke() -> ShowJoke:
    async with httpx.AsyncClient() as client:
        response = await client.get(JOKE_URL)
        joke = response.json(strict=False)  # \r\n
        content = joke['content']
        return ShowJoke(content=content)