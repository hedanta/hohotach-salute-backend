from sqlalchemy import Column, Integer, Text, ForeignKey, String
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()
# Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)
    favourites = relationship("Favourite", back_populates="users")


class JokesCategory(Base):
    __tablename__ = 'jokes_category'
    category_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    jokes = relationship("Joke", back_populates="jokes_category")


class Joke(Base):
    __tablename__ = 'jokes'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    alias = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey('jokes_category.category_id'), nullable=True)
    jokes_category = relationship("JokesCategory", back_populates="jokes")
    favourites = relationship("Favourite", back_populates="jokes")


class Favourite(Base):
    __tablename__ = 'favourites'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    joke_id = Column(Integer, ForeignKey('jokes.id'), primary_key=True)
    users = relationship("User", back_populates="favourites")
    jokes = relationship("Joke", back_populates="favourites")