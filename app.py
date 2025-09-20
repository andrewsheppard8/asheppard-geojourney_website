import sqlite3
import os
import io
import zipfile
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response, send_file
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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "db", "pictures.db")
IMAGE_FOLDER = os.path.join(BASE_DIR, "static", "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)  # ensure folder exists

BLOG_DB = os.path.join(BASE_DIR, "db", "blog.db")
GEOJSON_PATH = os.path.join(BASE_DIR, "static", "data", "cities.geojson")

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

# -------------------------
# Load GeoJSON for Map
# -------------------------
with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
    geo_data = json.load(f)

# Optional: print city names for verification
for feat in geo_data.get("features", []):
    print(feat.get("properties", {}).get("city"))

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

@app.route("/get_coordinates/<city_name>")
def get_coordinates(city_name):
    """Return coordinates of a city from GeoJSON."""
    city_name = city_name.lower()
    for feat in geo_data.get("features", []):
        if feat.get("properties", {}).get("city", "").lower() == city_name:
            coords = feat["geometry"]["coordinates"]
            return jsonify({"coordinates": f"{coords[1]}, {coords[0]}"})
    return jsonify({"error": "City not found"}), 404

@app.route("/terrain")
def terrain():
    return render_template("terrain.html")

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
    geojson_path = os.path.join(BASE_DIR, "static", "data", "cities.geojson")

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
    geojson_path = os.path.join(BASE_DIR, "static", "data", "mountains.geojson")

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
# Downloading the databases
# -------------------------
@app.route("/download")
@requires_auth
def download_all():
    # Create an in-memory bytes buffer
    zip_buffer = io.BytesIO()

    # Create a zip archive in the buffer
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Add database files
        zip_file.write("db/pictures.db", arcname="pictures.db")
        zip_file.write("db/blog.db", arcname="blog.db")
        zip_file.write("static/data/cities.geojson", arcname="cities.geojson")
        
        # Add the entire images folder
        for root, dirs, files in os.walk("static/images"):
            for file in files:
                file_path = os.path.join(root, file)
                # Preserve folder structure inside the zip
                arcname = os.path.relpath(file_path, start="static")
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
# Run the Flask App
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)