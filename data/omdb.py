"""
OMDb API: Fetch movie data by title.
API key from .env (OMDB_API_KEY or OMDB_APY_KEY).
"""

import os
import requests

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Key from .env / environment: OMDB_API_KEY or OMDB_APY_KEY (MoviesApp style)
OMDB_API_KEY = os.environ.get("OMDB_API_KEY", "").strip() or os.environ.get("OMDB_APY_KEY", "").strip()

OMDB_URL = "https://www.omdbapi.com/"


def _parse_rating(value):
    """Parse imdbRating to float (1.0–10.0) or 0.0."""
    if value in (None, "", "N/A"):
        return 0.0
    try:
        f = float(str(value).strip())
        return f if 0 <= f <= 10 else 0.0
    except (ValueError, TypeError):
        return 0.0


def fetch_movie_by_title(title):
    """
    Fetch movie by title from OMDb (MoviesApp style).
    Returns dict with title, year, director, genre, plot, rating, imdb_id, poster_url
    or None on error / not found.
    """
    if not OMDB_API_KEY:
        return None
    params = {"apikey": OMDB_API_KEY, "t": title.strip()}
    try:
        r = requests.get(OMDB_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("Response") != "True":
            return None
        raw_poster = data.get("Poster")
        return {
            "title": data.get("Title", title),
            "year": data.get("Year"),
            "director": data.get("Director"),
            "genre": data.get("Genre"),
            "plot": data.get("Plot"),
            "rating": _parse_rating(data.get("imdbRating")),
            "imdb_id": data.get("imdbID"),
            "poster_url": raw_poster if raw_poster and str(raw_poster) != "N/A" else None,
        }
    except Exception:
        return None
