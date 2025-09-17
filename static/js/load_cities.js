// ---------------------------
// Initialize map
// ---------------------------
const map = L.map('map').setView([20, 80], 2);

// Add English OSM tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19
}).addTo(map);

// Timeline container
const timeline = document.getElementById("location-list");

let geojsonLayer = null;
let markers = []; // store markers to link with timeline

// Load GeoJSON
fetch("/static/data/cities.geojson")
  .then(res => res.json())
  .then(data => {
      // Sort features oldest -> newest
      data.features.sort((a,b) => {
          const dateA = a.properties.date ? new Date(a.properties.date) : new Date(0);
          const dateB = b.properties.date ? new Date(b.properties.date) : new Date(0);
          return dateA - dateB;
      });

      geojsonLayer = L.geoJSON(data, {
          onEachFeature: function(feature, layer) {
              const cityName = feature.properties.city || "Unknown";
              const dateStr = feature.properties.date || "";
              const formattedDate = dateStr ? new Date(dateStr).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
              }) : "";

              layer.bindPopup(`<b>${cityName}</b><br>${formattedDate}`);
              markers.push({feature, layer});
          }
      }).addTo(map);

      // Auto-zoom
      if (geojsonLayer.getBounds().isValid()) {
          map.fitBounds(geojsonLayer.getBounds().pad(0.2));
      }

      // Build interactive timeline
      markers.forEach((m, i) => {
          const li = document.createElement("li");
          li.style.cursor = "pointer";
          li.style.marginBottom = "6px";
          const cityName = m.feature.properties.city || "Unknown";
          const dateStr = m.feature.properties.date || "";
          const formattedDate = dateStr ? new Date(dateStr).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric'
          }) : "";

          li.textContent = `${formattedDate} - ${cityName}`;
          li.addEventListener("click", () => {
            //   map.setView(m.layer.getLatLng(), 8, {animate:true});
              m.layer.openPopup();
          });

          timeline.appendChild(li);
      });
  })
  .catch(err => console.error("Error loading GeoJSON:", err));