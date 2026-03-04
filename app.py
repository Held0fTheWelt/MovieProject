"""
MoviWeb – Flask application.

This is the Flask app entry point. It provides the web UI (HTML/CSS, forms)
and uses the DataManager class (data package) for all database operations.

Run: python app.py
Then open: http://127.0.0.1:5000
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session

from data import DataManager, fetch_movie_by_title

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "moviweb-dev-secret")
db = DataManager()


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
            user = db.create_user(name)
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
                user = db.get_user_by_id(user_id)
                if user:
                    session["user_id"] = user.id
                    session["user_name"] = user.name
                    return redirect(url_for("movie_list"))
            flash("Please select a user.", "error")
    users = db.get_all_users()
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
    user = db.get_user_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for("user_select"))
    movies = db.get_user_movies(user_id)
    return render_template("movie_list.html", user=user, movies=movies)


@app.route("/movies/add", methods=["GET", "POST"])
def movie_add():
    """Add a movie: user enters the name, app fetches other info from OMDb."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("user_select"))
    user = db.get_user_by_id(user_id)
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
            db.add_movie(
                user_id=user_id,
                title=info["title"],
                year=info.get("year"),
                director=info.get("director"),
                poster_url=info.get("poster_url"),
            )
            flash(f'Movie "{info["title"]}" added with details from OMDb.', "success")
        else:
            db.add_movie(user_id=user_id, title=name)
            flash(f'Movie "{name}" added (OMDb did not return details).', "info")
        return redirect(url_for("movie_list"))
    return render_template("movie_add.html", user=user)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
