"""Probe Community Extension capabilities in a live game"""
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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 4318))
print('Connected!')

# Drain
time.sleep(0.5)
recv_all(s, timeout=1)

# 1. Check all CE globals
print('\n--- CE Globals ---')
send_cmd(s, '''
local globals = {"Mem", "ObjMem", "RegisterCallEvent", "RegisterProcessor", 
                 "CityTradeManager", "CultureManager", "EmergencyManager",
                 "EconomicManager", "GovernorManager", "AIEspionageManager",
                 "NationalParks", "UnitManager", "OutcomeTypes", "FIELD_INT", "FIELD_SHORT"}
for _, name in ipairs(globals) do
    local val = _G[name]
    print("  " .. name .. " = " .. type(val) .. " (" .. tostring(val ~= nil) .. ")")
end
''')
time.sleep(2)
for msg in recv_all(s, timeout=2):
    print(msg)

# 2. Read a plot's appeal via ObjMem
print('\n--- Plot Appeal Test ---')
send_cmd(s, '''
local plot = Map.GetPlot(10, 10)
if plot then
    local appeal = ObjMem(plot, 0x4a, FIELD_SHORT)
    local baseAppeal = plot:GetAppeal()
    print("Plot(10,10): ObjMem appeal=" .. tostring(appeal) .. " API appeal=" .. tostring(baseAppeal))
else
    print("Plot(10,10) is nil")
end
''')
time.sleep(2)
for msg in recv_all(s, timeout=2):
    print(msg)

# 3. Check if RegisterProcessor works
print('\n--- RegisterProcessor Test ---')
send_cmd(s, '''
RegisterProcessor("DistrictTargetChooser", function(info)
    print("PROCESSOR FIRED: player=" .. tostring(info.PlayerId))
    return false
end)
print("Processor registered OK")
''')
time.sleep(2)
for msg in recv_all(s, timeout=2):
    print(msg)

# 4. List available players
print('\n--- Players ---')
send_cmd(s, '''
for i = 0, 20 do
    local player = Players[i]
    if player and player:IsAlive() then
        local cities = player:GetCities()
        local numCities = cities:GetCount()
        local civType = PlayerConfigurations[i]:GetCivilizationTypeName()
        print("Player " .. i .. ": " .. tostring(civType) .. " (" .. numCities .. " cities)")
    end
end
''')
time.sleep(2)
for msg in recv_all(s, timeout=2):
    print(msg)

s.close()
print('\nDone!')
