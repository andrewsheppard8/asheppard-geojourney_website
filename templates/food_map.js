  <script src="https://unpkg.com/maplibre-gl@2.4.0/dist/maplibre-gl.js"></script>
    // Replace with your MapTiler key
    const API_KEY = "pV5qrUWfj8Cyn942dyn6";

    // Init MapLibre with MapTiler basemap
    const map = new maplibregl.Map({
      container: 'map',
      style: `https://api.maptiler.com/maps/streets/style.json?key=${API_KEY}`,
      center: [-122.42, 37.78], // default center
      zoom: 13
    });

    let foodLocations = [];
    const cuisineFilter = document.getElementById('cuisineFilter');
    const ratingFilter = document.getElementById('ratingFilter');
    const ratingValue = document.getElementById('ratingValue');
    let markers = [];

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

        const marker = new maplibregl.Marker({ color: "#FF5722" })
          .setLngLat(loc.coords)
          .setPopup(popup)
          .addTo(map);

        markers.push(marker);
      });
    }

    function updateFilters() {
      addMarkers(cuisineFilter.value, parseFloat(ratingFilter.value));
    }

    // Rating slider display
    ratingFilter.addEventListener('input', () => {
      ratingValue.textContent = ratingFilter.value;
      updateFilters();
    });
    cuisineFilter.addEventListener('change', updateFilters);

    // Load data from Flask API
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