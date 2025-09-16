import json
import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

"""Just testing to ensure the geojson properties are accessible"""
# Load GeoJSON once at startup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
geojson_path = os.path.join(BASE_DIR, "static", "data", "cities.geojson")
with open(geojson_path, "r", encoding="utf-8") as f:
    geo_data = json.load(f)

for feat in geo_data.get("features",[]):
    print(feat.get("properties", {}).get("city"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_coordinates/<city_name>")
def get_coordinates(city_name):
    city_name = city_name.lower()  # make case-insensitive
    for feat in geo_data.get("features", []):
        if feat.get("properties", {}).get("city", "").lower() == city_name:
            coords = feat["geometry"]["coordinates"]
            # Return as string "lat, lon"
            return jsonify({"coordinates": f"{coords[1]}, {coords[0]}"})
    return jsonify({"error": "City not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)