# Events & Processors
> [!WARNING]
> RegisterProcessor suffers from potential race conditions. Every so often it could crash the game! (Though rarely)

## Processors
Event dispatch system which influences function execution.

### RegisterProcessor

#### Parameters

| Parameter | Type | Description |
| - | - | - |
| name | `string` | Name of the processor. |
| processor | `function` | Lua function to process data. |

#### Example

```lua
-- The ai will always choose to vote for the city center on the urban development congress resolution
-- Additionally, print the other inputted parameters
RegisterProcessor("DistrictTargetChooser", function (info)
    local outcomeType: string
    if info.OutcomeType == OutcomeTypes.A then
        outcomeType = "A"
    elseif info.OutcomeType == OutcomeTypes.B then
        outcomeType = "B"
    end

    print("Player Id: " .. tostring(info.PlayerId))
    print("Outcome type: " .. outcomeType)
    info.DistrictIndex = GameInfo.Districts.DISTRICT_CITY_CENTER.Index

    return true -- Return true to stop execution. Return false to pass execution to original function.
end)
```

### Available processors

| Name | Immutable Parameters | Mutable Parameters | Description |
| - | - | - | - |
| DistrictTargetChooser | `PlayerId: number`, `OutcomeType: number` | `DistrictIndex: number` | Original algorithm scores districts by the sum total of buildings that can be constructed for that district across the player's empire. |