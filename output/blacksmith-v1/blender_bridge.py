import json, socket, sys
command = {'type': 'execute_code', 'params': {'code': open(sys.argv[1]).read()}} if len(sys.argv)>1 else {'type':'get_scene_info','params':{}}
with socket.create_connection(('127.0.0.1',9876),timeout=15) as s:
    s.settimeout(180)
    s.sendall(json.dumps(command).encode())
    buf=b''
    while True:
        chunk=s.recv(65536)
        if not chunk: break
        buf+=chunk
        try:
            result=json.loads(buf)
            print(json.dumps(result,indent=2))
            break
        except json.JSONDecodeError: pass
