import shutil
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSISTENT_DIR = os.path.join(BASE_DIR, "data")  # local folder

import shutil
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Use Render persistent disk if available, else local "data" folder
if os.path.exists("/var/data"):
    PERSISTENT_DIR = "/var/data"
else:
    PERSISTENT_DIR = os.path.join(BASE_DIR, "data")  # local folder

os.makedirs(PERSISTENT_DIR, exist_ok=True)
print("Migrating files to:", PERSISTENT_DIR)

# --- Copy databases ---
for db_file in ["pictures.db", "blog.db"]:
    src = os.path.join(BASE_DIR, "db", db_file)
    dst = os.path.join(PERSISTENT_DIR, db_file)
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f"Copied {db_file}")
    else:
        print(f"Missing source database: {src}")

# --- Copy GeoJSON files ---
for geo_file in ["cities.geojson", "mountains.geojson"]:
    src = os.path.join(BASE_DIR, "static", "data", geo_file)
    dst = os.path.join(PERSISTENT_DIR, geo_file)
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f"Copied {geo_file}")
    else:
        print(f"Missing source GeoJSON: {src}")

# --- Copy images folder ---
images_src = os.path.join(BASE_DIR, "static", "images")
images_dst = os.path.join(PERSISTENT_DIR, "images")
if os.path.exists(images_src):
    shutil.copytree(images_src, images_dst, dirs_exist_ok=True)
    print("Copied images folder")
else:
    print(f"Missing source images folder: {images_src}")

print("Migration complete!")

# Copy databases
shutil.copy(os.path.join(BASE_DIR, "db", "pictures.db"), os.path.join(PERSISTENT_DIR, "pictures.db"))
shutil.copy(os.path.join(BASE_DIR, "db", "blog.db"), os.path.join(PERSISTENT_DIR, "blog.db"))

# Copy GeoJSON
shutil.copy(os.path.join(BASE_DIR, "static", "data", "cities.geojson"), os.path.join(PERSISTENT_DIR, "cities.geojson"))
shutil.copy(os.path.join(BASE_DIR, "static", "data", "mountains.geojson"), os.path.join(PERSISTENT_DIR, "mountains.geojson"))

# Copy images folder
images_src = os.path.join(BASE_DIR, "static", "images")
images_dst = os.path.join(PERSISTENT_DIR, "images")
shutil.copytree(images_src, images_dst, dirs_exist_ok=True)

print("Migration complete at:", PERSISTENT_DIR)