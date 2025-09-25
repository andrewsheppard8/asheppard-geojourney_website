// ---------------------------
// food_map.js
// ---------------------------

// Replace with your MapTiler key
const API_KEY = "pV5qrUWfj8Cyn942dyn6";

// Initialize MapLibre map
const map = new maplibregl.Map({
    container: 'map',
    style: `https://api.maptiler.com/maps/streets/style.json?key=${API_KEY}`,
    center: [0,20],
    zoom: 1
});

let foodLocations = [];
let markers = [];

// ---------------------------
// Filter elements
// ---------------------------
const cuisineFilter = document.getElementById('cuisineFilter');
const ratingFilter = document.getElementById('ratingFilter');
const ratingValue = document.getElementById('ratingValue');

// ---------------------------
// Add markers function
// ---------------------------
function getColorByRating(r) {
    if (r >= 4.5) return "#2E7D32";
    if (r >= 4.0) return "#558B2F";
    if (r >= 3.5) return "#FBC02D";
    if (r >= 3.0) return "#F57C00";
    return "#D32F2F";
}

function addMarkers(filterCuisine = "All", minRating = 0) {
    // Remove old markers
    markers.forEach(m => m.remove());
    markers = [];

    const filtered = foodLocations.filter(f =>
        (filterCuisine === "All" || f.cuisine === filterCuisine) &&
        f.rating >= minRating
    );

    filtered.forEach(loc => {
        const color = getColorByRating(loc.rating);
        const popup = new maplibregl.Popup({ offset: 25 }).setHTML(`
            <strong>${loc.name}</strong><br>
            Cuisine: ${loc.cuisine}<br>
            ⭐ ${loc.rating}<br>
            <em>${loc.desc}</em><br>
            <a href="https://www.google.com/maps/dir/?api=1&destination=${loc.coords[1]},${loc.coords[0]}" target="_blank">
                Get Directions
            </a>
        `);

        const marker = new maplibregl.Marker({ color })
            .setLngLat(loc.coords)
            .setPopup(popup)
            .addTo(map);

        markers.push(marker);
    });
}

// ---------------------------
// Update filters
// ---------------------------
function updateFilters() {
    addMarkers(cuisineFilter.value, parseFloat(ratingFilter.value));
}

// Rating slider display
ratingFilter.addEventListener('input', () => {
    ratingValue.textContent = ratingFilter.value;
    updateFilters();
});
cuisineFilter.addEventListener('change', updateFilters);

// ---------------------------
// Load data from Flask API
// ---------------------------
map.on('load', () => {
    fetch("/api/food")
        .then(res => res.json())
        .then(data => {
            foodLocations = data;

            // Populate cuisine filter
            const cuisineSet = new Set(foodLocations.map(f => f.cuisine));
            cuisineSet.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c;
                opt.textContent = c;
                cuisineFilter.appendChild(opt);
            });

            addMarkers();
        })
        .catch(err => console.error("Error fetching food locations:", err));
});

// ---------------------------
// Geocode search (Nominatim)
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

                // Center map on result
                map.flyTo({ center: [lon, lat], zoom: 12 });

                // Optional: add a temporary marker
                const tempMarker = new maplibregl.Marker({ color: "#1E88E5" })
                    .setLngLat([lon, lat])
                    .setPopup(new maplibregl.Popup().setHTML(`<b>${place.display_name}</b>`))
                    .addTo(map)
                    .togglePopup();

                // Remove marker after 5s
                setTimeout(() => tempMarker.remove(), 5000);
            })
            .catch(err => console.error("Geocoding error:", err));
    });
}

// ---------------------------
// Legend
// ---------------------------
function addLegend() {
    const legend = document.createElement('div');
    legend.id = "legend";
    legend.innerHTML = `
        <p><span style="background:#2E7D32"></span> 4.5–5 ⭐</p>
        <p><span style="background:#558B2F"></span> 4.0–4.4 ⭐</p>
        <p><span style="background:#FBC02D"></span> 3.5–3.9 ⭐</p>
        <p><span style="background:#F57C00"></span> 3.0–3.4 ⭐</p>
        <p><span style="background:#D32F2F"></span> <3 ⭐</p>
    `;
    document.body.appendChild(legend);

    const style = document.createElement('style');
    style.innerHTML = `
        #legend {
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            font-family: sans-serif;
            color: #222;
            z-index: 1;
            box-shadow: 0 0 5px rgba(0,0,0,0.3);
        }
        #legend span {
            display: inline-block;
            width: 15px;
            height: 15px;
            margin-right: 5px;
            border: 1px solid #ccc;
        }
        .maplibregl-popup-content {
            color: #222 !important;
            font-family: sans-serif;
            font-size: 14px;
        }
        .maplibregl-popup-content a {
            color: #1E88E5 !important;
            text-decoration: underline;
        }
    `;
    document.head.appendChild(style);
}

addLegend();