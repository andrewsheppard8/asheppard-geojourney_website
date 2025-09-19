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
fetch("/static/data/cities.geojson")
    .then(res => res.json())
    .then(data => {
        geojsonData = data;

        // Sort features oldest -> newest
        geojsonData.features.sort((a, b) => {
            const dateA = a.properties.date ? new Date(a.properties.date) : new Date(0);
            const dateB = b.properties.date ? new Date(b.properties.date) : new Date(0);
            return dateA - dateB;
        });

        // ---------------------------
        // Initialize marker cluster group
        // ---------------------------
        const markerCluster = L.markerClusterGroup();

        // ---------------------------
        // Add markers to cluster instead of directly to map
        // ---------------------------
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
                .bindPopup(`<b>${cityName}</b><br>${formattedDate}`);

            markerCluster.addLayer(marker);
            markers.push({ feature, layer: marker });
        });

        // Add the cluster group to the map
        map.addLayer(markerCluster);

        // Auto-zoom to bounds
        if (markerCluster.getBounds().isValid()) {
            map.fitBounds(markerCluster.getBounds().pad(0.2));
        }

        // Add markers
        //   geojsonData.features.forEach((feature, i) => {
        //       const coords = feature.geometry.coordinates;
        //       const cityName = feature.properties.city || "Unknown";
        //       const dateStr = feature.properties.date || "";
        //       const formattedDate = dateStr ? new Date(dateStr).toLocaleDateString('en-US', {
        //           year: 'numeric',
        //           month: 'long',
        //           day: 'numeric'
        //       }) : "";

        //       const marker = L.marker([coords[1], coords[0]], {opacity:0.8})
        //                       .addTo(map)
        //                       .bindPopup(`<b>${cityName}</b><br>${formattedDate}`);

        //       markers.push({feature, layer: marker});
        //   });

        //   // Auto-zoom to bounds
        //   const allMarkers = L.featureGroup(markers.map(m => m.layer));
        //   if (allMarkers.getBounds().isValid()) {
        //       map.fitBounds(allMarkers.getBounds().pad(0.2));
        //   }

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

            // Click: highlight and open popup
            li.addEventListener("click", () => {
                // Remove active from others
                document.querySelectorAll("#location-list li").forEach(item => item.classList.remove("active"));
                li.classList.add("active");

                // Open popup
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