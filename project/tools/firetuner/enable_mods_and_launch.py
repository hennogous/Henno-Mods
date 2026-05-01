"""Enable mods via Modding API then launch game"""
import socket, struct, time, sys

def cmd(state, lua):
    payload = f'CMD:{state}:{lua}'.encode() + b'\x00'
    s.sendall(struct.pack('<II', len(payload), 1) + payload)
    time.sleep(0.5)

def drain():
    s.settimeout(0.5)
    try:
        while True: s.recv(4096)
    except: pass

def recv(wait=3):
    time.sleep(wait)
    msgs = []
    s.settimeout(3)
    try:
        while True:
            data = s.recv(4096)
            clean = data.decode('utf-8', errors='replace').strip('\x00').lstrip('O\n').strip()
            if clean and 'L0Main' not in clean:
                msgs.append(clean)
    except: pass
    return msgs

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
s.connect(('127.0.0.1', 4318))
drain()

# First, list installed mods to find their handles
print("Listing installed mods...")
cmd(0, '''
local mods = Modding.GetInstalledMods()
print("Total mods: " .. #mods)
for i, mod in ipairs(mods) do
    local info = Modding.GetModInfo(mod.Handle)
    local enabled = Modding.IsModEnabled(mod.Handle)
    print(i .. ": [" .. tostring(enabled) .. "] " .. tostring(info and info.Name or mod.Handle))
end
''')
time.sleep(5)
for m in recv(3):
    if 'PROCESSOR' not in m:
        print(f'  {m}')

s.close()
print("Done - check mod list above")
