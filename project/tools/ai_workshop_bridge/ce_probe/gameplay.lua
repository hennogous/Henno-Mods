-- Read-only Community Extension capability/timing probe.
-- This never registers a native callback, writes memory, or changes game state.
-- CE cannot validate arbitrary memory spans: the exact-build guard and bounded
-- current-build paths reduce risk but are not a memory-safety guarantee.

include("CSC_CE_Probe_Target")

local TARGET = CSC_CE_PROBE_TARGET
local MAX_SNAPSHOTS, MAX_CITIES, MAX_ROWS = 96, 8, 3
local MAX_PLAYER, MAX_CITY_NODES, MAX_DISTRICT_INDEX = 63, 256, 511
local snapshots, disabled = 0, false
local quarterTypes = {"DISTRICT_CSC_BAKERS_QUARTER", "DISTRICT_CSC_TAILORS_QUARTER"}

local function emit(kind, fields)
  local keys = {}
  for key in pairs(fields or {}) do keys[#keys + 1] = key end
  table.sort(keys)
  local parts = {"[CSC_CE_PROBE]", "kind=" .. kind}
  for _, key in ipairs(keys) do
    local value = tostring(fields[key]):gsub("[%c%s|]", "_")
    parts[#parts + 1] = key .. "=" .. value
  end
  print(table.concat(parts, " "))
end

local function integer(value, low, high, label)
  value=tonumber(value)
  if value == nil or value ~= math.floor(value) or value < low or value > high then
    error("invalid_" .. label)
  end
  return value
end

local function pointerNumber(value, label)
  -- All supported Windows user pointers fit exactly in a Lua number. Null
  -- lightuserdata is truthy, so test the numeric representation before following.
  if value == 0 then return nil end
  integer(value, 65536, 140737488355320, label)
  if value % 8 ~= 0 then error("unaligned_" .. label) end
  return value
end

local function globalPointer(offset, label)
  local number = pointerNumber(Mem(offset, FIELD_UNSIGNED_LONG_LONG), label)
  if not number then return nil, nil end
  return Mem(offset, FIELD_POINTER), number
end

local function objectPointer(object, offset, label)
  local number = pointerNumber(ObjMem(object, offset, FIELD_UNSIGNED_LONG_LONG), label)
  if not number then return nil, nil end
  return ObjMem(object, offset, FIELD_POINTER), number
end

local function headerCheck()
  if type(Mem) ~= "function" or type(ObjMem) ~= "function" then error("CE_memory_API_missing") end
  -- HavokScript gameplay contexts do not expose the standard Lua _G alias.
  local fieldTypes={FIELD_SHORT=tonumber(FIELD_SHORT),FIELD_INT=tonumber(FIELD_INT),
                    FIELD_UNSIGNED_INT=tonumber(FIELD_UNSIGNED_INT),FIELD_UNSIGNED_LONG_LONG=tonumber(FIELD_UNSIGNED_LONG_LONG),
                    FIELD_POINTER=tonumber(FIELD_POINTER),FIELD_BYTE=tonumber(FIELD_BYTE)}
  local required={'FIELD_SHORT','FIELD_INT','FIELD_UNSIGNED_INT','FIELD_UNSIGNED_LONG_LONG','FIELD_POINTER','FIELD_BYTE'}
  for _,key in ipairs(required) do
    if fieldTypes[key]==nil then error("CE_field_type_missing_" .. key) end
  end
  -- Use the established signed-short API and normalize its result. Do not
  -- guess enum numbers or require every alias documented by a newer CE source.
  local function u16(offset) return Mem(offset,FIELD_SHORT)%65536 end
  if u16(0) ~= 0x5a4d then error("MZ_mismatch") end
  local nt = integer(Mem(0x3c, FIELD_UNSIGNED_INT), 64, 8192, "PE_header_offset")
  if Mem(nt, FIELD_UNSIGNED_INT) ~= 0x4550 then error("PE_signature_mismatch") end
  if u16(nt + 4) ~= 0x8664 then error("machine_mismatch") end
  if Mem(nt + 8, FIELD_UNSIGNED_INT) ~= TARGET.timestamp then error("timestamp_mismatch") end
  if u16(nt + 24) ~= 0x20b then error("optional_header_mismatch") end
  if Mem(nt + 24 + 56, FIELD_UNSIGNED_INT) ~= TARGET.image_size then error("image_size_mismatch") end
  for _, fingerprint in ipairs(TARGET.fingerprints) do
    for index, byte in ipairs(fingerprint.bytes) do
      if Mem(fingerprint.rva + index - 1, FIELD_BYTE) ~= byte then
        error("function_fingerprint_mismatch_" .. fingerprint.name)
      end
    end
  end
  -- The SHA is a build-time qualification; CE does not calculate an entire-file
  -- hash here. The shared controller must independently verify the loaded file.
  return true
end

local function expectedCities(playerID)
  local result, count = {}, 0
  local player = Players[playerID]
  if not player then return result, count end
  local cities = player:GetCities()
  if not cities then return result, count end
  for _, city in cities:Members() do
    local cityID = tonumber(city:GetID())
    result[cityID] = {x=tonumber(city:GetX()), y=tonumber(city:GetY())}
    count = count + 1
    if count > MAX_CITY_NODES then error("native_city_limit") end
  end
  return result, count
end

local function scoreRows(build, fields, width, height)
  local rowCount = integer(ObjMem(build, 0x4d8, FIELD_UNSIGNED_INT), 0, 37, "row_count")
  fields.rows = rowCount
  if rowCount == 0 then return end
  local rows = objectPointer(build, 0x4c8, "plot_rows")
  if not rows then error("missing_plot_rows") end
  local sampled = 0
  for rowIndex = 0, rowCount - 1 do
    local offset = rowIndex * 0x78
    local x = integer(ObjMem(rows, offset + 8, FIELD_INT), -9999, width - 1, "row_x")
    local y = integer(ObjMem(rows, offset + 12, FIELD_INT), -9999, height - 1, "row_y")
    local canDistrict = ObjMem(rows, offset + 0x55, FIELD_BYTE)
    local owned = ObjMem(rows, offset + 0x5a, FIELD_BYTE)
    local frontier = ObjMem(rows, offset + 0x57, FIELD_BYTE)
    if canDistrict ~= 0 and (owned ~= 0 or frontier ~= 0) and x >= 0 and y >= 0 then
      local scores = objectPointer(rows, offset + 0x20, "district_scores")
      if not scores then error("missing_district_scores") end
      sampled = sampled + 1
      for _, districtType in ipairs(quarterTypes) do
        local definition = GameInfo.Districts[districtType]
        if definition then
          local districtIndex = integer(definition.Index, 0, MAX_DISTRICT_INDEX, "district_index")
          local score = ObjMem(scores, districtIndex * 4, FIELD_INT)
          emit("score", {snapshot=fields.snapshot, event=fields.event, turn=fields.turn,
                         player=fields.player, city=fields.city, row=rowIndex, x=x, y=y,
                         district=districtType, index=districtIndex, raw_q8=score,
                         owned=owned, frontier=frontier})
        end
      end
      if sampled >= MAX_ROWS then break end
    end
  end
  fields.sampled_rows = sampled
end

local function inspectPlayer(array, playerID, event, turn, width, height)
  local expected, expectedCount = expectedCities(playerID)
  if expectedCount == 0 then return end
  local player, playerNumber = objectPointer(array, playerID * 8, "player")
  if not player then error("missing_live_player") end
  -- GetPlayer63d080 -> Player+650 CityManager, confirmed in InitializeAiSystems.
  -- Players[id].__instance is a Lua reference wrapper and is NOT used here.
  local manager = objectPointer(player, 0x650, "city_manager")
  if not manager then error("missing_city_manager") end
  if ObjMem(manager, 0, FIELD_UNSIGNED_LONG_LONG) ~= playerNumber then error("manager_owner_mismatch") end
  local node, nodeNumber = objectPointer(manager, 0x98, "city_list_head")
  local seen, visited, sampledCities = {}, 0, 0
  while node do
    if seen[nodeNumber] then error("city_list_cycle") end
    seen[nodeNumber] = true
    visited = visited + 1
    if visited > expectedCount or visited > MAX_CITY_NODES then error("city_list_limit") end
    local build = objectPointer(node, 0, "city_build")
    if not build then error("missing_city_build") end
    local city = objectPointer(build, 0x90, "city")
    if not city then error("missing_city_instance") end
    local owner = tonumber(ObjMem(city, 0xd8, FIELD_INT))
    local cityID = tonumber(ObjMem(city, 0xa8, FIELD_INT))
    local x, y = tonumber(ObjMem(city, 0xc0, FIELD_INT)), tonumber(ObjMem(city, 0xc4, FIELD_INT))
    local known = expected[cityID]
    if owner ~= playerID or not known or known.x ~= x or known.y ~= y then error("city_identity_mismatch") end
    if sampledCities < MAX_CITIES then
      sampledCities = sampledCities + 1
      local fields = {snapshot=snapshots, event=event, turn=turn, player=playerID,
                      city=cityID, x=x, y=y, job_done=ObjMem(build, 0x4c0, FIELD_BYTE),
                      offturn_done=ObjMem(build, 0x1b0, FIELD_BYTE), expected_cities=expectedCount}
      -- These flags are observations, not a lock or exclusive-writer proof.
      if fields.job_done == 1 and fields.offturn_done == 1 then
        scoreRows(build, fields, width, height)
      else
        fields.cache_skipped = "analysis_not_done"
      end
      emit("city", fields)
    end
    node, nodeNumber = objectPointer(node, 0x10, "city_list_next")
  end
  if visited ~= expectedCount then error("city_count_mismatch") end
end

local function capture(event, playerID)
  if disabled or snapshots >= MAX_SNAPSHOTS then return end
  snapshots = snapshots + 1
  local ok, message = pcall(function()
    headerCheck()
    local turn = Game.GetCurrentGameTurn()
    local width, height = Map.GetGridSize()
    integer(width, 1, 1024, "map_width")
    integer(height, 1, 1024, "map_height")
    emit("boundary", {snapshot=snapshots, event=event, turn=turn, argument_player=playerID or "none"})
    local game = globalPointer(0xb8aa68, "game")
    if not game then emit("skip", {event=event, reason="game_missing"}); return end
    local playerManager = objectPointer(game, 0x240, "player_manager")
    if not playerManager then error("missing_player_manager") end
    local array = objectPointer(playerManager, 0x20, "player_array")
    if not array then error("missing_player_array") end
    if type(playerID) == "number" then
      integer(playerID, 0, MAX_PLAYER, "event_player")
      inspectPlayer(array, playerID, event, turn, width, height)
    else
      for _, id in ipairs(PlayerManager.GetAliveMajorIDs()) do
        integer(id, 0, MAX_PLAYER, "major_player")
        inspectPlayer(array, id, event, turn, width, height)
      end
    end
  end)
  if not ok then
    disabled = true
    emit("disabled", {snapshot=snapshots, event=event, reason=message})
  elseif snapshots == MAX_SNAPSHOTS then
    emit("complete", {reason="snapshot_budget", snapshots=snapshots})
  end
end

local function register(container, key, label, hasPlayerArgument)
  local event = container and container[key]
  if event and type(event.Add) == "function" then
    event.Add(function(playerID) capture(label, hasPlayerArgument and playerID or nil) end)
    emit("registered", {event=label})
  else
    emit("unavailable", {event=label})
  end
end

emit("capabilities", {mem=type(Mem), objmem=type(ObjMem),
                      call_event=type(RegisterCallEvent), mode="read_only",
                      field_short=FIELD_SHORT,field_int=FIELD_INT,field_pointer=FIELD_POINTER,
                      type_short=type(FIELD_SHORT),type_int=type(FIELD_INT),type_pointer=type(FIELD_POINTER),
                      expected_sha256=TARGET.sha256, snapshot_budget=MAX_SNAPSHOTS})
register(GameEvents, "OnGameTurnStarted", "GameEvents.OnGameTurnStarted", false)
register(GameEvents, "PlayerTurnStarted", "GameEvents.PlayerTurnStarted", true)
register(Events, "PlayerTurnActivated", "Events.PlayerTurnActivated", true)
capture("module_loaded")
