// ---------------------------
// MapLibre setup
// ---------------------------
const API_KEY = "pV5qrUWfj8Cyn942dyn6";

const map = new maplibregl.Map({
  container: 'map',
  style: `https://api.maptiler.com/maps/streets/style.json?key=${API_KEY}`,
  center: [-122.42, 37.78], // default center
  zoom: 13
});

// ---------------------------
// Global variables
// ---------------------------
let foodLocations = [];
let markers = [];
let searchMarker = null;

const cuisineFilter = document.getElementById('cuisineFilter');
const ratingFilter = document.getElementById('ratingFilter');
const ratingValue = document.getElementById('ratingValue');
const geocodeBtn = document.getElementById("geocode-btn");
const addressInput = document.getElementById("address-input");

// ---------------------------
// Helper: get marker color by rating
// ---------------------------
function getColorByRating(rating) {
  if (rating >= 4.5) return "#2E7D32"; // green
  if (rating >= 4.0) return "#FFB300"; // amber
  return "#D32F2F"; // red
}

// ---------------------------
// Add markers
// ---------------------------
function addMarkers(filterCuisine = "All", minRating = 0) {
  // Remove old markers
  markers.forEach(m => m.remove());
  markers = [];

  // Filter locations
  const filtered = foodLocations.filter(f =>
    (filterCuisine === "All" || f.cuisine === filterCuisine) &&
    f.rating >= minRating
  );

  filtered.forEach(loc => {
    const popup = new maplibregl.Popup({ offset: 25 })
      .setHTML(`
                <strong>${loc.name}</strong><br>
                Cuisine: ${loc.cuisine}<br>
                ⭐ ${loc.rating}<br>
                <em>${loc.desc}</em><br>
                <a href="${loc.link}" target="_blank">Get Directions</a>
            `);

    const marker = new maplibregl.Marker({ color: getColorByRating(loc.rating) })
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

// ---------------------------
// Event listeners for filters
// ---------------------------
ratingFilter.addEventListener('input', () => {
  ratingValue.textContent = ratingFilter.value;
  updateFilters();
});
cuisineFilter.addEventListener('change', updateFilters);

// ---------------------------
// Add legend/styles
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
}

  const style = document.createElement('style');
  style.innerHTML = `
    #legend {
      position: absolute;
      bottom: 5px;
      left: 50px;
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

// ---------------------------
// Load food data from Flask API
// ---------------------------
map.on('load', () => {
  fetch("/api/food")
    .then(res => res.json())
    .then(data => {
      foodLocations = data;

      // Populate cuisine filter dynamically
      const cuisineSet = new Set(foodLocations.map(f => f.cuisine));
      cuisineSet.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        cuisineFilter.appendChild(opt);
      });

      addMarkers(); // initial display
    })
    .catch(err => console.error("Error fetching food locations:", err));
});

// ---------------------------
// Geocoding search with Nominatim
// ---------------------------
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

        // Remove old search marker
        if (searchMarker) searchMarker.remove();

        // Add new search marker
        searchMarker = new maplibregl.Marker({ color: "#1976D2" })
          .setLngLat([lon, lat])
          .setPopup(new maplibregl.Popup({ offset: 25 })
            .setHTML(`<b>${place.display_name}</b>`))
          .addTo(map)
          .togglePopup();

        // Zoom to location
        map.flyTo({ center: [lon, lat], zoom: 12 });
      })
      .catch(err => console.error("Geocoding error:", err));
  });

  // Press Enter to search
  addressInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      geocodeBtn.click();
    }
  });
}