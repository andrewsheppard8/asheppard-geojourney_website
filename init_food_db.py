import sqlite3
from app import FOOD_DB  # points to C:\var\data\food_map.db

def init_food_db():
    conn = sqlite3.connect(FOOD_DB)
    cur = conn.cursor()

    # Drop old table if exists (safe if empty)
    cur.execute("DROP TABLE IF EXISTS food_locations")

    # Create table
    cur.execute("""
        CREATE TABLE food_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            rating REAL NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            desc TEXT,
            link TEXT
        )
    """)

    # Optional: add sample restaurants
    sample_food = [
        ("Sushi House", "Japanese", 4.5, 37.78, -122.42,
         "Fresh sushi and sashimi with a cozy vibe.",
         "https://www.google.com/maps/dir/?api=1&destination=37.78,-122.42"),
        ("Pasta Corner", "Italian", 4.2, 37.79, -122.41,
         "Homemade pasta and classic Italian wines.",
         "https://www.google.com/maps/dir/?api=1&destination=37.79,-122.41"),
        ("Taco Fiesta", "Mexican", 4.0, 37.77, -122.43,
         "Street tacos and margaritas that hit the spot.",
         "https://www.google.com/maps/dir/?api=1&destination=37.77,-122.43")
    ]

    cur.executemany(
        "INSERT INTO food_locations (name, cuisine, rating, lat, lon, desc, link) VALUES (?, ?, ?, ?, ?, ?, ?)",
        sample_food
    )

    conn.commit()
    conn.close()
    print("✅ food_locations table created with sample data.")

if __name__ == "__main__":
    init_food_db()