classdef RoadNetwork < handle
    % RoadNetwork - Represents Indian road network with realistic features
    
    properties
        roads           % Array of road segments
        junctions       % Array of junctions
        entryPoints     % Entry points for vehicles
        exitPoints      % Exit points for vehicles
        graph           % Graph representation of network
        roadQuality     % Quality map for road segments
        laneMarkings    % Lane marking quality (0-1)
    end
    
    methods
        function obj = RoadNetwork()
            % Constructor
            obj.roads = [];
            obj.junctions = [];
            obj.entryPoints = [];
            obj.exitPoints = [];
            obj.graph = digraph();
            obj.roadQuality = containers.Map();
            obj.laneMarkings = containers.Map();
        end
        
        function createIndianJunction(obj, varargin)
            % Create a typical Indian junction with irregular features
            p = inputParser;
            addParameter(p, 'center', [0, 0]);
            addParameter(p, 'roadWidths', [12, 12, 12, 12]);
            addParameter(p, 'numLanes', [3, 3, 3, 3]);
            addParameter(p, 'hasDivider', [false, false, false, false]);
            addParameter(p, 'surfaceQuality', [0.7, 0.7, 0.7, 0.7]);
            parse(p, varargin{:});
            
            center = p.Results.center;
            roadWidths = p.Results.roadWidths;
            numLanes = p.Results.numLanes;
            hasDivider = p.Results.hasDivider;
            surfaceQuality = p.Results.surfaceQuality;
            
            % Create junction
            junction = struct();
            junction.id = sprintf('J%d', length(obj.junctions) + 1);
            junction.position = center;
            junction.type = '4way';
            junction.signalized = rand() > 0.3; % 70% chance of signal
            
            % Create roads connecting to junction
            roadAngles = [0, 90, 180, 270]; % North, East, South, West
            roadLength = 200; % meters
            
            for i = 1:4
                road = struct();
                road.id = sprintf('R%d', length(obj.roads) + 1);
                road.startPoint = center;
                road.angle = roadAngles(i);
                road.length = roadLength;
                road.width = roadWidths(i);
                road.numLanes = numLanes(i);
                road.hasDivider = hasDivider(i);
                
                % Calculate end point
                rad = deg2rad(roadAngles(i));
                road.endPoint = center + roadLength * [cos(rad), sin(rad)];
                
                % Add Indian road characteristics
                road.laneWidth = road.width / road.numLanes;
                road.laneMarkingQuality = 0.3 + rand() * 0.5; % Poor to moderate
                road.surfaceQuality = surfaceQuality(i);
                road.hasFootpath = rand() > 0.5;
                road.footpathEncroachment = rand() * 0.3; % 0-30% encroachment
                
                % Store road quality
                obj.roadQuality(road.id) = road.surfaceQuality;
                obj.laneMarkings(road.id) = road.laneMarkingQuality;
                
                % Add to roads array
                obj.roads = [obj.roads, road];
                
                % Create entry/exit points
                entryPoint = struct();
                entryPoint.position = road.endPoint;
                entryPoint.heading = mod(road.angle + 180, 360);
                entryPoint.roadId = road.id;
                obj.entryPoints = [obj.entryPoints, entryPoint];
                
                exitPoint = struct();
                exitPoint.position = road.endPoint;
                exitPoint.heading = road.angle;
                exitPoint.roadId = road.id;
                obj.exitPoints = [obj.exitPoints, exitPoint];
            end
            
            obj.junctions = [obj.junctions, junction];
            
            % Build graph representation
            obj.buildGraph();
        end
        
        function createRoadFromOSM(obj, osmData)
            % Create road network from OpenStreetMap data
            % This would interface with OSM data import
            fprintf('Creating road network from OSM data...\n');
            % Implementation would go here
        end
        
        function buildGraph(obj)
            % Build graph representation of road network
            if isempty(obj.roads)
                return;
            end
            
            % Create nodes for each road segment
            nodeNames = {};
            for i = 1:length(obj.roads)
                nodeNames{end+1} = obj.roads(i).id;
            end
            
            % Create edges based on connectivity
            edges = [];
            for i = 1:length(obj.roads)
                for j = 1:length(obj.roads)
                    if i ~= j
                        % Check if roads connect
                        if obj.areRoadsConnected(obj.roads(i), obj.roads(j))
                            edges = [edges; i, j];
                        end
                    end
                end
            end
            
            if ~isempty(edges)
                obj.graph = digraph(edges(:,1), edges(:,2), [], nodeNames);
            end
        end
        
        function connected = areRoadsConnected(obj, road1, road2)
            % Check if two roads are connected
            threshold = 5; % meters
            
            % Check if end of road1 connects to start of road2
            dist1 = norm(road1.endPoint - road2.startPoint);
            % Check if start of road1 connects to end of road2
            dist2 = norm(road1.startPoint - road2.endPoint);
            % Check if they share a junction
            dist3 = norm(road1.startPoint - road2.startPoint);
            
            connected = (dist1 < threshold) || (dist2 < threshold) || (dist3 < threshold);
        end
        
        function position = getRandomRoadPosition(obj)
            % Get a random position on a road
            if isempty(obj.roads)
                position = [0, 0];
                return;
            end
            
            road = obj.roads(randi(length(obj.roads)));
            t = rand(); % Random point along road
            position = road.startPoint + t * (road.endPoint - road.startPoint);
            
            % Add lateral offset for lane position
            lateralOffset = (rand() - 0.5) * road.width;
            perpAngle = road.angle + 90;
            position = position + lateralOffset * [cosd(perpAngle), sind(perpAngle)];
        end
        
        function position = getRoadsidePosition(obj)
            % Get a position on the roadside (for vendors, parked vehicles)
            if isempty(obj.roads)
                position = [0, 0];
                return;
            end
            
            road = obj.roads(randi(length(obj.roads)));
            t = rand(); % Random point along road
            basePosition = road.startPoint + t * (road.endPoint - road.startPoint);
            
            % Position on the side of the road
            sideOffset = road.width/2 + 1 + rand() * 2; % 1-3m from road edge
            side = sign(rand() - 0.5); % Random side
            perpAngle = road.angle + 90;
            position = basePosition + side * sideOffset * [cosd(perpAngle), sind(perpAngle)];
        end
        
        function segment = getRoadSegmentAt(obj, position)
            % Get road segment at given position
            minDist = inf;
            segment = [];
            
            for i = 1:length(obj.roads)
                road = obj.roads(i);
                % Calculate distance from position to road line
                dist = obj.pointToLineDistance(position, road.startPoint, road.endPoint);
                
                if dist < road.width/2 && dist < minDist
                    minDist = dist;
                    segment = road;
                end
            end
        end
        
        function junction = getNearestJunction(obj, position)
            % Get nearest junction to position
            if isempty(obj.junctions)
                junction = [];
                return;
            end
            
            minDist = inf;
            nearestIdx = 1;
            
            for i = 1:length(obj.junctions)
                dist = norm(obj.junctions(i).position - position);
                if dist < minDist
                    minDist = dist;
                    nearestIdx = i;
                end
            end
            
            junction = obj.junctions(nearestIdx);
        end
        
        function junctions = getJunctions(obj)
            % Get all junctions
            junctions = obj.junctions;
        end
        
        function entryPoints = getEntryPoints(obj)
            % Get all entry points
            entryPoints = obj.entryPoints;
        end
        
        function route = generateRandomRoute(obj, startPoint)
            % Generate a random route through the network
            if isempty(obj.graph)
                route = struct('waypoints', [startPoint.position], 'roads', []);
                return;
            end
            
            % Select random exit point
            exitIdx = randi(length(obj.exitPoints));
            endPoint = obj.exitPoints(exitIdx);
            
            % Find path through network
            try
                startNode = startPoint.roadId;
                endNode = endPoint.roadId;
                pathNodes = shortestpath(obj.graph, startNode, endNode);
                
                % Convert to waypoints
                waypoints = [];
                roads = [];
                for i = 1:length(pathNodes)
                    roadIdx = find(strcmp({obj.roads.id}, pathNodes{i}));
                    if ~isempty(roadIdx)
                        road = obj.roads(roadIdx);
                        waypoints = [waypoints; road.startPoint; road.endPoint];
                        roads = [roads, road];
                    end
                end
                
                route = struct('waypoints', waypoints, 'roads', roads);
            catch
                % If no path found, create simple route
                route = struct('waypoints', [startPoint.position; endPoint.position], 'roads', []);
            end
        end
        
        function dist = pointToLineDistance(obj, point, lineStart, lineEnd)
            % Calculate distance from point to line segment
            lineVec = lineEnd - lineStart;
            pointVec = point - lineStart;
            lineLen = norm(lineVec);
            
            if lineLen == 0
                dist = norm(pointVec);
                return;
            end
            
            lineUnitVec = lineVec / lineLen;
            pointVecScaled = pointVec / lineLen;
            
            t = dot(lineUnitVec, pointVecScaled);
            t = max(0, min(1, t));
            
            nearest = lineVec * t;
            dist = norm(pointVec - nearest);
        end
        
        function quality = getRoadQuality(obj, roadId)
            % Get road surface quality
            if obj.roadQuality.isKey(roadId)
                quality = obj.roadQuality(roadId);
            else
                quality = 0.7; % Default
            end
        end
        
        function addPothole(obj, roadId, position, severity)
            % Add a pothole to a road segment
            if obj.roadQuality.isKey(roadId)
                % Reduce road quality based on pothole severity
                currentQuality = obj.roadQuality(roadId);
                obj.roadQuality(roadId) = max(0.1, currentQuality - severity * 0.2);
            end
        end
        
        function addConstruction(obj, roadId, startPos, endPos)
            % Add construction zone to road
            % This would mark a section of road as under construction
            fprintf('Construction added on road %s\n', roadId);
        end
        
        function lanes = getAvailableLanes(obj, roadId, position)
            % Get available lanes at a position (considering blockages)
            roadIdx = find(strcmp({obj.roads.id}, roadId));
            if isempty(roadIdx)
                lanes = [];
                return;
            end
            
            road = obj.roads(roadIdx);
            totalLanes = road.numLanes;
            
            % Account for parked vehicles, vendors, etc.
            encroachment = road.footpathEncroachment;
            availableLanes = max(1, totalLanes - floor(encroachment * totalLanes));
            
            lanes = 1:availableLanes;
        end
        
        function clearNetwork(obj)
            % Clear the entire network
            obj.roads = [];
            obj.junctions = [];
            obj.entryPoints = [];
            obj.exitPoints = [];
            obj.graph = digraph();
            obj.roadQuality = containers.Map();
            obj.laneMarkings = containers.Map();
        end
    end
end
