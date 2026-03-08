// Initialize Map centered roughly on Mumbai
const map = L.map('map').setView([19.0760, 72.8777], 12);

// Add Esri World Imagery (High-Res Satellite)
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EAP, and the GIS User Community',
    maxZoom: 18
}).addTo(map);

// Add a dark overlay to make markers pop more like a command center
L.rectangle([[-90, -180], [90, 180]], {
    color: 'none',
    fillColor: '#001a33',
    fillOpacity: 0.3
}).addTo(map);

// Store active vehicle markers
const vehicleMarkers = {};

// Custom DivIcon for vehicles
function createVehicleIcon(vtype, heading) {
    return L.divIcon({
        className: 'vehicle-marker',
        html: `<div class="vehicle-dot ${vtype}" style="transform: rotate(${heading}deg);"></div>`,
        iconSize: [12, 12],
        iconAnchor: [6, 6]
    });
}

// Fetch map infrastructure (Roads & Nodes)
fetch('/api/map')
    .then(response => response.json())
    .then(data => {
        // Draw roads
        data.edges.forEach(edge => {
            L.polyline(edge.path, {
                color: '#4da8da',
                weight: 2,
                opacity: 0.4,
                dashArray: '5, 5'
            }).addTo(map);
        });

        // Optionally draw nodes
        /* data.nodes.forEach(node => {
            L.circleMarker([node.lat, node.lon], {
                radius: 3,
                color: '#fff',
                fillColor: '#fff',
                fillOpacity: 0.8
            }).addTo(map)
            .bindTooltip(node.name);
        }); */
    });

// Connect to WebSocket for live traffic
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);

ws.onopen = () => {
    document.getElementById('conn-status').textContent = 'Connected';
    document.getElementById('conn-status').className = 'connected';
};

ws.onclose = () => {
    document.getElementById('conn-status').textContent = 'Disconnected';
    document.getElementById('conn-status').className = 'disconnected';
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const vehicles = data.vehicles;
    
    document.getElementById('veh-count').textContent = vehicles.length;

    // Track which vehicles we got in this frame
    const currentIds = new Set();

    vehicles.forEach(v => {
        currentIds.add(v.id);
        
        if (vehicleMarkers[v.id]) {
            // Update position
            vehicleMarkers[v.id].setLatLng([v.lat, v.lon]);
            // Fast rotation update via DOM
            const el = vehicleMarkers[v.id].getElement();
            if(el) {
                const dot = el.querySelector('.vehicle-dot');
                if(dot) dot.style.transform = `rotate(${v.heading}deg)`;
            }
        } else {
            // Create new marker
            const marker = L.marker([v.lat, v.lon], {
                icon: createVehicleIcon(v.type, v.heading)
            }).addTo(map);
            vehicleMarkers[v.id] = marker;
        }
    });

    // Remove vehicles that left the active path
    Object.keys(vehicleMarkers).forEach(id => {
        if (!currentIds.has(parseInt(id))) {
            map.removeLayer(vehicleMarkers[id]);
            delete vehicleMarkers[id];
        }
    });
};
