"""Test if Community Extension is loaded via FireTuner"""
import socket, struct, time

def send_cmd(sock, lua, state=0):
    payload = f'CMD:{state}:{lua}'.encode() + b'\x00'
    header = struct.pack('<II', len(payload), 1)
    sock.sendall(header + payload)

def recv_msg(sock, timeout=5):
    sock.settimeout(timeout)
    try:
        hdr = sock.recv(8)
        if len(hdr) < 8:
            return None
        length, sender = struct.unpack('<II', hdr)
        data = b''
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                break
            data += chunk
        return data.decode('utf-8', errors='replace').rstrip('\x00')
    except socket.timeout:
        return None

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 4318))
    print('Connected to FireTuner!')
    
    # Drain initial messages
    time.sleep(1)
    while True:
        msg = recv_msg(s, timeout=1)
        if msg is None:
            break
    
    # Check if CE globals exist (UI context, state=0)
    send_cmd(s, 'print("CE_MEM=" .. tostring(Mem ~= nil) .. " CE_OBJMEM=" .. tostring(ObjMem ~= nil) .. " CE_PROC=" .. tostring(RegisterProcessor ~= nil))', state=0)
    time.sleep(2)
    
    # Also try GameCore context (state=3)
    send_cmd(s, 'print("GC_CE_MEM=" .. tostring(Mem ~= nil) .. " GC_CE_OBJMEM=" .. tostring(ObjMem ~= nil))', state=3)
    time.sleep(2)
    
    # Read all responses
    for i in range(20):
        msg = recv_msg(s, timeout=2)
        if msg is None:
            break
        # FireTuner console output has 'O\n' prefix
        clean = msg.lstrip('O\n').strip()
        if clean:
            print(f'  {clean}')
    
    s.close()
    print('Done.')
except ConnectionRefusedError:
    print('FireTuner connection refused - game not running or tuner not enabled')
except Exception as e:
    print(f'Error: {e}')
