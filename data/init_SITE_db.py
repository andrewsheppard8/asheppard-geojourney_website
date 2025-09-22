import sqlite3
import os
import json

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "site_update.db")

# Ensure the data folder exists
os.makedirs(BASE_DIR, exist_ok=True)

def init_db():
    """Initialize the site updates database with sample data."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Drop old table if exists
    cur.execute("DROP TABLE IF EXISTS posts")

    # Create fresh table
    cur.execute("""
    CREATE TABLE posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,        -- HTML or Markdown content
        images TEXT,             -- optional JSON array of image filenames
        location TEXT,
        date TEXT
    )
    """)

    # Optional: insert sample data
    sample_posts = [
        (
            "Everest Base Camp Trek",
            "<p>Amazing trek to the base camp of Mount Everest.</p>",
            json.dumps([]),  # images can be empty list
            "Nepal",
            "2025-04-10"
        )
    ]

    cur.executemany(
        "INSERT INTO posts (title, description, images, location, date) VALUES (?, ?, ?, ?, ?)",
        sample_posts
    )

    conn.commit()
    conn.close()
    print(f"✅ {DB_NAME} initialized with {len(sample_posts)} sample posts.")

if __name__ == "__main__":
    init_db()