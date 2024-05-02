from __future__ import annotations

import uuid
from typing import Union, List
from uuid import UUID

import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Favourite, User, Joke
from sqlalchemy.orm.exc import NoResultFound


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_or_create_user(
            self,
            user_id: str
    ) -> User:
        '''Создает или возвращает пользователя по его id'''
        existing_user_query = select(User).filter_by(id=user_id)

        result = await self.db_session.execute(existing_user_query)
        existing_user = result.scalar()

        if existing_user:
            return existing_user
        else:
            new_user = User(
                id=user_id
            )
            self.db_session.add(new_user)
            await self.db_session.flush()
            return new_user


class FavJokeDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add_fav_joke(
            self,
            user_id: str,
            joke_id: UUID
    ) -> Favourite:
        existing_fav_joke = select(Favourite).filter_by(user_id=user_id, joke_id=joke_id)
        result = await self.db_session.execute(existing_fav_joke)
        existing_fav_joke = result.scalar()
        if existing_fav_joke:
            return existing_fav_joke
        else:
            new_fav_joke = Favourite(user_id=user_id, joke_id=joke_id)
            self.db_session.add(new_fav_joke)
            await self.db_session.flush()
            return new_fav_joke

    async def get_user_fav_jokes(
            self,
            user_id: str
    ):
        user_favs_query = select(Joke).join(Joke.favourites).where(Favourite.user_id == user_id)
        result = await self.db_session.execute(user_favs_query)
        result = result.scalars().all()
        return result

    async def delete_fav_joke(
            self,
            joke_id: UUID
    ):
        query = sqlalchemy.delete(Favourite).where(Favourite.joke_id == joke_id)
        await self.db_session.execute(query)
        await self.db_session.flush()



class JokeDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_joke_by_id(self, joke_id: UUID) -> Joke | None:
        """
        Retrieve a joke from the database by its ID.
        """
        query = select(Joke).filter_by(id=joke_id)
        result = await self.db_session.execute(query)
        joke = result.scalars().first()
        if joke:
            return joke

    async def add_joke(self,
                       content: str,
                       alias: str = None
    ) -> Joke:
        """
        Create and add a new joke to the database if it doesn't already exist. Alias and category_id are optional.
        """
        # Check if the joke content already exists
        existing_joke_query = select(Joke).filter_by(content=content)
        result = await self.db_session.execute(existing_joke_query)
        existing_joke = result.scalar()

        if existing_joke:
            # If a joke with the same content already exists, return it or handle as needed
            return existing_joke
        else:
            # If the joke does not exist, create and add it
            new_joke = Joke(content=content, alias=alias)
            self.db_session.add(new_joke)
            await self.db_session.flush()  # flush is used here to get the ID if needed immediately after
            return new_joke

    async def delete_joke(self, joke_id: UUID) -> None:
        """
        Delete a joke from the database by its ID.
        """
        joke = await self.get_joke_by_id(joke_id)
        await self.db_session.delete(joke)
        await self.db_session.flush()

    '''
    async def update_joke_category(self, joke_id: UUID, category_id: int) -> None:
        """
        Пока не тестил
        """
        query = select(Joke).filter_by(id=joke_id)
        result = await self.db_session.execute(query)
        try:
            joke_to_update = result.scalar_one()
            # joke_to_update.category_id = category_id
            await self.db_session.flush()
        except NoResultFound:
            raise ValueError(f"No joke found with ID {joke_id}")
    '''