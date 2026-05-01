"""Start a new game - fixed ServerType"""
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

# SERVER_TYPE_NONE = -1 from the Civ 6 source
# Try HostGame with raw integer
print("--- Starting new game ---")
run(s, '''
print("Calling Network.HostGame(-1)...")
Network.HostGame(-1)
print("HostGame called!")
''', wait=10)

# Wait for game to set up
print("\nWaiting for game to initialize...")
time.sleep(30)

# Try to reconnect and check GameCore
s.close()
time.sleep(3)

for attempt in range(30):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect(('127.0.0.1', 4318))
        print(f"Reconnected! (attempt {attempt+1})")
        break
    except (ConnectionRefusedError, socket.timeout, OSError):
        s.close()
        s = None
        time.sleep(3)

if not s:
    print("Could not reconnect")
    exit(1)

time.sleep(3)
recv_all(s, timeout=2)

# Check if we're in a game
print("\n--- Check game state ---")
run(s, 'print("GC_TURN=" .. tostring(Game ~= nil and Game.GetCurrentGameTurn() or "NO_GAME"))', state=3, wait=3)

# Also check UI state
run(s, '''
local inGame = Network.IsInSession()
local gameStarted = Network.IsInGameStartedState()
print("InSession=" .. tostring(inGame) .. " GameStarted=" .. tostring(gameStarted))
''', state=0, wait=2)

s.close()
print("\nDone!")
