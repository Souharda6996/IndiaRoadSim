"use client";

import { useEffect, useState } from "react";
import {
    MapContainer,
    TileLayer,
    Polyline,
    Marker,
    Tooltip,
    useMap
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix for default marker icons in Leaflet + Next.js
const DefaultIcon = L.icon({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

// Custom Icons for different Indian vehicle types
const getVehicleIcon = (vtype: string, heading: number) => {
    let color = "#38bdf8"; // Sky-400 (Car)
    let size = [6, 10]; // Proportionate to road

    // Adjusted sizes for better realism at zoom level 13-16
    if (vtype === "bike") { color = "#ffffff"; size = [3, 5]; }
    else if (vtype === "auto") { color = "#fbbf24"; size = [5, 7]; }
    else if (vtype === "bus") { color = "#22c55e"; size = [8, 16]; }
    else if (vtype === "truck") { color = "#f97316"; size = [8, 18]; }
    else if (vtype === "emergency") { color = "#ef4444"; size = [7, 10]; }

    return L.divIcon({
        className: "custom-vehicle-marker",
        html: `
      <div style="
        width: ${size[0]}px; 
        height: ${size[1]}px; 
        background-color: ${color}; 
        transform: rotate(${heading}deg);
        border-radius: 1px;
        box-shadow: 0 0 6px ${color};
        transition: all 0.2s linear;
        position: relative;
      ">
        <div style="
            position: absolute;
            top: 0; left: 0; width: 100%; height: 20%;
            background: rgba(255,255,255,0.4);
            border-radius: 1px 1px 0 0;
        "></div>
      </div>
    `,
        iconSize: size as [number, number],
        iconAnchor: [(size[0] / 2), (size[1] / 2)]
    });
};

interface MapProps {
    vehicles: any[];
    mapData: any;
}

const MapAutoCenter = ({ mapData }: { mapData: any }) => {
    const map = useMap();
    useEffect(() => {
        if (mapData?.nodes?.length > 0) {
            const firstNode = mapData.nodes[0];
            map.setView([firstNode.lat, firstNode.lon], 15);
        }
    }, [mapData, map]);
    return null;
};

const SimulationMap = ({ vehicles, mapData }: MapProps) => {
    return (
        <MapContainer
            center={[19.076, 72.877]}
            zoom={13}
            style={{ height: "100%", width: "100%", background: "#0b101e" }}
            zoomControl={false}
        >
            <MapAutoCenter mapData={mapData} />
            {/* High-Res Satellite Tiles */}
            <TileLayer
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                attribution="&copy; Esri"
            />

            {/* Road Network Overlays */}
            {mapData?.edges?.map((edge: any, idx: number) => (
                <Polyline
                    key={`edge-${idx}`}
                    positions={edge.path}
                    pathOptions={{
                        color: "#4da8da",
                        weight: edge.lanes * 1.5,
                        opacity: 0.3,
                        dashArray: "5, 10"
                    }}
                />
            ))}

            {/* Live Vehicle Agents */}
            {vehicles.map((v) => (
                <Marker
                    key={v.id}
                    position={[v.lat, v.lon]}
                    icon={getVehicleIcon(v.vtype, v.heading)}
                >
                    <Tooltip direction="top" offset={[0, -10]} opacity={0.8}>
                        <div className="text-xs">
                            <span className="font-bold uppercase">{v.vtype}</span><br />
                            Speed: {(v.speed * 3.6).toFixed(1)} km/h
                        </div>
                    </Tooltip>
                </Marker>
            ))}
        </MapContainer>
    );
};

export default SimulationMap;
