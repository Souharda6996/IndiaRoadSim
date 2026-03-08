classdef IndianTrafficSimulationGUI < handle
    % Interactive GUI for Indian Traffic Simulation
    % Features real road visualization and interactive blocking capabilities
    
    properties
        figure          % Main figure handle
        mainAxes        % Main visualization axes
        statsPanel      % Statistics display panel
        controlPanel    % Control panel
        simulator       % Traffic simulator instance
        
        % UI Components
        startButton
        stopButton
        pauseButton
        speedSlider
        blockageDropdown
        scenarioDropdown
        
        % Display elements
        statsText
        timeText
        vehicleCountText
        congestionBar
        
        % Interaction state
        isBlockingMode
        currentBlockageType
        selectedRoadSegment
        
        % Visualization settings
        viewScale
        viewCenter
        showTrafficFlow
        showHeatmap
    end
    
    methods
        function obj = IndianTrafficSimulationGUI()
            % Constructor
            obj.simulator = [];
            obj.isBlockingMode = false;
            obj.viewScale = 1;
            obj.viewCenter = [0, 0];
            obj.showTrafficFlow = true;
            obj.showHeatmap = false;
            
            % Create GUI
            obj.createGUI();
            
            % Initialize simulator
            obj.initializeSimulator();
        end
        
        function createGUI(obj)
            % Create main figure
            obj.figure = figure(...
                'Name', 'Indian Traffic Simulation - Interactive Road Network', ...
                'Position', [100, 100, 1400, 800], ...
                'MenuBar', 'none', ...
                'ToolBar', 'none', ...
                'NumberTitle', 'off', ...
                'CloseRequestFcn', @(~,~)obj.onClose());
            
            % Create main layout
            mainLayout = uigridlayout(obj.figure, [1, 3]);
            mainLayout.ColumnWidth = {'1x', '3x', '1x'};
            
            % Create control panel (left)
            obj.createControlPanel(mainLayout);
            
            % Create visualization area (center)
            obj.createVisualizationArea(mainLayout);
            
            % Create statistics panel (right)
            obj.createStatsPanel(mainLayout);
            
            % Set up callbacks
            obj.setupCallbacks();
        end
        
        function createControlPanel(obj, parent)
            % Create control panel
            controlLayout = uigridlayout(parent, [12, 1]);
            controlLayout.RowHeight = repmat({'fit'}, 1, 12);
            controlLayout.Padding = [10, 10, 10, 10];
            
            % Title
            uilabel(controlLayout, ...
                'Text', 'Simulation Control', ...
                'FontSize', 16, ...
                'FontWeight', 'bold', ...
                'HorizontalAlignment', 'center');
            
            % Scenario selection
            uilabel(controlLayout, 'Text', 'Select Scenario:');
            obj.scenarioDropdown = uidropdown(controlLayout, ...
                'Items', {'Default Junction', 'Mumbai Traffic', 'Delhi NCR', ...
                          'Bangalore IT Corridor', 'Custom OSM'}, ...
                'Value', 'Default Junction', ...
                'ValueChangedFcn', @(~,~)obj.onScenarioChanged());
            
            % Simulation controls
            obj.startButton = uibutton(controlLayout, ...
                'Text', '▶ Start Simulation', ...
                'BackgroundColor', [0.2, 0.8, 0.2], ...
                'FontWeight', 'bold', ...
                'ButtonPushedFcn', @(~,~)obj.startSimulation());
            
            obj.pauseButton = uibutton(controlLayout, ...
                'Text', '⏸ Pause', ...
                'BackgroundColor', [1, 0.8, 0.2], ...
                'Enable', 'off', ...
                'ButtonPushedFcn', @(~,~)obj.pauseSimulation());
            
            obj.stopButton = uibutton(controlLayout, ...
                'Text', '⏹ Stop', ...
                'BackgroundColor', [0.8, 0.2, 0.2], ...
                'Enable', 'off', ...
                'ButtonPushedFcn', @(~,~)obj.stopSimulation());
            
            % Speed control
            uilabel(controlLayout, 'Text', 'Simulation Speed:');
            obj.speedSlider = uislider(controlLayout, ...
                'Limits', [0.1, 5], ...
                'Value', 1, ...
                'MajorTicks', [0.1, 0.5, 1, 2, 5], ...
                'ValueChangedFcn', @(~,~)obj.onSpeedChanged());
            
            % Road blocking controls
            uilabel(controlLayout, ...
                'Text', 'Road Blocking:', ...
                'FontWeight', 'bold');
            
            obj.blockageDropdown = uidropdown(controlLayout, ...
                'Items', {'Select Blockage Type', 'Water Logging', 'Construction', ...
                          'Festival/Procession', 'Accident', 'VIP Movement', ...
                          'Protest/Rally', 'Market Day'}, ...
                'Value', 'Select Blockage Type', ...
                'ValueChangedFcn', @(~,~)obj.onBlockageTypeSelected());
            
            blockButton = uibutton(controlLayout, ...
                'Text', '🚧 Click Road to Block', ...
                'BackgroundColor', [1, 0.6, 0.2], ...
                'ButtonPushedFcn', @(~,~)obj.enableBlockingMode());
            
            clearButton = uibutton(controlLayout, ...
                'Text', '✓ Clear All Blockages', ...
                'BackgroundColor', [0.2, 0.6, 1], ...
                'ButtonPushedFcn', @(~,~)obj.clearAllBlockages());
        end
        
        function createVisualizationArea(obj, parent)
            % Create visualization panel
            vizPanel = uipanel(parent, ...
                'Title', 'Traffic Simulation View', ...
                'FontSize', 14, ...
                'FontWeight', 'bold');
            
            % Create axes for visualization
            obj.mainAxes = axes(vizPanel, ...
                'Position', [0.05, 0.05, 0.9, 0.9]);
            
            % Set up axes properties
            hold(obj.mainAxes, 'on');
            grid(obj.mainAxes, 'on');
            axis(obj.mainAxes, 'equal');
            xlabel(obj.mainAxes, 'Distance (m)');
            ylabel(obj.mainAxes, 'Distance (m)');
            title(obj.mainAxes, 'Indian Urban Traffic Network');
            
            % Set initial view
            xlim(obj.mainAxes, [-250, 250]);
            ylim(obj.mainAxes, [-250, 250]);
            
            % Add zoom and pan controls
            zoom(obj.mainAxes, 'on');
            pan(obj.mainAxes, 'on');
            
            % Set up mouse click callback for road blocking
            obj.mainAxes.ButtonDownFcn = @(~,evt)obj.onAxesClick(evt);
        end
        
        function createStatsPanel(obj, parent)
            % Create statistics panel
            statsLayout = uigridlayout(parent, [10, 1]);
            statsLayout.RowHeight = repmat({'fit'}, 1, 10);
            statsLayout.Padding = [10, 10, 10, 10];
            
            % Title
            uilabel(statsLayout, ...
                'Text', 'Traffic Statistics', ...
                'FontSize', 16, ...
                'FontWeight', 'bold', ...
                'HorizontalAlignment', 'center');
            
            % Simulation time
            uilabel(statsLayout, 'Text', 'Simulation Time:');
            obj.timeText = uilabel(statsLayout, ...
                'Text', '00:00:00', ...
                'FontSize', 14, ...
                'FontWeight', 'bold', ...
                'HorizontalAlignment', 'center');
            
            % Vehicle count
            uilabel(statsLayout, 'Text', 'Total Vehicles:');
            obj.vehicleCountText = uilabel(statsLayout, ...
                'Text', '0', ...
                'FontSize', 20, ...
                'FontWeight', 'bold', ...
                'HorizontalAlignment', 'center', ...
                'FontColor', [0, 0.5, 0]);
            
            % Vehicle breakdown
            vehicleBreakdownPanel = uipanel(statsLayout);
            vehicleBreakdownLayout = uigridlayout(vehicleBreakdownPanel, [6, 2]);
            
            % Vehicle type counts
            vehicleTypes = {'Cars:', 'Buses:', 'Trucks:', 'Auto-rickshaws:', ...
                           'Motorcycles:', 'Bicycles:'};
            for i = 1:6
                uilabel(vehicleBreakdownLayout, 'Text', vehicleTypes{i});
                uilabel(vehicleBreakdownLayout, 'Text', '0', 'Tag', ['vcount_' num2str(i)]);
            end
            
            % Congestion level
            uilabel(statsLayout, 'Text', 'Congestion Level:');
            obj.congestionBar = uigauge(statsLayout, ...
                'Limits', [0, 1], ...
                'Value', 0.2);
            
            % Average speed
            uilabel(statsLayout, 'Text', 'Average Speed:');
            avgSpeedText = uilabel(statsLayout, ...
                'Text', '0 km/h', ...
                'FontSize', 14, ...
                'HorizontalAlignment', 'center', ...
                'Tag', 'avgSpeed');
            
            % Active blockages
            uilabel(statsLayout, 'Text', 'Active Blockages:');
            blockageCountText = uilabel(statsLayout, ...
                'Text', '0', ...
                'FontSize', 14, ...
                'FontColor', [0.8, 0.2, 0.2], ...
                'HorizontalAlignment', 'center', ...
                'Tag', 'blockageCount');
        end
        
        function initializeSimulator(obj)
            % Initialize the traffic simulator
            addpath(fullfile('E:', 'indian_traffic_simulation', 'src', 'models'));
            addpath(fullfile('E:', 'indian_traffic_simulation', 'src', 'controllers'));
            addpath(fullfile('E:', 'indian_traffic_simulation', 'src', 'utils'));
            
            try
                % Create simulator instance
                obj.simulator = IndianTrafficSimulator();
                
                % Initialize with default scenario
                obj.simulator.initialize();
                
                % Draw initial road network
                obj.drawRoadNetwork();
            catch ME
                fprintf('Error initializing simulator: %s\n', ME.message);
                % Create a simple default setup if initialization fails
                obj.createSimpleSetup();
            end
        end
        
        function drawRoadNetwork(obj)
            % Draw the road network
            cla(obj.mainAxes);
            hold(obj.mainAxes, 'on');
            
            if isempty(obj.simulator) || isempty(obj.simulator.roadNetwork)
                return;
            end
            
            roadNetwork = obj.simulator.roadNetwork;
            
            % Draw roads
            for i = 1:length(roadNetwork.roads)
                road = roadNetwork.roads(i);
                
                % Calculate road polygon
                perpAngle = road.angle + 90;
                offset = road.width/2 * [cosd(perpAngle), sind(perpAngle)];
                
                corners = [
                    road.startPoint + offset;
                    road.endPoint + offset;
                    road.endPoint - offset;
                    road.startPoint - offset;
                    road.startPoint + offset
                ];
                
                % Determine road color based on quality
                quality = road.surfaceQuality;
                if quality > 0.7
                    roadColor = [0.3, 0.3, 0.3]; % Good road - dark gray
                elseif quality > 0.4
                    roadColor = [0.5, 0.5, 0.4]; % Average road - lighter
                else
                    roadColor = [0.6, 0.5, 0.3]; % Poor road - brownish
                end
                
                % Draw road surface
                fill(obj.mainAxes, corners(:,1), corners(:,2), roadColor, ...
                    'EdgeColor', 'none', 'FaceAlpha', 0.8);
                
                % Draw lane markings if quality is good enough
                if road.laneMarkingQuality > 0.3
                    obj.drawLaneMarkings(road);
                end
                
                % Draw footpath if exists
                if road.hasFootpath
                    obj.drawFootpath(road);
                end
                
                % Label road
                midPoint = (road.startPoint + road.endPoint) / 2;
                text(obj.mainAxes, midPoint(1), midPoint(2), road.id, ...
                    'Color', 'white', 'FontSize', 8, 'HorizontalAlignment', 'center');
            end
            
            % Draw junctions
            for i = 1:length(roadNetwork.junctions)
                junction = roadNetwork.junctions(i);
                
                % Draw junction area
                rectangle(obj.mainAxes, ...
                    'Position', [junction.position(1)-15, junction.position(2)-15, 30, 30], ...
                    'Curvature', [0.5, 0.5], ...
                    'FaceColor', [0.4, 0.4, 0.4], ...
                    'EdgeColor', 'yellow', ...
                    'LineWidth', 2);
                
                % Draw traffic signal if present
                if junction.signalized
                    obj.drawTrafficSignal(junction.position);
                end
            end
            
            % Draw obstacles
            obj.drawObstacles();
            
            % Draw blockages
            obj.drawBlockages();
        end
        
        function drawLaneMarkings(obj, road)
            % Draw lane markings on road
            numLanes = road.numLanes;
            if numLanes <= 1
                return;
            end
            
            % Calculate lane positions
            perpAngle = road.angle + 90;
            laneWidth = road.width / numLanes;
            
            for i = 1:numLanes-1
                offset = (i * laneWidth - road.width/2) * [cosd(perpAngle), sind(perpAngle)];
                lineStart = road.startPoint + offset;
                lineEnd = road.endPoint + offset;
                
                % Draw dashed line
                numDashes = 10;
                dashPoints = linspace(0, 1, numDashes*2);
                
                for j = 1:2:length(dashPoints)-1
                    dashStart = lineStart + dashPoints(j) * (lineEnd - lineStart);
                    dashEnd = lineStart + dashPoints(j+1) * (lineEnd - lineStart);
                    
                    % Line quality affects visibility
                    alpha = road.laneMarkingQuality;
                    plot(obj.mainAxes, [dashStart(1), dashEnd(1)], ...
                        [dashStart(2), dashEnd(2)], 'w-', ...
                        'LineWidth', 1, 'Color', [1, 1, 1, alpha]);
                end
            end
        end
        
        function drawFootpath(obj, road)
            % Draw footpath along road
            perpAngle = road.angle + 90;
            footpathWidth = 2; % meters
            
            % Draw on both sides
            for side = [-1, 1]
                offset = side * (road.width/2 + footpathWidth/2) * ...
                    [cosd(perpAngle), sind(perpAngle)];
                
                corners = [
                    road.startPoint + offset + side*footpathWidth/2*[cosd(perpAngle), sind(perpAngle)];
                    road.endPoint + offset + side*footpathWidth/2*[cosd(perpAngle), sind(perpAngle)];
                    road.endPoint + offset - side*footpathWidth/2*[cosd(perpAngle), sind(perpAngle)];
                    road.startPoint + offset - side*footpathWidth/2*[cosd(perpAngle), sind(perpAngle)];
                ];
                
                fill(obj.mainAxes, corners(:,1), corners(:,2), [0.7, 0.7, 0.6], ...
                    'EdgeColor', [0.5, 0.5, 0.4], 'LineWidth', 0.5);
            end
        end
        
        function drawTrafficSignal(obj, position)
            % Draw traffic signal at junction
            signalSize = 3;
            
            % Draw signal pole
            rectangle(obj.mainAxes, ...
                'Position', [position(1)-signalSize/2, position(2)-signalSize/2, ...
                            signalSize, signalSize*2], ...
                'FaceColor', [0.2, 0.2, 0.2], ...
                'EdgeColor', 'black');
            
            % Draw signal lights (will be updated during simulation)
            for i = 1:3
                yOffset = (i-2) * signalSize * 0.6;
                rectangle(obj.mainAxes, ...
                    'Position', [position(1)-signalSize/4, position(2)+yOffset-signalSize/4, ...
                                signalSize/2, signalSize/2], ...
                    'Curvature', [1, 1], ...
                    'FaceColor', [0.3, 0.3, 0.3], ...
                    'EdgeColor', 'black', ...
                    'Tag', sprintf('signal_%d_%d', position(1), i));
            end
        end
        
        function drawObstacles(obj)
            % Draw obstacles on the road
            if isempty(obj.simulator) || isempty(obj.simulator.obstacles)
                return;
            end
            
            for i = 1:length(obj.simulator.obstacles)
                obstacle = obj.simulator.obstacles(i);
                
                switch obstacle.type
                    case 'pothole'
                        % Draw pothole
                        rectangle(obj.mainAxes, ...
                            'Position', [obstacle.position(1)-obstacle.radius, ...
                                        obstacle.position(2)-obstacle.radius, ...
                                        obstacle.radius*2, obstacle.radius*2], ...
                            'Curvature', [1, 1], ...
                            'FaceColor', [0.2, 0.15, 0.1], ...
                            'EdgeColor', [0.1, 0.1, 0.1], ...
                            'LineWidth', 1);
                        
                    case 'street_vendor'
                        % Draw street vendor stall
                        rectangle(obj.mainAxes, ...
                            'Position', [obstacle.position(1)-obstacle.size(1)/2, ...
                                        obstacle.position(2)-obstacle.size(2)/2, ...
                                        obstacle.size(1), obstacle.size(2)], ...
                            'FaceColor', [0.8, 0.6, 0.3], ...
                            'EdgeColor', [0.6, 0.4, 0.2], ...
                            'LineWidth', 1);
                        
                    case 'parked_vehicle'
                        % Draw parked vehicle
                        rectangle(obj.mainAxes, ...
                            'Position', [obstacle.position(1)-2, obstacle.position(2)-1, 4, 2], ...
                            'FaceColor', [0.5, 0.5, 0.6], ...
                            'EdgeColor', [0.3, 0.3, 0.3], ...
                            'LineWidth', 1);
                end
            end
        end
        
        function drawBlockages(obj)
            % Draw road blockages
            if isempty(obj.simulator) || obj.simulator.blockages.Count == 0
                return;
            end
            
            keys = obj.simulator.blockages.keys;
            for i = 1:length(keys)
                roadId = keys{i};
                blockage = obj.simulator.blockages(roadId);
                
                % Find road
                roadIdx = find(strcmp({obj.simulator.roadNetwork.roads.id}, roadId));
                if isempty(roadIdx)
                    continue;
                end
                
                road = obj.simulator.roadNetwork.roads(roadIdx);
                
                % Draw blockage overlay
                perpAngle = road.angle + 90;
                offset = road.width/2 * [cosd(perpAngle), sind(perpAngle)];
                
                corners = [
                    road.startPoint + offset;
                    road.endPoint + offset;
                    road.endPoint - offset;
                    road.startPoint - offset;
                ];
                
                % Color based on blockage type
                switch blockage.type
                    case 1 % Water logging
                        color = [0.2, 0.4, 0.8, 0.6];
                    case 2 % Construction
                        color = [0.8, 0.6, 0.2, 0.6];
                    case 3 % Festival
                        color = [0.8, 0.2, 0.8, 0.6];
                    case 4 % Accident
                        color = [0.8, 0.2, 0.2, 0.6];
                    otherwise
                        color = [0.5, 0.5, 0.5, 0.6];
                end
                
                patch(obj.mainAxes, corners(:,1), corners(:,2), color(1:3), ...
                    'FaceAlpha', color(4), 'EdgeColor', 'red', 'LineWidth', 2);
                
                % Add blockage text
                midPoint = (road.startPoint + road.endPoint) / 2;
                text(obj.mainAxes, midPoint(1), midPoint(2)+5, ...
                    ['BLOCKED: ' obj.getBlockageTypeName(blockage.type)], ...
                    'Color', 'red', 'FontWeight', 'bold', 'HorizontalAlignment', 'center');
            end
        end
        
        function updateVisualization(obj)
            % Update visualization during simulation
            if isempty(obj.simulator)
                return;
            end
            
            % Clear previous vehicles
            delete(findobj(obj.mainAxes, 'Tag', 'vehicle'));
            
            % Draw vehicles
            for i = 1:length(obj.simulator.vehicles)
                vehicle = obj.simulator.vehicles(i);
                if vehicle.isActive
                    vehicle.draw(obj.mainAxes);
                    
                    % Tag for easy deletion
                    h = findobj(obj.mainAxes, 'Type', 'patch');
                    if ~isempty(h)
                        h(1).Tag = 'vehicle';
                    end
                end
            end
            
            % Update statistics
            obj.updateStatistics();
            
            % Update traffic signals
            obj.updateTrafficSignals();
            
            drawnow limitrate;
        end
        
        function updateStatistics(obj)
            % Update statistics display
            if isempty(obj.simulator)
                return;
            end
            
            stats = obj.simulator.getSimulationStats();
            
            % Update time
            hours = floor(stats.simulationTime / 3600);
            minutes = floor(mod(stats.simulationTime, 3600) / 60);
            seconds = floor(mod(stats.simulationTime, 60));
            obj.timeText.Text = sprintf('%02d:%02d:%02d', hours, minutes, seconds);
            
            % Update vehicle count
            obj.vehicleCountText.Text = num2str(stats.totalVehicles);
            
            % Update congestion
            obj.congestionBar.Value = stats.congestionLevel;
            
            % Update average speed
            avgSpeedLabel = findobj(obj.figure, 'Tag', 'avgSpeed');
            if ~isempty(avgSpeedLabel)
                avgSpeedLabel.Text = sprintf('%.1f km/h', stats.averageSpeed);
            end
            
            % Update blockage count
            blockageLabel = findobj(obj.figure, 'Tag', 'blockageCount');
            if ~isempty(blockageLabel)
                blockageLabel.Text = num2str(stats.activeBlockages);
            end
        end
        
        function updateTrafficSignals(obj)
            % Update traffic signal displays
            % Implementation for updating signal colors
        end
        
        function startSimulation(obj)
            % Start the simulation
            obj.startButton.Enable = 'off';
            obj.pauseButton.Enable = 'on';
            obj.stopButton.Enable = 'on';
            
            % Run simulation
            obj.simulator.isRunning = true;
            
            while obj.simulator.isRunning
                obj.simulator.step();
                obj.updateVisualization();
                pause(obj.simulator.timeStep / obj.speedSlider.Value);
                
                % Check if stop was pressed
                if ~isvalid(obj.figure)
                    break;
                end
            end
        end
        
        function pauseSimulation(obj)
            % Pause the simulation
            obj.simulator.isRunning = false;
            obj.startButton.Enable = 'on';
            obj.pauseButton.Enable = 'off';
        end
        
        function stopSimulation(obj)
            % Stop the simulation
            obj.simulator.stop();
            obj.startButton.Enable = 'on';
            obj.pauseButton.Enable = 'off';
            obj.stopButton.Enable = 'off';
            
            % Reset visualization
            obj.drawRoadNetwork();
        end
        
        function onSpeedChanged(obj)
            % Handle speed slider change
            % Speed is applied in the simulation loop
        end
        
        function onScenarioChanged(obj)
            % Handle scenario change
            scenario = obj.scenarioDropdown.Value;
            
            switch scenario
                case 'Mumbai Traffic'
                    obj.loadMumbaiScenario();
                case 'Delhi NCR'
                    obj.loadDelhiScenario();
                case 'Bangalore IT Corridor'
                    obj.loadBangaloreScenario();
                case 'Custom OSM'
                    obj.loadOSMData();
                otherwise
                    obj.simulator.createDefaultScenario();
            end
            
            obj.drawRoadNetwork();
        end
        
        function onBlockageTypeSelected(obj)
            % Handle blockage type selection
            blockageType = obj.blockageDropdown.Value;
            
            if ~strcmp(blockageType, 'Select Blockage Type')
                obj.currentBlockageType = obj.getBlockageTypeCode(blockageType);
            end
        end
        
        function enableBlockingMode(obj)
            % Enable road blocking mode
            obj.isBlockingMode = true;
            obj.figure.Pointer = 'crosshair';
            
            % Show instruction
            msgbox('Click on a road segment to add blockage', 'Road Blocking Mode', 'help');
        end
        
        function onAxesClick(obj, evt)
            % Handle click on axes
            if ~obj.isBlockingMode
                return;
            end
            
            % Get click position
            clickPoint = evt.IntersectionPoint(1:2);
            
            % Find nearest road segment
            roadSegment = obj.simulator.roadNetwork.getRoadSegmentAt(clickPoint);
            
            if ~isempty(roadSegment)
                % Add blockage
                duration = 300; % 5 minutes default
                obj.simulator.addBlockage(roadSegment.id, obj.currentBlockageType, duration);
                
                % Update visualization
                obj.drawBlockages();
                
                % Show confirmation
                msgbox(sprintf('Blockage added to road %s', roadSegment.id), ...
                    'Blockage Added', 'help');
            end
            
            % Disable blocking mode
            obj.isBlockingMode = false;
            obj.figure.Pointer = 'arrow';
        end
        
        function clearAllBlockages(obj)
            % Clear all road blockages
            if ~isempty(obj.simulator) && obj.simulator.blockages.Count > 0
                keys = obj.simulator.blockages.keys;
                for i = 1:length(keys)
                    obj.simulator.removeBlockage(keys{i});
                end
                
                obj.drawRoadNetwork();
                msgbox('All blockages cleared', 'Success', 'help');
            end
        end
        
        function typeCode = getBlockageTypeCode(obj, typeName)
            % Convert blockage type name to code
            switch typeName
                case 'Water Logging'
                    typeCode = 1;
                case 'Construction'
                    typeCode = 2;
                case 'Festival/Procession'
                    typeCode = 3;
                case 'Accident'
                    typeCode = 4;
                case 'VIP Movement'
                    typeCode = 5;
                case 'Protest/Rally'
                    typeCode = 6;
                case 'Market Day'
                    typeCode = 7;
                otherwise
                    typeCode = 1;
            end
        end
        
        function typeName = getBlockageTypeName(obj, typeCode)
            % Convert blockage type code to name
            names = {'Water Logging', 'Construction', 'Festival', 'Accident', ...
                    'VIP Movement', 'Protest', 'Market Day'};
            if typeCode >= 1 && typeCode <= length(names)
                typeName = names{typeCode};
            else
                typeName = 'Unknown';
            end
        end
        
        function loadMumbaiScenario(obj)
            % Load Mumbai-specific traffic scenario
            % This would load a Mumbai-specific road network
            msgbox('Loading Mumbai traffic scenario...', 'Loading', 'help');
        end
        
        function loadDelhiScenario(obj)
            % Load Delhi-specific traffic scenario
            msgbox('Loading Delhi NCR traffic scenario...', 'Loading', 'help');
        end
        
        function loadBangaloreScenario(obj)
            % Load Bangalore-specific traffic scenario
            msgbox('Loading Bangalore IT Corridor scenario...', 'Loading', 'help');
        end
        
        function loadOSMData(obj)
            % Load OpenStreetMap data
            [file, path] = uigetfile('*.osm', 'Select OpenStreetMap file');
            if file ~= 0
                osmFile = fullfile(path, file);
                msgbox(['Loading OSM data from: ' osmFile], 'Loading', 'help');
                % Implementation for OSM loading would go here
            end
        end
        
        function setupCallbacks(obj)
            % Set up additional callbacks
            % Already set up in individual component creation
        end
        
        function onClose(obj)
            % Handle figure close
            if ~isempty(obj.simulator)
                obj.simulator.stop();
            end
            delete(obj.figure);
        end
        
        function createSimpleSetup(obj)
            % Create a simple default setup if full initialization fails
            fprintf('Creating simplified simulation setup...\n');
            
            % Draw a simple road network for demonstration
            cla(obj.mainAxes);
            hold(obj.mainAxes, 'on');
            
            % Draw simple crossroads
            rectangle(obj.mainAxes, 'Position', [-100, -10, 200, 20], ...
                'FaceColor', [0.3, 0.3, 0.3], 'EdgeColor', 'none');
            rectangle(obj.mainAxes, 'Position', [-10, -100, 20, 200], ...
                'FaceColor', [0.3, 0.3, 0.3], 'EdgeColor', 'none');
            
            % Draw center junction
            rectangle(obj.mainAxes, 'Position', [-15, -15, 30, 30], ...
                'Curvature', [0.5, 0.5], 'FaceColor', [0.4, 0.4, 0.4], ...
                'EdgeColor', 'yellow', 'LineWidth', 2);
            
            title(obj.mainAxes, 'Indian Traffic Simulation - Simplified View');
        end
    end
end
