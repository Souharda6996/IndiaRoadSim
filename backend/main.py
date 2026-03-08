from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from .engine.controller import SimulationController

app = FastAPI(title="TraffiSim AI Backend")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulation instance
sim = SimulationController()

@app.on_event("startup")
async def startup_event():
    # Load defaults on startup
    await sim.initialize("Mumbai, India")
    asyncio.create_task(run_simulation_loop())

async def run_simulation_loop():
    """Background task to run the simulation engine continuously"""
    last_time = asyncio.get_event_loop().time()
    while True:
        now = asyncio.get_event_loop().time()
        dt = now - last_time
        last_time = now
        
        sim.update(dt)
        await asyncio.sleep(0.033) # ~30 ticks per second

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "agents": len(sim.agents)}

@app.get("/api/map")
async def get_map():
    """Returns the map structure for the frontend to render"""
    return sim.get_map_data()

@app.websocket("/ws/traffic")
async def traffic_websocket(websocket: WebSocket):
    """Streams live agent positions to the frontend"""
    await websocket.accept()
    try:
        while True:
            state = sim.get_state()
            await websocket.send_json({"vehicles": state})
            await asyncio.sleep(0.1) # 10 updates per second for smooth web animation
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
