let geojsonData = null;  // store once
let markers = [];         // store markers to link with timeline

// ---------------------------
// Initialize map
// ---------------------------
const map = L.map('map').setView([20, 80], 2);

// ---------------------------
// Basemap layers
// ---------------------------
const light = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
    subdomains: 'abcd',
    maxZoom: 19
});

const dark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
    subdomains: 'abcd',
    maxZoom: 19
});

const satellite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    {
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics, and others',
        maxZoom: 19
    }
);

// Add the default basemap
light.addTo(map);

// ---------------------------
// Basemap configuration for thumbnails
// ---------------------------
const basemapThumbnails = [
    { name: "Light", layer: light, img: "https://basemaps.cartocdn.com/light_all/0/0/0.png" },
    { name: "Dark", layer: dark, img: "https://basemaps.cartocdn.com/dark_all/0/0/0.png" },
    { name: "Satellite", layer: satellite, img: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/0/0/0" }
];

// ---------------------------
// Expandable basemap widget with icon
// ---------------------------
const expandableBasemapControl = L.Control.extend({
    options: { position: "bottomleft" }, // put on left

    onAdd: function (map) {
        const container = L.DomUtil.create("div", "expandable-basemap");
        container.style.background = "white";
        container.style.padding = "5px";
        container.style.borderRadius = "2px";
        container.style.boxShadow = "0 0 5px rgba(0,0,0,0.3)";
        container.style.cursor = "pointer";
        container.style.width = "30px";
        container.style.transition = "width 0.3s";
        container.style.marginTop = "50px"; // under zoom controls
        container.style.position = "relative";

        // Use an icon image instead of text
        const icon = L.DomUtil.create("img", "", container);
        icon.src = "/static/icons/basemap.png"; // basemap icon
        // icon.website = "<a href=""https://www.flaticon.com/free-icons/map-location" title="map location icons">Map location icons created by Freepik - Flaticon</a>";
        icon.style.width = "25px";
        icon.style.height = "25px";
        icon.style.display = "block";
        icon.style.margin = "0 auto";

        // Arrow element for expand/collapse
        const arrow = L.DomUtil.create("div", "", container);
        arrow.textContent = "▼";
        arrow.style.textAlign = "center";
        arrow.style.fontSize = "0.6rem";
        arrow.style.color = "black";
        arrow.style.marginTop = "2px";

        // Content container (thumbnails)
        const content = L.DomUtil.create("div", "", container);
        content.style.display = "none";
        content.style.flexDirection = "column";
        content.style.alignItems = "center";
        const row = L.DomUtil.create("div", "", content);
        row.style.display = "flex";

        basemapThumbnails.forEach(b => {
            const thumbContainer = L.DomUtil.create("div", "", row);
            thumbContainer.style.display = "flex";
            thumbContainer.style.flexDirection = "column";
            thumbContainer.style.alignItems = "center";
            thumbContainer.style.margin = "4px";
            thumbContainer.style.transition = "transform 0.2s, box-shadow 0.2s";

            const img = L.DomUtil.create("img", "", thumbContainer);
            img.src = b.img;
            img.title = b.name;
            img.style.width = "50px";
            img.style.height = "50px";
            img.style.cursor = "pointer";
            img.style.border = b.layer === light ? "2px solid #0372eaff" : "1px solid #ccc";
            img.style.borderRadius = "3px";

            const label = L.DomUtil.create("div", "", thumbContainer);
            label.textContent = b.name;
            label.style.fontSize = "0.7rem";
            label.style.textAlign = "center";
            label.style.marginTop = "2px";
            label.style.color = "black";
            label.style.transition = "font-weight 0.2s";

            // Click to switch basemap
            img.addEventListener("click", (e) => {
                e.stopPropagation(); // IMPORTANT: prevent closing
                basemapThumbnails.forEach(x => map.removeLayer(x.layer));
                b.layer.addTo(map);
                row.querySelectorAll("img").forEach(i => i.style.border = "1px solid #ccc");
                img.style.border = "3px solid #007bff";
            });

            container.addEventListener("mouseenter", () => {
                // container.style.transform = "translateY(-5px) scale(1.1)"; // lift + grow
                container.style.background = "#f0f0f0"; // light grey on hover
            });
            container.addEventListener("mouseleave", () => {
                // container.style.transform = "translateY(0) scale(1)"; // reset
                container.style.background = "white"; // revert to white
            });

            // Hover effects
            img.addEventListener("mouseenter", () => {
                thumbContainer.style.transform = "scale(1.04)";
                thumbContainer.style.boxShadow = "0 2px 8px rgba(0,0,0,0.4)";
                label.style.fontWeight = "bold";
            });
            img.addEventListener("mouseleave", () => {
                thumbContainer.style.transform = "scale(1)";
                thumbContainer.style.boxShadow = "none";
                label.style.fontWeight = "normal";
            });
        });

        // Toggle only when clicking icon or arrow
        const toggle = () => {
            if (content.style.display === "none") {
                content.style.display = "flex";
                arrow.textContent = "▲";
                container.style.width = "auto";
            } else {
                content.style.display = "none";
                arrow.textContent = "▼";
                container.style.width = "30px";
            }
        };
        icon.addEventListener("click", toggle);
        arrow.addEventListener("click", toggle);

        // Close if user clicks outside the widget
        document.addEventListener("click", (e) => {
            if (!container.contains(e.target)) {
                content.style.display = "none";
                arrow.textContent = "▼";
                container.style.width = "30px";
            }
        });

        return container;
    }
});

// ---------------------------
// Expandable layers widget with icon
// ---------------------------
const expandableLayerControl = L.Control.extend({
    options: { position: "bottomleft" }, // put on left

    onAdd: function (map) {
        const container = L.DomUtil.create("div", "expandable-layer");
        container.style.background = "white";
        container.style.padding = "5px";
        container.style.borderRadius = "2px";
        container.style.boxShadow = "0 0 5px rgba(0,0,0,0.3)";
        container.style.cursor = "pointer";
        container.style.width = "30px";
        container.style.transition = "width 0.3s";
        container.style.marginTop = "50px"; // under zoom controls
        container.style.position = "relative";

        // Use an icon image
        const icon = L.DomUtil.create("img", "", container);
        icon.src = "/static/icons/layer.png"; // local project icon
        // icon.website = "<a href=""https://www.flaticon.com/free-icons/bundle" title="bundle icons">Bundle icons created by Amazona Adorada - Flaticon</a>";
        icon.style.width = "25px";
        icon.style.height = "25px";
        icon.style.display = "block";
        icon.style.margin = "0 auto";

        // Arrow element
        const arrow = L.DomUtil.create("div", "", container);
        arrow.textContent = "▼";
        arrow.style.textAlign = "center";
        arrow.style.fontSize = "0.6rem";
        arrow.style.color = "black";
        arrow.style.marginTop = "2px";

        // Content container
        const content = L.DomUtil.create("div", "", container);
        content.style.display = "none";
        content.style.flexDirection = "column";
        content.style.alignItems = "center";
        const row = L.DomUtil.create("div", "", content);
        row.style.display = "flex";

        // ---------------------------
        // COUNTRY LAYER TOGGLE
        // ---------------------------
        let countryLayer = null;
        let countryVisible = true; // default ON

        // Create row with checkbox + label
        const countryRow = L.DomUtil.create("div", "", content);
        countryRow.style.display = "flex";
        countryRow.style.alignItems = "center";
        countryRow.style.marginBottom = "4px";
        countryRow.style.cursor = "pointer";

        const countryCheck = L.DomUtil.create("span", "", countryRow);
        countryCheck.textContent = "✔"; // checkmark
        countryCheck.style.display = "inline-block";
        countryCheck.style.width = "16px";
        countryCheck.style.marginRight = "6px";
        countryCheck.style.color = "#000";        // <-- make checkmark dark
        countryCheck.style.fontWeight = "bold";   // optional, makes it clearer

        const countryLabel = L.DomUtil.create("span", "", countryRow);
        countryLabel.textContent = "Countries";
        countryLabel.style.fontSize = "0.85rem";
        countryLabel.style.color = "#000";

        // Load GeoJSON
        fetch("/static/layers/countries.json")
            .then(res => res.json())
            .then(data => {
                countryLayer = L.geoJSON(data, {
                    style: {
                        weight: 1,
                        fill: true,
                        fillColor: "rgba(200,200,200,0.2)"
                    },
                    onEachFeature: (feature, layer) => {
                        layer.bindPopup(feature.properties.ADMIN || "Country");
                    }
                });

                // Add by default
                countryLayer.addTo(map);
            })
            .catch(err => console.error("Error loading country boundaries:", err));

        // Toggle layer when clicking the row
        countryRow.addEventListener("click", (e) => {
            e.stopPropagation();
            if (!countryLayer) return;

            if (countryVisible) {
                map.removeLayer(countryLayer);
                countryCheck.textContent = ""; // hide checkmark
            } else {
                countryLayer.addTo(map);
                countryCheck.textContent = "✔"; // show checkmark
            }
            countryVisible = !countryVisible;
        });

        // ---------------------------
        // Expand/collapse logic
        // ---------------------------
        const toggle = () => {
            if (content.style.display === "none") {
                content.style.display = "flex";
                arrow.textContent = "▲";
                container.style.width = "auto";
            } else {
                content.style.display = "none";
                arrow.textContent = "▼";
                container.style.width = "30px";
            }
        };
        icon.addEventListener("click", toggle);
        arrow.addEventListener("click", toggle);

        document.addEventListener("click", (e) => {
            if (!container.contains(e.target)) {
                content.style.display = "none";
                arrow.textContent = "▼";
                container.style.width = "30px";
            }
        });

        return container;
    }
});

// Add layers to map
const layerControl = new expandableLayerControl();
map.addControl(layerControl);

// Add Basemap widget
const basemapControl = new expandableBasemapControl();
map.addControl(basemapControl);

// Adjust containers to be side by side
const basemapEl = document.querySelector(".expandable-basemap");
const layerEl = document.querySelector(".expandable-layer");

// Make both absolute to place them next to each other
basemapEl.style.position = "absolute";
basemapEl.style.bottom = "10px";      // same vertical alignment
basemapEl.style.left = "10px";        // distance from map edge

layerEl.style.position = "absolute";
layerEl.style.bottom = "10px";        // same vertical alignment
layerEl.style.left = (basemapEl.offsetWidth + 20) + "px";  // right of basemap widget

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