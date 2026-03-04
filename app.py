"""
MoviWeb – Flask application.

This is the Flask app entry point. It provides the web UI (HTML/CSS, forms)
and uses the DataManager class (data package) for all database operations.

Run: python app.py
Then open: http://127.0.0.1:5000
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from data.models import db
from data import DataManager, fetch_movie_by_title

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "moviweb-dev-secret")

# Session cookie settings for HTTPS (e.g. PythonAnywhere): set PREFER_HTTPS=1 in env
_prefer_https = os.environ.get("PREFER_HTTPS", "").strip().lower() in (
    "1", "true", "yes"
)
if _prefer_https:
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

_db_path = os.environ.get("MOVIWEB_DB") or os.path.join(
    os.path.dirname(__file__), "data", "moviweb.db"
)
if not _db_path.startswith("sqlite:"):
    _db_path = "sqlite:///" + _db_path.replace("\\", "/")
app.config["SQLALCHEMY_DATABASE_URI"] = _db_path
db.init_app(app)
with app.app_context():
    db.create_all()
    # Ensure from_omdb column exists (migration for existing DBs)
    try:
        r = db.session.execute(text("PRAGMA table_info(movies)")).fetchall()
        cols = {row[1] for row in r}
        if "from_omdb" not in cols:
            db.session.execute(text(
                "ALTER TABLE movies ADD COLUMN from_omdb INTEGER DEFAULT 0"
            ))
            db.session.commit()
        if "rating" not in cols:
            db.session.execute(text("ALTER TABLE movies ADD COLUMN rating REAL"))
            db.session.commit()
        if "imdb_id" not in cols:
            db.session.execute(
                text("ALTER TABLE movies ADD COLUMN imdb_id VARCHAR(20)")
            )
            db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
data_manager = DataManager()


@app.errorhandler(404)
def page_not_found(_e):
    """Render 404 Not Found page."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(_e):
    """Render 500 Internal Server Error page."""
    return render_template("500.html"), 500


@app.route("/")
def index():
    """Show the users list (home page)."""
    users = data_manager.get_all_users()
    return render_template("users.html", users=users)


@app.route("/users", methods=["GET"])
def list_users():
    """List all users (HTML page with user list and add-user form)."""
    try:
        users = data_manager.get_all_users()
        return render_template("users.html", users=users)
    except SQLAlchemyError:
        flash("A temporary error occurred. Please try again.", "error")
        return redirect(url_for("index"))


@app.route("/users", methods=["POST"])
def create_user():
    """Create a new user (from task form on /users page)."""
    name = request.form.get("name", "").strip()
    if not name:
        flash("Please enter a name.", "error")
        return redirect(url_for("list_users"))
    try:
        user = data_manager.create_user(name)
    except SQLAlchemyError:
        flash("A temporary error occurred. Please try again.", "error")
        return redirect(url_for("list_users"))
    if user is None:
        flash("A user with this name already exists.", "error")
        return redirect(url_for("list_users"))
    flash(f"User \"{user.name}\" created.", "success")
    return redirect(url_for("list_users"))


@app.route("/users/<int:user_id>")
def get_movies(user_id):
    """Show a user's list of favorite movies (task: link from /users)."""
    try:
        user = data_manager.get_user_by_id(user_id)
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("list_users"))
        movies = data_manager.get_user_movies(user_id)
        return render_template("movie_list.html", user=user, movies=movies)
    except SQLAlchemyError:
        flash("A temporary error occurred. Please try again.", "error")
        return redirect(url_for("list_users"))


def _handle_user_select_post():
    """Handle POST for user/select. Returns Flask response or None."""
    action = request.form.get("action")
    result = None
    if action == "create":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Please enter a name.", "error")
            result = redirect(url_for("user_select"))
        else:
            try:
                user = data_manager.create_user(name)
                if user is None:
                    flash("A user with this name already exists.", "error")
                    result = redirect(url_for("user_select"))
                else:
                    session["user_id"] = user.id
                    session["user_name"] = user.name
                    flash(f"Welcome, {user.name}!", "success")
                    result = redirect(url_for("movie_list"))
            except SQLAlchemyError:
                flash("A temporary error occurred. Please try again.", "error")
                result = redirect(url_for("user_select"))
    elif action == "select":
        uid = request.form.get("user_id", type=int)
        if uid:
            try:
                user = data_manager.get_user_by_id(uid)
                if user:
                    session["user_id"] = user.id
                    session["user_name"] = user.name
                    result = redirect(url_for("movie_list"))
                else:
                    flash("Please select a user.", "error")
            except SQLAlchemyError:
                flash("A temporary error occurred. Please try again.", "error")
                result = redirect(url_for("user_select"))
        else:
            flash("Please select a user.", "error")
    return result


@app.route("/user/select", methods=["GET", "POST"])
def user_select():
    """Log in: select identity from list of users (or create new user)."""
    if request.method == "POST":
        response = _handle_user_select_post()
        if response is not None:
            return response
    try:
        users = data_manager.get_all_users()
        return render_template("user_select.html", users=users)
    except SQLAlchemyError:
        flash("A temporary error occurred. Please try again.", "error")
        return redirect(url_for("index"))


@app.route("/user/logout")
def user_logout():
    """Clear session and redirect to user selection."""
    session.clear()
    return redirect(url_for("user_select"))


@app.route("/movies")
def movie_list():
    """Show the logged-in user's movies."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("user_select"))
    try:
        user = data_manager.get_user_by_id(user_id)
        if not user:
            session.clear()
            return redirect(url_for("user_select"))
        movies = data_manager.get_user_movies(user_id)
        return render_template("movie_list.html", user=user, movies=movies)
    except SQLAlchemyError:
        flash("A temporary error occurred. Please try again.", "error")
        session.clear()
        return redirect(url_for("user_select"))


def _handle_movie_add_post(user_id, user):
    """Handle POST for movies/add. Returns Flask response or None."""
    name = request.form.get("title", "").strip()
    if not name:
        flash("Please enter a movie name.", "error")
        return render_template("movie_add.html", user=user)
    info = fetch_movie_by_title(name)
    try:
        if info:
            data_manager.add_movie(user_id, info["title"], details={
                "year": info.get("year"),
                "director": info.get("director"),
                "poster_url": info.get("poster_url"),
                "rating": info.get("rating"),
                "imdb_id": info.get("imdb_id"),
                "from_omdb": True,
            })
            flash(f'Movie "{info["title"]}" added with details from OMDb.', "success")
        else:
            data_manager.add_movie(user_id, name, details={"from_omdb": False})
            flash(f'Movie "{name}" added (OMDb did not return details).', "info")
        return redirect(url_for("movie_list"))
    except SQLAlchemyError:
        flash("A temporary error occurred. Please try again.", "error")
        return render_template("movie_add.html", user=user)


@app.route("/movies/add", methods=["GET", "POST"])
def movie_add():
    """Add a movie: user enters the name, app fetches other info from OMDb."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("user_select"))
    try:
        user = data_manager.get_user_by_id(user_id)
    except SQLAlchemyError:
        flash("A temporary error occurred. Please try again.", "error")
        session.clear()
        return redirect(url_for("user_select"))
    if not user:
        session.clear()
        return redirect(url_for("user_select"))
    if request.method == "POST":
        response = _handle_movie_add_post(user_id, user)
        if response is not None:
            return response
    return render_template("movie_add.html", user=user)


@app.route("/movies/<int:movie_id>/edit", methods=["GET", "POST"])
def movie_edit(movie_id):
    """Update a movie: modify the information of a movie from the user's list."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("user_select"))
    try:
        movie = data_manager.get_movie_by_id(movie_id)
        if not movie or movie.user_id != user_id:
            flash("Movie not found or access denied.", "error")
            return redirect(url_for("movie_list"))
        user = data_manager.get_user_by_id(user_id)
    except SQLAlchemyError:
        flash("A temporary error occurred. Please try again.", "error")
        return redirect(url_for("movie_list"))

    if request.method == "POST":
        note = request.form.get("note", "").strip() or None
        try:
            data_manager.update_movie(movie_id, {"note": note})
            flash("Movie updated.", "success")
            return redirect(url_for("movie_list"))
        except SQLAlchemyError:
            flash("A temporary error occurred. Please try again.", "error")
            return render_template("movie_edit.html", user=user, movie=movie)
    return render_template("movie_edit.html", user=user, movie=movie)


@app.route("/movies/<int:movie_id>/delete", methods=["POST"])
def movie_delete(movie_id):
    """Remove a movie from the user's list."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("user_select"))
    try:
        movie = data_manager.get_movie_by_id(movie_id)
        if not movie or movie.user_id != user_id:
            flash("Movie not found or access denied.", "error")
            return redirect(url_for("movie_list"))
        data_manager.delete_movie(movie_id)
        flash("Movie removed from your list.", "success")
        return redirect(url_for("movie_list"))
    except SQLAlchemyError:
        flash("A temporary error occurred. Please try again.", "error")
        return redirect(url_for("movie_list"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
