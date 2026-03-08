"""
Micro-Simulation: High-Fidelity Satellite Intersection
Produces a highly realistic, SUMO/Omniverse style top-down view of a highway interchange
featuring textured asphalt, lane markings, shadows, and detailed vehicle sprites.
"""

import pygame
import math
import random
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict

# Map Config
WIDTH = 1800
HEIGHT = 1000
FPS = 60

# Colors
GRASS_COLORS = [(70, 100, 50), (65, 95, 45), (75, 105, 55)]
ASPHALT_COLOR = (45, 45, 48)
LANE_MARKER_COLOR = (240, 240, 240)
YELLOW_LINE_COLOR = (240, 200, 50)
CONCRETE_COLOR = (180, 180, 175)

@dataclass
class Lane:
    start: Tuple[float, float]
    end: Tuple[float, float]
    width: float = 12.0
    is_left_edge: bool = False
    is_right_edge: bool = False

class RealVehicle:
    def __init__(self, lane: Lane, speed: float, vtype: str):
        self.lane = lane
        self.progress = 0.0 # 0.0 to 1.0 along the lane
        self.speed = speed
        self.vtype = vtype
        self.length = self._get_length()
        self.width = self._get_width()
        
        # Colors: Metallic realistic palette
        colors = [
            (210, 210, 215), # Silver
            (30, 30, 35),    # Black
            (240, 240, 240), # White
            (180, 50, 50),   # Dark Red
            (40, 60, 120),   # Navy Blue
        ]
        self.color = random.choice(colors)
        
        # Trucks might have separate trailer colors
        self.trailer_color = random.choice([(200, 200, 200), (150, 150, 150), (100, 120, 150)]) if vtype == 'truck' else None
        
        # Start with a random offset
        self.progress = random.uniform(0, 1.0)
        
    def _get_length(self):
        if self.vtype == 'car': return 25
        if self.vtype == 'truck': return 65
        if self.vtype == 'bus': return 50
        if self.vtype == 'bike': return 12
        return 20
        
    def _get_width(self):
        if self.vtype == 'bike': return 6
        if self.vtype in ['truck', 'bus']: return 14
        return 12

    def update(self, dt):
        dist = math.hypot(self.lane.end[0] - self.lane.start[0], self.lane.end[1] - self.lane.start[1])
        self.progress += (self.speed * dt) / dist
        
        if self.progress > 1.0:
            self.progress = 0.0

    def draw(self, surface):
        x = self.lane.start[0] + (self.lane.end[0] - self.lane.start[0]) * self.progress
        y = self.lane.start[1] + (self.lane.end[1] - self.lane.start[1]) * self.progress
        
        dx = self.lane.end[0] - self.lane.start[0]
        dy = self.lane.end[1] - self.lane.start[1]
        angle = math.degrees(math.atan2(-dy, dx))
        
        # Sub-surfaces for shadows and vehicles
        shadow_surf = pygame.Surface((self.length * 1.5, self.width * 2), pygame.SRCALPHA)
        veh_surf = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
        
        # Draw Shadow
        shadow_rect = pygame.Rect(self.length*0.25 + 4, self.width*0.5 + 4, self.length, self.width)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 100), shadow_rect, border_radius=3)
        
        # Draw Vehicle Body
        if self.vtype == 'truck':
            # Cabin
            pygame.draw.rect(veh_surf, self.color, (self.length - 15, 1, 15, self.width-2), border_radius=2)
            # Trailer
            pygame.draw.rect(veh_surf, self.trailer_color, (0, 0, self.length-18, self.width), border_radius=1)
            # Windshield
            pygame.draw.rect(veh_surf, (20, 30, 40), (self.length - 10, 2, 4, self.width-4))
        elif self.vtype == 'car':
            # Car body
            pygame.draw.rect(veh_surf, self.color, (0, 0, self.length, self.width), border_radius=4)
            # Windshield
            pygame.draw.rect(veh_surf, (20, 30, 40), (self.length - 8, 2, 4, self.width-4))
            # Rear window
            pygame.draw.rect(veh_surf, (20, 30, 40), (4, 2, 3, self.width-4))
        else:
            pygame.draw.rect(veh_surf, self.color, (0, 0, self.length, self.width), border_radius=3)
            
        rotated_shadow = pygame.transform.rotate(shadow_surf, angle)
        rotated_veh = pygame.transform.rotate(veh_surf, angle)
        
        # Place on screen
        surface.blit(rotated_shadow, rotated_shadow.get_rect(center=(int(x), int(y))))
        surface.blit(rotated_veh, rotated_veh.get_rect(center=(int(x), int(y))))


class SatelliteIntersection:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("High-Fidelity Satellite Intersection Micro-Simulation")
        self.clock = pygame.time.Clock()
        
        self.background = self.generate_satellite_background()
        
        # Generate lanes for a massive 8-lane highway crossing a 6-lane arterial
        self.lanes = []
        self.create_highway_network()
        
        # Vehicles
        self.vehicles = []
        for lane in self.lanes:
            # 2-5 vehicles per lane
            for _ in range(random.randint(2, 6)):
                vtype = random.choice(['car', 'car', 'car', 'truck', 'truck', 'bus', 'bike'])
                speed = random.uniform(80, 120) if 'Highway' in lane.__dict__.get('name', '') else random.uniform(40, 60)
                self.vehicles.append(RealVehicle(lane, speed, vtype))

    def generate_satellite_background(self):
        """Procedurally scatter grass/dirt polygons for a realistic satellite base"""
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill((80, 110, 60)) # Base grass
        
        # Draw organic patches
        for _ in range(500):
            color = random.choice(GRASS_COLORS)
            x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
            radius = random.randint(20, 100)
            
            # create irregular polygons
            points = []
            for i in range(8):
                ang = math.radians(i * 45 + random.uniform(-10, 10))
                r = radius * random.uniform(0.7, 1.3)
                points.append((x + math.cos(ang)*r, y + math.sin(ang)*r))
            
            pygame.draw.polygon(surf, color, points)
            
        # Draw some concrete buildings/parking lots
        for _ in range(15):
            x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
            w, h = random.randint(100, 300), random.randint(100, 300)
            pygame.draw.rect(surf, CONCRETE_COLOR, (x, y, w, h))
            # Roof details
            pygame.draw.rect(surf, (150, 150, 145), (x+10, y+10, w-20, h-20))
            
        return surf

    def create_highway_network(self):
        """Creates precise mathematical lanes for rendering detailed roads"""
        # Highway (Horizontal-ish, slight diagonal)
        hw_y_center = 400
        hw_lanes_per_dir = 5
        lane_width = 18
        
        # Arterial (Vertical-ish)
        art_x_center = 900
        art_lanes_per_dir = 3
        
        # Create Highway Lanes (Left to Right)
        for i in range(hw_lanes_per_dir):
            y_offset = hw_y_center - (i * lane_width) - (lane_width/2) - 10 # 10px median
            lane = Lane((-200, y_offset + 50), (WIDTH + 200, y_offset - 100))
            if i == hw_lanes_per_dir - 1: lane.is_left_edge = True
            self.lanes.append(lane)
            
        # Create Highway Lanes (Right to Left)
        for i in range(hw_lanes_per_dir):
            y_offset = hw_y_center + (i * lane_width) + (lane_width/2) + 10
            lane = Lane((WIDTH + 200, y_offset - 100), (-200, y_offset + 50))
            if i == hw_lanes_per_dir - 1: lane.is_right_edge = True
            self.lanes.append(lane)
            
        # Create Arterial Lanes (Top to Bottom) - going under the highway
        for i in range(art_lanes_per_dir):
            x_offset = art_x_center - (i * lane_width) - (lane_width/2) - 5
            lane = Lane((x_offset - 100, -200), (x_offset + 100, HEIGHT + 200))
            if i == art_lanes_per_dir - 1: lane.is_left_edge = True
            self.lanes.append(lane)
            
        # Create Arterial Lanes (Bottom to Top)
        for i in range(art_lanes_per_dir):
            x_offset = art_x_center + (i * lane_width) + (lane_width/2) + 5
            lane = Lane((x_offset + 100, HEIGHT + 200), (x_offset - 100, -200))
            if i == art_lanes_per_dir - 1: lane.is_right_edge = True
            self.lanes.append(lane)
            
        # Slip lanes (On/Off ramps)
        # We can approximate smooth curves by breaking them into segments
        # For this MVP simulation, we will draw thick asphalt lines spanning the lane boundaries
        
    def draw_dashed_line(self, surface, color, start, end, width=2, dash_len=20, spacing=20):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = math.hypot(dx, dy)
        if dist == 0: return
        
        dxs = dx / dist
        dys = dy / dist
        
        current_len = 0
        while current_len < dist:
            x1 = start[0] + dxs * current_len
            y1 = start[1] + dys * current_len
            current_len += dash_len
            
            x2 = start[0] + dxs * min(current_len, dist)
            y2 = start[1] + dys * min(current_len, dist)
            
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), width)
            current_len += spacing

    def draw_infrastructure(self):
        """Draws the asphalt and lane markings"""
        # Draw Arterial Asphalt (Bottom layer)
        for lane in self.lanes[10:]: # Hacky split for arterial
            pygame.draw.line(self.screen, ASPHALT_COLOR, lane.start, lane.end, int(lane.width * 1.5))
            
        # Draw Arterial markings
        for i, lane in enumerate(self.lanes[10:]):
            if not lane.is_right_edge and not lane.is_left_edge:
                self.draw_dashed_line(self.screen, LANE_MARKER_COLOR, lane.start, lane.end)
            
        # Draw Highway Asphalt (Top layer Bridge)
        bridge_shadow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for lane in self.lanes[:10]:
            # Add broad shadow for bridge
            pygame.draw.line(bridge_shadow, (0, 0, 0, 80), 
                             (lane.start[0], lane.start[1]+30), 
                             (lane.end[0], lane.end[1]+30), int(lane.width * 2))
        self.screen.blit(bridge_shadow, (0, 0))
                             
        for lane in self.lanes[:10]:
            pygame.draw.line(self.screen, ASPHALT_COLOR, lane.start, lane.end, int(lane.width * 1.2))
            
        # Draw Highway Markings
        for i, lane in enumerate(self.lanes[:10]):
            # Center median (Yellow double line)
            if i == 4:
                pygame.draw.line(self.screen, YELLOW_LINE_COLOR, lane.start, lane.end, 3)
            elif not lane.is_right_edge and not lane.is_left_edge:
                self.draw_dashed_line(self.screen, LANE_MARKER_COLOR, lane.start, lane.end)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Draw highly detailed satellite background
            self.screen.blit(self.background, (0, 0))
            
            # Draw roads
            self.draw_infrastructure()
            
            # Update and draw vehicles
            for veh in self.vehicles:
                veh.update(dt)
                veh.draw(self.screen)
                
            pygame.display.flip()
            
        pygame.quit()

if __name__ == "__main__":
    sim = SatelliteIntersection()
    sim.run()
