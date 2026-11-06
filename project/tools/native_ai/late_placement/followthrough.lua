-- Read the exact protected fixture tile after the diagnostic writer freezes.
local player = Players[1]
local city = player:GetCities():FindID(65536)
local plot = assert(Map.GetPlotByIndex(1210))
local districtType = assert(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER).Index
local civic = assert(GameInfo.Civics.CIVIC_CRAFTSMANSHIP).Index
local founded, complete = false, false
if city then
    local districts = city:GetDistricts()
    for i = 0, districts:GetNumDistricts() - 1 do
        local district = districts:GetDistrictByIndex(i)
        if district and district:GetType() == districtType
            and district:GetX() == plot:GetX() and district:GetY() == plot:GetY() then
            founded, complete = true, district:IsComplete()
            break
        end
    end
end
print(string.format('CSC_LATE_FOLLOWTHROUGH={"turn":%d,"owner":%d,"cityOwner":%d,'
    .. '"district":%d,"founded":%s,"complete":%s,"craftsmanship":%s}',
    Game.GetCurrentGameTurn(), plot:GetOwner(), city and city:GetOwner() or -1,
    plot:GetDistrictType(), tostring(founded), tostring(complete),
    tostring(player:GetCulture():HasCivic(civic))))
