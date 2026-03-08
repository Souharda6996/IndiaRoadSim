classdef SimpleIndianTrafficSimulator < handle
    % Simplified Indian Traffic Simulator for demonstration
    
    properties
        vehicles            % Array of vehicles
        roads               % Simple road structure
        simulationTime      % Current time
        timeStep           % Time step
        isRunning          % Running state
        blockages          % Road blockages
        mainAxes           % Axes for visualization
    end
    
    properties (Constant)
        DEFAULT_TIME_STEP = 0.1;
        MAX_VEHICLES = 50;
    end
    
    methods
        function obj = SimpleIndianTrafficSimulator()
            % Constructor
            obj.vehicles = [];
            obj.roads = [];
            obj.simulationTime = 0;
            obj.timeStep = obj.DEFAULT_TIME_STEP;
            obj.isRunning = false;
            obj.blockages = containers.Map();
            
            % Create simple road network
            obj.createSimpleRoads();
        end
        
        function createSimpleRoads(obj)
            % Create a simple crossroad
            obj.roads = struct(...
                'horizontal', struct('start', [-200, 0], 'end', [200, 0], 'width', 20), ...
                'vertical', struct('start', [0, -200], 'end', [0, 200], 'width', 20) ...
            );
        end
        
        function initialize(obj)
            % Initialize simulation
            obj.spawnInitialVehicles();
        end
        
        function spawnInitialVehicles(obj)
            % Spawn initial vehicles
            numVehicles = 20;
            
            for i = 1:numVehicles
                vehicle = struct();
                vehicle.id = i;
                vehicle.type = obj.getRandomVehicleType();
                vehicle.position = obj.getRandomStartPosition();
                vehicle.velocity = obj.getInitialVelocity(vehicle.type);
                vehicle.heading = obj.getInitialHeading(vehicle.position);
                vehicle.color = obj.getVehicleColor(vehicle.type);
                vehicle.size = obj.getVehicleSize(vehicle.type);
                vehicle.isActive = true;
                
                obj.vehicles = [obj.vehicles, vehicle];
            end
        end
        
        function type = getRandomVehicleType(obj)
            % Get random vehicle type with Indian traffic mix
            types = {'car', 'bus', 'truck', 'auto_rickshaw', 'motorcycle', 'bicycle'};
            weights = [0.25, 0.1, 0.05, 0.2, 0.35, 0.05];
            idx = randsample(1:6, 1, true, weights);
            type = types{idx};
        end
        
        function pos = getRandomStartPosition(obj)
            % Get random starting position on roads
            if rand() < 0.5
                % Horizontal road
                x = -200 + rand() * 400;
                y = -10 + rand() * 20;
            else
                % Vertical road
                x = -10 + rand() * 20;
                y = -200 + rand() * 400;
            end
            pos = [x, y];
        end
        
        function vel = getInitialVelocity(obj, vehicleType)
            % Get initial velocity based on vehicle type
            switch vehicleType
                case 'motorcycle'
                    vel = 8 + rand() * 4;
                case 'auto_rickshaw'
                    vel = 5 + rand() * 3;
                case 'car'
                    vel = 6 + rand() * 4;
                case 'bus'
                    vel = 4 + rand() * 2;
                case 'truck'
                    vel = 3 + rand() * 2;
                case 'bicycle'
                    vel = 2 + rand() * 1;
                otherwise
                    vel = 5;
            end
        end
        
        function heading = getInitialHeading(obj, position)
            % Get initial heading based on position
            if abs(position(2)) < 15
                % On horizontal road
                heading = sign(rand() - 0.5) * 180;
            else
                % On vertical road
                heading = 90 * sign(rand() - 0.5);
            end
        end
        
        function color = getVehicleColor(obj, vehicleType)
            % Get vehicle color
            switch vehicleType
                case 'car'
                    color = [0, 0, 1]; % Blue
                case 'bus'
                    color = [1, 0.5, 0]; % Orange
                case 'truck'
                    color = [0.5, 0.5, 0.5]; % Gray
                case 'auto_rickshaw'
                    color = [1, 1, 0]; % Yellow
                case 'motorcycle'
                    color = [1, 0, 0]; % Red
                case 'bicycle'
                    color = [0, 1, 0]; % Green
                otherwise
                    color = [0.5, 0.5, 0.5];
            end
        end
        
        function size = getVehicleSize(obj, vehicleType)
            % Get vehicle size [length, width]
            switch vehicleType
                case 'car'
                    size = [4.5, 1.8];
                case 'bus'
                    size = [12, 2.5];
                case 'truck'
                    size = [8, 2.5];
                case 'auto_rickshaw'
                    size = [3.2, 1.4];
                case 'motorcycle'
                    size = [2, 0.8];
                case 'bicycle'
                    size = [1.8, 0.6];
                otherwise
                    size = [4, 2];
            end
        end
        
        function step(obj)
            % Single simulation step
            
            % Update each vehicle
            for i = 1:length(obj.vehicles)
                if obj.vehicles(i).isActive
                    obj.updateVehicle(i);
                end
            end
            
            % Handle interactions
            obj.handleInteractions();
            
            % Spawn new vehicles occasionally
            if rand() < 0.05 && length(obj.vehicles) < obj.MAX_VEHICLES
                obj.spawnNewVehicle();
            end
            
            % Remove vehicles that left the area
            obj.removeOutOfBoundsVehicles();
            
            % Increment time
            obj.simulationTime = obj.simulationTime + obj.timeStep;
        end
        
        function updateVehicle(obj, idx)
            % Update vehicle position and behavior
            vehicle = obj.vehicles(idx);
            
            % Simple physics update
            dx = vehicle.velocity * cosd(vehicle.heading) * obj.timeStep;
            dy = vehicle.velocity * sind(vehicle.heading) * obj.timeStep;
            
            obj.vehicles(idx).position = vehicle.position + [dx, dy];
            
            % Add some randomness for Indian traffic behavior
            if strcmp(vehicle.type, 'motorcycle') || strcmp(vehicle.type, 'auto_rickshaw')
                % More erratic movement
                obj.vehicles(idx).heading = vehicle.heading + (rand() - 0.5) * 5;
            end
            
            % Check for blockages
            if obj.isPositionBlocked(vehicle.position)
                obj.vehicles(idx).velocity = max(0, vehicle.velocity - 2);
            end
        end
        
        function handleInteractions(obj)
            % Handle vehicle interactions
            for i = 1:length(obj.vehicles)
                if ~obj.vehicles(i).isActive
                    continue;
                end
                
                for j = i+1:length(obj.vehicles)
                    if ~obj.vehicles(j).isActive
                        continue;
                    end
                    
                    dist = norm(obj.vehicles(i).position - obj.vehicles(j).position);
                    
                    % Simple collision avoidance
                    if dist < 5
                        % Slow down
                        obj.vehicles(i).velocity = max(0, obj.vehicles(i).velocity - 1);
                        obj.vehicles(j).velocity = max(0, obj.vehicles(j).velocity - 1);
                        
                        % Motorcycles try to squeeze through
                        if strcmp(obj.vehicles(i).type, 'motorcycle')
                            obj.vehicles(i).heading = obj.vehicles(i).heading + 10;
                        end
                    end
                end
            end
        end
        
        function spawnNewVehicle(obj)
            % Spawn a new vehicle
            vehicle = struct();
            vehicle.id = length(obj.vehicles) + 1;
            vehicle.type = obj.getRandomVehicleType();
            vehicle.position = obj.getRandomStartPosition();
            vehicle.velocity = obj.getInitialVelocity(vehicle.type);
            vehicle.heading = obj.getInitialHeading(vehicle.position);
            vehicle.color = obj.getVehicleColor(vehicle.type);
            vehicle.size = obj.getVehicleSize(vehicle.type);
            vehicle.isActive = true;
            
            obj.vehicles = [obj.vehicles, vehicle];
        end
        
        function removeOutOfBoundsVehicles(obj)
            % Remove vehicles that left the simulation area
            for i = 1:length(obj.vehicles)
                pos = obj.vehicles(i).position;
                if abs(pos(1)) > 250 || abs(pos(2)) > 250
                    obj.vehicles(i).isActive = false;
                end
            end
            
            % Remove inactive vehicles
            obj.vehicles = obj.vehicles([obj.vehicles.isActive]);
        end
        
        function blocked = isPositionBlocked(obj, position)
            % Check if position is blocked
            blocked = false;
            
            % Check blockages
            keys = obj.blockages.keys;
            for i = 1:length(keys)
                blockage = obj.blockages(keys{i});
                if norm(position - blockage.position) < blockage.radius
                    blocked = true;
                    return;
                end
            end
        end
        
        function addBlockage(obj, position, type, radius)
            % Add a blockage
            id = sprintf('blockage_%d', obj.blockages.Count + 1);
            blockage = struct(...
                'position', position, ...
                'type', type, ...
                'radius', radius, ...
                'time', obj.simulationTime ...
            );
            obj.blockages(id) = blockage;
        end
        
        function removeBlockage(obj, id)
            % Remove a blockage
            if obj.blockages.isKey(id)
                remove(obj.blockages, id);
            end
        end
        
        function clearAllBlockages(obj)
            % Clear all blockages
            obj.blockages = containers.Map();
        end
        
        function stats = getStats(obj)
            % Get simulation statistics
            stats = struct();
            stats.totalVehicles = length(obj.vehicles);
            stats.simulationTime = obj.simulationTime;
            
            if ~isempty(obj.vehicles)
                velocities = [obj.vehicles.velocity];
                stats.averageSpeed = mean(velocities) * 3.6; % Convert to km/h
                stats.congestionLevel = 1 - (stats.averageSpeed / 60);
            else
                stats.averageSpeed = 0;
                stats.congestionLevel = 0;
            end
            
            stats.activeBlockages = obj.blockages.Count;
        end
        
        function draw(obj, ax)
            % Draw the simulation
            cla(ax);
            hold(ax, 'on');
            
            % Draw roads
            rectangle(ax, 'Position', [-200, -10, 400, 20], ...
                'FaceColor', [0.3, 0.3, 0.3], 'EdgeColor', 'none');
            rectangle(ax, 'Position', [-10, -200, 20, 400], ...
                'FaceColor', [0.3, 0.3, 0.3], 'EdgeColor', 'none');
            
            % Draw center junction
            rectangle(ax, 'Position', [-15, -15, 30, 30], ...
                'Curvature', [0.5, 0.5], 'FaceColor', [0.4, 0.4, 0.4], ...
                'EdgeColor', 'yellow', 'LineWidth', 2);
            
            % Draw lane markings
            for x = -200:20:200
                if abs(x) > 20
                    plot(ax, [x, x+10], [0, 0], 'w--', 'LineWidth', 1);
                end
            end
            for y = -200:20:200
                if abs(y) > 20
                    plot(ax, [0, 0], [y, y+10], 'w--', 'LineWidth', 1);
                end
            end
            
            % Draw blockages
            keys = obj.blockages.keys;
            for i = 1:length(keys)
                blockage = obj.blockages(keys{i});
                rectangle(ax, 'Position', [blockage.position(1)-blockage.radius, ...
                    blockage.position(2)-blockage.radius, ...
                    blockage.radius*2, blockage.radius*2], ...
                    'Curvature', [1, 1], ...
                    'FaceColor', [0.8, 0.2, 0.2, 0.5], ...
                    'EdgeColor', 'red', 'LineWidth', 2);
            end
            
            % Draw vehicles
            for i = 1:length(obj.vehicles)
                if obj.vehicles(i).isActive
                    vehicle = obj.vehicles(i);
                    
                    % Draw vehicle as rectangle
                    theta = deg2rad(vehicle.heading);
                    R = [cos(theta), -sin(theta); sin(theta), cos(theta)];
                    
                    % Vehicle corners
                    halfLength = vehicle.size(1) / 2;
                    halfWidth = vehicle.size(2) / 2;
                    corners = [-halfLength, -halfWidth;
                               halfLength, -halfWidth;
                               halfLength, halfWidth;
                               -halfLength, halfWidth;
                               -halfLength, -halfWidth];
                    
                    % Rotate and translate
                    rotatedCorners = (R * corners')';
                    finalCorners = rotatedCorners + vehicle.position;
                    
                    % Draw
                    fill(ax, finalCorners(:,1), finalCorners(:,2), vehicle.color, ...
                        'EdgeColor', 'black', 'LineWidth', 0.5);
                end
            end
            
            % Set axis properties
            axis(ax, 'equal');
            xlim(ax, [-250, 250]);
            ylim(ax, [-250, 250]);
            xlabel(ax, 'Distance (m)');
            ylabel(ax, 'Distance (m)');
            title(ax, 'Indian Traffic Simulation');
            grid(ax, 'on');
            
            hold(ax, 'off');
        end
        
        function stop(obj)
            % Stop simulation
            obj.isRunning = false;
        end
    end
end
