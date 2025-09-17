import sqlite3
import os
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from datetime import datetime

# -------------------------
# Flask App Initialization
# -------------------------
app = Flask(__name__)
app.secret_key = "supersecret"  # required for flash messages

# -------------------------
# Paths and Folders
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "pictures.db")
IMAGE_FOLDER = os.path.join(BASE_DIR, "static", "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)  # ensure folder exists

BLOG_DB = os.path.join(BASE_DIR, "blog.db")
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

# -------------------------
# Admin Login
# -------------------------

# Simple credentials
USERNAME = "admin"
PASSWORD = "BurtoN12#"

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
# Run the Flask App
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)