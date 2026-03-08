classdef EventManager < handle
    % EventManager - Manages special events, festivals, and their impact on traffic
    
    properties
        activeEvents
        scheduledEvents
        eventImpacts
    end
    
    methods
        function obj = EventManager()
            % Constructor
            obj.activeEvents = [];
            obj.scheduledEvents = [];
            obj.eventImpacts = containers.Map();
            
            % Define impact of various events
            obj.defineEventImpacts();
        end
        
        function defineEventImpacts(obj)
            % Define how different events impact traffic
            
            % Festivals
            obj.eventImpacts('Diwali') = struct(...
                'trafficMultiplier', 1.5, ...
                'marketAreas', true, ...
                'duration', 3600 * 5 ... % 5 hours
            );
            
            obj.eventImpacts('Holi') = struct(...
                'trafficMultiplier', 0.7, ... % Less traffic
                'randomBlockages', true, ...
                'duration', 3600 * 4 ...
            );
            
            obj.eventImpacts('Ganesh Chaturthi') = struct(...
                'trafficMultiplier', 2.0, ...
                'processionRoutes', true, ...
                'duration', 3600 * 6 ...
            );
            
            % Other events
            obj.eventImpacts('Cricket Match') = struct(...
                'trafficMultiplier', 1.3, ...
                'nearStadium', true, ...
                'duration', 3600 * 4 ...
            );
            
            obj.eventImpacts('VIP Visit') = struct(...
                'trafficMultiplier', 0.5, ...
                'routeCleared', true, ...
                'duration', 3600 * 2 ...
            );
        end
        
        function scheduleEvent(obj, eventName, startTime, location)
            % Schedule a special event
            event = struct(...
                'name', eventName, ...
                'startTime', startTime, ...
                'location', location, ...
                'impact', obj.eventImpacts(eventName) ...
            );
            
            obj.scheduledEvents = [obj.scheduledEvents, event];
        end
        
        function updateEvents(obj, currentTime)
            % Update active events based on current time
            
            % Check scheduled events
            for i = length(obj.scheduledEvents):-1:1
                if currentTime >= obj.scheduledEvents(i).startTime
                    % Activate event
                    obj.activeEvents = [obj.activeEvents, obj.scheduledEvents(i)];
                    obj.scheduledEvents(i) = [];
                end
            end
            
            % Remove expired events
            for i = length(obj.activeEvents):-1:1
                event = obj.activeEvents(i);
                if currentTime > event.startTime + event.impact.duration
                    obj.activeEvents(i) = [];
                end
            end
        end
        
        function impact = getCurrentImpact(obj)
            % Get cumulative impact of all active events
            impact = struct(...
                'trafficMultiplier', 1.0, ...
                'specialConditions', {} ...
            );
            
            for i = 1:length(obj.activeEvents)
                event = obj.activeEvents(i);
                impact.trafficMultiplier = impact.trafficMultiplier * ...
                    event.impact.trafficMultiplier;
                
                % Add special conditions
                fields = fieldnames(event.impact);
                for j = 1:length(fields)
                    if ~strcmp(fields{j}, 'trafficMultiplier') && ...
                       ~strcmp(fields{j}, 'duration')
                        impact.specialConditions{end+1} = fields{j};
                    end
                end
            end
        end
    end
end
