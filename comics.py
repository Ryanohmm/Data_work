import sqlite3

# -------------------------------------------------
# 1. CONNECT TO DATABASE
# -------------------------------------------------
# Establishes a connection to a SQLite database file named "comics.db".
# If the file does not exist, SQLite will create it.
conn = sqlite3.connect("comics.db")

# Creates a cursor object used to execute SQL commands.
cur = conn.cursor()

# -------------------------------------------------
# 2. CLEANUP: DROP EXISTING TABLES (FOR RERUNS)
# -------------------------------------------------
# Ensures a clean slate when rerunning the script by dropping tables
# if they already exist. This avoids schema conflicts or duplicate data.
tables = ["Issue_Characters", "Issues", "Series", "Characters", "Publishers"]
for t in tables:
    # Using f-string to dynamically build the DROP TABLE statement.
    cur.execute(f"DROP TABLE IF EXISTS {t};")

# -------------------------------------------------
# 3. CREATE TABLES (SCHEMA DEFINITION)
# -------------------------------------------------

# 3.1 PUBLISHERS TABLE
# - Stores comic book publishers (e.g., Marvel, DC).
# - publisher_id: Surrogate primary key, auto-incremented.
# - name: Publisher name, required.
# - country: Optional country of origin.
cur.execute("""
CREATE TABLE Publishers (
    publisher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT
);
""")

# 3.2 SERIES TABLE
# - Stores comic book series information.
# - series_id: Surrogate primary key.
# - publisher_id: Foreign key referencing Publishers, enforcing which publisher owns the series.
# - title: Series title, required.
# - start_year / end_year: Optional range of publication years.
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

# 3.3 ISSUES TABLE
# - Stores individual comic issues within a series.
# - issue_id: Surrogate primary key.
# - series_id: Foreign key linking each issue to a series.
# - issue_number: Numeric issue identifier within the series.
# - title: Optional issue title.
# - release_date: Stored as TEXT (ISO-like string).
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

# 3.4 CHARACTERS TABLE
# - Stores character-level metadata.
# - character_id: Surrogate primary key.
# - name: Character name, required.
# - alignment: Hero/Villain/etc.
# - universe: Marvel/DC/etc.
# - gender: Optional gender field.
cur.execute("""
CREATE TABLE Characters (
    character_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    alignment TEXT,
    universe TEXT,
    gender TEXT
);
""")

# 3.5 ISSUE_CHARACTERS TABLE (JUNCTION TABLE)
# - Many-to-many relationship between Issues and Characters.
# - issue_id: Foreign key to Issues.
# - character_id: Foreign key to Characters.
# - appearance: Flag/indicator (e.g., 1 = main appearance, 0 = cameo).
# Composite primary key (issue_id, character_id) ensures each character appears
# at most once per issue.
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

# Persist the schema changes to the database file.
conn.commit()
print("Schema created successfully!")

# -------------------------------------------------
# 4. INSERT SAMPLE DATA
# -------------------------------------------------

# 4.1 INSERT PUBLISHERS
# Seed the Publishers table with two major comic publishers.
cur.executemany("""
INSERT INTO Publishers (name, country)
VALUES (?, ?);
""", [
    ("Marvel Comics", "USA"),
    ("DC Comics", "USA")
])

# 4.2 INSERT SERIES
# Seed the Series table with one series per publisher.
# Assumes:
#   - Marvel Comics has publisher_id = 1
#   - DC Comics has publisher_id = 2
cur.executemany("""
INSERT INTO Series (publisher_id, title, start_year, end_year)
VALUES (?, ?, ?, ?);
""", [
    (1, "Amazing Spider-Man", 1963, None),
    (2, "Batman", 1940, None)
])

# 4.3 INSERT ISSUES
# Seed the Issues table with a few issues for each series.
cur.executemany("""
INSERT INTO Issues (series_id, issue_number, title, release_date)
VALUES (?, ?, ?, ?);
""", [
    (1, 1, "Spider-Man Debut", "1963-03-01"),
    (1, 2, "Spider-Man vs Vulture", "1963-05-01"),
    (2, 1, "Batman Begins", "1940-05-01"),
    (2, 2, "Joker's First Laugh", "1940-07-01")
])

# 4.4 INSERT CHARACTERS
# Seed the Characters table with four iconic characters.
cur.executemany("""
INSERT INTO Characters (name, alignment, universe, gender)
VALUES (?, ?, ?, ?);
""", [
    ("Spider-Man", "Hero", "Marvel", "Male"),
    ("Vulture", "Villain", "Marvel", "Male"),
    ("Batman", "Hero", "DC", "Male"),
    ("Joker", "Villain", "DC", "Male")
])

# 4.5 INSERT ISSUE-CHARACTER RELATIONSHIPS
# Links characters to the issues in which they appear.
# appearance:
#   - 1 might represent a primary or full appearance
#   - 0 might represent a cameo or secondary appearance
cur.executemany("""
INSERT INTO Issue_Characters (issue_id, character_id, appearance)
VALUES (?, ?, ?);
""", [
    (1, 1, 1),  # Spider-Man in "Spider-Man Debut"
    (2, 1, 1),  # Spider-Man in "Spider-Man vs Vulture"
    (2, 2, 0),  # Vulture cameo in "Spider-Man vs Vulture"
    (3, 3, 1),  # Batman in "Batman Begins"
    (4, 3, 1),  # Batman in "Joker's First Laugh"
    (4, 4, 0)   # Joker cameo in "Joker's First Laugh"
])

# **Purpose:** Persist all inserted sample data.
conn.commit()
print("Sample data inserted!")

# -------------------------------------------------
# 5. ANALYTICAL QUERIES
# -------------------------------------------------

# 5.1 TOTAL APPEARANCES PER CHARACTER
print("\nTotal appearances per character:")
# Counts how many issues each character appears in.
# Uses COUNT of issue_id grouped by character_id.
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
    # Each row: (character_name, total_appearances)
    print(row)

# 5.2 ISSUES WITH BOTH A HERO AND A VILLAIN
print("\nIssues with both a hero and a villain:")
# Indentifies issues that feature at least one Hero and at least one Villain.
# Strategy:
#   - Self-join Issue_Characters and Characters twice (ic1/c1 for hero, ic2/c2 for villain).
#   - Filter where one alignment is 'Hero' and the other is 'Villain'.
#   - GROUP BY issue_id to avoid duplicates.
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
    # Each row: (issue_id, issue_title, series_title)
    print(row)

# 5.3 CHARACTERS WITH ABOVE-AVERAGE APPEARANCES
print("\nCharacters with above-average appearances:")
# Finds characters whose number of appearances is greater than the average
# appearances per character.
# Inner subquery:
#   - Counts appearances per character (COUNT(issue_id) GROUP BY character_id).
#   - Computes the average of those counts.
# Outer query:
#   - Counts appearances per character again.
#   - Filters with HAVING appearances > (average).
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
    # Each row: (character_name, appearances)
    print(row)

# 5.4 SERIES WITH MORE THAN ONE ISSUE
print("\nSeries with more than one issue:")
# Indentifies series that have more than one issue in the Issues table.
# Uses COUNT of issue_id grouped by series_id and filters with HAVING.
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
    # Each row: (series_title, issue_count)
    print(row)

# -------------------------------------------------
# 6. UTILITY FUNCTIONS
# -------------------------------------------------
# Returns character appearances when searched to allow easier search than one by one.
def get_character_appearances(conn, character_name):
    """
    Returns all issues in which a given character appears.

    Parameters
    ----------
    conn : sqlite3.Connection
        Active database connection.
    character_name : str
        Exact name of the character to search for.

    Returns
    -------
    list of tuples
        Each tuple contains (issue_id, issue_title, series_title) for issues
        where the character appears, ordered by issue_id.
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
    # Creates a new cursor scoped to this function.
    cur = conn.cursor()
    # Executes parameterized query to avoid SQL injection and
    # safely substitute character_name.
    cur.execute(query, (character_name,))
    # Returns all matching rows to the caller.
    return cur.fetchall()


def add_issue_with_characters(conn, series_id, issue_number, title, release_date, character_ids):
    """
    Inserts a new issue and automatically links all provided character IDs.

    Parameters
    ----------
    conn : sqlite3.Connection
        Active database connection.
    series_id : int
        ID of the series to which this issue belongs.
    issue_number : int
        Numeric issue number within the series.
    title : str
        Title of the new issue.
    release_date : str
        Release date as a string (e.g., 'YYYY-MM-DD').
    character_ids : list of int
        List of character_id values to associate with this issue.

    Returns
    -------
    int
        The newly created issue_id.
    """
    cur = conn.cursor()

    # **Step 1:** Insert the new issue into the Issues table.
    cur.execute("""
        INSERT INTO Issues (series_id, issue_number, title, release_date)
        VALUES (?, ?, ?, ?)
    """, (series_id, issue_number, title, release_date))

    # Retrieves the auto-generated primary key for the new issue.
    issue_id = cur.lastrowid

    # **Step 2:** Link each character to the new issue in the junction table.
    for cid in character_ids:
        cur.execute("""
            INSERT INTO Issue_Characters (issue_id, character_id, appearance)
            VALUES (?, ?, 1)
        """, (issue_id, cid))

    # **Step 3:** Commit the transaction so both the issue and its relationships
    # are persisted atomically.
    conn.commit()
    return issue_id


def get_series_summary(conn, series_title):
    """
    Returns issue count, character count, and date range for a series.

    Parameters
    ----------
    conn : sqlite3.Connection
        Active database connection.
    series_title : str
        Exact title of the series to summarize.

    Returns
    -------
    tuple
        (issue_count, character_count, first_issue_date, last_issue_date)
        or (0, 0, None, None) if the series has no issues.
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
    #   - Executes an aggregate query to compute:
    #   - total distinct issues in the series
    #   - total distinct characters appearing in those issues
    #   - earliest and latest release dates
    cur.execute(query, (series_title,))
    return cur.fetchone()


def search_characters(conn, keyword):
    """
    Returns characters whose names contain the keyword.

    Parameters
    ----------
    conn : sqlite3.Connection
        Active database connection.
    keyword : str
        Substring to search for within character names (case-sensitive by default).

    Returns
    -------
    list of tuples
        Each tuple contains (character_id, name, alignment, universe) for
        characters whose names match the pattern.
    """
    query = """
        SELECT character_id, name, alignment, universe
        FROM Characters
        WHERE name LIKE ?;
    """
    cur = conn.cursor()
    # Uses a LIKE pattern with wildcards to perform a partial match
    # on the character name.
    cur.execute(query, (f"%{keyword}%",))
    return cur.fetchall()
