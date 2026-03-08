import osmnx as ox
import networkx as nx
import os
import json
import math
import random
from typing import Dict, Tuple

class MapManager:
    """
    Handles downloading, caching, and processing real-world road network 
    data using OpenStreetMap (OSM).
    """
    def __init__(self, cache_dir: str = "data/maps"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        self.graph = None
        self.locations = {} # node_id -> {lat, lon, ...}
        
    def load_city(self, city_name: str = "Mumbai, India", dist: int = 2000):
        """
        Downloads a section of a city based on center point or address.
        """
        cache_file = os.path.join(self.cache_dir, f"{city_name.replace(',', '_').replace(' ', '_')}.graphml")
        
        if os.path.exists(cache_file):
            print(f"Loading {city_name} from cache...")
            self.graph = ox.load_graphml(cache_file)
        else:
            print(f"Downloading {city_name} road network from OSM...")
            # 'drive' network type filters for drivable roads
            self.graph = ox.graph_from_address(city_name, dist=dist, network_type='drive')
            ox.save_graphml(self.graph, cache_file)
            
        # Standardize Graph
        # Ensure it is a MultiDiGraph (directed) for traffic flow
        if not isinstance(self.graph, nx.MultiDiGraph):
            self.graph = ox.get_digraph(self.graph)
            
        self._process_nodes()
        print(f"Map Loaded: {len(self.graph.nodes())} junctions, {len(self.graph.edges())} road segments.")
        
    def _process_nodes(self):
        """Extracts and stores node information for fast access"""
        self.locations = {}
        for node, data in self.graph.nodes(data=True):
            self.locations[node] = {
                "lat": data['y'],
                "lon": data['x'],
                "osmid": node
            }
            
    def get_edge_length(self, u, v):
        """Returns length of road segment in meters"""
        # MultiDiGraph might have multiple edges between same nodes, we take the first
        edge_data = self.graph.get_edge_data(u, v)
        if edge_data:
            # MultiDiGraph returns a dict of edges
            if 0 in edge_data:
                return edge_data[0].get('length', 10.0)
            return edge_data.get('length', 10.0)
        return 10.0

    def get_random_path(self, min_nodes=5):
        """Generates a random valid path for a vehicle agent"""
        nodes = list(self.graph.nodes())
        if not nodes: return []
        
        start = random.choice(nodes)
        end = random.choice(nodes)
        
        try:
            path = nx.shortest_path(self.graph, start, end, weight='length')
            if len(path) >= min_nodes:
                return path
        except nx.NetworkXNoPath:
            pass
        return []

    def get_map_json(self):
        """Export simplified map structure for frontend Leaflet rendering"""
        edges = []
        for u, v, data in self.graph.edges(data=True):
            # Coordinates for the polyline
            u_data = self.locations[u]
            v_data = self.locations[v]
            
            # If OSM has geometry (curves), use it, otherwise straight line
            if 'geometry' in data:
                coords = list(data['geometry'].coords)
                # Swap (x,y) to (lat,lon)
                path = [[lat, lon] for lon, lat in coords]
            else:
                path = [[u_data['lat'], u_data['lon']], [v_data['lat'], v_data['lon']]]
                
            edges.append({
                "u": u,
                "v": v,
                "path": path,
                "highway": data.get('highway', 'road'),
                "lanes": data.get('lanes', 1)
            })
            
        return {
            "nodes": list(self.locations.values()),
            "edges": edges
        }
