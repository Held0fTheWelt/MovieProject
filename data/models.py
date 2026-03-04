"""
SQLAlchemy ORM models for the database.

ORM (object-relational mapping): work with Python objects that map to database
tables and have in-built methods to communicate with the database.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """At least: a unique identifier (id) and a name (name)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)  # unique identifier
    name = Column(String(100), nullable=False, unique=True)  # name
    movies = relationship("Movie", back_populates="user", cascade="all, delete-orphan")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # foreign key to User
    title = Column(String(200), nullable=False)
    year = Column(String(20), nullable=True)
    director = Column(String(200), nullable=True)
    poster_url = Column(String(500), nullable=True)
    note = Column(Text, nullable=True)
    from_omdb = Column(Boolean, default=False, nullable=False)
    user = relationship("User", back_populates="movies")
