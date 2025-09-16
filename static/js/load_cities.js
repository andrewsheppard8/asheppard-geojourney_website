let geojsonData = null;  // store once

//BUTTON FOR DISPLAYING GEOJSON
// Create the button dynamically
const toggleBtn = document.createElement("button");
toggleBtn.textContent = "Show GeoJSON";
document.body.insertBefore(toggleBtn, document.getElementById("output"));

// Make sure <pre> exists in HTML
const output = document.getElementById("output");
output.style.display = "none";

// Fetch data
fetch("/static/data/cities.geojson")
  .then(response => response.json())
  .then(data => {
    geojsonData = data;
    console.log("GeoJSON loaded:", data);
  })
  .catch(err => {
    console.error("Error loading GeoJSON: ", err);
  });

// Button click event
toggleBtn.addEventListener("click", () => {
  if (output.style.display === "none") {
    output.style.display = "block";
    toggleBtn.textContent = "Hide GeoJSON";
    if (geojsonData) {
      output.textContent = JSON.stringify(geojsonData, null, 2);
    }
  } else {
    output.style.display = "none";
    toggleBtn.textContent = "Show GeoJSON";
  }
});

//DOWNLOAD GEOJSON BUTTON
// Create download button
const downloadBtn = document.createElement("button");
downloadBtn.textContent = "Download GeoJSON";
downloadBtn.style.display = "block";
downloadBtn.style.marginTop = "20px";

// When clicked, trigger download
downloadBtn.addEventListener("click", () => {
    const link = document.createElement("a");
    link.href = "/static/data/cities.geojson";  // path to your GeoJSON
    link.download = "cities.geojson";           // suggested filename
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

// Add button to page (at top or bottom)
document.body.appendChild(downloadBtn);

//This was the original loading GeoJSON on the page
// fetch("/static/data/cities.geojson")
//       .then(response => response.json())
//       .then(data => {
//         console.log(data);
//         document.getElementById("output").textContent = JSON.stringify(data, null, 2);
//       })
//       .catch(err => {
//         console.error("Error loading GeoJSON: ", err);
//       });

//BUTTONS FOR COORDINATES FOR THE CITIES
const cities = ["Ulaanbaatar", "Beijing", "Kathmandu", "Mahabalipuram"];
const container = document.createElement("div");
document.body.appendChild(container);

//this is a code for dropdowns for the coordinates
// cities.forEach(city => {
//     const btn = document.createElement("button");
//     btn.textContent = city;
//     btn.addEventListener("click", () => {
//         fetch(`/get_coordinates/${encodeURIComponent(city)}`)
//             .then(res => res.json())
//             .then(data => {
//                 if (data.coordinates) {
//                     alert(`Coordinates of ${city}: ${data.coordinates}`);
//                 } else {
//                     alert(`Error: ${data.error}`);
//                 }
//             });
//     });
//     container.appendChild(btn);
// });

cities.forEach(city => {
    // Create the city button
    const btn = document.createElement("button");
    btn.textContent = city;
    btn.style.display = "block";       // each button on its own line
    btn.style.marginTop = "10px";

    // Create a div to hold the coordinates (initially hidden)
    const coordsDiv = document.createElement("div");
    coordsDiv.style.display = "none";
    coordsDiv.style.marginLeft = "20px";  // indent
    coordsDiv.style.fontStyle = "italic";

    // Button click toggles the coordinates
    btn.addEventListener("click", () => {
        if (coordsDiv.style.display === "none") {
            // Fetch coordinates from API
            fetch(`/get_coordinates/${encodeURIComponent(city)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.coordinates) {
                        coordsDiv.textContent = `Coordinates: ${data.coordinates}`;
                        coordsDiv.style.display = "block";
                    } else {
                        coordsDiv.textContent = `Error: ${data.error}`;
                        coordsDiv.style.display = "block";
                    }
                });
        } else {
            coordsDiv.style.display = "none";  // hide if already shown
        }
    });

    // Add the button and div to the container
    container.appendChild(btn);
    container.appendChild(coordsDiv);
});