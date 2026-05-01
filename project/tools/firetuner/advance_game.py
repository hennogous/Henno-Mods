"""Settle a city and advance turns via FireTuner"""
import socket, struct, time

def send_cmd(sock, lua, state=3):
    payload = f'CMD:{state}:{lua}'.encode() + b'\x00'
    header = struct.pack('<II', len(payload), 1)
    sock.sendall(header + payload)

def recv_all(sock, timeout=3):
    msgs = []
    while True:
        sock.settimeout(timeout)
        try:
            hdr = sock.recv(8)
            if len(hdr) < 8:
                break
            length, sender = struct.unpack('<II', hdr)
            data = b''
            while len(data) < length:
                chunk = sock.recv(length - len(data))
                if not chunk:
                    break
                data += chunk
            clean = data.decode('utf-8', errors='replace').rstrip('\x00').lstrip('O\n').strip()
            if clean:
                msgs.append(clean)
        except socket.timeout:
            break
    return msgs

def run(sock, lua, state=3, wait=2):
    recv_all(sock, timeout=0.5)  # drain
    send_cmd(sock, lua, state)
    time.sleep(wait)
    results = recv_all(sock, timeout=2)
    for r in results:
        print(f'  {r}')
    return results

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 4318))
print('Connected!')
time.sleep(0.5)
recv_all(s, timeout=1)

# 1. Check current game state
print('\n--- Game State ---')
run(s, '''
local turn = Game.GetCurrentGameTurn()
local player = Players[0]
local cities = player:GetCities():GetCount()
local units = player:GetUnits():GetCount()
print("Turn: " .. turn .. " | Cities: " .. cities .. " | Units: " .. units)

-- Find our settler
local pUnits = player:GetUnits()
for i, unit in pUnits:Members() do
    local unitType = GameInfo.Units[unit:GetUnitType()].UnitType
    local x, y = unit:GetX(), unit:GetY()
    print("  Unit: " .. unitType .. " at (" .. x .. "," .. y .. ")")
end
''')

# 2. Find the settler and settle
print('\n--- Settling City ---')
run(s, '''
local player = Players[0]
local pUnits = player:GetUnits()
local settler = nil
for i, unit in pUnits:Members() do
    if GameInfo.Units[unit:GetUnitType()].UnitType == "UNIT_SETTLER" then
        settler = unit
        break
    end
end

if settler then
    local x, y = settler:GetX(), settler:GetY()
    print("Found settler at (" .. x .. "," .. y .. "), settling...")
    UnitManager.RequestOperation(settler, UnitOperationTypes.FOUND_CITY)
    print("Settle command sent")
else
    print("No settler found")
end
''', wait=3)

# 3. Check if city was founded
print('\n--- Post-Settle Check ---')
run(s, '''
local player = Players[0]
local cities = player:GetCities()
print("Cities: " .. cities:GetCount())
for i, city in cities:Members() do
    print("  City: " .. Locale.Lookup(city:GetName()) .. " at (" .. city:GetX() .. "," .. city:GetY() .. ")")
    print("    Pop: " .. city:GetPopulation() .. " | Districts: " .. city:GetDistricts():GetCount())
end
''')

# 4. Try to advance a few turns
print('\n--- Advancing Turns ---')
for turn_num in range(5):
    run(s, '''
local player = Players[0]
-- Auto-end turn: skip unit commands, just advance
local pUnits = player:GetUnits()
for i, unit in pUnits:Members() do
    -- Skip unit if it has moves remaining
    UnitManager.RequestCommand(unit, UnitCommandTypes.SKIP)
end
-- Try UI context to click next turn
''', wait=1)
    
    # Use UI context to press "next turn"
    run(s, '''
UI.RequestAction(ActionTypes.ACTION_ENDTURN)
''', state=0, wait=3)
    
    results = run(s, '''
print("Turn: " .. Game.GetCurrentGameTurn())
''')
    print(f'  (advance {turn_num + 1}/5)')

# 5. Final state
print('\n--- Final State ---')
run(s, '''
local turn = Game.GetCurrentGameTurn()
local player = Players[0]
local cities = player:GetCities()
print("Turn: " .. turn .. " | Cities: " .. cities:GetCount())
for i, city in cities:Members() do
    local name = Locale.Lookup(city:GetName())
    local pop = city:GetPopulation()
    print("  " .. name .. ": pop " .. pop)
end
''')

s.close()
print('\nDone!')
