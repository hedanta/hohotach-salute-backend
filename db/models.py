import uuid

from sqlalchemy import Column, Integer, Text, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()
# Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    favourites = relationship("Favourite", back_populates="users")


class Joke(Base):
    __tablename__ = 'jokes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    alias = Column(Text, nullable=True)
    favourites = relationship("Favourite", back_populates="jokes")
    # category_id = Column(Integer, ForeignKey('jokes_category.category_id'), nullable=True)


class Favourite(Base):
    __tablename__ = 'favourites'
    user_id = Column(String, ForeignKey('users.id'), primary_key=True)
    joke_id = Column(UUID(as_uuid=True), ForeignKey('jokes.id'), primary_key=True)
    users = relationship("User", back_populates="favourites")
    jokes = relationship("Joke", back_populates="favourites")


'''
class JokesCategory(Base):
    __tablename__ = 'jokes_category'
    category_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    jokes = relationship("Joke", back_populates="jokes_category")
'''
