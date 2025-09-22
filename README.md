Asheppard GeoJourney Website

Overview
Asheppard GeoJourney is a fully interactive travel mapping and data platform built with Python and Flask. Originally created as a project to practice API development, it has evolved into a sophisticated multi-database web application that tracks adventures, hikes, and points of interest across Asia (and beyond). The platform is designed to be fully updatable directly in the browser.

Features

Interactive Maps:

Uses Leaflet, MapLibre, and Cesium for rich 2D and 3D visualizations.

Supports multiple map layers, geocoding search, filters, and custom markers.

Dynamic Data Management:

Multiple SQLite databases for storing locations, images, and travel metadata.

In-browser admin interfaces for adding, editing, and deleting locations.

GeoJSON integration for location data.

Authentication & Security:

User authentication for admin pages.

Secure handling of sensitive endpoints and operations.

Media Handling:

Automatic image cleanup and optimization.

Efficient storage and serving of media assets.

Site Updates Tracking:

Fully browser-accessible site update pages.

Keep a history of changes, additions, and edits across all mapped locations.

Some minor things I always forget:

geojson==3.2.0

git pull origin main --rebase

pip freeze > requirements.txt
