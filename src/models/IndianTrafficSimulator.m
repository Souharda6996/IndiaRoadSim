classdef IndianTrafficSimulator < handle
    % IndianTrafficSimulator - Main simulation engine for Indian traffic conditions
    % This class handles the core simulation logic including vehicle movement,
    % traffic rules, and dynamic obstacles typical of Indian roads
    
    properties
        roadNetwork         % Road network object
        vehicles            % Array of vehicle objects
        trafficControllers  % Traffic signal controllers
        obstacles           % Dynamic obstacles (potholes, construction, etc.)
        simulationTime      % Current simulation time
        timeStep            % Simulation time step
        isRunning           % Simulation state
        visualizer          % Visualization handler
        blockages           % Road blockages with reasons
        weatherCondition    % Current weather state
        eventManager        % Manages special events/festivals
    end
    
    properties (Constant)
        % Indian traffic specific constants
        DEFAULT_TIME_STEP = 0.1;  % 100ms time step
        MAX_VEHICLES = 500;
        
        % Vehicle types common in India
        VEHICLE_TYPES = struct(...
            'CAR', 1, ...
            'BUS', 2, ...
            'TRUCK', 3, ...
            'AUTO_RICKSHAW', 4, ...
            'MOTORCYCLE', 5, ...
            'BICYCLE', 6, ...
            'PEDESTRIAN', 7 ...
        );
        
        % Blockage types
        BLOCKAGE_TYPES = struct(...
            'WATER_LOGGING', 1, ...
            'CONSTRUCTION', 2, ...
            'FESTIVAL', 3, ...
            'ACCIDENT', 4, ...
            'VIP_MOVEMENT', 5, ...
            'PROTEST', 6, ...
            'MARKET_DAY', 7 ...
        );
    end
    
    methods
        function obj = IndianTrafficSimulator()
            % Constructor
            obj.simulationTime = 0;
            obj.timeStep = obj.DEFAULT_TIME_STEP;
            obj.isRunning = false;
            obj.vehicles = [];
            obj.obstacles = [];
            obj.blockages = containers.Map();
            obj.weatherCondition = 'clear';
            
            % Initialize road network
            obj.roadNetwork = RoadNetwork();
            
            % Initialize event manager
            obj.eventManager = EventManager();
            
            % Initialize visualizer
            obj.visualizer = TrafficVisualizer();
        end
        
        function initialize(obj, scenarioFile)
            % Initialize simulation with a scenario file
            if nargin > 1 && exist(scenarioFile, 'file')
                obj.loadScenario(scenarioFile);
            else
                obj.createDefaultScenario();
            end
            
            % Initialize traffic controllers
            obj.initializeTrafficControllers();
            
            % Set up initial vehicles
            obj.spawnInitialVehicles();
        end
        
        function createDefaultScenario(obj)
            % Create a default Indian urban junction scenario
            fprintf('Creating default Indian urban junction scenario...\n');
            
            % Create a typical Indian 4-way junction with irregular lanes
            obj.roadNetwork.createIndianJunction(...
                'center', [0, 0], ...
                'roadWidths', [12, 10, 11, 13], ... % Irregular widths
                'numLanes', [3, 2, 3, 3], ... % Variable lanes
                'hasDivider', [true, false, true, false], ...
                'surfaceQuality', [0.7, 0.5, 0.8, 0.6] ... % Road quality factor
            );
            
            % Add typical Indian road features
            obj.addIndianRoadFeatures();
        end
        
        function addIndianRoadFeatures(obj)
            % Add realistic Indian road features
            
            % Add potholes randomly
            numPotholes = randi([5, 15]);
            for i = 1:numPotholes
                pothole = struct(...
                    'type', 'pothole', ...
                    'position', obj.roadNetwork.getRandomRoadPosition(), ...
                    'severity', rand(), ... % 0 to 1
                    'radius', 0.5 + rand() * 1.5 ...
                );
                obj.obstacles = [obj.obstacles, pothole];
            end
            
            % Add street vendors (common in India)
            numVendors = randi([3, 8]);
            for i = 1:numVendors
                vendor = struct(...
                    'type', 'street_vendor', ...
                    'position', obj.roadNetwork.getRoadsidePosition(), ...
                    'size', [2, 3], ...
                    'mobilityType', 'stationary' ...
                );
                obj.obstacles = [obj.obstacles, vendor];
            end
            
            % Add parked vehicles on roadside
            numParked = randi([5, 10]);
            for i = 1:numParked
                parked = struct(...
                    'type', 'parked_vehicle', ...
                    'position', obj.roadNetwork.getRoadsidePosition(), ...
                    'vehicleType', obj.getRandomVehicleType(), ...
                    'angle', rand() * 30 - 15 ... % Slightly angled parking
                );
                obj.obstacles = [obj.obstacles, parked];
            end
        end
        
        function initializeTrafficControllers(obj)
            % Initialize traffic signal controllers
            junctions = obj.roadNetwork.getJunctions();
            obj.trafficControllers = [];
            
            for i = 1:length(junctions)
                controller = IndianTrafficController(junctions(i));
                % Set irregular timing patterns common in India
                controller.setTimingPattern('irregular');
                obj.trafficControllers = [obj.trafficControllers, controller];
            end
        end
        
        function spawnInitialVehicles(obj)
            % Spawn initial set of vehicles with Indian traffic mix
            trafficMix = struct(...
                'motorcycle', 0.35, ...
                'auto_rickshaw', 0.20, ...
                'car', 0.25, ...
                'bus', 0.10, ...
                'truck', 0.05, ...
                'bicycle', 0.05 ...
            );
            
            numInitialVehicles = 50;
            
            for i = 1:numInitialVehicles
                vehicleType = obj.selectVehicleByMix(trafficMix);
                obj.spawnVehicle(vehicleType);
            end
        end
        
        function vehicle = spawnVehicle(obj, vehicleType)
            % Spawn a new vehicle
            entryPoints = obj.roadNetwork.getEntryPoints();
            entryPoint = entryPoints(randi(length(entryPoints)));
            
            vehicle = IndianVehicle(vehicleType);
            vehicle.setPosition(entryPoint.position);
            vehicle.setHeading(entryPoint.heading);
            vehicle.setRoute(obj.roadNetwork.generateRandomRoute(entryPoint));
            
            % Set Indian driving behavior parameters
            vehicle.setBehaviorParams(obj.getIndianDrivingParams(vehicleType));
            
            obj.vehicles = [obj.vehicles, vehicle];
        end
        
        function params = getIndianDrivingParams(obj, vehicleType)
            % Get typical Indian driving behavior parameters
            switch vehicleType
                case 'motorcycle'
                    params = struct(...
                        'aggressiveness', 0.7 + rand() * 0.3, ...
                        'laneDisciple', 0.2 + rand() * 0.3, ... % Low lane discipline
                        'gapAcceptance', 0.5, ... % Small gap acceptance
                        'maxSpeed', 60, ...
                        'acceleration', 3.5 ...
                    );
                case 'auto_rickshaw'
                    params = struct(...
                        'aggressiveness', 0.6 + rand() * 0.3, ...
                        'laneDisciple', 0.3 + rand() * 0.2, ...
                        'gapAcceptance', 0.6, ...
                        'maxSpeed', 40, ...
                        'acceleration', 2.0 ...
                    );
                case 'car'
                    params = struct(...
                        'aggressiveness', 0.4 + rand() * 0.4, ...
                        'laneDisciple', 0.5 + rand() * 0.3, ...
                        'gapAcceptance', 0.8, ...
                        'maxSpeed', 80, ...
                        'acceleration', 2.5 ...
                    );
                case 'bus'
                    params = struct(...
                        'aggressiveness', 0.3 + rand() * 0.2, ...
                        'laneDisciple', 0.4 + rand() * 0.2, ...
                        'gapAcceptance', 1.2, ...
                        'maxSpeed', 50, ...
                        'acceleration', 1.5 ...
                    );
                otherwise
                    params = struct(...
                        'aggressiveness', 0.5, ...
                        'laneDisciple', 0.4, ...
                        'gapAcceptance', 0.8, ...
                        'maxSpeed', 60, ...
                        'acceleration', 2.0 ...
                    );
            end
        end
        
        function run(obj, duration)
            % Run simulation for specified duration
            obj.isRunning = true;
            endTime = obj.simulationTime + duration;
            
            while obj.simulationTime < endTime && obj.isRunning
                obj.step();
                obj.visualizer.update(obj);
                pause(obj.timeStep);
            end
            
            obj.isRunning = false;
        end
        
        function step(obj)
            % Single simulation step
            
            % Update traffic signals
            for i = 1:length(obj.trafficControllers)
                obj.trafficControllers(i).update(obj.simulationTime);
            end
            
            % Update vehicle positions and behaviors
            for i = 1:length(obj.vehicles)
                if obj.vehicles(i).isActive
                    obj.updateVehicle(obj.vehicles(i));
                end
            end
            
            % Handle vehicle interactions
            obj.handleVehicleInteractions();
            
            % Spawn new vehicles based on traffic flow
            obj.manageTrafficFlow();
            
            % Update obstacles and blockages
            obj.updateObstacles();
            
            % Increment simulation time
            obj.simulationTime = obj.simulationTime + obj.timeStep;
        end
        
        function updateVehicle(obj, vehicle)
            % Update individual vehicle behavior
            
            % Get surrounding vehicles
            nearbyVehicles = obj.getNearbyVehicles(vehicle, 50);
            
            % Check for obstacles
            nearbyObstacles = obj.getNearbyObstacles(vehicle, 30);
            
            % Check for road blockages
            blockages = obj.checkBlockages(vehicle.getPosition());
            
            % Get traffic signal state
            signalState = obj.getTrafficSignalState(vehicle);
            
            % Update vehicle behavior based on Indian driving patterns
            vehicle.updateBehavior(...
                nearbyVehicles, ...
                nearbyObstacles, ...
                blockages, ...
                signalState, ...
                obj.roadNetwork ...
            );
            
            % Update position
            vehicle.updatePosition(obj.timeStep);
        end
        
        function handleVehicleInteractions(obj)
            % Handle complex vehicle interactions typical in Indian traffic
            
            for i = 1:length(obj.vehicles)
                if ~obj.vehicles(i).isActive
                    continue;
                end
                
                for j = i+1:length(obj.vehicles)
                    if ~obj.vehicles(j).isActive
                        continue;
                    end
                    
                    dist = norm(obj.vehicles(i).position - obj.vehicles(j).position);
                    
                    if dist < 5 % Within interaction range
                        % Handle honking behavior (common in India)
                        if rand() < 0.1 % 10% chance per timestep
                            obj.vehicles(i).honk();
                        end
                        
                        % Handle gap squeezing behavior
                        if obj.vehicles(i).vehicleType == obj.VEHICLE_TYPES.MOTORCYCLE
                            obj.vehicles(i).attemptGapSqueeze(obj.vehicles(j));
                        end
                    end
                end
            end
        end
        
        function addBlockage(obj, roadSegmentID, blockageType, duration)
            % Add a road blockage
            blockage = struct(...
                'type', blockageType, ...
                'startTime', obj.simulationTime, ...
                'duration', duration, ...
                'severity', rand(), ... % 0 to 1
                'affectedLanes', obj.determineAffectedLanes(blockageType) ...
            );
            
            obj.blockages(roadSegmentID) = blockage;
            
            % Update visualization
            obj.visualizer.highlightBlockage(roadSegmentID, blockage);
            
            fprintf('Road blockage added: %s on segment %s\n', ...
                blockageType, roadSegmentID);
        end
        
        function removeBlockage(obj, roadSegmentID)
            % Remove a road blockage
            if obj.blockages.isKey(roadSegmentID)
                remove(obj.blockages, roadSegmentID);
                obj.visualizer.clearBlockage(roadSegmentID);
                fprintf('Road blockage removed from segment %s\n', roadSegmentID);
            end
        end
        
        function lanes = determineAffectedLanes(obj, blockageType)
            % Determine which lanes are affected by blockage type
            switch blockageType
                case obj.BLOCKAGE_TYPES.WATER_LOGGING
                    lanes = 'all'; % Usually affects all lanes
                case obj.BLOCKAGE_TYPES.CONSTRUCTION
                    lanes = 'partial'; % Usually 1-2 lanes
                case obj.BLOCKAGE_TYPES.FESTIVAL
                    lanes = 'sides'; % Usually affects roadside lanes
                case obj.BLOCKAGE_TYPES.ACCIDENT
                    lanes = 'random'; % Random lanes blocked
                otherwise
                    lanes = 'partial';
            end
        end
        
        function manageTrafficFlow(obj)
            % Manage traffic flow and spawn new vehicles
            
            % Check if we need more vehicles
            if length(obj.vehicles) < obj.MAX_VEHICLES
                % Use Poisson process for vehicle arrivals
                lambda = 0.5; % Average vehicles per timestep
                if rand() < lambda * obj.timeStep
                    vehicleType = obj.selectVehicleByTimeOfDay();
                    obj.spawnVehicle(vehicleType);
                end
            end
            
            % Remove vehicles that have completed their routes
            completedVehicles = [];
            for i = 1:length(obj.vehicles)
                if obj.vehicles(i).hasCompletedRoute()
                    completedVehicles = [completedVehicles, i];
                end
            end
            obj.vehicles(completedVehicles) = [];
        end
        
        function vehicleType = selectVehicleByTimeOfDay(obj)
            % Select vehicle type based on time of day patterns
            hour = mod(obj.simulationTime / 3600, 24);
            
            if hour >= 7 && hour <= 10 % Morning rush
                weights = [0.3, 0.25, 0.25, 0.1, 0.05, 0.05]; % More bikes and cars
            elseif hour >= 17 && hour <= 20 % Evening rush
                weights = [0.35, 0.2, 0.25, 0.15, 0.03, 0.02];
            else % Normal hours
                weights = [0.25, 0.2, 0.2, 0.15, 0.1, 0.1];
            end
            
            types = {'motorcycle', 'auto_rickshaw', 'car', 'bus', 'truck', 'bicycle'};
            vehicleType = types{randsample(1:6, 1, true, weights)};
        end
        
        function vehicleType = selectVehicleByMix(obj, trafficMix)
            % Select vehicle type based on traffic mix
            types = fieldnames(trafficMix);
            weights = cellfun(@(x) trafficMix.(x), types);
            idx = randsample(1:length(types), 1, true, weights);
            vehicleType = types{idx};
        end
        
        function updateObstacles(obj)
            % Update dynamic obstacles
            for i = 1:length(obj.obstacles)
                if strcmp(obj.obstacles(i).type, 'street_vendor')
                    % Street vendors might move occasionally
                    if rand() < 0.001 % Very low probability
                        obj.obstacles(i).position = obj.roadNetwork.getRoadsidePosition();
                    end
                end
            end
        end
        
        function stats = getSimulationStats(obj)
            % Get current simulation statistics
            stats = struct();
            stats.totalVehicles = length(obj.vehicles);
            stats.averageSpeed = mean([obj.vehicles.speed]);
            stats.congestionLevel = obj.calculateCongestion();
            stats.activeBlockages = obj.blockages.Count;
            stats.simulationTime = obj.simulationTime;
            
            % Vehicle type distribution
            for i = 1:length(obj.vehicles)
                type = obj.vehicles(i).vehicleType;
                if isfield(stats, type)
                    stats.(type) = stats.(type) + 1;
                else
                    stats.(type) = 1;
                end
            end
        end
        
        function congestion = calculateCongestion(obj)
            % Calculate congestion level (0 to 1)
            if isempty(obj.vehicles)
                congestion = 0;
                return;
            end
            
            % Based on average speed vs free flow speed
            avgSpeed = mean([obj.vehicles.speed]);
            freeFlowSpeed = 60; % km/h
            congestion = 1 - (avgSpeed / freeFlowSpeed);
            congestion = max(0, min(1, congestion));
        end
        
        function vehicles = getNearbyVehicles(obj, vehicle, radius)
            % Get vehicles within specified radius
            vehicles = [];
            pos = vehicle.position;
            
            for i = 1:length(obj.vehicles)
                if obj.vehicles(i) ~= vehicle
                    dist = norm(obj.vehicles(i).position - pos);
                    if dist <= radius
                        vehicles = [vehicles, obj.vehicles(i)];
                    end
                end
            end
        end
        
        function obstacles = getNearbyObstacles(obj, vehicle, radius)
            % Get obstacles within specified radius
            obstacles = [];
            pos = vehicle.position;
            
            for i = 1:length(obj.obstacles)
                dist = norm(obj.obstacles(i).position - pos);
                if dist <= radius
                    obstacles = [obstacles, obj.obstacles(i)];
                end
            end
        end
        
        function blockages = checkBlockages(obj, position)
            % Check for blockages at given position
            blockages = [];
            roadSegment = obj.roadNetwork.getRoadSegmentAt(position);
            
            if ~isempty(roadSegment) && obj.blockages.isKey(roadSegment.id)
                blockages = obj.blockages(roadSegment.id);
            end
        end
        
        function state = getTrafficSignalState(obj, vehicle)
            % Get traffic signal state for vehicle
            state = 'green'; % Default
            
            junction = obj.roadNetwork.getNearestJunction(vehicle.position);
            if ~isempty(junction) && norm(junction.position - vehicle.position) < 30
                for i = 1:length(obj.trafficControllers)
                    if obj.trafficControllers(i).junction == junction
                        state = obj.trafficControllers(i).getSignalState(vehicle.heading);
                        break;
                    end
                end
            end
        end
        
        function vehicleType = getRandomVehicleType(obj)
            % Get random vehicle type
            types = fieldnames(obj.VEHICLE_TYPES);
            vehicleType = types{randi(length(types)-1)}; % Exclude pedestrian
        end
        
        function loadScenario(obj, scenarioFile)
            % Load scenario from file
            fprintf('Loading scenario from %s...\n', scenarioFile);
            % Implementation for loading scenario
        end
        
        function stop(obj)
            % Stop simulation
            obj.isRunning = false;
        end
    end
end
