# MoviWeb

A simple Flask app to manage users and their favorite movie lists. Movie data can be fetched from the OMDb API.

# Running Instance

This project does have a running instance (for now) at:
https://held0fthewelt.pythonanywhere.com/

## Features

- **Users**: Create and select a user identity; view a list of all users.
- **Movies**: For each user, add, edit, and delete movies. Add by title; the app can fetch details (poster, year, director, rating) from OMDb.
- **Session-based login**: Select a user, then manage that user’s movie list. Poster links open the movie on IMDb.

## Requirements

- Python 3
- Dependencies in `requirements.txt`: Flask, Flask-SQLAlchemy, requests, sqlalchemy, python-dotenv

## Setup

1. Clone or download the project and go to the project folder.
2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # Linux/macOS
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Optional: Create a `.env` file in the project root with:
   - `OMDB_API_KEY=your_omdb_api_key` (for fetching movie data from OMDb)
   - `SECRET_KEY=your_secret_key` (for production; optional for local dev)
   - `PREFER_HTTPS=1` (only when running over HTTPS, e.g. PythonAnywhere)

## Run

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

## Project structure

- `app.py` – Flask app, routes, and configuration
- `data/` – Data layer: `models.py` (User, Movie), `database.py` (DataManager), `omdb.py` (OMDb API)
- `templates/` – Jinja2 HTML templates
- `static/` – CSS and static assets (e.g. `style.css`, `logo.png`)

The app uses SQLite by default; the database file is created in `data/moviweb.db`. You can override the path with the `MOVIWEB_DB` environment variable.
