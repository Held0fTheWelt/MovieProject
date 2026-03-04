"""
SQLAlchemy ORM models for the database.

Flask has its own SQLAlchemy package for using SQLAlchemy within a Flask application.
ORM (object-relational mapping): work with Python objects that map to database
tables and have in-built methods to communicate with the database.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """User model: unique identifier (id) and name (name)."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    movies = db.relationship("Movie", back_populates="user", cascade="all, delete-orphan")


class Movie(db.Model):
    """Movie model: define all properties and link to User via user_id."""
    __tablename__ = "movies"

    # Define all the Movie properties
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.String(20), nullable=True)
    director = db.Column(db.String(200), nullable=True)
    poster_url = db.Column(db.String(500), nullable=True)
    note = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, nullable=True)  # e.g. IMDb 0–10
    imdb_id = db.Column(db.String(20), nullable=True)  # e.g. tt0137523 for IMDb link
    from_omdb = db.Column(db.Boolean, default=False, nullable=False)

    # Link Movie to User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="movies")
