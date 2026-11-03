"""Fresh framed LSQ discovery; return on a complete response, not a fixed sleep.

This never executes Lua or caches context IDs. Partial frames and unrelated
console output cannot complete discovery. Control transport remains unchanged.
"""
import socket,struct,time

def query_states(port, *, timeout=2, connect=None, clock=None):
    connect=connect or socket.create_connection;clock=clock or time.monotonic
    pending=b'';deadline=clock()+timeout
    with connect(('127.0.0.1',port),timeout=timeout) as sock:
        payload=b'LSQ:\0';sock.sendall(struct.pack('<II',len(payload),1)+payload)
        while clock()<deadline:
            sock.settimeout(max(.01,deadline-clock()))
            chunk=sock.recv(65536)
            if not chunk:raise EOFError('State discovery closed before a complete list')
            pending+=chunk
            while len(pending)>=8:
                size,_=struct.unpack('<II',pending[:8]);assert size<=16*1024*1024
                if len(pending)<8+size:break
                body=pending[8:8+size];pending=pending[8+size:]
                encoding='utf-16le'if body.count(b'\0')>len(body)*.3 else 'utf-8'
                message=body.decode(encoding,errors='replace').strip('\x00')
                # Current native LSQ frames start with a numeric ID; other
                # builds prefix L/LSQ:. Console O frames are never a state list.
                if not message or not(message[0].isdigit()or message.startswith('L')):continue
                fields=message.removeprefix('LSQ:').removeprefix('L').split('\0')
                result={fields[i+1]:int(fields[i])for i in range(0,len(fields)-1,2)if fields[i].isdigit()and fields[i+1]}
                if result:
                    try:sock.shutdown(socket.SHUT_WR)
                    except OSError:pass
                    return result
    raise TimeoutError('No complete native state list')

def discover_contexts(required=None, ports=(4318,4319,4320,4321,4322)):
    fallback=[]
    for port in ports:
        try:states=query_states(port)
        except (OSError,EOFError,ValueError):continue
        if states:fallback.append((port,states))
        if (required and required in states)or(not required and 'GameCore_Tuner'in states):return port,states
    if fallback:return fallback[0]
    raise RuntimeError('No responsive tuner states')
