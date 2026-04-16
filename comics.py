"""
comics.py
---------
Builds a SQLite database for comic character analytics.

This script expects a cleaned CSV exported from the Jupyter notebook
containing the fields:

    name, ALIGN, SEX, publisher, APPEARANCES, YEAR

The goal here is to:
    - load the cleaned dataset
    - build the database schema
    - populate the Characters table
    - expose helper query functions
"""

import sqlite3
import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# Load cleaned character data
# ------------------------------------------------------------
def load_data(cleaned_path: str) -> pd.DataFrame:
    """
    Load the cleaned character dataset produced by the Jupyter notebook.
    """
    path = Path(cleaned_path)

    if not path.exists():
        raise FileNotFoundError(f"Cleaned data not found: {cleaned_path}")

    df = pd.read_csv(path)

    # Required columns based on your notebook cleaning
    required_cols = {"name", "ALIGN", "SEX", "publisher"}
    missing = required_cols - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


# ------------------------------------------------------------
# Build database schema
# ------------------------------------------------------------
def build_database(db_path: str) -> sqlite3.Connection:
    """
    Create a fresh SQLite database with the required tables.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Drop existing tables to ensure a clean rebuild
    tables = ["Issue_Characters", "Issues", "Series", "Characters", "Publishers"]
    for t in tables:
        cur.execute(f"DROP TABLE IF EXISTS {t}")

    # Publishers
    cur.execute("""
        CREATE TABLE Publishers (
            publisher_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT
        )
    """)

    # Characters
    cur.execute("""
        CREATE TABLE Characters (
            character_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            alignment TEXT,
            universe TEXT,
            gender TEXT
        )
    """)

    # Minimal Series + Issues tables
    cur.execute("""
        CREATE TABLE Series (
            series_id INTEGER PRIMARY KEY AUTOINCREMENT,
            publisher_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            start_year INTEGER,
            end_year INTEGER,
            FOREIGN KEY (publisher_id) REFERENCES Publishers(publisher_id)
        )
    """)

    cur.execute("""
        CREATE TABLE Issues (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_id INTEGER NOT NULL,
            issue_number INTEGER NOT NULL,
            title TEXT,
            release_date TEXT,
            FOREIGN KEY (series_id) REFERENCES Series(series_id)
        )
    """)

    cur.execute("""
        CREATE TABLE Issue_Characters (
            issue_id INTEGER NOT NULL,
            character_id INTEGER NOT NULL,
            appearance INTEGER NOT NULL,
            PRIMARY KEY (issue_id, character_id),
            FOREIGN KEY (issue_id) REFERENCES Issues(issue_id),
            FOREIGN KEY (character_id) REFERENCES Characters(character_id)
        )
    """)

    conn.commit()
    return conn


# ------------------------------------------------------------
# Populate Characters table
# ------------------------------------------------------------
def populate_characters(conn: sqlite3.Connection, df: pd.DataFrame) -> None:
    """
    Insert cleaned character data into the Characters table.
    """
    cur = conn.cursor()

    # Insert publishers
    cur.executemany("""
        INSERT INTO Publishers (name, country)
        VALUES (?, ?)
    """, [
        ("Marvel Comics", "USA"),
        ("DC Comics", "USA")
    ])

    # Prepare character rows
    character_rows = [
        (row["name"], row["ALIGN"], row["publisher"], row["SEX"])
        for _, row in df.iterrows()
    ]

    cur.executemany("""
        INSERT INTO Characters (name, alignment, universe, gender)
        VALUES (?, ?, ?, ?)
    """, character_rows)

    conn.commit()


# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------
def get_character_appearances(conn, character_name):
    """
    Return all issues a character appears in.
    """
    query = """
        SELECT i.issue_id, i.title, s.title
        FROM Characters c
        JOIN Issue_Characters ic ON c.character_id = ic.character_id
        JOIN Issues i ON ic.issue_id = i.issue_id
        JOIN Series s ON i.series_id = s.series_id
        WHERE c.name = ?
        ORDER BY i.issue_id
    """
    cur = conn.cursor()
    cur.execute(query, (character_name,))
    return cur.fetchall()


def search_characters(conn, keyword):
    """
    Search for characters by partial name match.
    """
    query = """
        SELECT character_id, name, alignment, universe, gender
        FROM Characters
        WHERE name LIKE ?
        ORDER BY name
    """
    cur = conn.cursor()
    cur.execute(query, (f"%{keyword}%",))
    return cur.fetchall()


# ------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------
def main():
    cleaned_csv = "cleaned_characters.csv"
    db_path = "comics.db"

    print("Loading cleaned data...")
    df = load_data(cleaned_csv)

    print("Building database...")
    conn = build_database(db_path)

    print("Populating Characters table...")
    populate_characters(conn, df)

    conn.close()
    print("Database build complete.")


if __name__ == "__main__":
    main()
