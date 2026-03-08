import asyncio
import json
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple
import networkx as nx

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")


# ==============================================================================
# HEADLESS SIMULATION LOGIC
# ==============================================================================

def pixel_to_gps(x: float, y: float) -> Tuple[float, float]:
    """
    Converts the Pygame pixel coordinates into real-world Lat/Lon for Leaflet.
    Mumbai rough bounds:
    Min X: 380 -> Lon 72.81
    Max X: 1260 -> Lon 72.96
    Min Y: 25 -> Lat 19.23
    Max Y: 920 -> Lat 18.92
    """
    lon = 72.81 + (x - 380) * (72.96 - 72.81) / (1260 - 380)
    lat = 19.23 - (y - 25) * (19.23 - 18.92) / (920 - 25)
    return lat, lon

@dataclass
class HeadlessVehicle:
    id: int
    path: List[str]
    position: float # 0 to 1 along current edge
    current_index: int
    speed: float 
    vtype: str
    
class HeadlessSimulation:
    def __init__(self):
        self.graph = nx.Graph()
        self.locations = {}
        self.vehicles = []
        self.roads = []
        self.vehicle_counter = 0
        
        # Pull in the same locations as main.py
        from main import RealisticMumbaiSimulation
        try:
            # We initialize without Pygame by mocking just what we need, 
            # Or we just import the method
            dummy = object.__new__(RealisticMumbaiSimulation)
            dummy.create_realistic_mumbai_map()
            self.locations = dummy.locations
            self.graph = dummy.graph
        except Exception:
            # Fallback if Pygame init crashes it
            pass

        # Calculate GPS coordinates for all locations
        for loc_id, data in self.locations.items():
            px, py = data['pos']
            lat, lon = pixel_to_gps(px, py)
            data['lat'] = lat
            data['lon'] = lon
            
        # Add some initial traffic
        for _ in range(150):
            self.add_random_vehicle()
            
    def add_random_vehicle(self):
        nodes = list(self.graph.nodes())
        if len(nodes) < 2: return
        start = random.choice(nodes)
        end = random.choice(nodes)
        while start == end: end = random.choice(nodes)
        
        try:
            path = nx.shortest_path(self.graph, start, end, weight='weight')
            if len(path) > 1:
                vtype = random.choices(['car', 'bike', 'auto', 'truck', 'bus'], weights=[0.4, 0.3, 0.15, 0.1, 0.05])[0]
                bases = {'car': 40, 'bike': 45, 'auto': 35, 'truck': 25, 'bus': 30}
                base_speed = bases.get(vtype, 40) * random.uniform(0.8, 1.2)
                
                self.vehicles.append(HeadlessVehicle(
                    id=self.vehicle_counter,
                    path=path,
                    position=0.0,
                    current_index=0,
                    speed=base_speed,
                    vtype=vtype
                ))
                self.vehicle_counter += 1
        except nx.NetworkXNoPath:
            pass

    def update(self, dt: float):
        vehicles_to_remove = []
        for v in self.vehicles:
            if v.current_index >= len(v.path) - 1:
                vehicles_to_remove.append(v)
                continue
                
            current_node = v.path[v.current_index]
            next_node = v.path[v.current_index + 1]
            
            p1 = self.locations[current_node]['pos']
            p2 = self.locations[next_node]['pos']
            
            # Distance in pixels
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            if dist == 0: dist = 1
            
            # Move vehicle
            v.position += (v.speed * 2 * dt) / dist # Mult by 2 to make it visually faster
            
            if v.position >= 1.0:
                v.position = 0.0
                v.current_index += 1
                
        for v in vehicles_to_remove:
            if v in self.vehicles:
                self.vehicles.remove(v)
                
        # Continually replenish traffic
        while len(self.vehicles) < 150:
            self.add_random_vehicle()
            
    def get_frontend_state(self) -> dict:
        """Serializes map and vehicle state for the frontend"""
        v_list = []
        # We only send active vehicles to save bandwidth
        for v in self.vehicles:
            if v.current_index < len(v.path) - 1:
                c_node = v.path[v.current_index]
                n_node = v.path[v.current_index + 1]
                
                c_loc = self.locations[c_node]
                n_loc = self.locations[n_node]
                
                lat = c_loc['lat'] + (n_loc['lat'] - c_loc['lat']) * v.position
                lon = c_loc['lon'] + (n_loc['lon'] - c_loc['lon']) * v.position
                
                dx = n_loc['lon'] - c_loc['lon']
                dy = n_loc['lat'] - c_loc['lat']
                angle = math.degrees(math.atan2(dx, dy)) # Facing angle
                
                v_list.append({
                    "id": v.id,
                    "lat": lat,
                    "lon": lon,
                    "type": v.vtype,
                    "heading": angle
                })
                
        return {
            "vehicles": v_list
        }
        
    def get_map_data(self) -> dict:
        """Sends the static Graph nodes and edges so Leaflet can draw the roads"""
        nodes = []
        for nid, data in self.locations.items():
            nodes.append({
                "id": nid,
                "name": data['name'],
                "lat": data['lat'],
                "lon": data['lon'],
                "type": data['type']
            })
            
        edges = []
        for u, v in self.graph.edges():
            # Get edge data
            n1 = self.locations[u]
            n2 = self.locations[v]
            edges.append({
                "path": [[n1['lat'], n1['lon']], [n2['lat'], n2['lon']]]
            })
            
        return {
            "nodes": nodes,
            "edges": edges
        }

# Global Simulation Instance
sim = HeadlessSimulation()


# ==============================================================================
# WEBSOCKET ENDPOINTS
# ==============================================================================

@app.get("/api/map")
def get_map():
    return sim.get_map_data()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send current frame
            state = sim.get_frontend_state()
            await websocket.send_json(state)
            await asyncio.sleep(0.1) # 10 updates per second
    except WebSocketDisconnect:
        print("Client disconnected")

# Background task to run simulation loop globally
async def simulation_loop():
    last_time = asyncio.get_event_loop().time()
    while True:
        current_time = asyncio.get_event_loop().time()
        dt = current_time - last_time
        last_time = current_time
        
        sim.update(dt)
        await asyncio.sleep(0.016) # ~60 fps internal simulation tick

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulation_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
