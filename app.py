"""
MoviWeb – Flask application.

This is the Flask app entry point. It provides the web UI (HTML/CSS, forms)
and uses the DataManager class (data package) for all database operations.

Run: python app.py
Then open: http://127.0.0.1:5000
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session

from data.models import db
from data import DataManager, fetch_movie_by_title

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "moviweb-dev-secret")
_db_path = os.environ.get("MOVIWEB_DB") or os.path.join(os.path.dirname(__file__), "data", "moviweb.db")
if not _db_path.startswith("sqlite:"):
    _db_path = "sqlite:///" + _db_path.replace("\\", "/")
app.config["SQLALCHEMY_DATABASE_URI"] = _db_path
db.init_app(app)
with app.app_context():
    db.create_all()
    # Ensure from_omdb column exists (migration for existing DBs)
    from sqlalchemy import text
    try:
        r = db.session.execute(text("PRAGMA table_info(movies)")).fetchall()
        cols = {row[1] for row in r}
        if "from_omdb" not in cols:
            db.session.execute(text("ALTER TABLE movies ADD COLUMN from_omdb INTEGER DEFAULT 0"))
            db.session.commit()
    except Exception:
        db.session.rollback()
data_manager = DataManager()


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("movie_list"))
    return redirect(url_for("user_select"))


@app.route("/user/select", methods=["GET", "POST"])
def user_select():
    """Log in: select identity from list of users (or create new user)."""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            name = request.form.get("name", "").strip()
            if not name:
                flash("Please enter a name.", "error")
                return redirect(url_for("user_select"))
            user = data_manager.create_user(name)
            if user is None:
                flash("A user with this name already exists.", "error")
                return redirect(url_for("user_select"))
            session["user_id"] = user.id
            session["user_name"] = user.name
            flash(f"Welcome, {user.name}!", "success")
            return redirect(url_for("movie_list"))
        if action == "select":
            user_id = request.form.get("user_id", type=int)
            if user_id:
                user = data_manager.get_user_by_id(user_id)
                if user:
                    session["user_id"] = user.id
                    session["user_name"] = user.name
                    return redirect(url_for("movie_list"))
            flash("Please select a user.", "error")
    users = data_manager.get_all_users()
    return render_template("user_select.html", users=users)


@app.route("/user/logout")
def user_logout():
    session.clear()
    return redirect(url_for("user_select"))


@app.route("/movies")
def movie_list():
    """Show the logged-in user's movies."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("user_select"))
    user = data_manager.get_user_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for("user_select"))
    movies = data_manager.get_user_movies(user_id)
    return render_template("movie_list.html", user=user, movies=movies)


@app.route("/movies/add", methods=["GET", "POST"])
def movie_add():
    """Add a movie: user enters the name, app fetches other info from OMDb."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("user_select"))
    user = data_manager.get_user_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for("user_select"))

    if request.method == "POST":
        name = request.form.get("title", "").strip()
        if not name:
            flash("Please enter a movie name.", "error")
            return render_template("movie_add.html", user=user)
        info = fetch_movie_by_title(name)
        if info:
            data_manager.add_movie(
                user_id=user_id,
                title=info["title"],
                year=info.get("year"),
                director=info.get("director"),
                poster_url=info.get("poster_url"),
                from_omdb=True,
            )
            flash(f'Movie "{info["title"]}" added with details from OMDb.', "success")
        else:
            data_manager.add_movie(user_id=user_id, title=name, from_omdb=False)
            flash(f'Movie "{name}" added (OMDb did not return details).', "info")
        return redirect(url_for("movie_list"))
    return render_template("movie_add.html", user=user)


@app.route("/movies/<int:movie_id>/edit", methods=["GET", "POST"])
def movie_edit(movie_id):
    """Update a movie: modify the information of a movie from the user's list."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("user_select"))
    movie = data_manager.get_movie_by_id(movie_id)
    if not movie or movie.user_id != user_id:
        flash("Movie not found or access denied.", "error")
        return redirect(url_for("movie_list"))
    user = data_manager.get_user_by_id(user_id)

    if request.method == "POST":
        note = request.form.get("note", "").strip() or None
        data_manager.update_movie(movie_id, note=note)
        flash("Movie updated.", "success")
        return redirect(url_for("movie_list"))
    return render_template("movie_edit.html", user=user, movie=movie)


@app.route("/movies/<int:movie_id>/delete", methods=["POST"])
def movie_delete(movie_id):
    """Remove a movie from the user's list."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("user_select"))
    movie = data_manager.get_movie_by_id(movie_id)
    if not movie or movie.user_id != user_id:
        flash("Movie not found or access denied.", "error")
        return redirect(url_for("movie_list"))
    data_manager.delete_movie(movie_id)
    flash("Movie removed from your list.", "success")
    return redirect(url_for("movie_list"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
