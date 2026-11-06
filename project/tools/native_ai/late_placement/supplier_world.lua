-- The established Quarter's six neighbors. Scope supply to the player, since
-- the gameplay requirements permit another of its cities to own the deposit.
local target = assert(CSC_BAKERS_TARGET)
local quarter = assert(Map.GetPlotByIndex(target.plot))
local player = assert(Players[target.player])
local city = assert(player:GetCities():FindID(target.city))
local techs = player:GetTechs()
local tags = {}
for row in GameInfo.TypeTags() do
    if row.Tag == 'CLASS_CSC_BAKERS_BASE' then tags[row.Type] = 'Base' end
    if row.Tag == 'CLASS_CSC_BAKERS_SPEC' then tags[row.Type] = 'Spec' end
end

local rows = {}
for _, plot in ipairs(Map.GetAdjacentPlots(quarter:GetX(), quarter:GetY())) do
    local owner = plot:GetOwner()
    local resource = GameInfo.Resources[plot:GetResourceType()]
    local classification = resource and tags[resource.ResourceType] or ''
    local improvement = plot:GetImprovementType()
    local district = plot:GetDistrictType()
    local pillaged = plot:IsImprovementPillaged()
    local revealed = PlayersVisibility[target.player]:IsRevealed(plot:GetX(), plot:GetY())
    local intact = owner == target.player and district == -1 and revealed and classification ~= ''
    local compatible, working, developable = false, false, false
    if intact then
        for option in GameInfo.Improvement_ValidResources() do
            if option.ResourceType == resource.ResourceType then
                local definition = assert(GameInfo.Improvements[option.ImprovementType])
                compatible = true
                if improvement == definition.Index and not pillaged then working = true end
                local tech = definition.PrereqTech and GameInfo.Technologies[definition.PrereqTech]
                local legal = ImprovementBuilder.CanHaveImprovement(plot, definition.Index, target.player)
                if (not tech or techs:HasTech(tech.Index)) and legal then developable = true end
            end
        end
    end
    rows[#rows + 1] = string.format(
        '{"plot":%d,"owner":%d,"resource":"%s","district":%d,"improvement":%d,"class":"%s",'
        .. '"revealed":%s,"deposit":%s,"working":%s,"developable":%s,"pillaged":%s}',
        plot:GetIndex(), owner, resource and resource.ResourceType or '', district, improvement, classification,
        tostring(revealed), tostring(compatible), tostring(working), tostring(developable), tostring(pillaged))
end
assert(#rows == 6, 'Expected all six Quarter neighbors')

-- Emit the adjacent records separately to stay inside the console line limit.
for _, row in ipairs(rows) do print('CSC_BAKERS_SUPPLIER=' .. row) end
local width, height = Map.GetGridSize()
local count = 0
for _ in GameInfo.Districts() do count = count + 1 end
print(string.format('CSC_BAKERS_SUPPLY_WORLD={"turn":%d,"width":%d,"height":%d,"districtCount":%d,'
    .. '"cityOwner":%d,"population":%d,"quarterDistrict":%d,"campus":%d}',
    Game.GetCurrentGameTurn(), width, height, count, city:GetOwner(), city:GetPopulation(),
    quarter:GetDistrictType(), assert(GameInfo.Districts.DISTRICT_CAMPUS).Index))
