import random
import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional

class VehicleType(Enum):
    CAR = "car"
    BIKE = "bike"
    AUTO = "auto"
    BUS = "bus"
    TRUCK = "truck"
    CYCLE = "cycle"
    EMERGENCY = "emergency"

@dataclass
class VehicleSpecs:
    length: float
    width: float
    max_speed: float  # pixels per second (macro) or meters per second
    acceleration: float
    deceleration: float
    lane_flexibility: float # 0 to 1, how much it ignores lanes (Indian style)

VEHICLE_CONFIGS = {
    VehicleType.CAR: VehicleSpecs(4.5, 1.8, 22.0, 2.5, 4.5, 0.3),
    VehicleType.BIKE: VehicleSpecs(2.0, 0.8, 25.0, 4.0, 6.0, 0.9),
    VehicleType.AUTO: VehicleSpecs(2.8, 1.4, 15.0, 1.5, 3.5, 0.7),
    VehicleType.BUS: VehicleSpecs(12.0, 2.6, 12.0, 0.8, 2.0, 0.1),
    VehicleType.TRUCK: VehicleSpecs(15.0, 2.6, 10.0, 0.6, 1.8, 0.1),
    VehicleType.CYCLE: VehicleSpecs(1.8, 0.6, 6.0, 0.5, 3.0, 0.5),
    VehicleType.EMERGENCY: VehicleSpecs(5.0, 2.0, 30.0, 3.5, 5.0, 0.8),
}

class TrafficAgent:
    """
    An intelligent agent representing a vehicle on Indian roads.
    Simulates 'Weak Lane Discipline' via gap-seeking behavior.
    """
    def __init__(self, agent_id: int, vtype: VehicleType, path: List[str]):
        self.id = agent_id
        self.vtype = vtype
        self.specs = VEHICLE_CONFIGS[vtype]
        self.path = path
        self.current_idx = 0
        self.progress = 0.0 # 0 to 1 along current segment
        
        self.current_speed = 0.0
        self.target_speed = self.specs.max_speed
        
        # Indian-style positioning: offset from the ideal lane center
        # -1.0 to 1.0 (left to right wobble/gap seeking)
        self.lane_offset = random.uniform(-0.5, 0.5) * self.specs.lane_flexibility
        
        # State tracking
        self.is_braking = False
        self.wait_time = 0.0
        
    def move(self, dt: float, neighbors: List['TrafficAgent'], segment_length: float):
        """
        Advanced agent-based movement logic.
        Implements Intelligent Driver Model (IDM) with lane-cutting modifications.
        """
        if self.current_idx >= len(self.path) - 1:
            return False

        # 1. Update Speed based on Distance to Leader (IDM-like)
        leader = self._get_leader(neighbors)
        
        speed_diff = 0
        if leader:
            # Distance in pixels (or meters, depending on scale)
            dist = self._dist_to(leader, segment_length)
            safe_dist = self.specs.length * 1.5 + self.current_speed * 1.0 # 1s gap
            
            if dist < safe_dist:
                # Braking
                self.is_braking = True
                self.target_speed = max(0, leader.current_speed - 2)
                # Overtaking Logic (The 'Weak Lane Discipline' part)
                if self.specs.lane_flexibility > 0.4 and random.random() < 0.2:
                    self._try_overtake()
            else:
                self.is_braking = False
                self.target_speed = self.specs.max_speed
        else:
            self.target_speed = self.specs.max_speed
            self.is_braking = False

        # Acceleration/Deceleration
        if self.current_speed < self.target_speed:
            self.current_speed += self.specs.acceleration * dt
        elif self.current_speed > self.target_speed:
            self.current_speed -= self.specs.deceleration * dt
            
        self.current_speed = max(0, min(self.current_speed, self.specs.max_speed))

        # 2. Update Progress
        if segment_length > 0:
            self.progress += (self.current_speed * dt) / segment_length
            
        if self.progress >= 1.0:
            self.progress = 0.0
            self.current_idx += 1
            # Adjust lane offset slightly when entering new road
            self.lane_offset *= 0.8 
            
        return True

    def _get_leader(self, neighbors: List['TrafficAgent']) -> Optional['TrafficAgent']:
        """Finds the vehicle directly in front in the same 'perceived' lane"""
        leader = None
        min_dist = 999999
        
        for n in neighbors:
            if n.id == self.id: continue
            if n.current_idx != self.current_idx: continue
            
            # Check if in front
            if n.progress > self.progress:
                # Check horizontal overlap (Agent-based lane discipline)
                # Indian context: 'Lanes' are messy, overlap is based on width + offset
                if abs(n.lane_offset - self.lane_offset) < (self.specs.width + n.specs.width) / 20.0:
                    dist = n.progress - self.progress
                    if dist < min_dist:
                        min_dist = dist
                        leader = n
        return leader

    def _dist_to(self, other: 'TrafficAgent', segment_len: float) -> float:
        return (other.progress - self.progress) * segment_len

    def _try_overtake(self):
        """Simulates Indian overtaking by shifting lane offset"""
        # Shift to the side where there's more room
        direction = 1 if self.lane_offset < 0 else -1
        self.lane_offset += direction * random.uniform(0.1, 0.3)
        # Clamp it
        self.lane_offset = max(-1.0, min(1.0, self.lane_offset))

    def get_pos_data(self, graph, locations) -> dict:
        """Calculate real-world lat/lon based on progress and street geometry"""
        if self.current_idx >= len(self.path) - 1:
            u = self.path[-1]
            loc = locations[u]
            return {
                "id": self.id, "vtype": self.vtype.value,
                "lat": loc['lat'], "lon": loc['lon'],
                "heading": 0, "speed": self.current_speed, "is_braking": self.is_braking
            }

        u = self.path[self.current_idx]
        v = self.path[self.current_idx + 1]
        
        # Get edge data for geometry
        edge_data = graph.get_edge_data(u, v)
        if edge_data and 0 in edge_data:
            data = edge_data[0]
        else:
            data = edge_data if edge_data else {}

        if 'geometry' in data:
            # INTERPOLATE ALONG CURVE
            coords = list(data['geometry'].coords)
            # coords is list of (lon, lat)
            
            # 1. Total curve length (already in OSM or calculated)
            total_len = data.get('length', 1.0)
            target_dist = self.progress * total_len
            
            # 2. Find the segment in the geometry that contains the target_dist
            accum_dist = 0
            lat, lon = coords[0][1], coords[0][0]
            heading = 0
            
            for i in range(len(coords) - 1):
                p1 = coords[i]
                p2 = coords[i+1]
                # Approximation of distance between GPS points (Euclidean for micro-sim)
                d = math.sqrt((p2[1]-p1[1])**2 + (p2[0]-p1[0])**2) * 111320 # Approx meters
                
                if accum_dist + d >= target_dist:
                    # Found the segment! Interpolate within it
                    seg_progress = (target_dist - accum_dist) / d if d > 0 else 0
                    lat = p1[1] + (p2[1] - p1[1]) * seg_progress
                    lon = p1[0] + (p2[0] - p1[0]) * seg_progress
                    heading = math.degrees(math.atan2(p2[0]-p1[0], p2[1]-p1[1]))
                    break
                accum_dist += d
        else:
            # Straight line fallback
            loc1 = locations[u]
            loc2 = locations[v]
            lat = loc1['lat'] + (loc2['lat'] - loc1['lat']) * self.progress
            lon = loc1['lon'] + (loc2['lon'] - loc1['lon']) * self.progress
            heading = math.degrees(math.atan2(loc2['lon'] - loc1['lon'], loc2['lat'] - loc1['lat']))
            
        # Apply Lane Offset (perpendicular shift)
        # This makes vehicles move side-by-side or cut lanes
        angle_rad = math.radians(heading + 90)
        offset_magnitude = 0.00004 * self.lane_offset # Scale to ~4 meters
        lat += math.cos(angle_rad) * offset_magnitude
        lon += math.sin(angle_rad) * offset_magnitude
        
        return {
            "id": self.id,
            "vtype": self.vtype.value,
            "lat": lat,
            "lon": lon,
            "heading": heading,
            "speed": self.current_speed,
            "is_braking": self.is_braking
        }
