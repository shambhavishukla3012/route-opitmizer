let map;
let markers = [];
let routeLayer;

// Initialize map
function initMap() {
    map = L.map('map').setView([0, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}

// Clear existing markers and route
function clearMap() {
    markers.forEach(marker => marker.remove());
    markers = [];
    if (routeLayer) {
        routeLayer.remove();
    }
}

// Create numbered marker icon
function createNumberedIcon(number) {
    return L.divIcon({
        className: 'numbered-marker',
        html: `<div class="marker-number">${number}</div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30]
    });
}

// Add markers for locations
function addMarkers(coordinates, addresses) {
    clearMap();

    coordinates.forEach((coord, index) => {
        const marker = L.marker([coord[0], coord[1]], {
            icon: createNumberedIcon(index + 1)
        })
            .bindPopup(`Stop ${index + 1}: ${addresses[index]}`)
            .addTo(map);
        markers.push(marker);
    });

    // Fit map to show all markers
    const bounds = L.latLngBounds(coordinates);
    map.fitBounds(bounds, { padding: [50, 50] });
}

// Draw route on map
function drawRoute(routeData) {
    if (routeLayer) {
        routeLayer.remove();
    }

    // Handle GeoJSON format from OpenRouteService
    const coordinates = routeData.features[0].geometry.coordinates;
    const latLngs = coordinates.map(coord => [coord[1], coord[0]]); // Convert [lon, lat] to [lat, lon]

    routeLayer = L.polyline(latLngs, {
        color: 'blue',
        weight: 3,
        opacity: 0.7
    }).addTo(map);
}

// Initialize map on page load
document.addEventListener('DOMContentLoaded', initMap);