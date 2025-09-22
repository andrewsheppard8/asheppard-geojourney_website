// Replace with your Mapbox API token
mapboxgl.accessToken = 'YOUR_MAPBOX_ACCESS_TOKEN';

// Initialize the map
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [-98.5795, 39.8283], // USA center
    zoom: 4
});

// Add navigation controls
map.addControl(new mapboxgl.NavigationControl());

// Sample food locations
const foodData = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": { "name": "Joe's Pizza", "cuisine": "Italian" },
            "geometry": { "type": "Point", "coordinates": [-73.9851, 40.7589] }
        },
        {
            "type": "Feature",
            "properties": { "name": "Sushi Zen", "cuisine": "Japanese" },
            "geometry": { "type": "Point", "coordinates": [-122.4194, 37.7749] }
        }
        // Add more points here
    ]
};

map.on('load', () => {
    map.addSource('food', {
        type: 'geojson',
        data: foodData,
        cluster: true,
        clusterMaxZoom: 14,
        clusterRadius: 50
    });

    // Clusters
    map.addLayer({
        id: 'clusters',
        type: 'circle',
        source: 'food',
        filter: ['has', 'point_count'],
        paint: {
            'circle-color': '#f28cb1',
            'circle-radius': ['step', ['get', 'point_count'], 15, 5, 20, 10, 25]
        }
    });

    // Cluster count labels
    map.addLayer({
        id: 'cluster-count',
        type: 'symbol',
        source: 'food',
        filter: ['has', 'point_count'],
        layout: {
            'text-field': '{point_count_abbreviated}',
            'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
            'text-size': 12
        }
    });

    // Unclustered points
    map.addLayer({
        id: 'unclustered-point',
        type: 'circle',
        source: 'food',
        filter: ['!', ['has', 'point_count']],
        paint: {
            'circle-color': '#11b4da',
            'circle-radius': 8
        }
    });

    // Popups
    map.on('click', 'unclustered-point', (e) => {
        const coordinates = e.features[0].geometry.coordinates.slice();
        const { name, cuisine } = e.features[0].properties;

        new mapboxgl.Popup()
            .setLngLat(coordinates)
            .setHTML(`<strong>${name}</strong><p>${cuisine}</p>`)
            .addTo(map);
    });

    // Cursor pointer on hover
    map.on('mouseenter', 'unclustered-point', () => map.getCanvas().style.cursor = 'pointer');
    map.on('mouseleave', 'unclustered-point', () => map.getCanvas().style.cursor = '');
});