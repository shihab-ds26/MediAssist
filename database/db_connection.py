
import sqlite3
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database file location
DB_PATH = BASE_DIR / "database" / "mediassist.db"


def get_connection():
    """
    Create and return a database connection.
    """

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    # Return rows as dictionary-like objects
    connection.row_factory = sqlite3.Row

    # Enable foreign key relationships
    connection.execute("PRAGMA foreign_keys = ON")

    return connection
