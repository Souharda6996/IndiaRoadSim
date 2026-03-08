"""
Ultra-Realistic Mumbai Traffic Simulation
Accurate map representation with intelligent road avoidance system
"""

import pygame
import networkx as nx
import random
import math
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from enum import Enum
import colorsys

class RoadCondition(Enum):
    """Different road conditions with visual indicators"""
    NORMAL = ("normal", (80, 80, 80), 1.0)  # Gray, full speed
    BLOCKED = ("blocked", (255, 0, 0), 0.0)  # Red, no passage
    ACCIDENT = ("accident", (255, 128, 0), 0.2)  # Orange, very slow
    CONSTRUCTION = ("construction", (255, 200, 0), 0.3)  # Yellow, slow
    FESTIVAL = ("festival", (255, 0, 255), 0.4)  # Magenta, moderate
    HEAVY_TRAFFIC = ("heavy_traffic", (150, 100, 50), 0.3)  # Brown, slow
    WATERLOGGED = ("waterlogged", (0, 150, 255), 0.2)  # Blue, very slow
    VIP_MOVEMENT = ("vip_movement", (128, 0, 128), 0.0)  # Purple, blocked
    PROTEST = ("protest", (255, 100, 100), 0.1)  # Light red, nearly blocked
    BREAKDOWN = ("breakdown", (200, 150, 100), 0.5)  # Tan, half speed

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_exhaust(self, x, y, angle, speed, is_truck=False):
        """Add exhaust particles behind a vehicle"""
        if random.random() > (0.6 if is_truck else 0.8):
            return
            
        rad = math.radians(angle + 180 + random.uniform(-15, 15))
        vx = math.cos(rad) * speed * 0.2
        vy = math.sin(rad) * speed * 0.2
        
        life = random.uniform(0.5, 1.5)
        color = (150, 150, 150) if is_truck else (200, 200, 200)
        size = random.uniform(2, 4) if is_truck else random.uniform(1, 2.5)
        
        self.particles.append(Particle(x, y, vx, vy, life, life, color, size))

    def add_fire_smoke(self, x, y):
        """Adds fire and smoke for accidents/protests"""
        if random.random() > 0.3:
            return
            
        is_fire = random.random() > 0.6
        vx = random.uniform(-5, 5)
        vy = random.uniform(-15, -5) # rising
        
        life = random.uniform(1.0, 2.0)
        
        if is_fire:
            color = (random.randint(200, 255), random.randint(50, 150), 0)
            size = random.uniform(3, 6)
        else:
            color = (100, 100, 100)
            size = random.uniform(4, 8)
            
        self.particles.append(Particle(x, y, vx, vy, life, life, color, size))

    def update(self, dt):
        for p in self.particles[:]:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.life -= dt
            if p.life <= 0:
                self.particles.remove(p)

    def draw(self, surface):
        for p in self.particles:
            alpha = int((p.life / p.max_life) * 200)
            if alpha > 0:
                surf = pygame.Surface((p.size*2, p.size*2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*p.color, alpha), (p.size, p.size), p.size)
                surface.blit(surf, (int(p.x - p.size), int(p.y - p.size)))

@dataclass
class Vehicle:
    """Vehicle that intelligently avoids blocked roads"""
    id: int
    path: List[str]
    current_index: int = 0
    position: float = 0.0
    speed: float = 30.0
    color: Tuple[int, int, int] = (255, 0, 0)
    vehicle_type: str = "car"
    original_destination: str = None
    avoiding_roads: set = None
    last_reroute_time: float = 0
    
    def __post_init__(self):
        if self.avoiding_roads is None:
            self.avoiding_roads = set()

class RealisticMumbaiSimulation:
    """Ultra-realistic Mumbai traffic with accurate geography"""
    
    def __init__(self):
        print("\n" + "="*70)
        print("ULTRA-REALISTIC MUMBAI TRAFFIC SIMULATION")
        print("="*70)
        print("Features:")
        print("✓ Accurate Mumbai road network and geography")
        print("✓ Click roads to block them - vehicles will avoid automatically")
        print("✓ Blocked roads shown in bright colors for easy identification")
        print("✓ Real-time rerouting around obstacles")
        print("✓ Multiple traffic conditions with visual feedback")
        print("="*70 + "\n")
        
        # Initialize pygame with larger window for better map
        pygame.init()
        self.width = 1800
        self.height = 1000
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Realistic Mumbai Traffic - Smart Road Avoidance System")
        self.clock = pygame.time.Clock()
        
        # Fonts - Cyberpunk style
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.tiny_font = pygame.font.Font(None, 16)
        self.location_font = pygame.font.Font(None, 18)
        self.major_location_font = pygame.font.Font(None, 24)
        
        # Create accurate Mumbai map
        self.create_realistic_mumbai_map()
        
        # Road conditions tracking
        self.road_conditions = {}  # (start, end) -> RoadCondition
        self.blocked_roads = set()  # Set of blocked road edges
        
        # Vehicles
        self.vehicles = []
        self.vehicle_counter = 0
        
        # UI state
        self.selected_condition = RoadCondition.BLOCKED
        self.show_road_names = True  # Show road names by default for navigation
        self.show_traffic_density = False  # Start with traffic density hidden
        self.show_major_only = True  # Only show major location names
        self.paused = False
        self.simulation_time = 0
        
        # Statistics
        self.stats = {
            'total_vehicles': 0,
            'reroutes': 0,
            'blocked_roads': 0,
            'avg_speed': 0,
            'vehicles_affected': 0
        }
        
        # Phase 2 Realism
        self.particles = ParticleSystem()
        self.radar_angle = 0
        self.time_of_day = 0.0 # 0 to 24
        self.is_raining = False
        self.rain_drops = [(random.randint(0, self.width), random.randint(0, self.height), random.uniform(5, 15)) for _ in range(200)]
        
        # Create map visualization
        self.create_map_surface()
        
        # Add initial traffic
        self.add_initial_traffic()
        
        # Print network statistics
        print(f"Network initialized with {len(self.locations)} locations and {self.graph.number_of_edges()} roads")
        print(f"Average connectivity: {self.graph.number_of_edges() * 2 / len(self.locations):.1f} roads per location\n")
    
    def create_realistic_mumbai_map(self):
        """Create highly accurate Mumbai road network"""
        self.graph = nx.Graph()
        
        # Accurate Mumbai locations with realistic positions - Better Spread
        # Scaled to fit the window while maintaining geographic accuracy
        self.locations = {
            # === SOUTH MUMBAI === (Bottom of map, more spread out)
            'gateway': {'pos': (600, 920), 'name': 'Gateway of India', 'type': 'landmark', 'zone': 'South'},
            'colaba': {'pos': (550, 900), 'name': 'Colaba', 'type': 'area', 'zone': 'South'},
            'cuffe_parade': {'pos': (480, 910), 'name': 'Cuffe Parade', 'type': 'area', 'zone': 'South'},
            'regal': {'pos': (580, 870), 'name': 'Regal Cinema', 'type': 'junction', 'zone': 'South'},
            'kala_ghoda': {'pos': (610, 840), 'name': 'Kala Ghoda', 'type': 'area', 'zone': 'South'},
            'flora': {'pos': (640, 810), 'name': 'Flora Fountain', 'type': 'major_junction', 'zone': 'South'},
            'cst': {'pos': (700, 780), 'name': 'CST/VT', 'type': 'major_station', 'zone': 'South'},
            'crawford': {'pos': (730, 750), 'name': 'Crawford Market', 'type': 'market', 'zone': 'South'},
            'marine_lines': {'pos': (520, 800), 'name': 'Marine Lines', 'type': 'station', 'zone': 'South'},
            'churchgate': {'pos': (480, 780), 'name': 'Churchgate', 'type': 'major_station', 'zone': 'South'},
            'nariman_point': {'pos': (420, 850), 'name': 'Nariman Point', 'type': 'business', 'zone': 'South'},
            
            # === CENTRAL MUMBAI === (More spacing)
            'charni_road': {'pos': (510, 740), 'name': 'Charni Road', 'type': 'station', 'zone': 'Central'},
            'grant_road': {'pos': (560, 700), 'name': 'Grant Road', 'type': 'station', 'zone': 'Central'},
            'opera_house': {'pos': (530, 670), 'name': 'Opera House', 'type': 'area', 'zone': 'Central'},
            'mumbai_central': {'pos': (600, 640), 'name': 'Mumbai Central', 'type': 'major_station', 'zone': 'Central'},
            'jacob_circle': {'pos': (640, 610), 'name': 'Jacob Circle', 'type': 'junction', 'zone': 'Central'},
            'haji_ali': {'pos': (450, 680), 'name': 'Haji Ali', 'type': 'landmark', 'zone': 'Central'},
            'mahalaxmi': {'pos': (490, 630), 'name': 'Mahalaxmi', 'type': 'station', 'zone': 'Central'},
            'race_course': {'pos': (520, 590), 'name': 'Race Course', 'type': 'landmark', 'zone': 'Central'},
            'lower_parel': {'pos': (650, 560), 'name': 'Lower Parel', 'type': 'business', 'zone': 'Central'},
            'elphinstone': {'pos': (680, 530), 'name': 'Elphinstone', 'type': 'station', 'zone': 'Central'},
            'prabhadevi': {'pos': (580, 520), 'name': 'Prabhadevi', 'type': 'area', 'zone': 'Central'},
            'worli': {'pos': (420, 580), 'name': 'Worli', 'type': 'major_area', 'zone': 'Central'},
            'shivaji_park': {'pos': (540, 480), 'name': 'Shivaji Park', 'type': 'landmark', 'zone': 'Central'},
            'dadar_west': {'pos': (600, 450), 'name': 'Dadar West', 'type': 'major_junction', 'zone': 'Central'},
            'dadar_east': {'pos': (700, 450), 'name': 'Dadar East', 'type': 'major_junction', 'zone': 'Central'},
            
            # === WESTERN SUBURBS === (Better vertical spacing)
            'mahim': {'pos': (560, 410), 'name': 'Mahim', 'type': 'junction', 'zone': 'West'},
            'bandra_west': {'pos': (480, 380), 'name': 'Bandra West', 'type': 'major_area', 'zone': 'West'},
            'bandra_east': {'pos': (580, 370), 'name': 'Bandra East', 'type': 'major_area', 'zone': 'West'},
            'bkc': {'pos': (640, 360), 'name': 'BKC', 'type': 'business', 'zone': 'West'},
            'khar': {'pos': (500, 340), 'name': 'Khar', 'type': 'area', 'zone': 'West'},
            'santacruz_west': {'pos': (520, 300), 'name': 'Santacruz West', 'type': 'area', 'zone': 'West'},
            'santacruz_east': {'pos': (620, 290), 'name': 'Santacruz East', 'type': 'area', 'zone': 'West'},
            'vile_parle_west': {'pos': (540, 260), 'name': 'Vile Parle West', 'type': 'area', 'zone': 'West'},
            'vile_parle_east': {'pos': (640, 250), 'name': 'Vile Parle East', 'type': 'area', 'zone': 'West'},
            'andheri_west': {'pos': (560, 220), 'name': 'Andheri West', 'type': 'major_area', 'zone': 'West'},
            'andheri_east': {'pos': (680, 210), 'name': 'Andheri East', 'type': 'major_area', 'zone': 'West'},
            'jogeshwari_west': {'pos': (580, 180), 'name': 'Jogeshwari West', 'type': 'area', 'zone': 'West'},
            'jogeshwari_east': {'pos': (700, 170), 'name': 'Jogeshwari East', 'type': 'area', 'zone': 'West'},
            'goregaon_west': {'pos': (600, 140), 'name': 'Goregaon West', 'type': 'area', 'zone': 'West'},
            'goregaon_east': {'pos': (720, 130), 'name': 'Goregaon East', 'type': 'area', 'zone': 'West'},
            'malad_west': {'pos': (620, 100), 'name': 'Malad West', 'type': 'area', 'zone': 'West'},
            'malad_east': {'pos': (740, 90), 'name': 'Malad East', 'type': 'area', 'zone': 'West'},
            'kandivali_west': {'pos': (640, 60), 'name': 'Kandivali West', 'type': 'area', 'zone': 'West'},
            'kandivali_east': {'pos': (760, 50), 'name': 'Kandivali East', 'type': 'area', 'zone': 'West'},
            'borivali_west': {'pos': (660, 30), 'name': 'Borivali West', 'type': 'major_area', 'zone': 'West'},
            'borivali_east': {'pos': (780, 25), 'name': 'Borivali East', 'type': 'major_area', 'zone': 'West'},
            
            # === CENTRAL LINE / EASTERN AREAS === (Spread out eastward)
            'sion': {'pos': (780, 500), 'name': 'Sion', 'type': 'major_junction', 'zone': 'East'},
            'kings_circle': {'pos': (740, 480), 'name': 'Kings Circle', 'type': 'junction', 'zone': 'East'},
            'matunga': {'pos': (720, 460), 'name': 'Matunga', 'type': 'station', 'zone': 'East'},
            'wadala': {'pos': (820, 520), 'name': 'Wadala', 'type': 'junction', 'zone': 'East'},
            'kurla_west': {'pos': (860, 440), 'name': 'Kurla West', 'type': 'major_junction', 'zone': 'East'},
            'kurla_east': {'pos': (920, 430), 'name': 'Kurla East', 'type': 'major_junction', 'zone': 'East'},
            'chembur': {'pos': (880, 500), 'name': 'Chembur', 'type': 'area', 'zone': 'East'},
            'ghatkopar_west': {'pos': (960, 400), 'name': 'Ghatkopar West', 'type': 'area', 'zone': 'East'},
            'ghatkopar_east': {'pos': (1020, 390), 'name': 'Ghatkopar East', 'type': 'area', 'zone': 'East'},
            'vidyavihar': {'pos': (980, 420), 'name': 'Vidyavihar', 'type': 'station', 'zone': 'East'},
            'vikhroli_west': {'pos': (1060, 360), 'name': 'Vikhroli West', 'type': 'area', 'zone': 'East'},
            'vikhroli_east': {'pos': (1120, 350), 'name': 'Vikhroli East', 'type': 'area', 'zone': 'East'},
            'kanjurmarg': {'pos': (1100, 320), 'name': 'Kanjurmarg', 'type': 'station', 'zone': 'East'},
            'bhandup_west': {'pos': (1160, 280), 'name': 'Bhandup West', 'type': 'area', 'zone': 'East'},
            'bhandup_east': {'pos': (1220, 270), 'name': 'Bhandup East', 'type': 'area', 'zone': 'East'},
            'mulund_west': {'pos': (1200, 240), 'name': 'Mulund West', 'type': 'area', 'zone': 'East'},
            'mulund_east': {'pos': (1260, 230), 'name': 'Mulund East', 'type': 'area', 'zone': 'East'},
            
            # === SPECIAL LOCATIONS === (Strategic positions)
            'bandra_worli_sealink': {'pos': (380, 480), 'name': 'Bandra-Worli Sea Link', 'type': 'bridge', 'zone': 'Bridge'},
            'airport_t1': {'pos': (660, 270), 'name': 'Airport T1', 'type': 'airport', 'zone': 'Airport'},
            'airport_t2': {'pos': (680, 260), 'name': 'Airport T2', 'type': 'airport', 'zone': 'Airport'},
            'seepz': {'pos': (740, 190), 'name': 'SEEPZ', 'type': 'business', 'zone': 'East'},
            'powai': {'pos': (880, 280), 'name': 'Powai', 'type': 'area', 'zone': 'East'},
            'iit_bombay': {'pos': (920, 260), 'name': 'IIT Bombay', 'type': 'landmark', 'zone': 'East'},
            'hiranandani': {'pos': (960, 240), 'name': 'Hiranandani', 'type': 'business', 'zone': 'East'},
            'aarey': {'pos': (800, 160), 'name': 'Aarey Colony', 'type': 'area', 'zone': 'East'},
            'film_city': {'pos': (840, 140), 'name': 'Film City', 'type': 'landmark', 'zone': 'East'},
            'national_park': {'pos': (880, 100), 'name': 'National Park', 'type': 'landmark', 'zone': 'East'},
        }
        
        # Add nodes to graph
        for loc_id, data in self.locations.items():
            self.graph.add_node(loc_id, **data)
        
        # Realistic Mumbai road connections - comprehensive network
        self.roads = [
            # === MAJOR HIGHWAYS ===
            # Western Express Highway (Main North-South Artery)
            ('borivali_west', 'kandivali_west', {'name': 'Western Express Highway', 'type': 'highway', 'lanes': 8}),
            ('kandivali_west', 'malad_west', {'name': 'Western Express Highway', 'type': 'highway', 'lanes': 8}),
            ('malad_west', 'goregaon_west', {'name': 'Western Express Highway', 'type': 'highway', 'lanes': 8}),
            ('goregaon_west', 'jogeshwari_west', {'name': 'Western Express Highway', 'type': 'highway', 'lanes': 8}),
            ('jogeshwari_west', 'andheri_west', {'name': 'Western Express Highway', 'type': 'highway', 'lanes': 8}),
            ('andheri_west', 'vile_parle_west', {'name': 'Western Express Highway', 'type': 'highway', 'lanes': 8}),
            ('vile_parle_west', 'santacruz_west', {'name': 'Western Express Highway', 'type': 'highway', 'lanes': 8}),
            
            # SV Road (Parallel to WEH)
            ('borivali_west', 'kandivali_west', {'name': 'SV Road', 'type': 'main', 'lanes': 4}),
            ('kandivali_west', 'malad_west', {'name': 'SV Road', 'type': 'main', 'lanes': 4}),
            ('malad_west', 'goregaon_west', {'name': 'SV Road', 'type': 'main', 'lanes': 4}),
            ('goregaon_west', 'jogeshwari_west', {'name': 'SV Road', 'type': 'main', 'lanes': 4}),
            ('jogeshwari_west', 'andheri_west', {'name': 'SV Road', 'type': 'main', 'lanes': 4}),
            ('andheri_west', 'vile_parle_west', {'name': 'SV Road', 'type': 'main', 'lanes': 4}),
            ('vile_parle_west', 'santacruz_west', {'name': 'SV Road', 'type': 'main', 'lanes': 4}),
            ('santacruz_west', 'khar', {'name': 'SV Road', 'type': 'main', 'lanes': 6}),
            ('khar', 'bandra_west', {'name': 'SV Road', 'type': 'main', 'lanes': 6}),
            ('bandra_west', 'mahim', {'name': 'SV Road', 'type': 'main', 'lanes': 6}),
            
            # Eastern Express Highway (Main Eastern Artery)
            ('mulund_east', 'bhandup_east', {'name': 'Eastern Express Highway', 'type': 'highway', 'lanes': 6}),
            ('bhandup_east', 'kanjurmarg', {'name': 'Eastern Express Highway', 'type': 'highway', 'lanes': 6}),
            ('kanjurmarg', 'vikhroli_east', {'name': 'Eastern Express Highway', 'type': 'highway', 'lanes': 6}),
            ('vikhroli_east', 'ghatkopar_east', {'name': 'Eastern Express Highway', 'type': 'highway', 'lanes': 6}),
            ('ghatkopar_east', 'kurla_east', {'name': 'Eastern Express Highway', 'type': 'highway', 'lanes': 6}),
            ('kurla_east', 'chembur', {'name': 'Eastern Express Highway', 'type': 'highway', 'lanes': 6}),
            ('chembur', 'wadala', {'name': 'Eastern Express Highway', 'type': 'highway', 'lanes': 6}),
            ('wadala', 'sion', {'name': 'Eastern Express Highway', 'type': 'highway', 'lanes': 6}),
            
            # LBS Marg (Parallel to Eastern Express)
            ('mulund_west', 'bhandup_west', {'name': 'LBS Marg', 'type': 'main', 'lanes': 6}),
            ('bhandup_west', 'kanjurmarg', {'name': 'LBS Marg', 'type': 'main', 'lanes': 6}),
            ('kanjurmarg', 'vikhroli_west', {'name': 'LBS Marg', 'type': 'main', 'lanes': 6}),
            ('vikhroli_west', 'ghatkopar_west', {'name': 'LBS Marg', 'type': 'main', 'lanes': 6}),
            ('ghatkopar_west', 'vidyavihar', {'name': 'LBS Marg', 'type': 'main', 'lanes': 6}),
            ('vidyavihar', 'kurla_east', {'name': 'LBS Marg', 'type': 'main', 'lanes': 6}),
            ('kurla_west', 'kurla_east', {'name': 'LBS Marg', 'type': 'main', 'lanes': 6}),
            
            # === MAJOR ROADS ===
            # Marine Drive & Coastal Road
            ('nariman_point', 'marine_lines', {'name': 'Marine Drive', 'type': 'seaface', 'lanes': 6}),
            ('marine_lines', 'churchgate', {'name': 'Marine Drive', 'type': 'seaface', 'lanes': 6}),
            ('churchgate', 'charni_road', {'name': 'Marine Drive', 'type': 'seaface', 'lanes': 6}),
            ('charni_road', 'grant_road', {'name': 'NS Road', 'type': 'main', 'lanes': 4}),
            ('grant_road', 'opera_house', {'name': 'Lamington Road', 'type': 'main', 'lanes': 4}),
            ('opera_house', 'mumbai_central', {'name': 'Bellasis Road', 'type': 'main', 'lanes': 4}),
            
            # Pedder Road - Haji Ali - Worli Connection
            ('nariman_point', 'haji_ali', {'name': 'Pedder Road', 'type': 'main', 'lanes': 4}),
            ('haji_ali', 'mahalaxmi', {'name': 'Pedder Road', 'type': 'main', 'lanes': 4}),
            ('mahalaxmi', 'race_course', {'name': 'Mahalaxmi Road', 'type': 'main', 'lanes': 4}),
            ('race_course', 'worli', {'name': 'Dr Annie Besant Road', 'type': 'main', 'lanes': 6}),
            
            # South Mumbai Grid (Fort, Colaba, Churchgate)
            ('gateway', 'colaba', {'name': 'Colaba Causeway', 'type': 'main', 'lanes': 4}),
            ('colaba', 'cuffe_parade', {'name': 'Cuffe Parade Road', 'type': 'main', 'lanes': 4}),
            ('cuffe_parade', 'nariman_point', {'name': 'Captain Prakash Pethe Marg', 'type': 'main', 'lanes': 4}),
            ('colaba', 'regal', {'name': 'SP Mukherjee Road', 'type': 'main', 'lanes': 4}),
            ('regal', 'kala_ghoda', {'name': 'MG Road', 'type': 'main', 'lanes': 4}),
            ('kala_ghoda', 'flora', {'name': 'MG Road', 'type': 'main', 'lanes': 4}),
            ('flora', 'cst', {'name': 'DN Road', 'type': 'main', 'lanes': 4}),
            ('cst', 'crawford', {'name': 'Mohammed Ali Road', 'type': 'main', 'lanes': 4}),
            ('flora', 'churchgate', {'name': 'Veer Nariman Road', 'type': 'main', 'lanes': 4}),
            ('flora', 'marine_lines', {'name': 'K Dubash Marg', 'type': 'main', 'lanes': 3}),
            ('crawford', 'mumbai_central', {'name': 'P DMello Road', 'type': 'main', 'lanes': 4}),
            
            # Central Mumbai Connections (Worli - Lower Parel - Dadar)
            ('worli', 'prabhadevi', {'name': 'Annie Besant Road', 'type': 'main', 'lanes': 6}),
            ('prabhadevi', 'lower_parel', {'name': 'NM Joshi Marg', 'type': 'main', 'lanes': 4}),
            ('lower_parel', 'elphinstone', {'name': 'Senapati Bapat Marg', 'type': 'main', 'lanes': 6}),
            ('elphinstone', 'dadar_west', {'name': 'Senapati Bapat Marg', 'type': 'main', 'lanes': 6}),
            ('prabhadevi', 'shivaji_park', {'name': 'Sayani Road', 'type': 'main', 'lanes': 4}),
            ('lower_parel', 'jacob_circle', {'name': 'Sane Guruji Marg', 'type': 'main', 'lanes': 4}),
            ('jacob_circle', 'mumbai_central', {'name': 'Tardeo Road', 'type': 'main', 'lanes': 4}),
            ('race_course', 'jacob_circle', {'name': 'August Kranti Marg', 'type': 'main', 'lanes': 4}),
            
            # Dadar Hub - Major Junction Connections
            ('dadar_west', 'dadar_east', {'name': 'Dadar TT Bridge', 'type': 'main', 'lanes': 6}),
            ('dadar_west', 'shivaji_park', {'name': 'Cadell Road', 'type': 'main', 'lanes': 4}),
            ('shivaji_park', 'mahim', {'name': 'Lady Jamshedji Road', 'type': 'main', 'lanes': 4}),
            ('dadar_east', 'matunga', {'name': 'Dr Ambedkar Road', 'type': 'main', 'lanes': 4}),
            ('matunga', 'kings_circle', {'name': 'Dr Ambedkar Road', 'type': 'main', 'lanes': 4}),
            ('kings_circle', 'sion', {'name': 'Sion Circle Road', 'type': 'main', 'lanes': 4}),
            ('dadar_east', 'wadala', {'name': 'Katrak Road', 'type': 'main', 'lanes': 4}),
            ('mahim', 'bandra_east', {'name': 'Mahim Causeway', 'type': 'main', 'lanes': 6}),
            
            # Bandra-Kurla Complex (BKC) Network
            ('bandra_east', 'bkc', {'name': 'BKC Road', 'type': 'main', 'lanes': 6}),
            ('bkc', 'kurla_west', {'name': 'CST Road', 'type': 'main', 'lanes': 6}),
            ('bandra_west', 'bandra_east', {'name': 'Western Railway Bridge', 'type': 'main', 'lanes': 4}),
            ('bkc', 'santacruz_east', {'name': 'Santacruz-Chembur Link Road', 'type': 'main', 'lanes': 6}),
            ('santacruz_east', 'kurla_west', {'name': 'Santacruz-Chembur Link Road', 'type': 'main', 'lanes': 4}),
            
            # Airport Area Network
            ('santacruz_east', 'airport_t1', {'name': 'Western Express Highway', 'type': 'main', 'lanes': 6}),
            ('vile_parle_east', 'airport_t2', {'name': 'Western Express Highway', 'type': 'main', 'lanes': 6}),
            ('airport_t1', 'airport_t2', {'name': 'Airport Link Road', 'type': 'main', 'lanes': 4}),
            ('santacruz_west', 'santacruz_east', {'name': 'Milan Subway', 'type': 'main', 'lanes': 4}),
            ('vile_parle_west', 'vile_parle_east', {'name': 'Vile Parle Station Road', 'type': 'main', 'lanes': 4}),
            ('andheri_west', 'andheri_east', {'name': 'Andheri Bridge', 'type': 'main', 'lanes': 6}),
            
            # Important East-West Connectors
            ('andheri_east', 'kurla_west', {'name': 'Andheri-Kurla Road', 'type': 'main', 'lanes': 6}),
            ('andheri_east', 'seepz', {'name': 'MIDC Road', 'type': 'main', 'lanes': 4}),
            ('jogeshwari_west', 'jogeshwari_east', {'name': 'Jogeshwari Bridge', 'type': 'main', 'lanes': 4}),
            ('goregaon_west', 'goregaon_east', {'name': 'Goregaon Bridge', 'type': 'main', 'lanes': 4}),
            ('malad_west', 'malad_east', {'name': 'Malad Bridge', 'type': 'main', 'lanes': 4}),
            ('kandivali_west', 'kandivali_east', {'name': 'Kandivali Bridge', 'type': 'main', 'lanes': 4}),
            ('borivali_west', 'borivali_east', {'name': 'Borivali Bridge', 'type': 'main', 'lanes': 4}),
            
            # JVLR (Jogeshwari-Vikhroli Link Road) - Major East-West Corridor
            ('jogeshwari_east', 'seepz', {'name': 'JVLR', 'type': 'highway', 'lanes': 6}),
            ('seepz', 'powai', {'name': 'JVLR', 'type': 'highway', 'lanes': 6}),
            ('powai', 'vikhroli_west', {'name': 'JVLR', 'type': 'highway', 'lanes': 6}),
            ('vikhroli_west', 'vikhroli_east', {'name': 'Vikhroli Bridge', 'type': 'main', 'lanes': 4}),
            
            # Powai Tech Hub Network
            ('powai', 'iit_bombay', {'name': 'Powai Road', 'type': 'main', 'lanes': 4}),
            ('iit_bombay', 'hiranandani', {'name': 'Main Avenue', 'type': 'main', 'lanes': 4}),
            ('hiranandani', 'vikhroli_west', {'name': 'Hiranandani Road', 'type': 'main', 'lanes': 4}),
            ('powai', 'kanjurmarg', {'name': 'Powai-Kanjurmarg Road', 'type': 'main', 'lanes': 4}),
            ('hiranandani', 'ghatkopar_east', {'name': 'Hiranandani Link Road', 'type': 'main', 'lanes': 4}),
            
            # Goregaon-Mulund Link Road and Aarey Network
            ('goregaon_east', 'aarey', {'name': 'GMLR', 'type': 'main', 'lanes': 4}),
            ('aarey', 'film_city', {'name': 'Film City Road', 'type': 'main', 'lanes': 4}),
            ('film_city', 'national_park', {'name': 'National Park Road', 'type': 'main', 'lanes': 2}),
            ('aarey', 'powai', {'name': 'Aarey Road', 'type': 'main', 'lanes': 4}),
            ('borivali_east', 'national_park', {'name': 'Borivali Park Road', 'type': 'main', 'lanes': 4}),
            
            # Bandra-Worli Sea Link - Premium Connectivity
            ('bandra_west', 'bandra_worli_sealink', {'name': 'Sea Link Entry', 'type': 'bridge', 'lanes': 8}),
            ('bandra_worli_sealink', 'worli', {'name': 'Bandra-Worli Sea Link', 'type': 'bridge', 'lanes': 8}),
            ('worli', 'lower_parel', {'name': 'Worli-Lower Parel Road', 'type': 'main', 'lanes': 4}),
            
            # Central Mumbai Grid Connections
            ('mumbai_central', 'grant_road', {'name': 'Falkland Road', 'type': 'main', 'lanes': 4}),
            ('grant_road', 'charni_road', {'name': 'Girgaum Road', 'type': 'main', 'lanes': 4}),
            ('opera_house', 'charni_road', {'name': 'Queen Road', 'type': 'main', 'lanes': 3}),
            
            # Eastern Mumbai Network (Chembur-Wadala-Sion Triangle)
            ('chembur', 'wadala', {'name': 'Chembur-Wadala Link Road', 'type': 'main', 'lanes': 4}),
            ('wadala', 'sion', {'name': 'Sion-Wadala Link Road', 'type': 'main', 'lanes': 4}),
            ('chembur', 'ghatkopar_east', {'name': 'RC Marg', 'type': 'main', 'lanes': 4}),
            ('sion', 'kurla_west', {'name': 'Sion-Trombay Road', 'type': 'main', 'lanes': 6}),
            ('kings_circle', 'wadala', {'name': 'RAK Marg', 'type': 'main', 'lanes': 4}),
            
            # Ghatkopar Hub Connections
            ('ghatkopar_west', 'ghatkopar_east', {'name': 'Ghatkopar Station Road', 'type': 'main', 'lanes': 4}),
            ('ghatkopar_west', 'vidyavihar', {'name': 'LBS Marg', 'type': 'main', 'lanes': 6}),
            ('vidyavihar', 'kurla_east', {'name': 'LBS Marg', 'type': 'main', 'lanes': 6}),
            ('ghatkopar_west', 'kurla_west', {'name': 'Ghatkopar-Kurla Road', 'type': 'main', 'lanes': 4}),
            
            # Northern Mumbai Connections
            ('mulund_west', 'mulund_east', {'name': 'Mulund Station Road', 'type': 'main', 'lanes': 4}),
            ('bhandup_west', 'bhandup_east', {'name': 'Bhandup Station Road', 'type': 'main', 'lanes': 4}),
            ('mulund_east', 'aarey', {'name': 'Mulund-Goregaon Link', 'type': 'main', 'lanes': 4}),
            
            # Service Roads and Additional Connectivity
            ('kandivali_east', 'malad_east', {'name': 'WEH Service Road East', 'type': 'main', 'lanes': 4}),
            ('malad_east', 'goregaon_east', {'name': 'WEH Service Road East', 'type': 'main', 'lanes': 4}),
            ('goregaon_east', 'jogeshwari_east', {'name': 'WEH Service Road East', 'type': 'main', 'lanes': 4}),
            ('jogeshwari_east', 'andheri_east', {'name': 'WEH Service Road East', 'type': 'main', 'lanes': 4}),
            ('andheri_east', 'vile_parle_east', {'name': 'WEH Service Road East', 'type': 'main', 'lanes': 4}),
            ('vile_parle_east', 'santacruz_east', {'name': 'WEH Service Road East', 'type': 'main', 'lanes': 4}),
            
            # Additional Strategic Connections for Better Flow
            ('airport_t2', 'seepz', {'name': 'Sahar Road', 'type': 'main', 'lanes': 6}),
            ('bkc', 'wadala', {'name': 'BKC-Wadala Link', 'type': 'main', 'lanes': 4}),
            ('sion', 'dadar_east', {'name': 'Sion-Dadar Link', 'type': 'main', 'lanes': 4}),
            ('worli', 'mahim', {'name': 'Worli Sea Face', 'type': 'seaface', 'lanes': 4}),
            ('bandra_west', 'khar', {'name': 'Waterfield Road', 'type': 'main', 'lanes': 4}),
            ('santacruz_west', 'vile_parle_west', {'name': 'Linking Road Extension', 'type': 'main', 'lanes': 4}),
            ('lower_parel', 'wadala', {'name': 'Lower Parel-Wadala Bridge', 'type': 'main', 'lanes': 4}),
            ('kurla_west', 'vidyavihar', {'name': 'Kurla-Vidyavihar Road', 'type': 'main', 'lanes': 4}),
            ('matunga', 'wadala', {'name': 'Matunga-Wadala Road', 'type': 'main', 'lanes': 3}),
            ('mahim', 'dadar_west', {'name': 'Mahim-Dadar Road', 'type': 'main', 'lanes': 4}),
        ]
        
        # Add all roads to graph with distance calculation
        for start, end, attrs in self.roads:
            if start in self.locations and end in self.locations:
                p1 = self.locations[start]['pos']
                p2 = self.locations[end]['pos']
                distance = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
                attrs['distance'] = distance
                attrs['traffic'] = 0
                self.graph.add_edge(start, end, **attrs)
        
        # Fix the linking_road reference
        if 'linking_road' not in self.locations:
            # Remove the invalid edge or fix it
            if self.graph.has_edge('khar', 'linking_road'):
                self.graph.remove_edge('khar', 'linking_road')
            # Add correct connection
            if 'bandra_west' in self.locations:
                self.graph.add_edge('khar', 'bandra_west', 
                                   name='Linking Road', type='main', lanes=4, 
                                   distance=50, traffic=0)
    
    def create_map_surface(self):
        """Create the base map visualization"""
        self.map_surface = pygame.Surface((self.width, self.height))
        self.update_map()
    
    def draw_elegant_junctions(self):
        """Draw elegant junction indicators at major intersections"""
        # Identify major junctions (nodes with 4+ connections)
        for node in self.graph.nodes():
            if node not in self.locations:
                continue
            
            connections = list(self.graph.neighbors(node))
            num_connections = len(connections)
            
            if num_connections >= 4:
                # Major junction
                junction_type = 'major'
                radius = 8
            elif num_connections >= 3:
                # Regular junction
                junction_type = 'regular'
                radius = 5
            else:
                continue
            
            pos = self.locations[node]['pos']
            
            # Draw elegant junction circle
            if junction_type == 'major':
                # Major junction - subtle gradient effect
                for i in range(3):
                    color = (140 + i*5, 140 + i*5, 150 + i*5)
                    pygame.draw.circle(self.map_surface, color, pos, radius - i)
                
                # Center dot
                pygame.draw.circle(self.map_surface, (130, 130, 140), pos, 2)
                
                # Outer ring for major junctions
                pygame.draw.circle(self.map_surface, (150, 150, 160), pos, radius + 2, 1)
            else:
                # Regular junction - simple circle
                pygame.draw.circle(self.map_surface, (150, 150, 160), pos, radius)
                pygame.draw.circle(self.map_surface, (140, 140, 150), pos, radius, 1)
    
    def draw_road_names(self):
        """Draw road names with smart placement to avoid overlaps"""
        # Priority roads to label (most important first)
        priority_roads = [
            ('Western Express Highway', 'highway', (100, 100, 140)),
            ('Eastern Express Highway', 'highway', (100, 100, 140)),
            ('Bandra-Worli Sea Link', 'bridge', (80, 100, 160)),
            ('JVLR', 'highway', (100, 100, 140)),
            ('Marine Drive', 'seaface', (80, 120, 150)),
            ('SV Road', 'main', (110, 110, 130)),
            ('LBS Marg', 'main', (110, 110, 130)),
            ('Andheri-Kurla Road', 'main', (120, 120, 140)),
            ('Linking Road', 'main', (120, 120, 140)),
            ('Senapati Bapat Marg', 'main', (120, 120, 140)),
            ('Mahim Causeway', 'main', (120, 120, 140)),
        ]
        
        # Track which roads we've already labeled
        labeled_roads = set()
        label_positions = []  # Track label positions to avoid overlaps
        
        # First pass: Label priority roads
        for road_name, road_type, color in priority_roads:
            self.label_road(road_name, road_type, color, labeled_roads, label_positions)
        
        # Second pass: Label other significant roads if space available
        for edge in self.graph.edges(data=True):
            start, end, data = edge
            road_name = data.get('name', '')
            road_type = data.get('type', 'main')
            
            # Skip if already labeled or not significant
            if road_name in labeled_roads or not road_name:
                continue
            
            # Only label longer main roads
            if road_type in ['main', 'seaface'] and start in self.locations and end in self.locations:
                start_pos = self.locations[start]['pos']
                end_pos = self.locations[end]['pos']
                length = math.sqrt((end_pos[0]-start_pos[0])**2 + (end_pos[1]-start_pos[1])**2)
                
                if length > 150:  # Increase minimum length to reduce clutter
                    color = (140, 140, 160)  # Even more subtle color for secondary roads
                    self.label_road(road_name, road_type, color, labeled_roads, label_positions)
    
    def label_road(self, road_name, road_type, color, labeled_roads, label_positions):
        """Label a specific road with smart positioning"""
        # Find the longest segment of this road
        best_segment = None
        best_length = 0
        
        for edge in self.graph.edges(data=True):
            start, end, data = edge
            if data.get('name', '') == road_name and start in self.locations and end in self.locations:
                start_pos = self.locations[start]['pos']
                end_pos = self.locations[end]['pos']
                length = math.sqrt((end_pos[0]-start_pos[0])**2 + (end_pos[1]-start_pos[1])**2)
                
                if length > best_length:
                    best_length = length
                    best_segment = (start_pos, end_pos, data)
        
        if best_segment and best_length > 50:  # Minimum length to label
            start_pos, end_pos, data = best_segment
            
            # Calculate position for label
            mid_x = (start_pos[0] + end_pos[0]) // 2
            mid_y = (start_pos[1] + end_pos[1]) // 2
            
            # Calculate angle for text rotation
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            angle = math.degrees(math.atan2(-dy, dx))
            
            # Normalize angle for readability
            if angle > 90:
                angle -= 180
            elif angle < -90:
                angle += 180
            
            # Create text with smaller font
            font_size = 11 if road_type == 'highway' else 10
            font = pygame.font.Font(None, font_size)
            text = font.render(road_name, True, color)
            
            # Calculate perpendicular offset to place text above/beside road
            offset_distance = 18 if road_type == 'highway' else 15
            perp_angle = math.radians(angle - 90)
            offset_x = offset_distance * math.cos(perp_angle)
            offset_y = offset_distance * math.sin(perp_angle)
            
            # Adjust position
            label_x = mid_x + offset_x
            label_y = mid_y + offset_y
            
            # Check for overlap with existing labels
            text_rect = text.get_rect(center=(label_x, label_y))
            
            # Check if this position overlaps with any existing label
            overlap = False
            for existing_rect in label_positions:
                if text_rect.colliderect(existing_rect):
                    overlap = True
                    break
            
            # If no overlap, draw the label
            if not overlap:
                # Draw subtle background for better readability
                bg_rect = text_rect.copy()
                bg_rect.inflate_ip(4, 2)
                bg_surface = pygame.Surface(bg_rect.size)
                bg_surface.set_alpha(230)
                bg_surface.fill((255, 255, 253))
                self.map_surface.blit(bg_surface, bg_rect)
                
                # Draw the text
                self.map_surface.blit(text, text_rect)
                
                # Mark as labeled with expanded rect to ensure spacing
                labeled_roads.add(road_name)
                expanded_rect = text_rect.copy()
                expanded_rect.inflate_ip(10, 6)  # Add extra padding for spacing
                label_positions.append(expanded_rect)
    
    def update_map(self):
        """Update map visualization with current road conditions using an elegant dark mode digital twin style"""
        # Clear map with deep dark background (Cyberpunk/Digital Twin aesthetic)
        self.map_surface.fill((10, 12, 20))  # Very dark blue-black
        
        # Draw water bodies (Arabian Sea) - Deep glowing blue
        sea_color = (0, 20, 40)
        for i in range(5):
            alpha = 255 - i * 30
            color = (5 + i*2, 25 + i*5, 50 + i*10)
            pygame.draw.rect(self.map_surface, color, (i*20, 0, 350-i*20, self.height))
        
        # Worli Sea Face curve
        pygame.draw.ellipse(self.map_surface, (10, 30, 60), (300, 500, 150, 400))
        # Back Bay area
        pygame.draw.ellipse(self.map_surface, (10, 30, 60), (320, 750, 120, 200))
        
        # Draw zones with subtle colors
        zone_colors = {
            'South': (255, 250, 245),
            'Central': (250, 255, 245),
            'West': (245, 250, 255),
            'East': (255, 245, 250),
        }
        
        # Draw roads with conditions
        for edge in self.graph.edges(data=True):
            start, end, data = edge
            if start not in self.locations or end not in self.locations:
                continue
                
            start_pos = self.locations[start]['pos']
            end_pos = self.locations[end]['pos']
            
            # Get road condition
            edge_tuple = (start, end)
            rev_edge_tuple = (end, start)
            
            # Check if road is blocked or has condition
            if edge_tuple in self.road_conditions:
                condition = self.road_conditions[edge_tuple]
                color = condition.value[1]  # Get color from enum
                width = data.get('lanes', 4) + 4  # Make it thicker for visibility
                
                # Draw glow effect for blocked roads
                if condition in [RoadCondition.BLOCKED, RoadCondition.VIP_MOVEMENT]:
                    for i in range(3):
                        glow_color = (*color, 100 - i*30)[:3]
                        pygame.draw.line(self.map_surface, glow_color, 
                                       start_pos, end_pos, width + (3-i)*2)
            else:
                # Elegant road colors - more subtle
                road_type = data.get('type', 'main')
                if road_type == 'highway':
                    color = (120, 120, 130)  # Lighter gray
                    width = max(2, data.get('lanes', 6) - 2)  # Thinner lines
                elif road_type == 'bridge':
                    color = (140, 140, 180)  # Subtle purple
                    width = max(3, data.get('lanes', 8) - 2)
                elif road_type == 'seaface':
                    color = (130, 150, 170)  # Subtle blue-gray
                    width = max(2, data.get('lanes', 6) - 2)
                else:
                    color = (160, 160, 165)  # Very light gray
                    width = max(1, data.get('lanes', 4) - 2)
            
            # Draw road
            pygame.draw.line(self.map_surface, color, start_pos, end_pos, width)
            
            # Draw traffic density if enabled
            if self.show_traffic_density and data.get('traffic', 0) > 0:
                traffic_level = min(data['traffic'], 10)
                for i in range(traffic_level):
                    t = (i + 1) / (traffic_level + 1)
                    x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
                    y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
                    pygame.draw.circle(self.map_surface, (255, 100, 0), (int(x), int(y)), 2)
        
        # Draw elegant junction circles at major intersections
        self.draw_elegant_junctions()
        
        # Draw road names AFTER all roads are drawn to avoid overlap
        if self.show_road_names:
            self.draw_road_names()
        
        # Draw location nodes
        for loc_id, data in self.locations.items():
            pos = data['pos']
            loc_type = data.get('type', 'area')
            
            # Elegant node colors - more subtle and sophisticated
            node_colors = {
                'landmark': (220, 120, 120),  # Muted red
                'major_station': (120, 120, 220),  # Muted blue
                'station': (170, 170, 220),  # Light blue
                'major_junction': (220, 170, 80),  # Muted orange
                'junction': (220, 200, 140),  # Light orange
                'business': (120, 200, 120),  # Muted green
                'airport': (180, 120, 220),  # Muted purple
                'bridge': (170, 170, 200),  # Light purple
                'major_area': (180, 180, 180),  # Gray
                'area': (200, 200, 200),  # Light gray
                'market': (220, 180, 150),  # Muted peach
            }
            
            color = node_colors.get(loc_type, (200, 200, 200))
            # Larger node sizes for better visibility
            if 'major' in loc_type or loc_type in ['landmark', 'airport', 'bridge']:
                size = 10
            elif loc_type in ['major_station', 'business']:
                size = 8
            else:
                size = 6
            
            # Draw node
            pygame.draw.circle(self.map_surface, color, pos, size)
            pygame.draw.circle(self.map_surface, (50, 50, 50), pos, size, 1)
            
            # Draw labels selectively for elegance
            if self.show_road_names:
                # Skip regular areas if show_major_only is True
                if self.show_major_only and loc_type not in ['landmark', 'major_station', 'major_junction', 
                                                              'major_area', 'airport', 'bridge', 'business']:
                    continue
                # Count connections to determine label position
                num_connections = len(list(self.graph.neighbors(loc_id)))
                
                # Smart positioning based on location and connections
                # Determine best position for label to avoid roads
                if loc_id in ['gateway', 'colaba', 'cuffe_parade', 'nariman_point']:
                    # South Mumbai - labels below
                    offset_x, offset_y = 0, 15
                elif loc_id in ['borivali_west', 'kandivali_west', 'malad_west', 'goregaon_west']:
                    # Western suburbs - labels to the left
                    offset_x, offset_y = -60, 0
                elif loc_id in ['mulund_east', 'bhandup_east', 'vikhroli_east', 'ghatkopar_east']:
                    # Eastern suburbs - labels to the right  
                    offset_x, offset_y = 12, 0
                elif 'east' in loc_id:
                    # East side locations - labels to the right
                    offset_x, offset_y = 12, -2
                elif 'west' in loc_id:
                    # West side locations - labels to the left
                    offset_x, offset_y = -60, -2
                elif num_connections > 4:
                    # Busy junctions - labels above
                    offset_x, offset_y = 0, -15
                else:
                    # Default - labels to the right
                    offset_x, offset_y = 12, 0
                
                # Determine font and styling based on location type
                if 'major' in loc_type or loc_type in ['landmark', 'airport', 'bridge']:
                    # Major locations - elegant but not overwhelming
                    font = self.location_font  # Use smaller font
                    text_color = (60, 60, 100)  # Softer blue
                    text = font.render(data['name'], True, text_color)
                    text_rect = text.get_rect()
                    
                    # Adjust position based on offset
                    if offset_x < 0:
                        text_rect.midright = (pos[0] + offset_x, pos[1] + offset_y)
                    elif offset_y < 0:
                        text_rect.midbottom = (pos[0] + offset_x, pos[1] + offset_y)
                    elif offset_y > 0:
                        text_rect.midtop = (pos[0] + offset_x, pos[1] + offset_y)
                    else:
                        text_rect.midleft = (pos[0] + offset_x, pos[1] + offset_y)
                    
                    # White background with transparency
                    bg_rect = text_rect.copy()
                    bg_rect.inflate_ip(6, 3)
                    pygame.draw.rect(self.map_surface, (255, 255, 255), bg_rect)
                    pygame.draw.rect(self.map_surface, (180, 180, 200), bg_rect, 1)
                    self.map_surface.blit(text, text_rect)
                    
                elif loc_type in ['major_station', 'business', 'major_junction']:
                    # Important locations - subtle text
                    font = self.tiny_font  # Smaller for less clutter
                    text_color = (80, 80, 80)
                    text = font.render(data['name'], True, text_color)
                    text_rect = text.get_rect()
                    
                    # Adjust position based on offset
                    if offset_x < 0:
                        text_rect.midright = (pos[0] + offset_x, pos[1] + offset_y)
                    elif offset_y != 0:
                        text_rect.center = (pos[0] + offset_x + 20, pos[1] + offset_y)
                    else:
                        text_rect.midleft = (pos[0] + offset_x, pos[1] + offset_y)
                    
                    # Light background
                    bg_rect = text_rect.copy()
                    bg_rect.inflate_ip(4, 2)
                    pygame.draw.rect(self.map_surface, (255, 255, 245), bg_rect)
                    pygame.draw.rect(self.map_surface, (200, 200, 200), bg_rect, 1)
                    self.map_surface.blit(text, text_rect)
                    
                else:
                    # Regular locations - standard text
                    font = self.tiny_font
                    text_color = (50, 50, 50)
                    text = font.render(data['name'], True, text_color)
                    text_rect = text.get_rect()
                    
                    # Adjust position based on offset
                    if offset_x < 0:
                        text_rect.midright = (pos[0] + offset_x, pos[1] + offset_y)
                    else:
                        text_rect.midleft = (pos[0] + offset_x, pos[1] + offset_y)
                    
                    # Subtle background
                    bg_rect = text_rect.copy()
                    bg_rect.inflate_ip(3, 1)
                    pygame.draw.rect(self.map_surface, (255, 255, 250), bg_rect)
                    self.map_surface.blit(text, text_rect)
    
    def get_road_at_position(self, pos):
        """Get the road at mouse position"""
        min_dist = float('inf')
        closest_edge = None
        
        for edge in self.graph.edges():
            if edge[0] not in self.locations or edge[1] not in self.locations:
                continue
                
            start_pos = self.locations[edge[0]]['pos']
            end_pos = self.locations[edge[1]]['pos']
            
            # Calculate distance from point to line
            dist = self.point_to_line_distance(pos, start_pos, end_pos)
            
            if dist < min_dist and dist < 15:  # Within 15 pixels
                min_dist = dist
                closest_edge = edge
        
        return closest_edge
    
    def point_to_line_distance(self, point, line_start, line_end):
        """Calculate distance from point to line segment"""
        x, y = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return math.sqrt((x - x1)**2 + (y - y1)**2)
        
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx*dx + dy*dy)))
        
        projection_x = x1 + t * dx
        projection_y = y1 + t * dy
        
        return math.sqrt((x - projection_x)**2 + (y - projection_y)**2)
    
    def toggle_road_condition(self, edge, condition):
        """Toggle road condition and update visualization"""
        if not edge:
            return
        
        # Check current condition
        if edge in self.road_conditions and self.road_conditions[edge] == condition:
            # Remove condition
            del self.road_conditions[edge]
            if edge in self.blocked_roads:
                self.blocked_roads.remove(edge)
            # Also remove reverse edge
            rev_edge = (edge[1], edge[0])
            if rev_edge in self.road_conditions:
                del self.road_conditions[rev_edge]
            if rev_edge in self.blocked_roads:
                self.blocked_roads.remove(rev_edge)
            
            print(f"✓ Road {self.locations[edge[0]]['name']} - {self.locations[edge[1]]['name']} is now CLEAR")
            self.stats['blocked_roads'] = max(0, self.stats['blocked_roads'] - 1)
        else:
            # Apply condition
            self.road_conditions[edge] = condition
            self.road_conditions[(edge[1], edge[0])] = condition  # Both directions
            
            if condition in [RoadCondition.BLOCKED, RoadCondition.VIP_MOVEMENT]:
                self.blocked_roads.add(edge)
                self.blocked_roads.add((edge[1], edge[0]))
            
            print(f"⚠ Road {self.locations[edge[0]]['name']} - {self.locations[edge[1]]['name']} is now {condition.value[0].upper()}")
            print(f"  Speed factor: {condition.value[2]*100:.0f}%")
            
            if condition == RoadCondition.BLOCKED:
                self.stats['blocked_roads'] += 1
        
        # Update map
        self.update_map()
        
        # Trigger rerouting for affected vehicles
        self.reroute_affected_vehicles(edge)
    
    def reroute_affected_vehicles(self, affected_edge):
        """Reroute vehicles that are affected by road condition change"""
        rerouted = 0
        
        for vehicle in self.vehicles:
            if vehicle.current_index < len(vehicle.path) - 1:
                # Check if vehicle's next segment is affected
                next_segment = (vehicle.path[vehicle.current_index], 
                              vehicle.path[vehicle.current_index + 1])
                rev_segment = (next_segment[1], next_segment[0])
                
                # Check if this segment is now blocked
                if (next_segment in self.blocked_roads or rev_segment in self.blocked_roads or
                    next_segment == affected_edge or rev_segment == affected_edge):
                    
                    # Find alternative route
                    new_path = self.find_alternative_route(vehicle)
                    if new_path and new_path != vehicle.path[vehicle.current_index:]:
                        vehicle.path = vehicle.path[:vehicle.current_index] + new_path
                        vehicle.avoiding_roads.add(affected_edge)
                        vehicle.avoiding_roads.add((affected_edge[1], affected_edge[0]))
                        rerouted += 1
                        
                        print(f"  → Vehicle {vehicle.id} ({vehicle.vehicle_type}) rerouted to avoid blocked road")
        
        if rerouted > 0:
            self.stats['reroutes'] += rerouted
            self.stats['vehicles_affected'] += rerouted
            print(f"  → {rerouted} vehicles rerouted successfully")
    
    def find_alternative_route(self, vehicle):
        """Find alternative route avoiding blocked roads"""
        if vehicle.current_index >= len(vehicle.path) - 1:
            return None
        
        start = vehicle.path[vehicle.current_index]
        destination = vehicle.original_destination or vehicle.path[-1]
        
        # Create temporary graph without blocked roads
        temp_graph = self.graph.copy()
        
        # Remove blocked roads from temp graph
        for blocked_edge in self.blocked_roads:
            if temp_graph.has_edge(blocked_edge[0], blocked_edge[1]):
                temp_graph.remove_edge(blocked_edge[0], blocked_edge[1])
        
        # Also adjust weights for roads with conditions
        for edge, condition in self.road_conditions.items():
            if temp_graph.has_edge(edge[0], edge[1]):
                if condition.value[2] == 0:  # Completely blocked
                    temp_graph.remove_edge(edge[0], edge[1])
                else:
                    # Increase weight based on speed factor
                    original_weight = temp_graph[edge[0]][edge[1]].get('distance', 100)
                    new_weight = original_weight / max(condition.value[2], 0.1)
                    temp_graph[edge[0]][edge[1]]['distance'] = new_weight
        
        try:
            # Find shortest path avoiding blocked roads
            new_path = nx.shortest_path(temp_graph, start, destination, weight='distance')
            return new_path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            # No alternative route available
            return None
    
    def add_initial_traffic(self):
        """Add initial vehicles to simulation"""
        # Fewer vehicles for cleaner look
        for _ in range(20):
            self.add_random_vehicle()
    
    def add_random_vehicle(self):
        """Add a random vehicle"""
        nodes = list(self.graph.nodes())
        start = random.choice(nodes)
        end = random.choice(nodes)
        
        while end == start:
            end = random.choice(nodes)
        
        # Find initial path
        path = self.find_path_avoiding_blocked(start, end)
        
        if path:
            # Vehicle types with elegant colors
            vehicle_types = [
                ('car', (100, 150, 200), 40),  # Soft blue
                ('bus', (200, 140, 100), 25),  # Soft orange
                ('auto', (220, 200, 100), 35),  # Soft yellow
                ('bike', (180, 140, 180), 50),  # Soft purple
                ('truck', (140, 120, 100), 20),  # Soft brown
                ('taxi', (200, 200, 120), 45),  # Soft yellow-green
            ]
            
            # Occasionally add emergency vehicles
            if random.random() < 0.05:
                vehicle_types.append(('ambulance', (255, 255, 255), 60))
            if random.random() < 0.03:
                vehicle_types.append(('police', (0, 0, 255), 55))
            
            vtype, color, speed = random.choice(vehicle_types)
            
            self.vehicle_counter += 1
            vehicle = Vehicle(
                id=self.vehicle_counter,
                path=path,
                color=color,
                speed=speed + random.uniform(-5, 5),
                vehicle_type=vtype,
                original_destination=end
            )
            
            self.vehicles.append(vehicle)
            self.stats['total_vehicles'] += 1
            
            start_name = self.locations[start]['name']
            end_name = self.locations[end]['name']
            print(f"New {vtype}: {start_name} → {end_name} ({len(path)-1} segments)")
    
    def find_path_avoiding_blocked(self, start, end):
        """Find path that avoids currently blocked roads"""
        # Create temp graph without blocked roads
        temp_graph = self.graph.copy()
        
        for blocked_edge in self.blocked_roads:
            if temp_graph.has_edge(blocked_edge[0], blocked_edge[1]):
                temp_graph.remove_edge(blocked_edge[0], blocked_edge[1])
        
        try:
            return nx.shortest_path(temp_graph, start, end, weight='distance')
        except:
            return None
    
    def update_vehicles(self, dt):
        """Update vehicle positions"""
        vehicles_to_remove = []
        traffic_count = {}
        
        # Update particles
        self.particles.update(dt)
        self.radar_angle = (self.radar_angle + 60 * dt) % 360
        self.time_of_day = (self.time_of_day + dt * 0.1) % 24.0 # Cycle roughly every 4 minutes real-time
        
        if self.is_raining:
            for i, (rx, ry, s) in enumerate(self.rain_drops):
                ry += s * 30 * dt
                rx -= s * 10 * dt
                if ry > self.height:
                    ry = 0
                    rx = random.randint(0, self.width + 500)
                self.rain_drops[i] = (rx, ry, s)
        
        # Add particles to accidents/protests
        for edge_tuple, condition in self.road_conditions.items():
            if condition in [RoadCondition.ACCIDENT, RoadCondition.PROTEST] and edge_tuple[0] in self.locations and edge_tuple[1] in self.locations:
                p1 = self.locations[edge_tuple[0]]['pos']
                p2 = self.locations[edge_tuple[1]]['pos']
                mid_x = (p1[0] + p2[0]) / 2 + random.uniform(-20, 20)
                mid_y = (p1[1] + p2[1]) / 2 + random.uniform(-20, 20)
                self.particles.add_fire_smoke(mid_x, mid_y)
        
        for vehicle in self.vehicles:
            if vehicle.current_index >= len(vehicle.path) - 1:
                vehicles_to_remove.append(vehicle)
                continue
            
            # Get current segment
            current = vehicle.path[vehicle.current_index]
            next_loc = vehicle.path[vehicle.current_index + 1]
            segment = (current, next_loc)
            
            # Count traffic
            traffic_count[segment] = traffic_count.get(segment, 0) + 1
            
            # Check if road ahead is blocked
            if segment in self.blocked_roads or (next_loc, current) in self.blocked_roads:
                # Try to reroute around blocked road
                vehicle.last_reroute_time += dt
                if vehicle.last_reroute_time > 2.0:  # Try every 2 seconds
                    new_path = self.find_alternative_route(vehicle)
                    if new_path:
                        vehicle.path = new_path
                        vehicle.current_index = 0
                        vehicle.position = 0.0
                        vehicle.last_reroute_time = 0
                        self.stats['reroutes'] += 1
                        print(f"Vehicle {vehicle.id} found detour")
                continue
            
            # Get road condition and calculate speed
            condition = self.road_conditions.get(segment, 
                       self.road_conditions.get((next_loc, current), RoadCondition.NORMAL))
            speed_factor = condition.value[2]
            
            # Move vehicle
            if speed_factor > 0:
                edge_data = self.graph.get_edge_data(current, next_loc)
                if edge_data:
                    distance = edge_data.get('distance', 100)
                    effective_speed = vehicle.speed * speed_factor * 2  # Scaling
                    vehicle.position += (effective_speed * dt) / distance
                    
                    if vehicle.position >= 1.0:
                        vehicle.current_index += 1
                        vehicle.position = 0.0
        
        # Update traffic density
        for edge in self.graph.edges():
            self.graph[edge[0]][edge[1]]['traffic'] = traffic_count.get(edge, 0)
        
        # Remove completed vehicles and add new ones
        for vehicle in vehicles_to_remove:
            self.vehicles.remove(vehicle)
            dest_name = self.locations.get(vehicle.original_destination, {}).get('name', 'destination')
            print(f"Vehicle {vehicle.id} reached {dest_name}")
            self.add_random_vehicle()
        
        # Update stats
        if self.vehicles:
            speeds = []
            for v in self.vehicles:
                if v.current_index < len(v.path) - 1:
                    segment = (v.path[v.current_index], v.path[v.current_index + 1])
                    condition = self.road_conditions.get(segment, RoadCondition.NORMAL)
                    speeds.append(v.speed * condition.value[2])
            self.stats['avg_speed'] = sum(speeds) / len(speeds) if speeds else 0
    
    def draw_location_labels(self):
        """Draw location labels with better visibility"""
        # Draw subtle zone labels only if not too cluttered
        if not self.show_major_only:
            zone_labels = {
                'South': (250, 900, (150, 150, 180)),
                'Central': (250, 600, (180, 150, 150)),
                'West': (200, 200, (150, 180, 150)),
                'East': (1400, 350, (180, 180, 150))
            }
            
            for zone, (x, y, color) in zone_labels.items():
                text = self.font.render(f"{zone} Mumbai", True, color)
                text.set_alpha(60)  # Very subtle
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)
    
    def draw(self):
        """Draw everything with high-fidelity digital twin graphics"""
        # Draw map
        self.screen.blit(self.map_surface, (0, 0))
        
        # Determine day/night styling
        is_night = (self.time_of_day > 18 or self.time_of_day < 6)
        
        # Calculate ambient darkness based on time of day (12 is noon)
        time_factor = abs(self.time_of_day - 12) / 12  # 0 at noon, 1 at midnight
        ambient_darkness = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ambient_darkness.fill((0, 5, 10, int(150 * time_factor)))
        self.screen.blit(ambient_darkness, (0, 0))
        
        # Draw background radar sweep (Command Center feel)
        center = (self.width // 2, self.height // 2)
        radar_radius = 600
        radar_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.circle(radar_surf, (0, 100, 50, 20), center, radar_radius, 1)
        pygame.draw.circle(radar_surf, (0, 100, 50, 10), center, radar_radius//2, 1)
        
        # Radar sweeping line
        end_x = center[0] + math.cos(math.radians(self.radar_angle)) * radar_radius
        end_y = center[1] + math.sin(math.radians(self.radar_angle)) * radar_radius
        pygame.draw.line(radar_surf, (0, 255, 100, 50), center, (end_x, end_y), 2)
        
        # Radar trailing wedge
        for i in range(20):
            trail_angle = math.radians(self.radar_angle - i)
            tx = center[0] + math.cos(trail_angle) * radar_radius
            ty = center[1] + math.sin(trail_angle) * radar_radius
            pygame.draw.line(radar_surf, (0, 200, 100, max(0, 40 - i*2)), center, (tx, ty), 2)
            
        self.screen.blit(radar_surf, (0, 0))

        # Draw vehicles with orientations and glow
        for vehicle in self.vehicles:
            if vehicle.current_index < len(vehicle.path) - 1:
                current = vehicle.path[vehicle.current_index]
                next_loc = vehicle.path[vehicle.current_index + 1]
                
                if current in self.locations and next_loc in self.locations:
                    current_pos = self.locations[current]['pos']
                    next_pos = self.locations[next_loc]['pos']
                    
                    # Interpolate position
                    x = current_pos[0] + (next_pos[0] - current_pos[0]) * vehicle.position
                    y = current_pos[1] + (next_pos[1] - current_pos[1]) * vehicle.position
                    
                    # Calculate angle
                    dx = next_pos[0] - current_pos[0]
                    dy = next_pos[1] - current_pos[1]
                    angle = math.degrees(math.atan2(-dy, dx))
                    
                    # Add vehicle exhaust particles
                    is_truck = vehicle.vehicle_type in ['truck', 'bus']
                    self.particles.add_exhaust(x, y, angle, vehicle.speed, is_truck)
                    
                    # Vehicle size based on type
                    sizes = {
                        'car': (12, 6), 'bus': (20, 8), 'auto': (8, 6), 'bike': (6, 3),
                        'truck': (18, 8), 'taxi': (12, 6), 'ambulance': (14, 7), 'police': (12, 6)
                    }
                    size_l, size_w = sizes.get(vehicle.vehicle_type, (10, 5))
                    
                    # Create surface for vehicle to allow rotation
                    veh_surface = pygame.Surface((size_l*4, size_w*4), pygame.SRCALPHA)
                    center_x, center_y = size_l*2, size_w*2
                    
                    # Draw base vehicle body
                    base_rect = pygame.Rect(center_x - size_l//2, center_y - size_w//2, size_l, size_w)
                    pygame.draw.rect(veh_surface, vehicle.color, base_rect, border_radius=2)
                    
                    # Headlights (glow)
                    headlight_color = (255, 255, 200, 150)
                    pygame.draw.circle(veh_surface, headlight_color, (center_x + size_l//2, center_y - size_w//4), 2)
                    pygame.draw.circle(veh_surface, headlight_color, (center_x + size_l//2, center_y + size_w//4), 2)
                    
                    # Long headlight cones at night
                    if is_night:
                        cone_len = 60
                        points = [
                            (center_x + size_l//2, center_y),
                            (center_x + size_l//2 + cone_len, center_y - cone_len//3),
                            (center_x + size_l//2 + cone_len, center_y + cone_len//3)
                        ]
                        pygame.draw.polygon(veh_surface, (255, 255, 200, 30), points)
                    
                    # Taillights
                    pygame.draw.circle(veh_surface, (255, 50, 50), (center_x - size_l//2, center_y - size_w//4), 1)
                    pygame.draw.circle(veh_surface, (255, 50, 50), (center_x - size_l//2, center_y + size_w//4), 1)
                    
                    # Rotate and blit
                    rotated_veh = pygame.transform.rotate(veh_surface, angle)
                    rot_rect = rotated_veh.get_rect(center=(int(x), int(y)))
                    
                    # Draw subtle glow under vehicle
                    glow_surf = pygame.Surface((size_l*3, size_w*3), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*vehicle.color[:3], 40), (size_l*1.5, size_w*1.5), size_l*0.8)
                    self.screen.blit(glow_surf, glow_surf.get_rect(center=(int(x), int(y))))
                    
                    self.screen.blit(rotated_veh, rot_rect)
                    
                    # Emergency vehicle siren
                    if vehicle.vehicle_type in ['ambulance', 'police']:
                        if int(self.simulation_time * 4) % 2:  # Fast blinking effect
                            siren_color = (255, 0, 0) if vehicle.vehicle_type == 'ambulance' else (0, 0, 255)
                            pygame.draw.circle(self.screen, siren_color, (int(x), int(y)), size_l, 2)
                            
        # Draw particles
        self.particles.draw(self.screen)
        
        # Draw rain
        if self.is_raining:
            for rx, ry, s in self.rain_drops:
                pygame.draw.line(self.screen, (150, 200, 255, 100), (rx, ry), (rx - s*2, ry + s*6), 1)
        
        # Draw location labels if enabled
        if self.show_road_names:
            self.draw_location_labels()
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw user interface"""
        # Elegant title bar with gradient effect
        title_bar = pygame.Surface((self.width, 50))
        title_bar.fill((50, 50, 55))
        self.screen.blit(title_bar, (0, 0))
        
        # Title with subtitle for elegance
        title = self.font.render("Mumbai Traffic Simulation", True, (255, 255, 255))
        subtitle = self.small_font.render("Click roads to block • Press M for minimal view • N to toggle names", 
                                         True, (200, 200, 200))
        self.screen.blit(title, (10, 8))
        self.screen.blit(subtitle, (10, 30))
        
        # Control panel - adjusted for wider screen
        panel_x = self.width - 380
        panel = pygame.Surface((370, 620))
        panel.set_alpha(240)
        panel.fill((255, 255, 255))
        self.screen.blit(panel, (panel_x, 60))
        
        y = 70
        
        # Section: Road Conditions
        section_title = self.font.render("ROAD CONDITIONS", True, (0, 0, 0))
        self.screen.blit(section_title, (panel_x + 10, y))
        y += 25
        
        conditions = [
            (RoadCondition.BLOCKED, "1: Block Road (No passage)"),
            (RoadCondition.ACCIDENT, "2: Accident (80% blocked)"),
            (RoadCondition.CONSTRUCTION, "3: Construction (70% blocked)"),
            (RoadCondition.FESTIVAL, "4: Festival (60% blocked)"),
            (RoadCondition.HEAVY_TRAFFIC, "5: Heavy Traffic (70% blocked)"),
            (RoadCondition.WATERLOGGED, "6: Waterlogged (80% blocked)"),
            (RoadCondition.VIP_MOVEMENT, "7: VIP Movement (Closed)"),
            (RoadCondition.PROTEST, "8: Protest (90% blocked)"),
            (RoadCondition.BREAKDOWN, "9: Breakdown (50% blocked)"),
        ]
        
        for condition, label in conditions:
            # Highlight selected condition
            if condition == self.selected_condition:
                pygame.draw.rect(self.screen, (200, 200, 255), 
                               (panel_x + 5, y - 2, 330, 18))
            
            # Color indicator
            pygame.draw.rect(self.screen, condition.value[1], 
                           (panel_x + 10, y, 20, 14))
            pygame.draw.rect(self.screen, (0, 0, 0), 
                           (panel_x + 10, y, 20, 14), 1)
            
            text = self.small_font.render(label, True, (50, 50, 50))
            self.screen.blit(text, (panel_x + 35, y))
            y += 18
        
        y += 15
        pygame.draw.line(self.screen, (200, 200, 200), 
                        (panel_x + 10, y), (panel_x + 330, y), 1)
        y += 15
        
        # Section: Statistics
        stats_title = self.font.render("TRAFFIC STATISTICS", True, (0, 0, 0))
        self.screen.blit(stats_title, (panel_x + 10, y))
        y += 25
        
        stats = [
            f"Active Vehicles: {len(self.vehicles)}",
            f"Total Vehicles: {self.stats['total_vehicles']}",
            f"Blocked Roads: {self.stats['blocked_roads']}",
            f"Vehicles Rerouted: {self.stats['reroutes']}",
            f"Average Speed: {self.stats['avg_speed']:.1f} km/h",
            f"Affected Vehicles: {self.stats['vehicles_affected']}",
        ]
        
        for stat in stats:
            text = self.small_font.render(stat, True, (50, 50, 50))
            self.screen.blit(text, (panel_x + 10, y))
            y += 20
        
        y += 10
        pygame.draw.line(self.screen, (200, 200, 200), 
                        (panel_x + 10, y), (panel_x + 330, y), 1)
        y += 10
        
        # Section: Controls
        controls_title = self.font.render("CONTROLS", True, (0, 0, 0))
        self.screen.blit(controls_title, (panel_x + 10, y))
        y += 25
        
        controls = [
            "Click Road: Apply/Remove condition",
            "1-9: Select condition type",
            "SPACE: Add vehicle",
            "P: Pause/Resume",
            "R: Clear all road blocks",
            "T: Toggle traffic density",
            "N: Toggle all location names",
            "M: Toggle major locations only",
            "W: Toggle weather (Rain)",
            "ESC: Exit",
        ]
        
        for control in controls:
            text = self.small_font.render(control, True, (50, 50, 50))
            self.screen.blit(text, (panel_x + 10, y))
            y += 18
        
        # Status bar
        status_bar = pygame.Surface((self.width, 30))
        status_bar.fill((50, 50, 50))
        self.screen.blit(status_bar, (0, self.height - 30))
        
        status = f"Status: {'PAUSED' if self.paused else 'RUNNING'} | "
        status += f"Locations: {len(self.locations)} | Roads: {len(self.roads)} | "
        status += f"Traffic View: {'ON' if self.show_traffic_density else 'OFF'}"
        
        status_text = self.small_font.render(status, True, (255, 255, 255))
        self.screen.blit(status_text, (10, self.height - 25))
    
    def handle_click(self, pos):
        """Handle mouse click on road"""
        edge = self.get_road_at_position(pos)
        if edge:
            self.toggle_road_condition(edge, self.selected_condition)
    
    def handle_key(self, key):
        """Handle keyboard input"""
        if pygame.K_1 <= key <= pygame.K_9:
            index = key - pygame.K_1
            conditions = list(RoadCondition)
            if index < len(conditions):
                self.selected_condition = conditions[index]
                print(f"Selected: {self.selected_condition.value[0]}")
        elif key == pygame.K_SPACE:
            self.add_random_vehicle()
        elif key == pygame.K_p:
            self.paused = not self.paused
        elif key == pygame.K_r:
            # Clear all road conditions
            self.road_conditions.clear()
            self.blocked_roads.clear()
            self.stats['blocked_roads'] = 0
            self.update_map()
            print("All roads cleared!")
        elif key == pygame.K_t:
            self.show_traffic_density = not self.show_traffic_density
            self.update_map()
        elif key == pygame.K_n:
            self.show_road_names = not self.show_road_names
            self.update_map()
        elif key == pygame.K_m:
            self.show_major_only = not self.show_major_only
            self.update_map()
            if self.show_major_only:
                print("Showing major locations only - cleaner view")
            else:
                print("Showing all locations")
        elif key == pygame.K_w:
            self.is_raining = not self.is_raining
            if self.is_raining:
                print("Weather: RAINING. Traffic slow down active.")
                # apply rain slow down globally
            else:
                print("Weather: CLEAR")
    
    def run(self):
        """Main simulation loop"""
        running = True
        print("\nSimulation started!")
        print("Click on roads to block/unblock them.")
        print("Vehicles will automatically avoid blocked roads.\n")
        
        while running:
            dt = self.clock.tick(30) / 1000.0
            self.simulation_time += dt
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
            
            if not self.paused:
                self.update_vehicles(dt)
            
            self.draw()
        
        pygame.quit()
        print("\nSimulation ended.")
        print(f"Final Statistics:")
        print(f"  Total vehicles: {self.stats['total_vehicles']}")
        print(f"  Total reroutes: {self.stats['reroutes']}")
        print(f"  Vehicles affected by blocks: {self.stats['vehicles_affected']}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ULTRA-REALISTIC MUMBAI TRAFFIC SIMULATION")
    print("="*70)
    print("\nFeatures:")
    print("• Accurate Mumbai geography with 75+ real locations")
    print("• Major highways: Western Express, Eastern Express, Sea Link")
    print("• Click any road to block it - see it turn RED")
    print("• Vehicles automatically avoid blocked roads")
    print("• Multiple conditions: Accident, Construction, Festival, etc.")
    print("• Real-time rerouting with smart pathfinding")
    print("\nVehicles will intelligently navigate around obstacles!")
    print("="*70)
    
    sim = RealisticMumbaiSimulation()
    sim.run()
