"""Small framed FireTuner client for adjacency checks; no launch/kill side effects."""
import argparse
import socket
import struct
import sys
PORT=4318
import time
from pathlib import Path


def exact(sock,length):
    data=b''
    while len(data)<length:
        chunk=sock.recv(length-len(data))
        if not chunk: raise EOFError('FireTuner closed the connection')
        data+=chunk
    return data


def collect(sock,seconds):
    end=time.monotonic()+seconds
    messages=[]
    while time.monotonic()<end:
        sock.settimeout(max(0.01,end-time.monotonic()))
        try:
            length,sender=struct.unpack('<II',exact(sock,8))
            payload=exact(sock,length)
            # Current game emits UTF-8; accept UTF-16 builds as documented.
            encoding='utf-16le' if payload.count(b'\0')>len(payload)*0.3 else 'utf-8'
            text=payload.decode(encoding,errors='replace').strip('\x00')
            messages.append(text)
        except socket.timeout: break
    return messages


def states():
    with socket.create_connection(('127.0.0.1',PORT),timeout=5) as sock:
        collect(sock,0.2)
        payload=b'LSQ:\0'
        sock.sendall(struct.pack('<II',len(payload),1)+payload)
        messages=collect(sock,1)
        sock.shutdown(socket.SHUT_WR)
    result={}
    for message in messages:
        fields=message.removeprefix('L').split('\0')
        for index in range(0,len(fields)-1,2):
            if fields[index].isdigit(): result[fields[index+1]]=int(fields[index])
    return result


def command(lua,state=0,wait=3):
    with socket.create_connection(('127.0.0.1',PORT),timeout=5) as sock:
        initial=collect(sock,0.3)
        payload=f'CMD:{state}:{lua}'.encode()+b'\0'
        sock.sendall(struct.pack('<II',len(payload),1)+payload)
        messages=initial+collect(sock,wait)
        sock.shutdown(socket.SHUT_WR)
        try: collect(sock,0.3)
        except (EOFError,OSError): pass
    return messages


def main():
    global PORT
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--lua')
    group.add_argument('--file',type=Path)
    parser.add_argument('--state',type=int,default=0)
    parser.add_argument('--state-name',help='Resolve the current Lua state by name; IDs change during loading')
    parser.add_argument('--wait',type=float,default=3)
    parser.add_argument('--port',type=int,default=4318,help='Native tuner port; reloads can advance it to 4319 etc.')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    PORT=args.port
    lua=args.lua if args.lua is not None else args.file.read_text(encoding='utf-8-sig')
    state=args.state
    if args.state_name:
        available=states()
        if args.state_name not in available: raise RuntimeError(f'State {args.state_name!r} unavailable; states: {available}')
        state=available[args.state_name]
    messages=command(lua,state,args.wait)
    text='\n'.join(messages)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text+'\n',encoding='utf-8')
    print(text)
    if any('ERR:' in message for message in messages):
        raise SystemExit(1)


if __name__=='__main__': main()
