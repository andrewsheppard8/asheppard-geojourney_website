// ---------------------------
// admin_food_map.js
// ---------------------------
document.addEventListener("DOMContentLoaded", () => {
    // ---------------------------
    // Initialize Leaflet map
    // ---------------------------
    const map = L.map('map').setView([20, 80], 2);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    // ---------------------------
    // Populate existing markers
    // ---------------------------
    const markers = [];

    if (window.locations && Array.isArray(window.locations)) {
        window.locations.forEach(loc => {
            const marker = L.marker([loc.lat, loc.lon], { draggable: false })
                .addTo(map)
                .bindPopup(`<strong>${loc.name}</strong><br>Cuisine: ${loc.cuisine}<br>Rating: ${loc.rating}`);

            // Update hidden lat/lon inputs when dragged
            marker.on('dragend', (e) => {
                const { lat, lng } = e.target.getLatLng();
                const latInput = document.querySelector(`input[name="lat_${loc.id}"]`);
                const lonInput = document.querySelector(`input[name="lon_${loc.id}"]`);
                if (latInput) latInput.value = lat.toFixed(6);
                if (lonInput) lonInput.value = lng.toFixed(6);
            });

            markers.push(marker);
        });

        // Fit map to markers
        const group = L.featureGroup(markers);
        if (group.getBounds().isValid()) {
            map.fitBounds(group.getBounds().pad(0.2));
        }
    }

    // ---------------------------
    // Click map → populate new lat/lon
    // ---------------------------
    map.on('click', (e) => {
        const { lat, lng } = e.latlng;
        const latInput = document.getElementById("new_lat");
        const lonInput = document.getElementById("new_lon");
        if (latInput && lonInput) {
            latInput.value = lat.toFixed(6);
            lonInput.value = lng.toFixed(6);
        }
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

                    // Add temporary marker
                    const tempMarker = L.marker([lat, lon], { draggable: true })
                        .addTo(map)
                        .bindPopup(`<b>${place.display_name}</b>`)
                        .openPopup();

                    // Fill new location form
                    const latInput = document.getElementById("new_lat");
                    const lonInput = document.getElementById("new_lon");
                    const nameInput = document.querySelector('input[name="new_name"]');

                    if (latInput) latInput.value = lat.toFixed(6);
                    if (lonInput) lonInput.value = lon.toFixed(6);
                    if (nameInput) nameInput.value = place.display_name;

                    map.setView([lat, lon], 12);
                })
                .catch(err => console.error("Geocoding error:", err));
        });
    }
});