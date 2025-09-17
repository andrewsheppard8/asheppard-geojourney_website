// --------------------------
// Initialize Leaflet Map
// --------------------------
const map = L.map('map').setView([20, 80], 2); // center world view

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// --------------------------
// Fetch GeoJSON and add to map
// --------------------------
let geojsonData = null;

fetch("/static/data/cities.geojson")
  .then(res => res.json())
  .then(data => {
      geojsonData = data;

      // Add GeoJSON points to map
      L.geoJSON(geojsonData, {
          onEachFeature: function(feature, layer) {
              const cityName = feature.properties?.city || "Unknown";
              layer.bindPopup(`<strong>${cityName}</strong>`);
          }
      }).addTo(map);

      // Fit map to all markers
      const bounds = L.geoJSON(geojsonData).getBounds();
      if (bounds.isValid()) map.fitBounds(bounds);

  })
  .catch(err => console.error("Error loading GeoJSON:", err));

// --------------------------
// Existing button logic (GeoJSON toggle & download)
// --------------------------
const container = document.getElementById("map-buttons");

// Toggle GeoJSON display
const toggleBtn = document.createElement("button");
toggleBtn.textContent = "Show GeoJSON";
toggleBtn.style.marginRight = "10px";
container.appendChild(toggleBtn);

const output = document.getElementById("output");
toggleBtn.addEventListener("click", () => {
    if (output.style.display === "none") {
        output.style.display = "block";
        toggleBtn.textContent = "Hide GeoJSON";
        if (geojsonData) output.textContent = JSON.stringify(geojsonData, null, 2);
    } else {
        output.style.display = "none";
        toggleBtn.textContent = "Show GeoJSON";
    }
});

// Download GeoJSON
const downloadBtn = document.createElement("button");
downloadBtn.textContent = "Download GeoJSON";
container.appendChild(downloadBtn);

downloadBtn.addEventListener("click", () => {
    const link = document.createElement("a");
    link.href = "/static/data/cities.geojson";
    link.download = "cities.geojson";
    document.body.appendChild(link);
    setTimeout(() => {
        link.click();
        document.body.removeChild(link);
    }, 100);
});