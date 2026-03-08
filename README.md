<<<<<<< HEAD
# Indian Traffic Simulation System
## SIH Problem Statement ID: 25100
### Accelerating High-Fidelity Road Network Modeling for Indian Traffic Simulations

## Overview
This MATLAB-based simulation system addresses the unique challenges of modeling Indian urban traffic conditions. Unlike conventional traffic simulators designed for developed countries, this system accounts for the complex realities of Indian roads including:

- **Irregular road conditions**: Potholes, varying road quality, incomplete lane markings
- **Mixed traffic**: Cars, buses, trucks, auto-rickshaws, motorcycles, bicycles
- **Indian driving behaviors**: Lane filtering, gap squeezing, variable lane discipline
- **Dynamic blockages**: Water logging, construction, festivals, VIP movements
- **Real-time visualization**: Actual road layouts instead of grid lines
- **Interactive controls**: Click-to-block roads with various Indian-specific criteria

## Features

### 1. Realistic Indian Road Network
- Irregular lane widths and markings
- Variable road surface quality
- Footpath encroachment modeling
- Street vendors and parked vehicles
- Potholes with severity levels

### 2. Indian Vehicle Mix
- **Cars**: Standard passenger vehicles
- **Buses**: Public transport with frequent stops
- **Trucks**: Heavy vehicles with slower speeds
- **Auto-rickshaws**: Three-wheelers with aggressive lane changing
- **Motorcycles**: Two-wheelers with lane filtering behavior
- **Bicycles**: Non-motorized vehicles

### 3. Interactive Road Blocking
Click on any road segment to add blockages based on Indian criteria:
- **Water Logging**: Monsoon flooding
- **Construction**: Road repairs and infrastructure work
- **Festival/Procession**: Religious and cultural events
- **Accident**: Vehicle collisions
- **VIP Movement**: Government official routes
- **Protest/Rally**: Public demonstrations
- **Market Day**: Weekly market congestion

### 4. Realistic Traffic Behaviors
- Variable lane discipline
- Honking patterns
- Gap acceptance behaviors
- Signal compliance variations
- Peak hour traffic patterns

## Installation

### Prerequisites
- MATLAB R2020b or later
- Required: Base MATLAB installation
- Optional (for enhanced features):
  - Automated Driving Toolbox
  - Mapping Toolbox
  - Image Processing Toolbox

### Setup Instructions
1. Ensure the project is located in `E:\indian_traffic_simulation`
2. Open MATLAB
3. Navigate to the project directory
4. Run `launchSimulation.m`

## Usage

### Starting the Simulation
```matlab
% Navigate to project directory
cd E:\indian_traffic_simulation

% Launch the simulation
launchSimulation
```

### GUI Controls

#### Simulation Control Panel (Left)
- **Scenario Selection**: Choose from predefined scenarios or load custom OSM data
- **Start/Pause/Stop**: Control simulation execution
- **Speed Slider**: Adjust simulation speed (0.1x to 5x)

#### Road Blocking Controls
1. Select blockage type from dropdown
2. Click "Click Road to Block" button
3. Click on desired road segment in visualization
4. Use "Clear All Blockages" to remove all blocks

#### Traffic Statistics Panel (Right)
- Real-time vehicle count
- Vehicle type distribution
- Average speed
- Congestion level indicator
- Active blockages count

### Keyboard Shortcuts
- `Space`: Pause/Resume simulation
- `Esc`: Stop simulation
- `+/-`: Zoom in/out
- Arrow keys: Pan view

## Project Structure
```
E:\indian_traffic_simulation\
├── src\
│   ├── models\
│   │   ├── IndianTrafficSimulator.m    # Main simulation engine
│   │   ├── IndianVehicle.m            # Vehicle behavior model
│   │   ├── RoadNetwork.m              # Road network representation
│   │   ├── TrafficVisualizer.m        # Visualization handler
│   │   └── EventManager.m             # Special events manager
│   ├── controllers\
│   │   └── IndianTrafficController.m  # Traffic signal controller
│   ├── gui\
│   │   └── IndianTrafficSimulationGUI.m # Interactive GUI
│   └── utils\
│       └── (Utility functions)
├── data\
│   └── (Scenario data files)
├── scenarios\
│   └── (Predefined traffic scenarios)
├── assets\
│   ├── vehicles\
│   └── roads\
├── launchSimulation.m                  # Main launcher script
└── README.md                           # This file
```

## Scenarios

### Default Junction
Basic 4-way intersection with typical Indian traffic patterns

### Mumbai Traffic
High-density traffic with significant two-wheeler presence

### Delhi NCR
Wide roads with mixed traffic and VIP movement patterns

### Bangalore IT Corridor
Tech hub traffic with peak hour congestion patterns

### Custom OSM
Load your own OpenStreetMap data for any Indian city

## Customization

### Adding New Vehicle Types
Edit `IndianVehicle.m` to add new vehicle types with specific behaviors:
```matlab
case 'new_vehicle_type'
    obj.maxSpeed = 50;
    obj.behaviorParams = struct(...
        'aggressiveness', 0.5, ...
        'laneDisciple', 0.4, ...
        'gapAcceptance', 0.7
    );
```

### Creating Custom Blockage Types
Modify `IndianTrafficSimulator.m` to add new blockage types:
```matlab
BLOCKAGE_TYPES = struct(...
    'CUSTOM_TYPE', 8, ...
);
```

### Modifying Traffic Patterns
Adjust traffic mix in `IndianTrafficSimulator.m`:
```matlab
trafficMix = struct(...
    'motorcycle', 0.35, ...
    'auto_rickshaw', 0.20, ...
    'car', 0.25, ...
    % Modify percentages as needed
);
```

## Performance Optimization

For large-scale simulations:
1. Reduce visualization update frequency
2. Limit maximum vehicle count
3. Simplify vehicle interaction calculations
4. Use compiled MATLAB functions for critical paths

## Known Limitations

1. OSM import functionality requires additional implementation
2. Traffic signal optimization not yet implemented
3. Pedestrian modeling simplified
4. Weather effects on traffic not fully modeled

## Future Enhancements

- [ ] Integration with real-time traffic data
- [ ] Machine learning for traffic prediction
- [ ] Advanced pedestrian modeling
- [ ] Weather impact simulation
- [ ] Emergency vehicle routing
- [ ] Public transport scheduling
- [ ] Pollution and noise modeling
- [ ] Mobile app for remote monitoring

## Contributing

This project was developed for the Smart India Hackathon (SIH) to address Problem Statement ID 25100. Contributions to enhance the simulation's accuracy and features are welcome.

## Troubleshooting

### Common Issues

1. **GUI doesn't launch**
   - Verify MATLAB version compatibility
   - Check all required files are present
   - Ensure paths are correctly set

2. **Simulation runs slowly**
   - Reduce number of vehicles
   - Lower visualization quality
   - Increase time step

3. **Vehicles behaving incorrectly**
   - Check behavior parameters
   - Verify road network connectivity
   - Review traffic controller settings

## Contact & Support

For issues, questions, or contributions related to this SIH project, please refer to the project documentation or contact the development team.

## License

This project was developed as part of the Smart India Hackathon for MathWorks India Pvt. Ltd.

---

**Note**: This simulation is designed specifically for Indian traffic conditions and may not accurately represent traffic patterns in other countries.
=======
# IndiaRoadSim
Accelerating High-Fidelity Road Network Modeling for Indian Traffic Simulations.
>>>>>>> 806d4633452890808296f16722cff92296418d6d
