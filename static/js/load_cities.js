    // fetch("/static/data/cities.geojson")
    //   .then(response => response.json())
    //   .then(data => {
    //     console.log(data);
    //     document.getElementById("output").textContent = JSON.stringify(data, null, 2);
    //   })
    //   .catch(err => {
    //     console.error("Error loading GeoJSON: ", err);
    //   });

const cities = ["Ulaanbaatar", "Beijing", "Kathmandu", "Mahabalipuram"];
const container = document.createElement("div");
document.body.appendChild(container);

cities.forEach(city => {
    const btn = document.createElement("button");
    btn.textContent = city;
    btn.addEventListener("click", () => {
        fetch(`/get_coordinates/${encodeURIComponent(city)}`)
            .then(res => res.json())
            .then(data => {
                if (data.coordinates) {
                    alert(`Coordinates of ${city}: ${data.coordinates}`);
                } else {
                    alert(`Error: ${data.error}`);
                }
            });
    });
    container.appendChild(btn);
});