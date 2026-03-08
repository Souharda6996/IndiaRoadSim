"""
Path Planning Module for Indian Traffic Simulation
Implements A* pathfinding algorithm for finding optimal routes on actual road networks
This solves the issue of random grid generation by using real map data
"""

import networkx as nx
import numpy as np
from typing import List, Tuple, Dict, Optional
import heapq
from dataclasses import dataclass
import math

@dataclass
class PathNode:
    """Node in the path planning algorithm"""
    node_id: int
    g_cost: float  # Cost from start
    h_cost: float  # Heuristic cost to goal
    f_cost: float  # Total cost (g + h)
    parent: Optional['PathNode'] = None
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost

class PathPlanner:
    """
    Path planning using A* algorithm on the actual road network
    This ensures vehicles follow real roads instead of generating random grids
    """
    
    def __init__(self, graph: nx.MultiDiGraph, map_handler=None):
        """
        Initialize PathPlanner with a road network graph
        
        Args:
            graph: NetworkX graph of the road network from OpenStreetMap
            map_handler: Reference to MapHandler for additional map operations
        """
        self.graph = graph
        self.map_handler = map_handler
        self.path_cache = {}  # Cache computed paths
        
    def find_shortest_path(self, start_node: int, end_node: int, 
                          weight: str = 'length',
                          consider_traffic: bool = True) -> List[int]:
        """
        Find the shortest path between two nodes using the actual road network
        
        Args:
            start_node: Starting node ID
            end_node: Destination node ID
            weight: Edge weight to use ('length', 'travel_time')
            consider_traffic: Whether to consider traffic conditions
            
        Returns:
            List of node IDs representing the path
        """
        # Check cache first
        cache_key = (start_node, end_node, weight, consider_traffic)
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]
        
        try:
            # Use NetworkX built-in shortest path for initial implementation
            if consider_traffic:
                # Adjust weights based on traffic conditions
                path = self._find_path_with_traffic(start_node, end_node, weight)
            else:
                path = nx.shortest_path(self.graph, start_node, end_node, weight=weight)
            
            # Cache the result
            self.path_cache[cache_key] = path
            return path
            
        except nx.NetworkXNoPath:
            print(f"No path found between nodes {start_node} and {end_node}")
            return []
        except Exception as e:
            print(f"Error finding path: {e}")
            return []
    
    def find_path_astar(self, start_node: int, end_node: int,
                       consider_indian_conditions: bool = True) -> List[int]:
        """
        A* pathfinding algorithm that considers Indian road conditions
        This ensures the simulation uses actual road paths instead of random grids
        
        Args:
            start_node: Starting node ID
            end_node: Destination node ID
            consider_indian_conditions: Include Indian-specific road conditions
            
        Returns:
            List of node IDs representing the optimal path
        """
        if start_node not in self.graph or end_node not in self.graph:
            print(f"Invalid nodes: start={start_node}, end={end_node}")
            return []
        
        # Initialize open and closed sets
        open_set = []
        closed_set = set()
        
        # Create start node
        start = PathNode(
            node_id=start_node,
            g_cost=0,
            h_cost=self._heuristic_cost(start_node, end_node),
            f_cost=0
        )
        start.f_cost = start.g_cost + start.h_cost
        
        heapq.heappush(open_set, start)
        node_map = {start_node: start}
        
        while open_set:
            current = heapq.heappop(open_set)
            
            # Check if we reached the goal
            if current.node_id == end_node:
                return self._reconstruct_path(current)
            
            closed_set.add(current.node_id)
            
            # Explore neighbors
            for neighbor_id in self.graph.neighbors(current.node_id):
                if neighbor_id in closed_set:
                    continue
                
                # Calculate costs
                edge_cost = self._calculate_edge_cost(
                    current.node_id, neighbor_id, consider_indian_conditions
                )
                tentative_g_cost = current.g_cost + edge_cost
                
                # Check if this path is better
                if neighbor_id not in node_map:
                    # Create new node
                    neighbor = PathNode(
                        node_id=neighbor_id,
                        g_cost=tentative_g_cost,
                        h_cost=self._heuristic_cost(neighbor_id, end_node),
                        f_cost=0,
                        parent=current
                    )
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    node_map[neighbor_id] = neighbor
                    heapq.heappush(open_set, neighbor)
                    
                elif tentative_g_cost < node_map[neighbor_id].g_cost:
                    # Update existing node
                    neighbor = node_map[neighbor_id]
                    neighbor.g_cost = tentative_g_cost
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    neighbor.parent = current
        
        print(f"No path found using A* from {start_node} to {end_node}")
        return []
    
    def _heuristic_cost(self, node1: int, node2: int) -> float:
        """Calculate heuristic cost (Euclidean distance) between nodes"""
        if node1 in self.graph.nodes and node2 in self.graph.nodes:
            n1 = self.graph.nodes[node1]
            n2 = self.graph.nodes[node2]
            
            # Use projected coordinates if available
            if 'x' in n1 and 'x' in n2:
                dx = n1['x'] - n2['x']
                dy = n1['y'] - n2['y']
            else:
                # Fall back to lat/lon
                dx = (n1.get('lon', 0) - n2.get('lon', 0)) * 111000  # Convert to meters
                dy = (n1.get('lat', 0) - n2.get('lat', 0)) * 111000
            
            return math.sqrt(dx*dx + dy*dy)
        return 0
    
    def _calculate_edge_cost(self, from_node: int, to_node: int,
                            consider_indian_conditions: bool) -> float:
        """
        Calculate the cost of traversing an edge considering Indian road conditions
        """
        base_cost = 100  # Default cost
        
        # Get edge data
        edge_data = self.graph.get_edge_data(from_node, to_node)
        if edge_data:
            # Get the first edge (in case of multiple edges)
            edge = list(edge_data.values())[0]
            base_cost = edge.get('length', 100)
            
            if consider_indian_conditions:
                # Factor in Indian road conditions
                multiplier = 1.0
                
                # Road type affects travel
                highway_type = edge.get('highway', 'residential')
                # Handle case where highway_type might be a list
                if isinstance(highway_type, list):
                    highway_type = highway_type[0] if highway_type else 'residential'
                road_multipliers = {
                    'motorway': 0.8,
                    'trunk': 0.9,
                    'primary': 1.0,
                    'secondary': 1.2,
                    'tertiary': 1.4,
                    'residential': 1.6,
                    'unclassified': 2.0,
                    'service': 2.2
                }
                multiplier *= road_multipliers.get(highway_type, 1.5)
                
                # Random traffic conditions (simulating Indian traffic)
                traffic_factor = np.random.uniform(1.0, 3.0)
                multiplier *= traffic_factor
                
                # Random road quality issues
                if np.random.random() < 0.3:  # 30% chance of poor road
                    multiplier *= 1.5
                
                base_cost *= multiplier
        
        return base_cost
    
    def _reconstruct_path(self, node: PathNode) -> List[int]:
        """Reconstruct the path from start to end"""
        path = []
        current = node
        while current:
            path.append(current.node_id)
            current = current.parent
        return list(reversed(path))
    
    def _find_path_with_traffic(self, start_node: int, end_node: int,
                               weight: str) -> List[int]:
        """Find path considering traffic conditions"""
        # Create a copy of the graph with modified weights
        G_traffic = self.graph.copy()
        
        for u, v, data in G_traffic.edges(data=True):
            # Modify edge weights based on traffic
            original_weight = data.get(weight, 100)
            traffic_multiplier = np.random.uniform(1.0, 2.5)  # Simulate traffic
            G_traffic[u][v][0]['traffic_weight'] = original_weight * traffic_multiplier
        
        try:
            return nx.shortest_path(G_traffic, start_node, end_node, 
                                   weight='traffic_weight')
        except:
            return nx.shortest_path(self.graph, start_node, end_node, weight=weight)
    
    def find_alternative_paths(self, start_node: int, end_node: int,
                              k: int = 3) -> List[List[int]]:
        """
        Find k alternative paths between two nodes
        Useful for simulating different route choices
        
        Args:
            start_node: Starting node ID
            end_node: Destination node ID
            k: Number of alternative paths to find
            
        Returns:
            List of alternative paths
        """
        try:
            # Use NetworkX k-shortest paths
            paths = list(nx.shortest_simple_paths(
                self.graph, start_node, end_node, weight='length'
            ))[:k]
            return paths
        except:
            # If k-shortest paths fails, return single shortest path
            main_path = self.find_shortest_path(start_node, end_node)
            return [main_path] if main_path else []
    
    def get_path_distance(self, path: List[int]) -> float:
        """Calculate total distance of a path"""
        if len(path) < 2:
            return 0
        
        total_distance = 0
        for i in range(len(path) - 1):
            edge_data = self.graph.get_edge_data(path[i], path[i+1])
            if edge_data:
                edge = list(edge_data.values())[0]
                total_distance += edge.get('length', 100)
        
        return total_distance
    
    def get_path_estimated_time(self, path: List[int],
                               consider_traffic: bool = True) -> float:
        """
        Estimate travel time for a path in seconds
        
        Args:
            path: List of node IDs
            consider_traffic: Whether to consider traffic conditions
            
        Returns:
            Estimated time in seconds
        """
        if len(path) < 2:
            return 0
        
        total_time = 0
        for i in range(len(path) - 1):
            edge_data = self.graph.get_edge_data(path[i], path[i+1])
            if edge_data:
                edge = list(edge_data.values())[0]
                distance = edge.get('length', 100)  # meters
                
                # Get speed limit or estimate
                speed_kph = edge.get('maxspeed', 30)
                if isinstance(speed_kph, str):
                    speed_kph = float(speed_kph.replace(' mph', '').replace(' kph', ''))
                
                # Convert to m/s
                speed_mps = speed_kph / 3.6
                
                # Calculate base time
                base_time = distance / speed_mps
                
                # Apply traffic factor
                if consider_traffic:
                    traffic_factor = np.random.uniform(1.5, 4.0)  # Indian traffic
                    base_time *= traffic_factor
                
                total_time += base_time
        
        return total_time
    
    def validate_path(self, path: List[int]) -> bool:
        """
        Validate that a path is connected in the graph
        
        Args:
            path: List of node IDs
            
        Returns:
            True if path is valid, False otherwise
        """
        if len(path) < 2:
            return len(path) == 1 and path[0] in self.graph
        
        for i in range(len(path) - 1):
            if not self.graph.has_edge(path[i], path[i+1]):
                return False
        
        return True
    
    def clear_cache(self):
        """Clear the path cache"""
        self.path_cache.clear()
