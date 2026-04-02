import sqlite3

conn = sqlite3.connect("comics.db")
cur = conn.cursor()

# Drop tables if rerunning
tables = ["Issue_Characters", "Issues", "Series", "Characters", "Publishers"]
for t in tables:
    cur.execute(f"DROP TABLE IF EXISTS {t};")

# --- Create Tables ---

cur.execute("""
CREATE TABLE Publishers (
    publisher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT
);
""")

cur.execute("""
CREATE TABLE Series (
    series_id INTEGER PRIMARY KEY AUTOINCREMENT,
    publisher_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    start_year INTEGER,
    end_year INTEGER,
    FOREIGN KEY (publisher_id) REFERENCES Publishers(publisher_id)
);
""")

cur.execute("""
CREATE TABLE Issues (
    issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    issue_number INTEGER NOT NULL,
    title TEXT,
    release_date TEXT,
    FOREIGN KEY (series_id) REFERENCES Series(series_id)
);
""")

cur.execute("""
CREATE TABLE Characters (
    character_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    alignment TEXT,
    universe TEXT,
    gender TEXT
);
""")

cur.execute("""
CREATE TABLE Issue_Characters (
    issue_id INTEGER NOT NULL,
    character_id INTEGER NOT NULL,
    appearance INTEGER NOT NULL,
    PRIMARY KEY (issue_id, character_id),
    FOREIGN KEY (issue_id) REFERENCES Issues(issue_id),
    FOREIGN KEY (character_id) REFERENCES Characters(character_id)
);
""")

conn.commit()
print("Schema created successfully!")

# --- Publishers ---
cur.executemany("""
INSERT INTO Publishers (name, country)
VALUES (?, ?);
""", [
    ("Marvel Comics", "USA"),
    ("DC Comics", "USA")
])

# --- Series ---
cur.executemany("""
INSERT INTO Series (publisher_id, title, start_year, end_year)
VALUES (?, ?, ?, ?);
""", [
    (1, "Amazing Spider-Man", 1963, None),
    (2, "Batman", 1940, None)
])

# --- Issues ---
cur.executemany("""
INSERT INTO Issues (series_id, issue_number, title, release_date)
VALUES (?, ?, ?, ?);
""", [
    (1, 1, "Spider-Man Debut", "1963-03-01"),
    (1, 2, "Spider-Man vs Vulture", "1963-05-01"),
    (2, 1, "Batman Begins", "1940-05-01"),
    (2, 2, "Joker's First Laugh", "1940-07-01")
])

# --- Characters ---
cur.executemany("""
INSERT INTO Characters (name, alignment, universe, gender)
VALUES (?, ?, ?, ?);
""", [
    ("Spider-Man", "Hero", "Marvel", "Male"),
    ("Vulture", "Villain", "Marvel", "Male"),
    ("Batman", "Hero", "DC", "Male"),
    ("Joker", "Villain", "DC", "Male")
])

# --- Issue_Characters ---
cur.executemany("""
INSERT INTO Issue_Characters (issue_id, character_id, appearance)
VALUES (?, ?, ?);
""", [
    (1, 1, 1),
    (2, 1, 1),
    (2, 2, 0),
    (3, 3, 1),
    (4, 3, 1),
    (4, 4, 0)
])

conn.commit()
print("Sample data inserted!")

# ======================
# RUN YOUR QUERIES
# ======================

print("\nTotal appearances per character:")
cur.execute("""
SELECT 
    c.name AS character,
    COUNT(ic.issue_id) AS total_appearances
FROM Characters c
JOIN Issue_Characters ic ON c.character_id = ic.character_id
GROUP BY c.character_id
ORDER BY total_appearances DESC;
""")
for row in cur.fetchall():
    print(row)

print("\nIssues with both a hero and a villain:")
cur.execute("""
SELECT 
    i.issue_id,
    i.title,
    s.title AS series_title
FROM Issues i
JOIN Series s ON i.series_id = s.series_id
JOIN Issue_Characters ic1 ON i.issue_id = ic1.issue_id
JOIN Characters c1 ON ic1.character_id = c1.character_id
JOIN Issue_Characters ic2 ON i.issue_id = ic2.issue_id
JOIN Characters c2 ON ic2.character_id = c2.character_id
WHERE c1.alignment = 'Hero'
  AND c2.alignment = 'Villain'
GROUP BY i.issue_id;
""")
for row in cur.fetchall():
    print(row)

print("\nCharacters with above-average appearances:")
cur.execute("""
SELECT 
    c.name,
    COUNT(ic.issue_id) AS appearances
FROM Characters c
JOIN Issue_Characters ic ON c.character_id = ic.character_id
GROUP BY c.character_id
HAVING appearances > (
    SELECT AVG(cnt)
    FROM (
        SELECT COUNT(issue_id) AS cnt
        FROM Issue_Characters
        GROUP BY character_id
    )
);
""")
for row in cur.fetchall():
    print(row)

print("\nSeries with more than one issue:")
cur.execute("""
SELECT 
    s.title AS series_title,
    COUNT(i.issue_id) AS issue_count
FROM Series s
JOIN Issues i ON s.series_id = i.series_id
GROUP BY s.series_id
HAVING COUNT(i.issue_id) > 1;
""")
for row in cur.fetchall():
    print(row)

# ======================
# FUNCTIONS
# ======================

def get_character_appearances(conn, character_name):
    """
    Returns all issues in which a given character appears.
    """
    query = """
        SELECT i.issue_id, i.title, s.title AS series_title
        FROM Characters c
        JOIN Issue_Characters ic ON c.character_id = ic.character_id
        JOIN Issues i ON ic.issue_id = i.issue_id
        JOIN Series s ON i.series_id = s.series_id
        WHERE c.name = ?
        ORDER BY i.issue_id;
    """
    cur = conn.cursor()
    cur.execute(query, (character_name,))
    return cur.fetchall()


def add_issue_with_characters(conn, series_id, issue_number, title, release_date, character_ids):
    """
    Inserts a new issue and automatically links all provided character IDs.
    """
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Issues (series_id, issue_number, title, release_date)
        VALUES (?, ?, ?, ?)
    """, (series_id, issue_number, title, release_date))
    issue_id = cur.lastrowid

    for cid in character_ids:
        cur.execute("""
            INSERT INTO Issue_Characters (issue_id, character_id, appearance)
            VALUES (?, ?, 1)
        """, (issue_id, cid))

    conn.commit()
    return issue_id


def get_series_summary(conn, series_title):
    """
    Returns issue count, character count, and date range for a series.
    """
    query = """
        SELECT 
            COUNT(DISTINCT i.issue_id) AS issue_count,
            COUNT(DISTINCT ic.character_id) AS character_count,
            MIN(i.release_date) AS first_issue,
            MAX(i.release_date) AS last_issue
        FROM Series s
        JOIN Issues i ON s.series_id = i.series_id
        LEFT JOIN Issue_Characters ic ON i.issue_id = ic.issue_id
        WHERE s.title = ?;
    """
    cur = conn.cursor()
    cur.execute(query, (series_title,))
    return cur.fetchone()


def search_characters(conn, keyword):
    """
    Returns characters whose names contain the keyword.
    """
    query = """
        SELECT character_id, name, alignment, universe
        FROM Characters
        WHERE name LIKE ?;
    """
    cur = conn.cursor()
    cur.execute(query, (f"%{keyword}%",))
    return cur.fetchall()
