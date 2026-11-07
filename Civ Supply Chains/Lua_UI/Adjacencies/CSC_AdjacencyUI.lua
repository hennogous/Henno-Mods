-- Native reads that are only available to the UI context.
-- This context does not set plot properties or mutate any gameplay object.
ExposedMembers.CSC_Adjacency = ExposedMembers.CSC_Adjacency or {};
ExposedMembers.CSC_Adjacency.GetUnitLevel = function(playerID,unitID)
    local player = Players[playerID];
    local unit = player and player:GetUnits():FindID(unitID);
    return unit and unit:GetExperience():GetLevel() or 0;
end;

ExposedMembers.CSC_Adjacency.IsSinglePlayer = function()
    return type(GameConfiguration.IsAnyMultiplayer) == 'function'
        and type(GameConfiguration.IsHotseat) == 'function'
        and GameConfiguration.IsAnyMultiplayer() == false
        and GameConfiguration.IsHotseat() == false;
end;
