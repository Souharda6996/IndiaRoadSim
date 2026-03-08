"""
Map Handler Module for Indian Traffic Simulation
Handles OpenStreetMap data loading and processing for Indian road networks
"""

import osmnx as ox
import networkx as nx
import numpy as np
import pandas as pd
import geopandas as gpd
from typing import Tuple, List, Dict, Optional
import pickle
import json

class MapHandler:
    """Handles map data loading and processing from OpenStreetMap"""
    
    def __init__(self, location: str = "Mumbai, India", network_type: str = "drive"):
        """
        Initialize MapHandler with a location
        
        Args:
            location: City or area name (e.g., "Mumbai, India", "Delhi, India")
            network_type: Type of street network ('drive', 'walk', 'bike', 'all')
        """
        self.location = location
        self.network_type = network_type
        self.graph = None
        self.graph_proj = None
        self.nodes = None
        self.edges = None
        self.bounds = None
        
    def load_map_from_place(self, dist: int = 2000) -> nx.MultiDiGraph:
        """
        Load map data from OpenStreetMap for a specific place
        
        Args:
            dist: Distance in meters from center point
            
        Returns:
            NetworkX graph of the road network
        """
        try:
            print(f"Loading map data for {self.location}...")
            
            # Configure osmnx
            ox.settings.use_cache = True
            ox.settings.log_console = True
            
            # Download the street network
            # Using bbox approach as it's more reliable
            try:
                self.graph = ox.graph_from_place(
                    self.location, 
                    network_type=self.network_type,
                    simplify=True,
                    retain_all=False
                )
            except:
                # Alternative: use point-based approach
                point = ox.geocode(self.location)
                self.graph = ox.graph_from_point(
                    point, 
                    dist=dist,
                    network_type=self.network_type,
                    simplify=True
                )
            
            # Project the graph to a local coordinate system
            self.graph_proj = ox.project_graph(self.graph)
            
            # Extract nodes and edges
            self.nodes, self.edges = ox.graph_to_gdfs(self.graph_proj)
            
            # Get bounds
            self.bounds = self._calculate_bounds()
            
            print(f"Map loaded successfully!")
            print(f"Nodes: {len(self.nodes)}, Edges: {len(self.edges)}")
            
            return self.graph
            
        except Exception as e:
            print(f"Error loading map: {e}")
            # Fallback to a simple grid if OSM fails
            return self._create_fallback_grid()
    
    def load_map_from_bbox(self, north: float, south: float, 
                           east: float, west: float) -> nx.MultiDiGraph:
        """
        Load map data from a bounding box
        
        Args:
            north, south, east, west: Bounding box coordinates
            
        Returns:
            NetworkX graph of the road network
        """
        try:
            print(f"Loading map data from bounding box...")
            
            self.graph = ox.graph_from_bbox(
                north, south, east, west,
                network_type=self.network_type,
                simplify=True
            )
            
            self.graph_proj = ox.project_graph(self.graph)
            self.nodes, self.edges = ox.graph_to_gdfs(self.graph_proj)
            self.bounds = self._calculate_bounds()
            
            print(f"Map loaded successfully!")
            return self.graph
            
        except Exception as e:
            print(f"Error loading map: {e}")
            return self._create_fallback_grid()
    
    def _create_fallback_grid(self) -> nx.MultiDiGraph:
        """
        Create a simple grid network as fallback when OSM data is unavailable
        """
        print("Creating fallback grid network...")
        
        # Create a 10x10 grid
        G = nx.grid_2d_graph(10, 10)
        
        # Convert to MultiDiGraph to match OSM format
        MG = nx.MultiDiGraph()
        
        # Add nodes with coordinates
        for node in G.nodes():
            x, y = node
            MG.add_node(node, x=x*100, y=y*100, 
                       lat=19.0 + y*0.01, lon=72.8 + x*0.01)
        
        # Add edges with attributes
        for edge in G.edges():
            u, v = edge
            distance = 100  # meters
            MG.add_edge(u, v, length=distance, 
                       highway='residential', speed_kph=30)
            MG.add_edge(v, u, length=distance, 
                       highway='residential', speed_kph=30)
        
        self.graph = MG
        self.graph_proj = MG
        
        return MG
    
    def _calculate_bounds(self) -> Dict[str, float]:
        """Calculate the bounds of the loaded map"""
        if self.nodes is not None:
            return {
                'min_x': self.nodes.geometry.x.min(),
                'max_x': self.nodes.geometry.x.max(),
                'min_y': self.nodes.geometry.y.min(),
                'max_y': self.nodes.geometry.y.max()
            }
        return {'min_x': 0, 'max_x': 1000, 'min_y': 0, 'max_y': 1000}
    
    def get_nearest_node(self, point: Tuple[float, float]) -> int:
        """
        Find the nearest node to a given point
        
        Args:
            point: (x, y) or (lat, lon) coordinates
            
        Returns:
            Node ID of the nearest node
        """
        if self.graph is None:
            return None
            
        # If using projected graph, use x, y
        if self.graph_proj:
            return ox.nearest_nodes(self.graph_proj, point[0], point[1])
        else:
            # Use lat, lon
            return ox.nearest_nodes(self.graph, point[1], point[0])
    
    def get_node_coordinates(self, node_id: int) -> Tuple[float, float]:
        """Get coordinates of a node"""
        if self.graph_proj and node_id in self.graph_proj.nodes:
            node = self.graph_proj.nodes[node_id]
            return (node['x'], node['y'])
        return None
    
    def get_edge_attributes(self, u: int, v: int, key: int = 0) -> Dict:
        """Get attributes of an edge"""
        if self.graph_proj and self.graph_proj.has_edge(u, v, key):
            return self.graph_proj[u][v][key]
        return {}
    
    def get_road_segments(self) -> List[Dict]:
        """
        Extract road segments with Indian traffic characteristics
        
        Returns:
            List of road segment dictionaries
        """
        segments = []
        
        if self.edges is not None:
            for idx, edge in self.edges.iterrows():
                segment = {
                    'id': idx,
                    'geometry': edge.geometry,
                    'length': edge.get('length', 100),
                    'highway_type': edge.get('highway', 'residential'),
                    'lanes': self._estimate_lanes(edge.get('highway', 'residential')),
                    'speed_limit': self._get_indian_speed_limit(edge.get('highway', 'residential')),
                    'congestion_factor': np.random.uniform(0.3, 0.9),  # Indian traffic congestion
                    'road_quality': np.random.choice(['good', 'average', 'poor'], p=[0.2, 0.5, 0.3]),
                    'has_potholes': np.random.choice([True, False], p=[0.4, 0.6]),
                    'under_construction': np.random.choice([True, False], p=[0.15, 0.85]),
                    'has_divider': edge.get('divider', False),
                    'traffic_signals': edge.get('traffic_signals', False)
                }
                segments.append(segment)
        
        return segments
    
    def _estimate_lanes(self, highway_type: str) -> int:
        """Estimate number of lanes based on Indian road types"""
        lane_mapping = {
            'motorway': 6,
            'trunk': 4,
            'primary': 4,
            'secondary': 2,
            'tertiary': 2,
            'residential': 2,
            'unclassified': 1,
            'service': 1
        }
        return lane_mapping.get(highway_type, 2)
    
    def _get_indian_speed_limit(self, highway_type: str) -> int:
        """Get typical Indian speed limits in km/h"""
        speed_limits = {
            'motorway': 80,
            'trunk': 60,
            'primary': 50,
            'secondary': 40,
            'tertiary': 30,
            'residential': 20,
            'unclassified': 30,
            'service': 20
        }
        return speed_limits.get(highway_type, 30)
    
    def save_map(self, filename: str):
        """Save the loaded map to a file"""
        if self.graph:
            with open(filename, 'wb') as f:
                pickle.dump({
                    'graph': self.graph,
                    'graph_proj': self.graph_proj,
                    'location': self.location,
                    'bounds': self.bounds
                }, f)
            print(f"Map saved to {filename}")
    
    def load_saved_map(self, filename: str):
        """Load a previously saved map"""
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                self.graph = data['graph']
                self.graph_proj = data['graph_proj']
                self.location = data['location']
                self.bounds = data['bounds']
                
                if self.graph_proj:
                    self.nodes, self.edges = ox.graph_to_gdfs(self.graph_proj)
                
                print(f"Map loaded from {filename}")
                return True
        except Exception as e:
            print(f"Error loading saved map: {e}")
            return False
    
    def export_to_geojson(self, filename: str):
        """Export the map to GeoJSON format"""
        if self.edges is not None:
            self.edges.to_file(filename, driver='GeoJSON')
            print(f"Map exported to {filename}")
