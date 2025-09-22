let geojsonData = null;  // store once
let markers = [];         // store markers to link with timeline

// ---------------------------
// Initialize map
// ---------------------------
const map = L.map('map').setView([20, 80], 2);

// Light tiles from Carto
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(map);

// Timeline container
const timeline = document.getElementById("location-list");

// ---------------------------
// Load GeoJSON
// ---------------------------
fetch("/data/cities.geojson")
    .then(res => res.json())
    .then(data => {
        geojsonData = data;

        // Sort features oldest -> newest
        geojsonData.features.sort((a, b) => {
            const dateA = a.properties.date ? new Date(a.properties.date) : new Date(0);
            const dateB = b.properties.date ? new Date(b.properties.date) : new Date(0);
            return dateA - dateB;
        });

        // Initialize marker cluster group
        const markerCluster = L.markerClusterGroup();

        // Add markers to cluster
        geojsonData.features.forEach((feature, i) => {
            const coords = feature.geometry.coordinates;
            const cityName = feature.properties.city || "Unknown";
            const dateStr = feature.properties.date || "";
            const formattedDate = dateStr ? new Date(dateStr).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }) : "";

            const marker = L.marker([coords[1], coords[0]], { opacity: 0.8 })
                .bindPopup(`<b>${cityName}</b><br>${formattedDate}`)
                .bindTooltip(cityName, {
                    permanent: true,
                    direction: "top",
                    className: "city-label"
                });

            markerCluster.addLayer(marker);
            markers.push({ feature, layer: marker });
        });

        // Add cluster to map
        map.addLayer(markerCluster);

        // Auto-zoom to bounds
        if (markerCluster.getBounds().isValid()) {
            map.fitBounds(markerCluster.getBounds().pad(0.2));
        }

        // ---------------------------
        // Build interactive timeline
        // ---------------------------
        markers.forEach((m, i) => {
            const li = document.createElement("li");
            li.textContent = `${new Date(m.feature.properties.date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            })} - ${m.feature.properties.city || "Unknown"}`;

            // Style for pointer
            li.style.cursor = "pointer";
            li.style.padding = "4px 6px";
            li.style.borderRadius = "4px";
            li.style.marginBottom = "2px";

            // Click: highlight, open popup, zoom
            li.addEventListener("click", () => {
                document.querySelectorAll("#location-list li").forEach(item => item.classList.remove("active"));
                li.classList.add("active");

                map.setView(m.layer.getLatLng(), 12);
                m.layer.openPopup();
            });

            // Hover: highlight background and marker opacity
            li.addEventListener("mouseenter", () => {
                li.style.backgroundColor = "#d0e6ff";
                m.layer.setOpacity(1);
            });
            li.addEventListener("mouseleave", () => {
                li.style.backgroundColor = "";
                m.layer.setOpacity(0.8);
            });

            timeline.appendChild(li);
        });

        // ---------------------------
        // Zoom-dependent labels
        // ---------------------------
        const minZoomForLabels = 6; // labels appear at this zoom or above

        function updateLabels() {
            const currentZoom = map.getZoom();
            markers.forEach(m => {
                const tooltipEl = m.layer.getTooltip()?.getElement();
                if (!tooltipEl) return;

                if (currentZoom >= minZoomForLabels) {
                    tooltipEl.style.display = "block";

                    // Optional: scale font with zoom
                    const fontSize = 0.6 + (currentZoom - minZoomForLabels) * 0.05;
                    tooltipEl.style.fontSize = fontSize + "rem";

                } else {
                    tooltipEl.style.display = "none";
                }
            });
        }

        // Initialize and attach to zoom event
        updateLabels();
        map.on("zoomend", updateLabels);
    })
    .catch(err => console.error("Error loading GeoJSON:", err));

// ---------------------------
// Simple Nominatim Geocoding
// ---------------------------
document.getElementById("geocode-btn").addEventListener("click", () => {
    const query = document.getElementById("address-input").value.trim();
    if (!query) return;

    // Use Nominatim API
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`;

    fetch(url)
        .then(res => res.json())
        .then(results => {
            if (results.length === 0) {
                alert("Location not found.");
                return;
            }

            // Take first result
            const place = results[0];
            const lat = parseFloat(place.lat);
            const lon = parseFloat(place.lon);

            // Add marker to map
            const marker = L.marker([lat, lon], { opacity: 0.8 })
                .addTo(map)
                .bindPopup(`<b>${place.display_name}</b>`)
                .openPopup();

            // Optional: zoom to location
            map.setView([lat, lon], 12);

            // Optionally store this marker if you want timeline interactions
            markers.push({ feature: { properties: { city: place.display_name, date: "" } }, layer: marker });
        })
        .catch(err => console.error("Geocoding error:", err));
});