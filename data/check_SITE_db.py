import sqlite3
import os

# Path to your database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "site_update.db")

def check_posts():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    try:
        # Get all table names in the database
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cur.fetchall()]
        print("Tables in the database:", tables)

        if "posts" not in tables:
            print("Table 'posts' does not exist.")
            return

        # Fetch all rows from posts
        cur.execute("SELECT * FROM posts")
        rows = cur.fetchall()

        if not rows:
            print("No posts found in the database.")
        else:
            for row in rows:
                print("ID:", row[0])
                print("Title:", row[1])
                print("Description:", row[2])
                print("Images:", row[3])
                print("Location:", row[4])
                print("Date:", row[5])
                print("-" * 40)

    except sqlite3.Error as e:
        print("Database error:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    check_posts()