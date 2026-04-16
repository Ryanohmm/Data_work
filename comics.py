"""
comics.py
---------
Builds a SQLite database for comic character analytics.

This script expects a cleaned CSV exported from the Jupyter notebook
containing the fields:

    name, ALIGN, SEX, publisher, APPEARANCES, YEAR

The goal here is to:
    - load the cleaned dataset
    - build the simplified database schema
    - populate Characters, Sex, Align, Appearances
    - expose helper query functions
"""

import sqlite3
import pandas as pd
from pathlib import Path



# Load cleaned character data

def load_data(cleaned_path: str) -> pd.DataFrame:
    path = Path(cleaned_path)

    if not path.exists():
        raise FileNotFoundError(f"Cleaned data not found: {cleaned_path}")

    df = pd.read_csv(path)

    required_cols = {"name", "ALIGN", "SEX", "publisher", "APPEARANCES", "YEAR"}
    missing = required_cols - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df



# Build simplified database schema

def build_database(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    tables = ["Appearances", "Characters", "Sex", "Align"]
    for t in tables:
        cur.execute(f"DROP TABLE IF EXISTS {t}")

    cur.execute("""
        CREATE TABLE Sex (
            sex_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sex_label TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE Align (
            align_id INTEGER PRIMARY KEY AUTOINCREMENT,
            align_label TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE Characters (
            character_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            publisher TEXT NOT NULL,
            sex_id INTEGER,
            align_id INTEGER,
            FOREIGN KEY (sex_id) REFERENCES Sex(sex_id),
            FOREIGN KEY (align_id) REFERENCES Align(align_id)
        )
    """)

    cur.execute("""
        CREATE TABLE Appearances (
            appearance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            appearances INTEGER NOT NULL,
            year INTEGER NOT NULL,
            FOREIGN KEY (character_id) REFERENCES Characters(character_id)
        )
    """)

    conn.commit()
    return conn



# Populate all tables

def populate_all(conn: sqlite3.Connection, df: pd.DataFrame) -> None:
    cur = conn.cursor()

    # Remove rows where ALIGN or SEX is missing
    df = df.dropna(subset=["ALIGN", "SEX"])

    # Ensure ALIGN and SEX are strings
    df["ALIGN"] = df["ALIGN"].astype(str)
    df["SEX"] = df["SEX"].astype(str)


   
    # Insert unique SEX values
    
    sex_values = sorted(df["SEX"].dropna().unique())
    cur.executemany("INSERT INTO Sex (sex_label) VALUES (?)", [(s,) for s in sex_values])

    cur.execute("SELECT sex_id, sex_label FROM Sex")
    sex_map = {label: sid for sid, label in cur.fetchall()}

    
    # Insert unique ALIGN values
    
    align_values = sorted(df["ALIGN"].dropna().unique())
    cur.executemany("INSERT INTO Align (align_label) VALUES (?)", [(a,) for a in align_values])

    cur.execute("SELECT align_id, align_label FROM Align")
    align_map = {label: aid for aid, label in cur.fetchall()}

    
    # Insert Characters
    
    character_rows = [
        (row["name"], row["publisher"], sex_map[row["SEX"]], align_map[row["ALIGN"]])
        for _, row in df.iterrows()
    ]

    cur.executemany("""
        INSERT INTO Characters (name, publisher, sex_id, align_id)
        VALUES (?, ?, ?, ?)
    """, character_rows)

    cur.execute("SELECT character_id, name FROM Characters")
    character_map = {name: cid for cid, name in cur.fetchall()}

    
    # Insert Appearances
    
    appearance_rows = [
        (character_map[row["name"]], int(row["APPEARANCES"]), int(row["YEAR"]))
        for _, row in df.iterrows()
    ]

    cur.executemany("""
        INSERT INTO Appearances (character_id, appearances, year)
        VALUES (?, ?, ?)
    """, appearance_rows)

    conn.commit()




# Search helper

def search_characters(conn, keyword):
    query = """
        SELECT c.character_id, c.name, c.publisher, s.sex_label, a.align_label
        FROM Characters c
        JOIN Sex s ON c.sex_id = s.sex_id
        JOIN Align a ON c.align_id = a.align_id
        WHERE c.name LIKE ?
        ORDER BY c.name
    """
    cur = conn.cursor()
    cur.execute(query, (f"%{keyword}%",))
    return cur.fetchall()



# Main

def main():
    cleaned_csv = "cleaned_characters.csv"
    db_path = "comics.db"

    print("Loading cleaned data...")
    df = load_data(cleaned_csv)

    print("Building database...")
    conn = build_database(db_path)

    print("Populating tables...")
    populate_all(conn, df)

    conn.close()
    print("Database build complete.")


if __name__ == "__main__":
    main()
