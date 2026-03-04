"""
Data package: database and OMDb access.
"""

from data.database import DataManager
from data.omdb import fetch_movie_by_title

__all__ = ["DataManager", "fetch_movie_by_title"]
