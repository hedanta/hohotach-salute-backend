from api.models import AddJoke
from api.models import CreateUser
from api.models import ShowJoke
from api.models import ShowUser
from db.dals import *


async def _get_or_create_user(user_id: str, session) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_or_create_user(
            user_id=user_id
        )
        return ShowUser(user_id=user.id)


async def _add_joke(
        body: AddJoke,
        session
) -> UUID:
    async with session.begin():
        joke_dal = JokeDAL(session)
        joke = await joke_dal.add_joke(content=body.content, alias=body.alias)
        return joke.id


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


async def _add_fav_joke(
        body: AddJoke,
        user_id: str,
        session
):
    user = await _get_or_create_user(CreateUser(user_id=user_id), session)
    joke = await _add_joke(AddJoke(content=body.content,
                                   alias=body.alias),
                           session)

    async with session.begin():
        fav_joke_dal = FavJokeDAL(session)
        fav_joke = await fav_joke_dal.add_fav_joke(user_id, joke)


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
