"""
FireTuner Protocol Proxy / Sniffer

Sits between FireTuner2.exe and the game, logging all traffic.

Usage:
1. Run this script: python firetuner_proxy.py
   (listens on 127.0.0.1:4319)
2. In FireTuner2.exe, change the connection port from 4318 to 4319
3. Connect FireTuner to the proxy
4. All traffic between FireTuner and the game is logged

This lets us see exactly what FireTuner sends on connect and how
the game responds to Lua console commands.
"""

import socket
import threading
import sys
import struct

GAME_HOST = "127.0.0.1"
GAME_PORT = 4318
PROXY_PORT = 4319


def hexdump(data, prefix=""):
    hex_str = data.hex()
    chunks = [hex_str[i:i+32] for i in range(0, len(hex_str), 32)]
    for chunk in chunks:
        pairs = [chunk[i:i+2] for i in range(0, len(chunk), 2)]
        printable = ''.join(chr(int(p, 16)) if 32 <= int(p, 16) < 127 else '.' for p in pairs)
        print(f"{prefix}{' '.join(pairs)}  |{printable}|")


def parse_message(data, direction):
    """Try to parse a FireTuner message."""
    if len(data) < 8:
        print(f"  [{direction}] Too short to parse ({len(data)} bytes)")
        return
    
    if direction == "CLIENT->GAME":
        # Request: [uint32 length][uint32 sender_id][utf8 string][0x00]
        content_len = struct.unpack_from('<I', data, 0)[0]
        sender_id = struct.unpack_from('<I', data, 4)[0]
        content = data[8:]
        try:
            text = content.rstrip(b'\x00').decode('utf-8')
        except:
            text = repr(content)
        print(f"  [{direction}] len={content_len} sender={sender_id} msg={repr(text)}")
    else:
        # Response: [uint32 msg_length][uint32 sender_id][content]
        msg_length = struct.unpack_from('<I', data, 0)[0]
        sender_id = struct.unpack_from('<I', data, 4)[0]
        content = data[8:8+msg_length] if msg_length > 0 else b''
        try:
            text = content.rstrip(b'\x00').decode('utf-8', errors='replace')
        except:
            text = repr(content)
        print(f"  [{direction}] msg_len={msg_length} sender={sender_id} content={repr(text)}")


def forward(src, dst, label):
    """Forward data from src to dst, logging it."""
    try:
        while True:
            data = src.recv(65536)
            if not data:
                print(f"[{label}] Connection closed")
                break
            print(f"\n[{label}] {len(data)} bytes:")
            hexdump(data, "  ")
            parse_message(data, label)
            dst.sendall(data)
    except Exception as e:
        print(f"[{label}] Error: {e}")
    finally:
        try:
            src.close()
            dst.close()
        except:
            pass


def handle_client(client_sock):
    """Handle a connection from FireTuner2 — forward to game."""
    print(f"\n[PROXY] FireTuner connected, connecting to game...")
    try:
        game_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        game_sock.connect((GAME_HOST, GAME_PORT))
        print("[PROXY] Connected to game!")
    except Exception as e:
        print(f"[PROXY] Could not connect to game: {e}")
        client_sock.close()
        return

    # Forward in both directions simultaneously
    t1 = threading.Thread(target=forward, args=(client_sock, game_sock, "CLIENT->GAME"), daemon=True)
    t2 = threading.Thread(target=forward, args=(game_sock, client_sock, "GAME->CLIENT"), daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("[PROXY] Session ended")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", PROXY_PORT))
    server.listen(1)
    print(f"[PROXY] Listening on 127.0.0.1:{PROXY_PORT}")
    print(f"[PROXY] Will forward to game at {GAME_HOST}:{GAME_PORT}")
    print(f"[PROXY] Connect FireTuner2 to port {PROXY_PORT}")
    print()

    while True:
        client, addr = server.accept()
        print(f"[PROXY] Connection from {addr}")
        t = threading.Thread(target=handle_client, args=(client,), daemon=True)
        t.start()


if __name__ == '__main__':
    main()
