import sqlite3
# import markdown
import os
import io
import zipfile
import json
from PIL import Image
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response, send_file, send_from_directory
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env for admin credentials
load_dotenv()

# -------------------------
# Flask App Initialization
# -------------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")

# -------------------------
# Paths and Folders
# -------------------------

# Use persistent disk location if available
# Use /var/data if it exists (Render persistent disk), otherwise use ./db locally

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------
# Persistent directory
# -------------------------
if os.path.exists("/var/data"):
    PERSISTENT_DIR = "/var/data"
else:
    PERSISTENT_DIR = os.path.join(BASE_DIR, "data")

# Normalize path (makes sure slashes are correct for OS)
PERSISTENT_DIR = os.path.abspath(PERSISTENT_DIR)
os.makedirs(PERSISTENT_DIR, exist_ok=True)

print(f"PERSISTENT_DIR is: {PERSISTENT_DIR}")
print("Contents of PERSISTENT_DIR:", os.listdir(PERSISTENT_DIR))

# -------------------------
# Database paths
# -------------------------
DB_NAME = os.path.join(PERSISTENT_DIR, "pictures.db")
BLOG_DB = os.path.join(PERSISTENT_DIR, "blog.db")
FOOD_DB = os.path.join(PERSISTENT_DIR, "food_map.db")
# UPDATES_DB = os.path.join(PERSISTENT_DIR, "site_updates.db")

# Create empty DB files if missing
for db_file in [DB_NAME, BLOG_DB,FOOD_DB]:
    if not os.path.exists(db_file):
        open(db_file, "a").close()

# -------------------------
# Images folder
# -------------------------
IMAGE_FOLDER = os.path.join(PERSISTENT_DIR, "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# GeoJSON files (persistent)
CITIES_GEOJSON = os.path.join(PERSISTENT_DIR, "cities.geojson")
MOUNTAINS_GEOJSON = os.path.join(PERSISTENT_DIR, "mountains.geojson")

for geojson_path in [CITIES_GEOJSON, MOUNTAINS_GEOJSON]:
    if not os.path.exists(geojson_path):
        with open(geojson_path, "w", encoding="utf-8") as f:
            json.dump({"type": "FeatureCollection", "features": []}, f, indent=2)

# -------------------------
# Database Connection Helpers
# -------------------------
def get_db_connection():
    """Return a connection to pictures.db with row access as dict."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def get_blog_connection():
    """Return a connection to blog.db with row access as dict."""
    conn = sqlite3.connect(BLOG_DB)
    conn.row_factory = sqlite3.Row
    return conn

# def get_updates_connection():
#     """Return a connection to site_updates.db with row access as dict."""
#     conn = sqlite3.connect(UPDATES_DB)
#     conn.row_factory = sqlite3.Row
#     return conn

def get_FOOD_connection():
    """Return a connection to blog.db with row access as dict."""
    conn = sqlite3.connect(FOOD_DB)
    conn.row_factory = sqlite3.Row
    return conn
# -------------------------------
# Load GeoJSON safely
# -------------------------------
def load_geojson(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON in {path}")
    return {"type": "FeatureCollection", "features": []}

cities_data = load_geojson(CITIES_GEOJSON)
mountains_data = load_geojson(MOUNTAINS_GEOJSON)

# Serve GeoJSON files from the persistent disk folder.
# This allows Flask to dynamically serve files from /var/data (PERSISTENT_DIR),
@app.route("/data/<path:filename>")
def serve_data(filename):
    return send_from_directory(PERSISTENT_DIR, filename)

# -------------------------
# Template Filters
# -------------------------
@app.template_filter('datetimeformat')
def datetimeformat(value):
    """Convert YYYY-MM-DD string to 'Month Day, Year' format."""
    if not value:
        return ""
    return datetime.strptime(value, "%Y-%m-%d").strftime("%B %d, %Y")

# -------------------------
# Public Routes
# -------------------------
@app.route("/")
def home():
    """Title page for website."""
    return render_template("title.html")

@app.route("/map")
def map_view():
    """Map page showing visited places."""
    return render_template("map_view.html")

@app.route("/pictures")
def pictures():
    """Public pictures page with optional sorting by date."""
    order = request.args.get("order", "desc").lower()
    if order not in ("asc", "desc"):
        order = "desc"

    conn = get_db_connection()
    pics = conn.execute(f"SELECT * FROM pictures ORDER BY date_taken {order}").fetchall()
    conn.close()

    # Format date for display
    formatted_pics = []
    for pic in pics:
        date_str = pic["date_taken"]
        formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y") if date_str else ""
        pic = dict(pic)
        pic["formatted_date"] = formatted_date
        formatted_pics.append(pic)

    toggle_order = "asc" if order == "desc" else "desc"
    return render_template(
        "pictures.html",
        pictures=formatted_pics,
        toggle_order=toggle_order,
        current_order=order
    )

@app.route("/blog")
def blog():
    """Public blog page."""
    conn = get_blog_connection()
    posts = conn.execute("SELECT * FROM posts ORDER BY date DESC").fetchall()
    conn.close()
    return render_template("blog.html", posts=posts)

# @app.route("/site_updates")
# def site_updates():
#     """Public site updates page."""
#     conn = get_updates_connection()
#     posts = conn.execute("SELECT * FROM posts ORDER BY date DESC").fetchall()
#     conn.close()

#     # Convert Markdown description to HTML
#     posts_html = []
#     for post in posts:
#         post = dict(post)
#         post["description"] = markdown.markdown(post["description"], extensions=["fenced_code", "codehilite"])
#         posts_html.append(post)

#     return render_template("site_updates.html", posts=posts_html)


# @app.route("/get_coordinates/<city_name>")
# def get_coordinates(city_name):
#     """Return coordinates of a city from GeoJSON."""
#     city_name = city_name.lower()
#     for feat in geo_data.get("features", []):
#         if feat.get("properties", {}).get("city", "").lower() == city_name:
#             coords = feat["geometry"]["coordinates"]
#             return jsonify({"coordinates": f"{coords[1]}, {coords[0]}"})
#     return jsonify({"error": "City not found"}), 404

@app.route("/terrain")
def terrain():
    return render_template("terrain.html")

@app.route("/food-map")
def food_map():
    return render_template("food_map.html")

@app.route("/api/food")
def get_food():
    """Return all food locations as JSON"""
    conn = get_FOOD_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM food_locations")
    rows = cur.fetchall()
    conn.close()

    food_list = [
        {
            "id": row["id"],
            "name": row["name"],
            "cuisine": row["cuisine"],
            "rating": row["rating"],
            "coords": [row["lon"], row["lat"]],
            "desc": row["desc"],
            "link": row["link"]
        }
        for row in rows
    ]
    return jsonify(food_list)

# -------------------------
# Admin Login
# -------------------------

# Pull credentials from environment
USERNAME = os.getenv("ADMIN_USERNAME")
PASSWORD = os.getenv("ADMIN_PASSWORD")

# Decorator to protect routes
def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Login required', 401,
        {'WWW-Authenticate': 'Basic realm="Admin Area"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated



# -------------------------
# Admin Routes: Dashboard
# -------------------------
@app.route("/admin")
@requires_auth
def admin_dashboard():
    return render_template("admin_dashboard.html")

# -------------------------
# Admin Routes: Blog
# -------------------------
@app.route("/admin/blog", methods=["GET", "POST"])
@requires_auth
def admin_blog():
    """Admin interface to add, edit, and view blog posts."""
    conn = get_blog_connection()

    # Add new post
    if request.method == "POST" and "new_title" in request.form:
        conn.execute(
            "INSERT INTO posts (title, description, location, date) VALUES (?, ?, ?, ?)",
            (
                request.form["new_title"],
                request.form["new_description"],
                request.form["new_location"],
                request.form["new_date"]
            )
        )
        conn.commit()
        conn.close()
        flash("Post added successfully!")
        return redirect(url_for("admin_blog"))

    # Edit existing post
    if request.method == "POST" and "edit_id" in request.form:
        conn.execute(
            "UPDATE posts SET title=?, description=?, location=?, date=? WHERE id=?",
            (
                request.form["edit_title"],
                request.form["edit_description"],
                request.form["edit_location"],
                request.form["edit_date"],
                request.form["edit_id"]
            )
        )
        conn.commit()
        conn.close()
        flash("Post updated successfully!")
        return redirect(url_for("admin_blog"))

    # Load all posts
    posts = conn.execute("SELECT * FROM posts ORDER BY date DESC").fetchall()
    conn.close()
    return render_template("admin_blog.html", posts=posts)

@app.route("/admin/blog/delete/<int:post_id>", methods=["POST"])
def delete_blog_post(post_id):
    """Delete a blog post."""
    conn = get_blog_connection()
    conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    flash("Post deleted successfully!")
    return redirect(url_for("admin_blog"))

# -------------------------
# Admin: Site Updates
# -------------------------
# @app.route("/admin/updates", methods=["GET", "POST"])
# @requires_auth
# def admin_updates():
#     """Admin interface to add, edit, and view site updates."""
#     conn = get_updates_connection()

#     # Add new post
#     if request.method == "POST" and "new_title" in request.form:
#         conn.execute(
#             "INSERT INTO posts (title, description, location, date) VALUES (?, ?, ?, ?)",
#             (
#                 request.form["new_title"],
#                 request.form["new_description"],
#                 request.form["new_location"],
#                 request.form["new_date"]
#             )
#         )
#         conn.commit()
#         conn.close()
#         flash("Update added successfully!")
#         return redirect(url_for("admin_updates"))

#     # Edit existing post
#     if request.method == "POST" and "edit_id" in request.form:
#         conn.execute(
#             "UPDATE posts SET title=?, description=?, location=?, date=? WHERE id=?",
#             (
#                 request.form["edit_title"],
#                 request.form["edit_description"],
#                 request.form["edit_location"],
#                 request.form["edit_date"],
#                 request.form["edit_id"]
#             )
#         )
#         conn.commit()
#         conn.close()
#         flash("Update edited successfully!")
#         return redirect(url_for("admin_updates"))

#     # Load all posts
#     posts = conn.execute("SELECT * FROM posts ORDER BY date DESC").fetchall()
#     conn.close()
#     return render_template("admin_updates.html", posts=posts)


# @app.route("/admin/updates/delete/<int:post_id>", methods=["POST"])
# @requires_auth
# def delete_update(post_id):
#     conn = get_updates_connection()
#     conn.execute("DELETE FROM posts WHERE id=?", (post_id,))
#     conn.commit()
#     conn.close()
#     flash("Update deleted successfully!")
#     return redirect(url_for("admin_updates"))

# -------------------------
# Admin Routes: Pictures
# -------------------------
@app.route("/admin/pictures", methods=["GET", "POST"])
@requires_auth
def admin_pictures():
    """Admin interface to add/edit pictures."""
    conn = get_db_connection()

    if request.method == "POST":
        # Upload new picture
        if "file" in request.files:
            file = request.files["file"]
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)

            title = request.form.get("title") or os.path.splitext(file.filename)[0]
            description = request.form.get("description") or ""
            date_taken = request.form.get("date_taken") or None
            filename = file.filename
            filepath = os.path.join(IMAGE_FOLDER, filename)
            file.save(filepath)

            conn.execute(
                "INSERT INTO pictures (title, description, filename, date_taken) VALUES (?, ?, ?, ?)",
                (title, description, filename, date_taken)
            )
            conn.commit()
            flash(f"Uploaded {filename} successfully!")

        # Edit existing picture
        if "edit_id" in request.form:
            conn.execute(
                "UPDATE pictures SET title = ?, description = ?, date_taken = ? WHERE id = ?",
                (
                    request.form["edit_title"],
                    request.form["edit_description"],
                    request.form.get("edit_date"),
                    request.form["edit_id"]
                )
            )
            conn.commit()
            flash(f"Updated picture ID {request.form['edit_id']} successfully!")

        return redirect(url_for("admin_pictures"))

    # GET → display admin pictures page
    pics = conn.execute("SELECT * FROM pictures").fetchall()
    conn.close()
    return render_template("admin_pictures.html", pictures=pics)

@app.route("/admin/pictures/delete/<int:pic_id>", methods=["POST"])
def delete_picture(pic_id):
    """Delete a picture and its file from disk."""
    conn = get_db_connection()
    pic = conn.execute("SELECT filename FROM pictures WHERE id = ?", (pic_id,)).fetchone()
    if pic:
        image_path = os.path.join(IMAGE_FOLDER, pic["filename"])
        if os.path.exists(image_path):
            os.remove(image_path)
        conn.execute("DELETE FROM pictures WHERE id = ?", (pic_id,))
        conn.commit()
    conn.close()
    flash("Picture deleted successfully!")
    return redirect(url_for("admin_pictures"))

# -------------------------
# Admin Routes: Rotate Pictures
# -------------------------
@app.route("/admin/pictures/rotate/<int:pic_id>/<int:degrees>", methods=["POST"])
@requires_auth
def rotate_picture(pic_id, degrees):
    """Rotate a picture by a given number of degrees."""
    conn = get_db_connection()
    pic = conn.execute("SELECT filename FROM pictures WHERE id = ?", (pic_id,)).fetchone()
    conn.close()

    if not pic:
        flash("Picture not found!")
        return redirect(url_for("admin_pictures"))

    file_path = os.path.join(IMAGE_FOLDER, pic["filename"])
    if not os.path.exists(file_path):
        flash("File not found on disk!")
        return redirect(url_for("admin_pictures"))

    try:
        with Image.open(file_path) as img:
            # Apply rotation (degrees clockwise)
            img = img.rotate(-degrees, expand=True)  # PIL rotates counter-clockwise, so we invert
            # Preserve format
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img.save(file_path, optimize=True)
            else:
                img = img.convert("RGB")
                img.save(file_path, format="JPEG", quality=85, optimize=True)
        flash(f"Rotated picture by {degrees}° successfully!")
    except Exception as e:
        flash(f"Failed to rotate picture: {e}")

    return redirect(url_for("admin_pictures"))

# -------------------------
# Admin Routes: Map_View
# -------------------------
@app.route("/admin/geojson", methods=["GET", "POST"])
@requires_auth
def admin_geojson():
    """
    Admin page for managing the cities.geojson file.
    Supports:
      - Editing existing features (city name, date, coordinates)
      - Deleting features
      - Adding new features with coordinates
    """
    geojson_path = CITIES_GEOJSON  # <-- use persistent file

    # -------------------
    # Load existing GeoJSON
    # -------------------
    if os.path.exists(geojson_path):
        with open(geojson_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"type": "FeatureCollection", "features": []}

    if request.method == "POST":
        updated_features = []

        # -------------------
        # Update existing features
        # -------------------
        for i, feature in enumerate(data.get("features", [])):
            if request.form.get(f"delete_{i}") == "on":
                continue  # skip deleted features

            # Update properties
            feature["properties"]["city"] = request.form.get(
                f"title_{i}", feature["properties"].get("city", "")
            )
            feature["properties"]["date"] = request.form.get(
                f"date_{i}", feature["properties"].get("date", "")
            )

            # Update coordinates if provided
            try:
                lat = float(request.form.get(f"lat_{i}", feature["geometry"]["coordinates"][1]))
                lng = float(request.form.get(f"lng_{i}", feature["geometry"]["coordinates"][0]))
                feature["geometry"]["coordinates"] = [lng, lat]
            except (TypeError, ValueError):
                pass  # keep original if invalid

            updated_features.append(feature)

        data["features"] = updated_features

        # -------------------
        # Add new feature if provided
        # -------------------
        new_city = request.form.get("new_city")
        new_date = request.form.get("new_date")
        new_lat = request.form.get("new_lat")
        new_lng = request.form.get("new_lng")

        if new_city and new_lat and new_lng:
            try:
                lat = float(new_lat)
                lng = float(new_lng)
                new_feature = {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lng, lat]},
                    "properties": {"city": new_city, "date": new_date or ""}
                }
                data["features"].append(new_feature)
            except ValueError:
                pass  # ignore if coordinates are invalid

        # -------------------
        # Save updated GeoJSON back to file
        # -------------------
        os.makedirs(os.path.dirname(geojson_path), exist_ok=True)
        with open(geojson_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return redirect(url_for("admin_geojson"))

    # -------------------
    # GET request → render admin page
    # -------------------
    return render_template("admin_geojson.html", features=data.get("features", []))

# -------------------------
# Admin Routes: Terrain (Cesium)
# -------------------------
@app.route("/admin/terrain", methods=["GET", "POST"])
@requires_auth
def admin_terrain():
    """
    Admin page for managing the mountains.geojson file.
    Allows add/edit/delete of mountain summit features.
    """
    geojson_path = MOUNTAINS_GEOJSON

    # Load
    if os.path.exists(geojson_path):
        with open(geojson_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"type": "FeatureCollection", "features": []}

    if request.method == "POST":
        updated_features = []

        # Update existing
        for i, feature in enumerate(data.get("features", [])):
            if request.form.get(f"delete_{i}") == "on":
                continue

            props = feature.get("properties", {})
            props["name"] = request.form.get(f"name_{i}", props.get("name", ""))
            props["crowds"] = request.form.get(f"crowds_{i}", props.get("crowds", ""))
            props["date"] = request.form.get(f"date_{i}", props.get("date", ""))
            props["rating"] = int(request.form.get(f"rating_{i}", props.get("rating", 0)))
            props["difficulty"] = int(request.form.get(f"difficulty_{i}", props.get("difficulty", 0)))
            props["distance (mi)"] = float(request.form.get(f"distance_{i}", props.get("distance (mi)", 0)))
            props["elevation (m)"] = float(request.form.get(f"elevation_{i}", props.get("elevation (m)", 0)))

            try:
                lat = float(request.form.get(f"lat_{i}", feature["geometry"]["coordinates"][1]))
                lng = float(request.form.get(f"lng_{i}", feature["geometry"]["coordinates"][0]))
                feature["geometry"]["coordinates"] = [lng, lat]
            except (TypeError, ValueError):
                pass

            feature["properties"] = props
            updated_features.append(feature)

        data["features"] = updated_features

        # Add new
        new_name = request.form.get("new_name")
        new_lat = request.form.get("new_lat")
        new_lng = request.form.get("new_lng")
        new_elev = request.form.get("new_elevation")

        if new_name and new_lat and new_lng:
            try:
                lat = float(new_lat)
                lng = float(new_lng)
                elev = float(new_elev) if new_elev else 0
                new_feature = {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lng, lat]},
                    "properties": {
                        "name": new_name,
                        "elevation (m)": elev,
                        "date": request.form.get("new_date", ""),
                        "rating": int(request.form.get("new_rating", 0)),
                        "difficulty": int(request.form.get("new_difficulty", 0)),
                        "distance (mi)": float(request.form.get("new_distance", 0)),
                        "crowds": request.form.get("new_crowds", "")
                    }
                }
                data["features"].append(new_feature)
            except ValueError:
                pass

        # Save back to file
        with open(geojson_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    return render_template("admin_terrain.html", features=data.get("features", []))

# -------------------------
# Admin Routes: Food Map
# -------------------------
@app.route("/admin/food_map", methods=["GET", "POST"])
@requires_auth
def admin_food_map():
    """
    Admin page for managing food locations.
    Supports:
      - Editing existing entries
      - Deleting entries
      - Adding new entries
    """
    conn = get_FOOD_connection()
    cur = conn.cursor()

    # -------------------
    # Handle POST updates
    # -------------------
    if request.method == "POST":
        # Get all IDs
        cur.execute("SELECT id FROM food_locations")
        all_ids = [row["id"] for row in cur.fetchall()]

        for fid in all_ids:
            if request.form.get(f"delete_{fid}") == "on":
                cur.execute("DELETE FROM food_locations WHERE id=?", (fid,))
                continue

            cur.execute(
                """
                UPDATE food_locations
                SET name=?, cuisine=?, rating=?, lat=?, lon=?, desc=?, link=?
                WHERE id=?
                """,
                (
                    request.form.get(f"name_{fid}"),
                    request.form.get(f"cuisine_{fid}"),
                    request.form.get(f"rating_{fid}"),
                    request.form.get(f"lat_{fid}"),
                    request.form.get(f"lon_{fid}"),
                    request.form.get(f"desc_{fid}"),
                    request.form.get(f"link_{fid}"),
                    fid
                )
            )

        # Add new entry
        new_name = request.form.get("new_name")
        new_cuisine = request.form.get("new_cuisine")
        new_rating = request.form.get("new_rating")
        new_lat = request.form.get("new_lat")
        new_lon = request.form.get("new_lon")
        new_desc = request.form.get("new_desc")
        new_link = request.form.get("new_link")

        if new_name and new_cuisine and new_lat and new_lon:
            cur.execute(
                """
                INSERT INTO food_locations
                (name, cuisine, rating, lat, lon, desc, link)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (new_name, new_cuisine, new_rating, new_lat, new_lon, new_desc, new_link)
            )

        conn.commit()
        conn.close()
        return redirect(url_for("admin_food_map"))

    # -------------------
    # GET → render page
    # -------------------
    cur.execute("SELECT * FROM food_locations ORDER BY name")
    rows = cur.fetchall()

    # Convert DB rows to JSON-serializable dicts
    locations = []
    for row in rows:
        locations.append({
            "id": row["id"],
            "name": row["name"],
            "cuisine": row["cuisine"],
            "rating": row["rating"],
            "lat": row["lat"],
            "lon": row["lon"],
            "desc": row["desc"],
            "link": row["link"]
        })

    conn.close()
    return render_template("admin_food_map.html", locations=locations)

# -------------------------
# Downloading the databases
# -------------------------
@app.route("/download")
@requires_auth
def download_all():
    # Create an in-memory bytes buffer
    zip_buffer = io.BytesIO()

    # Create a zip archive in the buffer
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        
        # Add the entire data folder
        for root, dirs, files in os.walk(PERSISTENT_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                # Preserve folder structure inside the zip
                arcname = os.path.relpath(file_path, start=PERSISTENT_DIR)
                zip_file.write(file_path, arcname=arcname)

    # Make sure the buffer’s pointer is at the start
    zip_buffer.seek(0)

    # Create a filename with the current date
    date_str = datetime.now().strftime("%Y-%m-%d")
    zip_filename = f"databases_{date_str}.zip"

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name=zip_filename,
        mimetype="application/zip"
    )

# -------------------------
# Unzipping to persistent database
# -------------------------

@app.route("/admin/upload_data", methods=["GET", "POST"])
@requires_auth
def upload_data():
    import zipfile

    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if file.filename.endswith(".zip"):
            # Save to a temporary location
            temp_path = os.path.join("/tmp", file.filename)
            file.save(temp_path)

            # Unzip into PERSISTENT_DIR
            with zipfile.ZipFile(temp_path, "r") as zip_ref:
                zip_ref.extractall(PERSISTENT_DIR)

            return "Data uploaded and extracted successfully!"

    return '''
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload ZIP">
    </form>
    '''

# -------------------------
# Check database path to ensure pulling from disk
# -------------------------
@app.route("/debug/persistent_dir")
@requires_auth
def debug_persistent_dir():
    return f"PERSISTENT_DIR = {PERSISTENT_DIR}"

# -------------------------
# Check size of image file
# -------------------------
@app.route("/image_space")
@requires_auth
def image_space():
    import os

    IMAGE_FOLDER = os.path.join(PERSISTENT_DIR, "images")
    DISK_LIMIT_MB = 1024  # 1 GB

    total_size = 0
    image_count = 0

    for root, dirs, files in os.walk(IMAGE_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
                image_count += 1

    total_size_mb = total_size / (1024 * 1024)
    avg_size_mb = total_size_mb / image_count if image_count else 0
    remaining_mb = DISK_LIMIT_MB - total_size_mb
    est_additional_images = int(remaining_mb / avg_size_mb) if avg_size_mb else 0

    return f"""
    <h2>Image Storage Info</h2>
    <p>Total images: {image_count}</p>
    <p>Total size: {total_size_mb:.2f} MB</p>
    <p>Average image size: {avg_size_mb:.2f} MB</p>
    <p>Remaining space: {remaining_mb:.2f} MB</p>
    <p>Estimated additional images you can add: {est_additional_images}</p>
    """

@app.route("/image_optimize")
@requires_auth
def image_optimize():
    optimized_count = 0
    optimized_bytes_saved = 0

    for filename in os.listdir(IMAGE_FOLDER):
        file_path = os.path.join(IMAGE_FOLDER, filename)

        if not os.path.isfile(file_path):
            continue

        try:
            with Image.open(file_path) as img:
                original_size = os.path.getsize(file_path)

                # Apply EXIF orientation if present, then remove EXIF orientation tag
                try:
                    exif = img.getexif()
                    orientation = exif.get(274)  # 274 is the EXIF orientation tag
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
                    # Remove orientation to prevent re-rotation
                    if exif is not None:
                        exif[274] = 1
                except Exception:
                    pass  # No EXIF or cannot read it

                # Resize if larger than 1920px width or height
                max_dim = 1920
                if img.width > max_dim or img.height > max_dim:
                    img.thumbnail((max_dim, max_dim), Image.LANCZOS)

                # Overwrite with optimized JPEG/PNG
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    # Preserve PNG with transparency
                    img.save(file_path, optimize=True)
                else:
                    img = img.convert("RGB")  # Ensure JPEG-compatible
                    img.save(file_path, format="JPEG", quality=85, optimize=True)

                new_size = os.path.getsize(file_path)
                optimized_bytes_saved += (original_size - new_size)
                optimized_count += 1

        except Exception as e:
            print(f"Skipping {filename}: {e}")

    return f"""
    Image Optimization Complete!<br>
    Total images processed: {optimized_count}<br>
    Approximate bytes saved: {optimized_bytes_saved / 1024:.2f} KB
    """

# -------------------------
# Run the Flask App
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)