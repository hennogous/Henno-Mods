"""Load an existing autosave"""
import socket, struct, time

def send_cmd(sock, lua, state=0):
    payload = f'CMD:{state}:{lua}'.encode() + b'\x00'
    header = struct.pack('<II', len(payload), 1)
    sock.sendall(header + payload)

def recv_all(sock, timeout=3):
    msgs = []
    while True:
        sock.settimeout(timeout)
        try:
            hdr = sock.recv(8)
            if len(hdr) < 8: break
            length, sender = struct.unpack('<II', hdr)
            data = b''
            while len(data) < length:
                chunk = sock.recv(length - len(data))
                if not chunk: break
                data += chunk
            clean = data.decode('utf-8', errors='replace').rstrip('\x00').lstrip('O\n').strip()
            if clean:
                msgs.append(clean)
        except socket.timeout:
            break
    return msgs

def run(sock, lua, state=0, wait=2):
    recv_all(sock, timeout=0.5)
    send_cmd(sock, lua, state)
    time.sleep(wait)
    results = recv_all(sock, timeout=2)
    for r in results:
        print(f'  {r}')
    return results

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
s.connect(('127.0.0.1', 4318))
time.sleep(1)
recv_all(s, timeout=1)

# Check current state
print("--- Current state ---")
run(s, '''
print("InSession=" .. tostring(Network.IsInSession()))
print("GameStarted=" .. tostring(Network.IsInGameStartedState()))
''')

# Load the autosave
print("\n--- Loading save ---")
run(s, '''
-- SERVER_TYPE_NONE = -1
print("Leaving any current game...")
Network.LeaveGame()
''', wait=3)

run(s, '''
print("Loading AutoSave_0151...")
Network.LoadGame("AutoSave_0151", -1)
print("LoadGame called!")
''', wait=5)

# Wait for load
print("\nWaiting for game to load...")
time.sleep(45)

# Reconnect
s.close()
time.sleep(5)
for attempt in range(30):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect(('127.0.0.1', 4318))
        print(f"Reconnected! (attempt {attempt+1})")
        break
    except:
        s.close()
        s = None
        time.sleep(3)

if not s:
    print("Could not reconnect")
    exit(1)

time.sleep(5)
recv_all(s, timeout=2)

# Check GameCore
print("\n--- Game state ---")
run(s, '''
if Game then
    print("TURN=" .. Game.GetCurrentGameTurn())
    for i = 0, 5 do
        local p = Players[i]
        if p and p:IsAlive() then
            print("P" .. i .. ": " .. PlayerConfigurations[i]:GetCivilizationTypeName() .. " " .. p:GetCities():GetCount() .. " cities")
        end
    end
else
    print("NO_GAME")
end
''', state=3, wait=3)

s.close()
print("\nDone!")
