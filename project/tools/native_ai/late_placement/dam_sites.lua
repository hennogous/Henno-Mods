-- Read legal Dam footprints and the floodplain each would protect.
-- Call in PlotInfo at a verified inactive boundary.
local scope = assert(CSC_DAM_SITE_SCOPE)
local player, cityID, protected = scope[1], scope[2], scope[3]
local city = assert(CityManager.GetCity(player, cityID), 'Missing Dam host city')
local dam = assert(GameInfo.Districts.DISTRICT_DAM)
local riverForPlot = assert(RiverManager.GetRiverForFloodplain)
local floodplainPlots = assert(RiverManager.GetFloodplainPlots)
local protectedPlot = assert(Map.GetPlotByIndex(protected))
local targetRiver = riverForPlot(protectedPlot:GetX(), protectedPlot:GetY())

local coverage = {}
local function floodplain(river, site)
    if river < 0 then return '-' end
    if not coverage[river] then
        local plots = assert(floodplainPlots(river))
        table.sort(plots)
        coverage[river] = { plots = plots, members = {} }
        for _, index in ipairs(plots) do coverage[river].members[index] = true end
    end
    assert(coverage[river].members[site], 'Dam footprint is outside its reported floodplain')
    return table.concat(coverage[river].plots, ',')
end

local function emit(kind, plot, river)
    river = river or -1
    local index = plot:GetIndex()
    print(string.format('CSC_DAM_%s\t%d\t%d\t%d\t%d\t%d\t%s', kind, index, river,
        plot:GetOwner(), plot:GetResourceType(), plot:GetImprovementType(), floodplain(river, index)))
end

emit('PROTECTED', protectedPlot, targetRiver)
-- Dams are limited per river. A Dam on a different river in this city is
-- not an automatic rejection. Check each new footprint with the build operation.
local build = CityOperationTypes.BUILD
local parameters = { [CityOperationTypes.PARAM_DISTRICT_TYPE] = dam.Hash }
local result = CityManager.GetOperationTargets(city, build, parameters)
local plots = result and result[CityOperationResults.PLOTS] or {}
table.sort(plots)
local count = 0
for _, index in ipairs(plots) do
    local plot = assert(Map.GetPlotByIndex(index))
    parameters[CityOperationTypes.PARAM_X], parameters[CityOperationTypes.PARAM_Y] = plot:GetX(), plot:GetY()
    if plot:GetDistrictType() == -1 and CityManager.CanStartOperation(city, build, parameters, true) then
        emit('LEGAL', plot, riverForPlot(plot:GetX(), plot:GetY()))
        count = count + 1
    end
end
print('CSC_DAM_COUNT=' .. count)
print('CSC_DAM_TURN=' .. Game.GetCurrentGameTurn())
