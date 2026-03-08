import asyncio
import time
import random
from typing import List, Dict
from .map_manager import MapManager
from .agent import TrafficAgent, VehicleType

class SimulationController:
    """
    Orchestrates the map and all vehicle agents.
    """
    def __init__(self):
        self.map_manager = MapManager()
        self.agents: List[TrafficAgent] = []
        self.agent_counter = 0
        self.is_running = False
        
    async def initialize(self, city: str = "Mumbai, India"):
        self.map_manager.load_city(city)
        self.agents = []
        # Populate with initial traffic
        self.populate_traffic(100)
        
    def populate_traffic(self, count: int):
        for _ in range(count):
            path = self.map_manager.get_random_path()
            if path:
                vtype = random.choices(list(VehicleType), weights=[0.4, 0.3, 0.1, 0.05, 0.05, 0.05, 0.05])[0]
                agent = TrafficAgent(self.agent_counter, vtype, path)
                self.agents.append(agent)
                self.agent_counter += 1

    def update(self, dt: float):
        """Main step function for the entire simulation"""
        agents_to_remove = []
        
        # In a real large-scale sim, we'd use spatial indexing (R-Tree) 
        # to find neighbors, but for 100-200 agents, simple iteration is fine.
        for agent in self.agents:
            if agent.current_idx >= len(agent.path) - 1:
                agents_to_remove.append(agent)
                continue
                
            # Simple neighbor detection (on same road segment)
            neighbors = [a for a in self.agents if a.current_idx == agent.current_idx and a.id != agent.id]
            
            u = agent.path[agent.current_idx]
            v = agent.path[agent.current_idx + 1]
            segment_len = self.map_manager.get_edge_length(u, v)
            
            still_active = agent.move(dt, neighbors, segment_len)
            if not still_active:
                agents_to_remove.append(agent)
                
        for agent in agents_to_remove:
            self.agents.remove(agent)
            
        # Respawn to keep density
        if len(self.agents) < 50:
            self.populate_traffic(20)

    def get_state(self):
        """Returns the current state of all agents for the frontend"""
        return [a.get_pos_data(self.map_manager.graph, self.map_manager.locations) for a in self.agents]

    def get_map_data(self):
        return self.map_manager.get_map_json()
