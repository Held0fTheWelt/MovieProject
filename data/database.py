"""
Data Management: one Python class for all database operations.

Uses Flask-SQLAlchemy (db from models.py); models are defined in models.py.
Required (per spec): get list of all users, get a user's movies, update a user's movie.
"""

from data.models import db, User, Movie


class DataManager:
    """
    Handles all database operations using Flask-SQLAlchemy's db.session.
    """

    def get_all_users(self):
        """Get a list of all users."""
        return db.session.query(User).order_by(User.name).all()

    def create_user(self, name):
        """Create a new user (identity). Returns the user or None if name already exists."""
        name = (name or "").strip()
        if not name:
            return None
        if db.session.query(User).filter(User.name == name).first():
            return None
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user

    def get_user_by_id(self, user_id):
        """Get a user by id (e.g. after selecting from the list)."""
        return db.session.query(User).filter(User.id == user_id).first()

    def get_user_movies(self, user_id):
        """Get a user's movies."""
        return db.session.query(Movie).filter(Movie.user_id == user_id).order_by(Movie.title).all()

    def add_movie(self, user_id, title, year=None, director=None, poster_url=None, note=None, rating=None, from_omdb=False):
        """Add a movie to a user's list (e.g. after fetching from OMDb)."""
        movie = Movie(
            user_id=user_id,
            title=title.strip(),
            year=year,
            director=director,
            poster_url=poster_url,
            note=note,
            rating=rating,
            from_omdb=from_omdb,
        )
        db.session.add(movie)
        db.session.commit()
        db.session.refresh(movie)
        return movie

    def get_movie_by_id(self, movie_id):
        """Get a single movie by id."""
        return db.session.query(Movie).filter(Movie.id == movie_id).first()

    def delete_movie(self, movie_id):
        """Remove a movie from the database."""
        movie = db.session.query(Movie).filter(Movie.id == movie_id).first()
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return True
        return False

    def update_movie(self, movie_id, title=None, year=None, director=None, poster_url=None, note=None, rating=None):
        """Update a user's movie. Only provided fields are changed."""
        movie = db.session.query(Movie).filter(Movie.id == movie_id).first()
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
        if rating is not None:
            movie.rating = rating
        db.session.commit()
        db.session.refresh(movie)
        return movie
