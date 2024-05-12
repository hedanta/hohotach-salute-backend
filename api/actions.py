import httpx
import re

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from api.models import AddJoke
from api.models import CreateUser
from api.models import ShowJoke
from api.models import ShowUser
from api.models import FavJoke
from db.dals import *


JOKE_URL = 'http://rzhunemogu.ru/RandJSON.aspx?CType=1'

def _generate_alias(
        content: str
):
    alias = content[:20]
    for i in range(19):
        if alias[i] == '\n':
            if i == 18:
                alias = alias[:i-1]
            else:
                alias = alias[:i-1] + ' ' + alias[i+1:]
    alias += "..."
    return alias


async def _get_joke_from_api():
    async with httpx.AsyncClient() as client:
        response = await client.get(JOKE_URL)
        content = response.text[12:-2]
        pattern = r'\r\n(?![A-Я-"])'
        content = re.sub(pattern, ' ', content)
        return content



async def _get_or_create_user(user_id: str, session) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_or_create_user(
            user_id=user_id
        )
        return ShowUser(user_id=user.id)


async def _get_joke_by_id(
        joke_id: UUID,
        session
) -> Union[ShowJoke, None]:
    async with session.begin():
        joke_dal = JokeDAL(session)
        joke = await joke_dal.get_joke_by_id(joke_id=joke_id)
        if joke:
            print(joke.content, joke.id, joke.alias)
            return ShowJoke(content=joke.content,
                            alias=joke.alias)


async def _add_joke(
        content: str,
        session
) -> UUID:
    async with session.begin():
        alias = str(_generate_alias(content))
        joke_dal = JokeDAL(session)
        joke = await joke_dal.add_joke(content=content, alias=alias)
        return joke.id


async def _add_fav_joke(
        content: str,
        user_id: str,
        session
):
    user = await _get_or_create_user(user_id, session)
    joke = await _add_joke(content,
                           session)
    alias = str(_generate_alias(content))

    async with session.begin():
        fav_joke_dal = FavJokeDAL(session)
        fav_joke = await fav_joke_dal.add_fav_joke(user_id, joke)
        return FavJoke(joke_id=fav_joke.joke_id, alias=alias)


async def _get_fav_jokes(
        user_id: str,
        session
) -> List[ShowJoke]:
    fav_joke_dal = FavJokeDAL(session)
    jokes = await fav_joke_dal.get_user_fav_jokes(user_id)

    show_jokes_list = []
    for joke in jokes:
        show_jokes_list.append(ShowJoke(joke_id=joke.id,
                                        content=joke.content,
                                        alias=joke.alias))
    return show_jokes_list
