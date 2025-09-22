from pathlib import Path
from app import FOOD_DB, get_FOOD_connection  # app.py has your DB logic

def test_food_db():
    db_path = Path(FOOD_DB)
    print(f"Looking for DB at: {db_path}")

    if not db_path.exists():
        print("❌ food_map.db does not exist.")
        return

    try:
        conn = get_FOOD_connection()
        cur = conn.cursor()
        # List tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        if not tables:
            print("⚠️ Database exists but has no tables.")
        else:
            print("✅ Tables in food_map.db:", [t[0] for t in tables])
        conn.close()
    except Exception as e:
        print("❌ Error opening database:", e)

if __name__ == "__main__":
    test_food_db()