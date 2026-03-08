classdef IndianVehicle < handle
    % IndianVehicle - Represents vehicles with Indian driving behaviors
    
    properties
        vehicleType     % Type of vehicle
        position        % Current position [x, y]
        heading         % Current heading angle (degrees)
        speed           % Current speed (km/h)
        maxSpeed        % Maximum speed (km/h)
        acceleration    % Current acceleration
        dimensions      % Vehicle dimensions [length, width]
        route           % Planned route
        routeIndex      % Current position in route
        isActive        % Whether vehicle is active
        behaviorParams  % Driving behavior parameters
        color           % Vehicle color for visualization
        honkCooldown    % Cooldown for honking
        lastHonkTime    % Last time honked
    end
    
    properties (Constant)
        % Vehicle dimensions (meters) for different types
        DIMENSIONS = struct(...
            'car', [4.5, 1.8], ...
            'bus', [12, 2.5], ...
            'truck', [8, 2.5], ...
            'auto_rickshaw', [3.2, 1.4], ...
            'motorcycle', [2, 0.8], ...
            'bicycle', [1.8, 0.6], ...
            'pedestrian', [0.5, 0.5] ...
        );
        
        % Default colors for vehicle types
        COLORS = struct(...
            'car', [0 0 1], ...           % Blue
            'bus', [1 0.5 0], ...          % Orange
            'truck', [0.5 0.5 0.5], ...    % Gray
            'auto_rickshaw', [1 1 0], ...  % Yellow
            'motorcycle', [1 0 0], ...      % Red
            'bicycle', [0 1 0], ...         % Green
            'pedestrian', [1 0 1] ...       % Magenta
        );
    end
    
    methods
        function obj = IndianVehicle(vehicleType)
            % Constructor
            obj.vehicleType = vehicleType;
            obj.position = [0, 0];
            obj.heading = 0;
            obj.speed = 0;
            obj.isActive = true;
            obj.routeIndex = 1;
            obj.honkCooldown = 0;
            obj.lastHonkTime = 0;
            
            % Set vehicle-specific properties
            if isfield(obj.DIMENSIONS, vehicleType)
                obj.dimensions = obj.DIMENSIONS.(vehicleType);
            else
                obj.dimensions = obj.DIMENSIONS.car; % Default
            end
            
            if isfield(obj.COLORS, vehicleType)
                obj.color = obj.COLORS.(vehicleType);
            else
                obj.color = [0.5 0.5 0.5]; % Default gray
            end
            
            % Set default behavior parameters
            obj.setDefaultBehaviorParams(vehicleType);
        end
        
        function setDefaultBehaviorParams(obj, vehicleType)
            % Set default Indian driving behavior parameters
            switch vehicleType
                case 'motorcycle'
                    obj.maxSpeed = 60;
                    obj.behaviorParams = struct(...
                        'aggressiveness', 0.8, ...
                        'laneDisciple', 0.2, ...
                        'gapAcceptance', 0.4, ...
                        'reactionTime', 0.3, ...
                        'honkingTendency', 0.7, ...
                        'overtakingTendency', 0.9 ...
                    );
                    
                case 'auto_rickshaw'
                    obj.maxSpeed = 40;
                    obj.behaviorParams = struct(...
                        'aggressiveness', 0.6, ...
                        'laneDisciple', 0.3, ...
                        'gapAcceptance', 0.5, ...
                        'reactionTime', 0.4, ...
                        'honkingTendency', 0.8, ...
                        'overtakingTendency', 0.7 ...
                    );
                    
                case 'car'
                    obj.maxSpeed = 80;
                    obj.behaviorParams = struct(...
                        'aggressiveness', 0.5, ...
                        'laneDisciple', 0.6, ...
                        'gapAcceptance', 0.8, ...
                        'reactionTime', 0.5, ...
                        'honkingTendency', 0.5, ...
                        'overtakingTendency', 0.6 ...
                    );
                    
                case 'bus'
                    obj.maxSpeed = 50;
                    obj.behaviorParams = struct(...
                        'aggressiveness', 0.4, ...
                        'laneDisciple', 0.5, ...
                        'gapAcceptance', 1.2, ...
                        'reactionTime', 0.6, ...
                        'honkingTendency', 0.6, ...
                        'overtakingTendency', 0.3 ...
                    );
                    
                case 'truck'
                    obj.maxSpeed = 50;
                    obj.behaviorParams = struct(...
                        'aggressiveness', 0.3, ...
                        'laneDisciple', 0.5, ...
                        'gapAcceptance', 1.5, ...
                        'reactionTime', 0.7, ...
                        'honkingTendency', 0.5, ...
                        'overtakingTendency', 0.2 ...
                    );
                    
                case 'bicycle'
                    obj.maxSpeed = 20;
                    obj.behaviorParams = struct(...
                        'aggressiveness', 0.2, ...
                        'laneDisciple', 0.1, ...
                        'gapAcceptance', 0.3, ...
                        'reactionTime', 0.2, ...
                        'honkingTendency', 0, ...
                        'overtakingTendency', 0.1 ...
                    );
                    
                otherwise
                    obj.maxSpeed = 60;
                    obj.behaviorParams = struct(...
                        'aggressiveness', 0.5, ...
                        'laneDisciple', 0.5, ...
                        'gapAcceptance', 0.8, ...
                        'reactionTime', 0.5, ...
                        'honkingTendency', 0.5, ...
                        'overtakingTendency', 0.5 ...
                    );
            end
        end
        
        function setPosition(obj, position)
            obj.position = position;
        end
        
        function pos = getPosition(obj)
            pos = obj.position;
        end
        
        function setHeading(obj, heading)
            obj.heading = heading;
        end
        
        function setRoute(obj, route)
            obj.route = route;
            obj.routeIndex = 1;
        end
        
        function setBehaviorParams(obj, params)
            % Override behavior parameters
            fields = fieldnames(params);
            for i = 1:length(fields)
                if isfield(obj.behaviorParams, fields{i})
                    obj.behaviorParams.(fields{i}) = params.(fields{i});
                end
            end
            
            % Update max speed if provided
            if isfield(params, 'maxSpeed')
                obj.maxSpeed = params.maxSpeed;
            end
            
            % Update acceleration if provided
            if isfield(params, 'acceleration')
                obj.acceleration = params.acceleration;
            end
        end
        
        function updateBehavior(obj, nearbyVehicles, obstacles, blockages, signalState, roadNetwork)
            % Update vehicle behavior based on surroundings
            
            % Calculate desired speed
            desiredSpeed = obj.calculateDesiredSpeed(nearbyVehicles, obstacles, blockages, signalState);
            
            % Calculate steering
            steeringAngle = obj.calculateSteering(roadNetwork);
            
            % Apply Indian traffic behaviors
            if strcmp(obj.vehicleType, 'motorcycle') || strcmp(obj.vehicleType, 'auto_rickshaw')
                % Lane filtering behavior
                obj.attemptLaneFiltering(nearbyVehicles);
            end
            
            % Update speed with acceleration limits
            speedDiff = desiredSpeed - obj.speed;
            maxAccel = 3; % m/s^2
            maxDecel = -5; % m/s^2
            
            if speedDiff > 0
                obj.acceleration = min(speedDiff, maxAccel);
            else
                obj.acceleration = max(speedDiff, maxDecel);
            end
            
            % Update heading
            obj.heading = obj.heading + steeringAngle;
        end
        
        function desiredSpeed = calculateDesiredSpeed(obj, nearbyVehicles, obstacles, blockages, signalState)
            % Calculate desired speed based on conditions
            
            desiredSpeed = obj.maxSpeed;
            
            % Check for vehicles ahead
            vehicleAhead = obj.getVehicleAhead(nearbyVehicles);
            if ~isempty(vehicleAhead)
                distance = norm(vehicleAhead.position - obj.position);
                safeDistance = obj.calculateSafeDistance(obj.speed);
                
                if distance < safeDistance
                    % Adjust speed based on Indian driving style
                    speedReduction = (1 - obj.behaviorParams.aggressiveness) * ...
                        (safeDistance - distance) / safeDistance;
                    desiredSpeed = vehicleAhead.speed * (1 - speedReduction);
                end
            end
            
            % Check for obstacles
            if ~isempty(obstacles)
                for i = 1:length(obstacles)
                    dist = norm(obstacles(i).position - obj.position);
                    if dist < 20 % Within reaction distance
                        if strcmp(obstacles(i).type, 'pothole')
                            % Slow down for potholes based on severity
                            speedFactor = 1 - obstacles(i).severity * 0.5;
                            desiredSpeed = min(desiredSpeed, obj.maxSpeed * speedFactor);
                        elseif strcmp(obstacles(i).type, 'street_vendor')
                            % Navigate around vendors
                            desiredSpeed = min(desiredSpeed, 20);
                        end
                    end
                end
            end
            
            % Check for blockages
            if ~isempty(blockages)
                if strcmp(blockages.affectedLanes, 'all')
                    desiredSpeed = 0; % Full stop
                else
                    desiredSpeed = min(desiredSpeed, 10); % Crawl through
                end
            end
            
            % Check traffic signal
            if strcmp(signalState, 'red')
                % Indian drivers may not always stop at red lights
                if rand() < obj.behaviorParams.laneDisciple
                    desiredSpeed = 0;
                else
                    desiredSpeed = min(desiredSpeed, 10); % Slow roll
                end
            elseif strcmp(signalState, 'yellow')
                % Most Indian drivers accelerate on yellow
                if obj.behaviorParams.aggressiveness > 0.5
                    desiredSpeed = obj.maxSpeed * 1.2; % Speed up
                else
                    desiredSpeed = 0; % Stop
                end
            end
            
            % Ensure non-negative speed
            desiredSpeed = max(0, desiredSpeed);
        end
        
        function steeringAngle = calculateSteering(obj, roadNetwork)
            % Calculate steering to follow route
            
            if isempty(obj.route)
                steeringAngle = 0;
                return;
            end
            
            % Get target waypoint
            if obj.routeIndex <= size(obj.route.waypoints, 1)
                targetPoint = obj.route.waypoints(obj.routeIndex, :);
            else
                steeringAngle = 0;
                return;
            end
            
            % Calculate angle to target
            vectorToTarget = targetPoint - obj.position;
            targetAngle = atan2d(vectorToTarget(2), vectorToTarget(1));
            
            % Calculate steering angle with Indian driving style
            angleDiff = wrapTo180(targetAngle - obj.heading);
            
            % Add some randomness based on lane discipline
            randomness = (1 - obj.behaviorParams.laneDisciple) * (rand() - 0.5) * 10;
            steeringAngle = angleDiff * 0.1 + randomness;
            
            % Limit steering angle
            maxSteeringAngle = 30; % degrees
            steeringAngle = max(-maxSteeringAngle, min(maxSteeringAngle, steeringAngle));
            
            % Check if reached waypoint
            if norm(vectorToTarget) < 5
                obj.routeIndex = obj.routeIndex + 1;
            end
        end
        
        function safeDistance = calculateSafeDistance(obj, speed)
            % Calculate safe following distance (Indian style - much shorter)
            reactionTime = obj.behaviorParams.reactionTime;
            gapAcceptance = obj.behaviorParams.gapAcceptance;
            
            % Convert speed from km/h to m/s
            speedMs = speed / 3.6;
            
            % Indian drivers maintain much smaller gaps
            safeDistance = speedMs * reactionTime * gapAcceptance + 2;
            safeDistance = max(2, safeDistance); % Minimum 2 meters
        end
        
        function vehicleAhead = getVehicleAhead(obj, nearbyVehicles)
            % Find vehicle directly ahead
            vehicleAhead = [];
            minDistance = inf;
            
            for i = 1:length(nearbyVehicles)
                other = nearbyVehicles(i);
                
                % Calculate relative position
                relPos = other.position - obj.position;
                relAngle = atan2d(relPos(2), relPos(1));
                angleDiff = abs(wrapTo180(relAngle - obj.heading));
                
                % Check if vehicle is ahead (within 30 degrees)
                if angleDiff < 30
                    dist = norm(relPos);
                    if dist < minDistance
                        minDistance = dist;
                        vehicleAhead = other;
                    end
                end
            end
        end
        
        function attemptLaneFiltering(obj, nearbyVehicles)
            % Attempt to filter through traffic (motorcycles and rickshaws)
            if isempty(nearbyVehicles)
                return;
            end
            
            % Look for gaps
            for i = 1:length(nearbyVehicles)-1
                gap = norm(nearbyVehicles(i).position - nearbyVehicles(i+1).position);
                requiredGap = obj.dimensions(2) + 0.5; % Width plus margin
                
                if gap > requiredGap
                    % Found a gap, adjust position slightly
                    gapCenter = (nearbyVehicles(i).position + nearbyVehicles(i+1).position) / 2;
                    vectorToGap = gapCenter - obj.position;
                    
                    if norm(vectorToGap) < 10 % If gap is nearby
                        % Adjust heading towards gap
                        obj.heading = obj.heading + sign(vectorToGap(1)) * 5;
                    end
                end
            end
        end
        
        function attemptGapSqueeze(obj, otherVehicle)
            % Attempt to squeeze through small gaps (motorcycle behavior)
            gap = norm(obj.position - otherVehicle.position);
            minGap = obj.dimensions(2) + otherVehicle.dimensions(2)/2 + 0.2;
            
            if gap > minGap && obj.behaviorParams.aggressiveness > 0.6
                % Attempt to squeeze
                % This would involve lateral movement logic
            end
        end
        
        function honk(obj)
            % Honk horn (common in Indian traffic)
            currentTime = tic;
            if currentTime - obj.lastHonkTime > obj.honkCooldown
                fprintf('Vehicle %s honking!\n', obj.vehicleType);
                obj.lastHonkTime = currentTime;
                obj.honkCooldown = 2 + rand() * 3; % 2-5 second cooldown
            end
        end
        
        function updatePosition(obj, timeStep)
            % Update vehicle position based on speed and heading
            
            % Convert speed from km/h to m/s
            speedMs = obj.speed / 3.6;
            
            % Update speed
            obj.speed = obj.speed + obj.acceleration * timeStep * 3.6;
            obj.speed = max(0, min(obj.maxSpeed, obj.speed));
            
            % Update position
            distance = speedMs * timeStep;
            obj.position(1) = obj.position(1) + distance * cosd(obj.heading);
            obj.position(2) = obj.position(2) + distance * sind(obj.heading);
        end
        
        function completed = hasCompletedRoute(obj)
            % Check if vehicle has completed its route
            if isempty(obj.route)
                completed = false;
                return;
            end
            
            completed = obj.routeIndex > size(obj.route.waypoints, 1);
            
            if completed
                obj.isActive = false;
            end
        end
        
        function bounds = getBounds(obj)
            % Get vehicle bounding box
            halfLength = obj.dimensions(1) / 2;
            halfWidth = obj.dimensions(2) / 2;
            
            % Calculate corners in vehicle coordinate system
            corners = [
                -halfLength, -halfWidth;
                halfLength, -halfWidth;
                halfLength, halfWidth;
                -halfLength, halfWidth
            ];
            
            % Rotate corners based on heading
            theta = deg2rad(obj.heading);
            R = [cos(theta), -sin(theta); sin(theta), cos(theta)];
            
            rotatedCorners = (R * corners')';
            
            % Translate to world coordinates
            bounds = rotatedCorners + obj.position;
        end
        
        function draw(obj, ax)
            % Draw vehicle on axes
            bounds = obj.getBounds();
            
            % Close the polygon
            bounds = [bounds; bounds(1,:)];
            
            % Draw vehicle
            fill(ax, bounds(:,1), bounds(:,2), obj.color, ...
                'EdgeColor', 'k', 'LineWidth', 0.5);
            
            % Draw heading indicator
            headingLength = obj.dimensions(1) * 0.3;
            headingEnd = obj.position + headingLength * [cosd(obj.heading), sind(obj.heading)];
            plot(ax, [obj.position(1), headingEnd(1)], ...
                [obj.position(2), headingEnd(2)], 'k-', 'LineWidth', 1);
        end
    end
end

function angle = wrapTo180(angle)
    % Wrap angle to [-180, 180] range
    angle = mod(angle + 180, 360) - 180;
end
