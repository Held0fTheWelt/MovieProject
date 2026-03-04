"""
Data Management: one Python class for all database operations.

Uses SQLAlchemy ORM; models are defined in models.py.
Required (per spec): get list of all users, get a user's movies, update a user's movie.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from data.models import Base, User, Movie

_data_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.environ.get("MOVIWEB_DB", os.path.join(_data_dir, "moviweb.db"))
engine = create_engine(f"sqlite:///{_db_path.replace(chr(92), '/')}", echo=False)

Base.metadata.create_all(engine)


def _ensure_from_omdb_column():
    """Add from_omdb column if the movies table existed without it."""
    with engine.connect() as conn:
        try:
            r = conn.execute(text("PRAGMA table_info(movies)"))
            cols = {row[1] for row in r.fetchall()}
        except Exception:
            return
        if "from_omdb" not in cols:
            try:
                conn.execute(text("ALTER TABLE movies ADD COLUMN from_omdb INTEGER DEFAULT 0"))
                conn.commit()
            except Exception:
                conn.rollback()


_ensure_from_omdb_column()
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

    def get_user_by_id(self, user_id):
        """Get a user by id (e.g. after selecting from the list)."""
        session = Session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()

    def get_user_movies(self, user_id):
        """Get a user's movies."""
        session = Session()
        try:
            return session.query(Movie).filter(Movie.user_id == user_id).order_by(Movie.title).all()
        finally:
            session.close()

    def add_movie(self, user_id, title, year=None, director=None, poster_url=None, note=None, from_omdb=False):
        """Add a movie to a user's list (e.g. after fetching from OMDb)."""
        session = Session()
        try:
            movie = Movie(
                user_id=user_id,
                title=title.strip(),
                year=year,
                director=director,
                poster_url=poster_url,
                note=note,
                from_omdb=from_omdb,
            )
            session.add(movie)
            session.commit()
            session.refresh(movie)
            return movie
        finally:
            session.close()

    def get_movie_by_id(self, movie_id):
        """Get a single movie by id."""
        session = Session()
        try:
            return session.query(Movie).filter(Movie.id == movie_id).first()
        finally:
            session.close()

    def delete_movie(self, movie_id):
        """Remove a movie from the database."""
        session = Session()
        try:
            movie = session.query(Movie).filter(Movie.id == movie_id).first()
            if movie:
                session.delete(movie)
                session.commit()
                return True
            return False
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
