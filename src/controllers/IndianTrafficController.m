classdef IndianTrafficController < handle
    % IndianTrafficController - Traffic signal controller with Indian patterns
    
    properties
        junction        % Junction being controlled
        signalStates    % Current signal states for each direction
        timingPattern   % Signal timing pattern
        currentPhase    % Current signal phase
        phaseTimer      % Timer for current phase
        cycleTime       % Total cycle time
        isManual        % Manual override mode
    end
    
    properties (Constant)
        % Signal states
        GREEN = 1;
        YELLOW = 2;
        RED = 3;
        
        % Timing patterns (seconds)
        REGULAR_PATTERN = struct(...
            'green', 45, ...
            'yellow', 3, ...
            'red', 60 ...
        );
        
        IRREGULAR_PATTERN = struct(...
            'green', [30, 60], ...  % Random between min and max
            'yellow', [2, 5], ...
            'red', [45, 90] ...
        );
    end
    
    methods
        function obj = IndianTrafficController(junction)
            % Constructor
            obj.junction = junction;
            obj.signalStates = containers.Map();
            obj.currentPhase = 1;
            obj.phaseTimer = 0;
            obj.isManual = false;
            
            % Initialize signal states (4-way junction)
            directions = {'north', 'south', 'east', 'west'};
            for i = 1:length(directions)
                obj.signalStates(directions{i}) = obj.RED;
            end
            
            % Set default timing pattern
            obj.setTimingPattern('regular');
        end
        
        function setTimingPattern(obj, pattern)
            % Set signal timing pattern
            switch pattern
                case 'regular'
                    obj.timingPattern = obj.REGULAR_PATTERN;
                    obj.cycleTime = obj.REGULAR_PATTERN.green + ...
                                   obj.REGULAR_PATTERN.yellow + ...
                                   obj.REGULAR_PATTERN.red;
                    
                case 'irregular'
                    % Indian traffic often has irregular patterns
                    obj.timingPattern = obj.IRREGULAR_PATTERN;
                    % Calculate average cycle time
                    obj.cycleTime = mean(obj.IRREGULAR_PATTERN.green) + ...
                                   mean(obj.IRREGULAR_PATTERN.yellow) + ...
                                   mean(obj.IRREGULAR_PATTERN.red);
                    
                case 'peakhour'
                    % Longer green times for main roads during peak hours
                    obj.timingPattern = struct(...
                        'green', 60, ...
                        'yellow', 3, ...
                        'red', 45 ...
                    );
                    obj.cycleTime = 108;
                    
                otherwise
                    obj.setTimingPattern('regular');
            end
        end
        
        function update(obj, simulationTime)
            % Update signal states
            if obj.isManual
                return; % Manual control, no automatic updates
            end
            
            obj.phaseTimer = obj.phaseTimer + 0.1; % Assuming 100ms timestep
            
            % Check if phase should change
            phaseTime = obj.getCurrentPhaseTime();
            
            if obj.phaseTimer >= phaseTime
                obj.nextPhase();
                obj.phaseTimer = 0;
            end
        end
        
        function phaseTime = getCurrentPhaseTime(obj)
            % Get duration for current phase
            phases = {'green', 'yellow', 'red'};
            currentPhaseName = phases{mod(obj.currentPhase-1, 3) + 1};
            
            if isstruct(obj.timingPattern)
                timing = obj.timingPattern.(currentPhaseName);
                if length(timing) == 2
                    % Random timing for irregular pattern
                    phaseTime = timing(1) + rand() * (timing(2) - timing(1));
                else
                    phaseTime = timing;
                end
            else
                phaseTime = 30; % Default
            end
        end
        
        function nextPhase(obj)
            % Move to next signal phase
            obj.currentPhase = mod(obj.currentPhase, 4) + 1;
            
            % Update signal states based on phase
            directions = {'north', 'south', 'east', 'west'};
            
            switch obj.currentPhase
                case 1 % North-South green
                    obj.signalStates('north') = obj.GREEN;
                    obj.signalStates('south') = obj.GREEN;
                    obj.signalStates('east') = obj.RED;
                    obj.signalStates('west') = obj.RED;
                    
                case 2 % North-South yellow
                    obj.signalStates('north') = obj.YELLOW;
                    obj.signalStates('south') = obj.YELLOW;
                    
                case 3 % East-West green
                    obj.signalStates('north') = obj.RED;
                    obj.signalStates('south') = obj.RED;
                    obj.signalStates('east') = obj.GREEN;
                    obj.signalStates('west') = obj.GREEN;
                    
                case 4 % East-West yellow
                    obj.signalStates('east') = obj.YELLOW;
                    obj.signalStates('west') = obj.YELLOW;
            end
        end
        
        function state = getSignalState(obj, heading)
            % Get signal state for a given heading
            
            % Determine direction from heading
            if heading >= 315 || heading < 45
                direction = 'north';
            elseif heading >= 45 && heading < 135
                direction = 'east';
            elseif heading >= 135 && heading < 225
                direction = 'south';
            else
                direction = 'west';
            end
            
            % Get state
            if obj.signalStates.isKey(direction)
                stateCode = obj.signalStates(direction);
                switch stateCode
                    case obj.GREEN
                        state = 'green';
                    case obj.YELLOW
                        state = 'yellow';
                    case obj.RED
                        state = 'red';
                    otherwise
                        state = 'red';
                end
            else
                state = 'green'; % Default to green if not found
            end
        end
        
        function setManualControl(obj, enable)
            % Enable/disable manual control
            obj.isManual = enable;
        end
        
        function setSignalManually(obj, direction, state)
            % Manually set signal state
            if obj.isManual && obj.signalStates.isKey(direction)
                obj.signalStates(direction) = state;
            end
        end
        
        function emergencyOverride(obj, direction)
            % Emergency vehicle override - all red except specified direction
            directions = {'north', 'south', 'east', 'west'};
            for i = 1:length(directions)
                if strcmp(directions{i}, direction)
                    obj.signalStates(directions{i}) = obj.GREEN;
                else
                    obj.signalStates(directions{i}) = obj.RED;
                end
            end
        end
    end
end
