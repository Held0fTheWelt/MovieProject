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

    def add_movie(self, user_id, title, details=None):
        """Add a movie to a user's list (e.g. after fetching from OMDb).

        details: optional dict with year, director, poster_url, note, rating,
                 imdb_id, from_omdb (default False).
        """
        details = details or {}
        movie = Movie(
            user_id=user_id,
            title=title.strip(),
            year=details.get("year"),
            director=details.get("director"),
            poster_url=details.get("poster_url"),
            note=details.get("note"),
            rating=details.get("rating"),
            imdb_id=details.get("imdb_id"),
            from_omdb=details.get("from_omdb", False),
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

    def update_movie(self, movie_id, updates):
        """Update a user's movie. updates is a dict of field names to values."""
        movie = db.session.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            return None
        for key, value in updates.items():
            if hasattr(movie, key):
                setattr(movie, key, value)
        db.session.commit()
        db.session.refresh(movie)
        return movie
