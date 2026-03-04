"""
Data Management: one Python class for all database operations.

Required (per spec):
  - getting a list of all users
  - getting a user's movies
  - updating a user's movie
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()
_data_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.environ.get("MOVIWEB_DB", os.path.join(_data_dir, "moviweb.db"))
engine = create_engine(f"sqlite:///{_db_path.replace(chr(92), '/')}", echo=False)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    movies = relationship("Movie", back_populates="user", cascade="all, delete-orphan")


class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    year = Column(String(20), nullable=True)
    director = Column(String(200), nullable=True)
    poster_url = Column(String(500), nullable=True)
    note = Column(Text, nullable=True)
    user = relationship("User", back_populates="movies")


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class DataManager:
    """
    Handles all database operations.
    Spec: get list of all users, get a user's movies, update a user's movie.
    """

    def get_all_users(self):
        """Get a list of all users."""
        session = Session()
        try:
            return session.query(User).order_by(User.name).all()
        finally:
            session.close()

    def create_user(self, name):
        """Create a new user (identity). Returns the user or None if name already exists."""
        session = Session()
        try:
            name = (name or "").strip()
            if not name:
                return None
            if session.query(User).filter(User.name == name).first():
                return None
            user = User(name=name)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()

    def get_user_movies(self, user_id):
        """Get a user's movies."""
        session = Session()
        try:
            return session.query(Movie).filter(Movie.user_id == user_id).order_by(Movie.title).all()
        finally:
            session.close()

    def update_movie(self, movie_id, title=None, year=None, director=None, poster_url=None, note=None):
        """Update a user's movie. Only provided fields are changed."""
        session = Session()
        try:
            movie = session.query(Movie).filter(Movie.id == movie_id).first()
            if not movie:
                return None
            if title is not None:
                movie.title = title
            if year is not None:
                movie.year = year
            if director is not None:
                movie.director = director
            if poster_url is not None:
                movie.poster_url = poster_url
            if note is not None:
                movie.note = note
            session.commit()
            session.refresh(movie)
            return movie
        finally:
            session.close()
