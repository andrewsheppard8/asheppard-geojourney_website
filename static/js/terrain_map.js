// ---------------------------
// terrain_map.js
// ---------------------------

let markers = [];

// ---------------------------
// Initialize map
// ---------------------------
const map = L.map('map').setView([30, 90], 4); // Center over Himalayas

// Topographic basemap (OpenTopoMap)
L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    maxZoom: 17,
    attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/">OSM</a>, <a href="https://opentopomap.org/">OpenTopoMap</a>'
}).addTo(map);

// ---------------------------
// Load existing features from Flask
// ---------------------------
if (window.geojsonFeatures && Array.isArray(window.geojsonFeatures)) {
    window.geojsonFeatures.forEach((feature, idx) => {
        const coords = feature.geometry.coordinates;
        const marker = L.marker([coords[1], coords[0]], { draggable: true })
            .addTo(map)
            .bindPopup(feature.properties.name || "Unknown");

        // Update hidden form inputs when marker is dragged
        marker.on('dragend', (e) => {
            document.querySelector(`input[name="lat_${idx}"]`).value = e.target.getLatLng().lat;
            document.querySelector(`input[name="lng_${idx}"]`).value = e.target.getLatLng().lng;
        });

        markers.push({ feature, marker });
    });

    // Auto-zoom to bounds
    const allMarkers = L.featureGroup(markers.map(m => m.marker));
    if (allMarkers.getBounds().isValid()) {
        map.fitBounds(allMarkers.getBounds().pad(0.2));
    }
}

// ---------------------------
// Click on map → fill new summit coordinates
// ---------------------------
map.on('click', function (e) {
    const { lat, lng } = e.latlng;
    document.getElementById("new_lat").value = lat.toFixed(6);
    document.getElementById("new_lng").value = lng.toFixed(6);
});

// ---------------------------
// Simple Nominatim Geocoding
// ---------------------------
const geocodeBtn = document.getElementById("geocode-btn");
const addressInput = document.getElementById("address-input");

if (geocodeBtn && addressInput) {
    geocodeBtn.addEventListener("click", () => {
        const query = addressInput.value.trim();
        if (!query) return;

        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`;

        fetch(url)
            .then(res => res.json())
            .then(results => {
                if (results.length === 0) {
                    alert("Location not found.");
                    return;
                }

                const place = results[0];
                const lat = parseFloat(place.lat);
                const lon = parseFloat(place.lon);

                // Add marker for the searched summit
                const marker = L.marker([lat, lon], { draggable: true })
                    .addTo(map)
                    .bindPopup(`<b>${place.display_name}</b>`)
                    .openPopup();

                // Fill the new summit form fields
                document.getElementById("new_name").value = place.display_name;
                document.getElementById("new_lat").value = lat.toFixed(6);
                document.getElementById("new_lng").value = lon.toFixed(6);

                // Optional: zoom to location
                map.setView([lat, lon], 12);

                markers.push({ feature: { properties: { name: place.display_name } }, marker });
            })
            .catch(err => console.error("Geocoding error:", err));
    });
}