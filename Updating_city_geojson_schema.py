import os
import json
from datetime import date

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build the full path to the GeoJSON
geojson_path = os.path.join(BASE_DIR, "static", "data", "cities.geojson")

# Make sure the file exists
if not os.path.exists(geojson_path):
    raise FileNotFoundError(f"{geojson_path} not found")

# Load and update
with open(geojson_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for feature in data.get("features", []):
    feature["properties"]["date"] = date.today().isoformat()  # YYYY-MM-DD

# Save back
with open(geojson_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("✅ Added date to each GeoJSON feature")