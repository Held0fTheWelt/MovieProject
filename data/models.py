"""
SQLAlchemy ORM models for the database.

Flask has its own SQLAlchemy package for using SQLAlchemy within a Flask application.
ORM (object-relational mapping): work with Python objects that map to database
tables and have in-built methods to communicate with the database.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """At least: a unique identifier (id) and a name (name)."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # unique identifier
    name = db.Column(db.String(100), nullable=False, unique=True)  # name
    movies = db.relationship("Movie", back_populates="user", cascade="all, delete-orphan")


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # foreign key to User
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.String(20), nullable=True)
    director = db.Column(db.String(200), nullable=True)
    poster_url = db.Column(db.String(500), nullable=True)
    note = db.Column(db.Text, nullable=True)
    from_omdb = db.Column(db.Boolean, default=False, nullable=False)
    user = db.relationship("User", back_populates="movies")
