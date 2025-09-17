import sqlite3
import os

# Base directory of the project (where this script lives)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "blog.db")
# IMAGE_FOLDER = os.path.join(BASE_DIR, "static", "images")

def init_db():
    # if not os.path.exists(IMAGE_FOLDER):
    #     raise FileNotFoundError(f"❌ Image folder not found: {IMAGE_FOLDER}")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Drop old table if you want a clean reset each time
    cur.execute("DROP TABLE IF EXISTS pictures")

    # Create fresh table
    cur.execute("""
    CREATE TABLE posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        location TEXT,
        date TEXT
    )
    """)

    # Optional: insert sample data
    sample_posts = [
        ("Everest Base Camp Trek", "Amazing trek to the base camp of Mount Everest.", "Nepal", "2025-04-10")
    ]
    # Loop through files in static/images
    # images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))]

    # data = []
    # for img in images:
    #     title = os.path.splitext(img)[0].replace("_", " ").title()  # e.g. "everest.jpg" → "Everest"
    #     description = f"A photo from {title}"  # placeholder description
    #     data.append((title, description, img))

    cur.executemany(
        "INSERT INTO posts (title, description, location, date) VALUES (?, ?, ?, ?)",
        sample_posts
    )

    conn.commit()
    conn.close()
    print(f"✅ {DB_NAME} initialized with {len(sample_posts)} sample posts.")


if __name__ == "__main__":
    init_db()