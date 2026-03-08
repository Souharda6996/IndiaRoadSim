"""
Visualization Module for Indian Traffic Simulation
Provides real-time visualization of traffic on the actual road network
"""

import pygame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import folium
from typing import Dict, List, Tuple
import io
from PIL import Image

class SimulationVisualizer:
    """Real-time visualization of traffic simulation"""
    
    def __init__(self, map_handler, width: int = 1200, height: int = 800):
        """
        Initialize the visualizer
        
        Args:
            map_handler: MapHandler instance
            width: Window width
            height: Window height
        """
        self.map_handler = map_handler
        self.width = width
        self.height = height
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Indian Traffic Simulation - Map-Based Pathfinding")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Colors
        self.colors = {
            'background': (240, 240, 240),
            'road': (100, 100, 100),
            'road_edge': (150, 150, 150),
            'car': (0, 100, 200),
            'bus': (200, 100, 0),
            'truck': (150, 75, 0),
            'auto_rickshaw': (200, 200, 0),
            'motorcycle': (100, 0, 100),
            'bicycle': (0, 200, 100),
            'pedestrian': (255, 100, 100),
            'traffic_light_green': (0, 255, 0),
            'traffic_light_yellow': (255, 255, 0),
            'traffic_light_red': (255, 0, 0),
            'pothole': (60, 60, 60),
            'construction': (255, 165, 0),
            'text': (20, 20, 20),
            'grid': (220, 220, 220),
            'path': (255, 0, 255)
        }
        
        # Calculate map bounds and scaling
        self._calculate_map_scaling()
        
        # Map rendering cache
        self.map_surface = None
        self.render_map()
        
    def _calculate_map_scaling(self):
        """Calculate scaling factors for map display"""
        if self.map_handler.bounds:
            map_width = self.map_handler.bounds['max_x'] - self.map_handler.bounds['min_x']
            map_height = self.map_handler.bounds['max_y'] - self.map_handler.bounds['min_y']
            
            # Leave margin for UI
            display_width = self.width - 100
            display_height = self.height - 150
            
            # Calculate scale to fit map in window
            self.scale_x = display_width / map_width if map_width > 0 else 1
            self.scale_y = display_height / map_height if map_height > 0 else 1
            self.scale = min(self.scale_x, self.scale_y)
            
            # Calculate offsets to center the map
            self.offset_x = 50 + (display_width - map_width * self.scale) / 2
            self.offset_y = 50 + (display_height - map_height * self.scale) / 2
            
            # Store map bounds for reference
            self.min_x = self.map_handler.bounds['min_x']
            self.min_y = self.map_handler.bounds['min_y']
        else:
            # Default scaling
            self.scale = 1
            self.offset_x = 50
            self.offset_y = 50
            self.min_x = 0
            self.min_y = 0
    
    def world_to_screen(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = int((x - self.min_x) * self.scale + self.offset_x)
        screen_y = int(self.height - ((y - self.min_y) * self.scale + self.offset_y))
        return (screen_x, screen_y)
    
    def render_map(self):
        """Render the road network map"""
        self.map_surface = pygame.Surface((self.width, self.height))
        self.map_surface.fill(self.colors['background'])
        
        # Draw grid
        for x in range(0, self.width, 50):
            pygame.draw.line(self.map_surface, self.colors['grid'], 
                           (x, 0), (x, self.height), 1)
        for y in range(0, self.height, 50):
            pygame.draw.line(self.map_surface, self.colors['grid'],
                           (0, y), (self.width, y), 1)
        
        # Draw roads from the actual map
        if self.map_handler.graph_proj:
            for u, v, data in self.map_handler.graph_proj.edges(data=True):
                # Get node positions
                u_pos = self.map_handler.get_node_coordinates(u)
                v_pos = self.map_handler.get_node_coordinates(v)
                
                if u_pos and v_pos:
                    start = self.world_to_screen(u_pos[0], u_pos[1])
                    end = self.world_to_screen(v_pos[0], v_pos[1])
                    
                    # Determine road width based on type
                    highway_type = data.get('highway', 'residential')
                    width = self._get_road_width(highway_type)
                    
                    # Draw road
                    pygame.draw.line(self.map_surface, self.colors['road'],
                                   start, end, width)
            
            # Draw nodes (intersections)
            for node in self.map_handler.graph_proj.nodes():
                pos = self.map_handler.get_node_coordinates(node)
                if pos:
                    screen_pos = self.world_to_screen(pos[0], pos[1])
                    pygame.draw.circle(self.map_surface, self.colors['road_edge'],
                                     screen_pos, 3)
    
    def _get_road_width(self, highway_type: str) -> int:
        """Get road width for visualization based on type"""
        widths = {
            'motorway': 8,
            'trunk': 6,
            'primary': 5,
            'secondary': 4,
            'tertiary': 3,
            'residential': 2,
            'unclassified': 2,
            'service': 1
        }
        return widths.get(highway_type, 2)
    
    def draw_vehicle(self, vehicle_data: Dict):
        """Draw a vehicle on the screen"""
        x, y = self.world_to_screen(vehicle_data['x'], vehicle_data['y'])
        
        # Get vehicle color
        color = self.colors.get(vehicle_data['type'], self.colors['car'])
        
        # Vehicle size based on type
        sizes = {
            'car': 8,
            'bus': 12,
            'truck': 12,
            'auto_rickshaw': 6,
            'motorcycle': 4,
            'bicycle': 3,
            'pedestrian': 3
        }
        size = sizes.get(vehicle_data['type'], 6)
        
        # Draw vehicle
        pygame.draw.circle(self.screen, color, (x, y), size)
        
        # Draw honking indicator
        if vehicle_data.get('is_honking', False):
            pygame.draw.circle(self.screen, (255, 255, 0), (x, y), size + 5, 2)
        
        # Draw behavior indicator for erratic drivers
        if vehicle_data.get('behavior') == 'erratic':
            pygame.draw.circle(self.screen, (255, 0, 0), (x, y), size + 3, 1)
    
    def draw_traffic_light(self, node_id: int, state: str):
        """Draw traffic light at a node"""
        pos = self.map_handler.get_node_coordinates(node_id)
        if pos:
            x, y = self.world_to_screen(pos[0], pos[1])
            
            # Get color based on state
            color_map = {
                'green': self.colors['traffic_light_green'],
                'yellow': self.colors['traffic_light_yellow'],
                'red': self.colors['traffic_light_red']
            }
            color = color_map.get(state, self.colors['traffic_light_red'])
            
            # Draw traffic light
            pygame.draw.circle(self.screen, (50, 50, 50), (x, y), 8)
            pygame.draw.circle(self.screen, color, (x, y), 6)
    
    def draw_road_conditions(self, road_conditions):
        """Draw road conditions like potholes and construction"""
        # Draw potholes
        for edge, potholes in road_conditions.potholes.items():
            if len(edge) == 2:
                start_pos = self.map_handler.get_node_coordinates(edge[0])
                end_pos = self.map_handler.get_node_coordinates(edge[1])
                
                if start_pos and end_pos:
                    for pothole in potholes:
                        # Interpolate position
                        x = start_pos[0] + (end_pos[0] - start_pos[0]) * pothole['position']
                        y = start_pos[1] + (end_pos[1] - start_pos[1]) * pothole['position']
                        screen_x, screen_y = self.world_to_screen(x, y)
                        
                        # Draw pothole
                        radius = int(3 + pothole['severity'] * 4)
                        pygame.draw.circle(self.screen, self.colors['pothole'],
                                         (screen_x, screen_y), radius)
        
        # Draw construction zones
        for edge, construction in road_conditions.construction_zones.items():
            if len(edge) == 2:
                start_pos = self.map_handler.get_node_coordinates(edge[0])
                end_pos = self.map_handler.get_node_coordinates(edge[1])
                
                if start_pos and end_pos:
                    start = self.world_to_screen(start_pos[0], start_pos[1])
                    end = self.world_to_screen(end_pos[0], end_pos[1])
                    
                    # Draw construction zone
                    pygame.draw.line(self.screen, self.colors['construction'],
                                   start, end, 10)
    
    def draw_path(self, path: List[int]):
        """Draw a path on the map"""
        if len(path) < 2:
            return
        
        for i in range(len(path) - 1):
            start_pos = self.map_handler.get_node_coordinates(path[i])
            end_pos = self.map_handler.get_node_coordinates(path[i + 1])
            
            if start_pos and end_pos:
                start = self.world_to_screen(start_pos[0], start_pos[1])
                end = self.world_to_screen(end_pos[0], end_pos[1])
                pygame.draw.line(self.screen, self.colors['path'], start, end, 2)
    
    def draw_statistics(self, stats: Dict):
        """Draw simulation statistics"""
        y_offset = 10
        
        # Title
        title = self.font.render("Indian Traffic Simulation - Real Map Navigation", 
                                True, self.colors['text'])
        self.screen.blit(title, (10, y_offset))
        y_offset += 30
        
        # Statistics
        stats_text = [
            f"Total Vehicles: {stats.get('total_vehicles', 0)}",
            f"Active Vehicles: {stats.get('active_vehicles', 0)}",
            f"Avg Speed: {stats.get('avg_speed', 0):.1f} km/h",
            f"Congestion: {stats.get('congestion_level', 0):.1%}",
            f"Honks/min: {stats.get('honks_per_minute', 0):.0f}"
        ]
        
        for text in stats_text:
            surface = self.small_font.render(text, True, self.colors['text'])
            self.screen.blit(surface, (10, y_offset))
            y_offset += 20
        
        # Instructions
        instructions = [
            "Press SPACE to pause/resume",
            "Press R to add random vehicle",
            "Press C to clear all vehicles",
            "Press P to show/hide paths",
            "Press ESC to exit"
        ]
        
        y_offset = self.height - len(instructions) * 20 - 10
        for text in instructions:
            surface = self.small_font.render(text, True, self.colors['text'])
            self.screen.blit(surface, (10, y_offset))
            y_offset += 20
    
    def update(self, vehicles: List[Dict], traffic_lights: Dict, 
              road_conditions, stats: Dict, show_paths: bool = False):
        """Update the visualization"""
        # Draw map background
        if self.map_surface:
            self.screen.blit(self.map_surface, (0, 0))
        else:
            self.screen.fill(self.colors['background'])
        
        # Draw road conditions
        if road_conditions:
            self.draw_road_conditions(road_conditions)
        
        # Draw traffic lights
        for node_id, light in traffic_lights.items():
            self.draw_traffic_light(node_id, light.state)
        
        # Draw vehicle paths if enabled
        if show_paths:
            # This would require passing vehicle objects, not just positions
            pass
        
        # Draw vehicles
        for vehicle_data in vehicles:
            self.draw_vehicle(vehicle_data)
        
        # Update statistics
        stats['active_vehicles'] = len(vehicles)
        
        # Draw UI
        self.draw_statistics(stats)
        
        # Update display
        pygame.display.flip()
        
        return self.clock.tick(30)  # 30 FPS
    
    def handle_events(self) -> Dict:
        """Handle pygame events"""
        events = {
            'quit': False,
            'pause': False,
            'add_vehicle': False,
            'clear_vehicles': False,
            'toggle_paths': False
        }
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events['quit'] = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events['quit'] = True
                elif event.key == pygame.K_SPACE:
                    events['pause'] = True
                elif event.key == pygame.K_r:
                    events['add_vehicle'] = True
                elif event.key == pygame.K_c:
                    events['clear_vehicles'] = True
                elif event.key == pygame.K_p:
                    events['toggle_paths'] = True
        
        return events
    
    def close(self):
        """Close the visualization"""
        pygame.quit()

def create_folium_map(map_handler, simulation, output_file: str = "traffic_map.html"):
    """
    Create an interactive Folium map with traffic visualization
    
    Args:
        map_handler: MapHandler instance
        simulation: TrafficSimulation instance
        output_file: Output HTML file name
    """
    # Get map center
    if map_handler.nodes is not None and len(map_handler.nodes) > 0:
        center_lat = map_handler.nodes.geometry.y.mean()
        center_lon = map_handler.nodes.geometry.x.mean()
    else:
        center_lat, center_lon = 19.076, 72.877  # Default to Mumbai
    
    # Create folium map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=14)
    
    # Add road network
    if map_handler.edges is not None:
        for idx, edge in map_handler.edges.iterrows():
            if hasattr(edge.geometry, 'coords'):
                coords = [[lat, lon] for lon, lat in edge.geometry.coords]
                
                # Color based on road type
                highway_type = edge.get('highway', 'residential')
                color_map = {
                    'motorway': 'red',
                    'trunk': 'orange',
                    'primary': 'yellow',
                    'secondary': 'green',
                    'residential': 'blue',
                    'service': 'gray'
                }
                color = color_map.get(highway_type, 'blue')
                
                folium.PolyLine(
                    coords,
                    color=color,
                    weight=3,
                    opacity=0.8,
                    popup=f"Type: {highway_type}"
                ).add_to(m)
    
    # Add vehicle positions
    vehicle_positions = simulation.get_vehicle_positions()
    for vehicle in vehicle_positions:
        if map_handler.graph:
            # Convert back to lat/lon if needed
            folium.CircleMarker(
                location=[vehicle['y'], vehicle['x']],  # Note: folium uses [lat, lon]
                radius=5,
                popup=f"Vehicle {vehicle['id']}: {vehicle['type']}<br>Speed: {vehicle['speed']:.1f} km/h",
                color='red' if vehicle['is_honking'] else 'blue',
                fill=True
            ).add_to(m)
    
    # Save map
    m.save(output_file)
    print(f"Interactive map saved to {output_file}")
