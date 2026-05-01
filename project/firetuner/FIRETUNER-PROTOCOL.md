# FireTuner2 Protocol — Reverse-Engineered

**Source:** ILSpy decompile of FireTuner2.exe v1.0.7354.28197  
**Date:** 2026-04-01  
**Method:** dnfile + manual IL disassembly of Connection, SocketConnection classes

---

## Architecture

```
FireTuner2.exe (client)           Civ 6 process (server)
      |                                    |
      |  TCP connect to 127.0.0.1:4318     |
      |<---------------------------------->|
      |                                    |
      |  CMD:<state>:<lua>\x00             |
      |  [framed with length+sender_id]    |
      |-------------------------------->   |
      |                                    |
      |  <unsolicited output on 0xFFFFFFFF>|
      |<--------------------------------   |
      |                                    |
      |  [game sends "Closing" when done]  |
      |<--------------------------------   |
      |  SocketConnection.CloseConnection()|
      |  (client closes socket gracefully) |
```

**Key insight:** The game is the *server*. It initiates the disconnect by sending a `"Closing"` message, which triggers FireTuner2 to call `CloseConnection()` on its own socket. The `btnForceDisconnect` button does the same thing unilaterally (client-side socket close only — no packet sent to game).

---

## Wire Format

### Request (FireTuner2 → Civ 6)

```
[uint32 LE] content_length     # byte count of everything after header
[uint32 LE] sender_id          # listener index for routing responses (1+)
[utf-8]     "CMD:<state>:<lua>"  # null-terminated
[byte 0x00]
```

Written char-by-char via `BinaryWriter.Write(char)` (UTF-8 encoded).  
`content_length` is corrected post-write if UTF-8 byte count differs from char count.

### Response (Civ 6 → FireTuner2)

```
[uint32 LE] message_length     # byte count AFTER the 8-byte header
[uint32 LE] sender_id
[body bytes]                   # UTF-16LE encoded response, null-separated
```

When `sender_id == 0xFFFFFFFF`: unsolicited console output from game.  
Console output starts with `"O\nGameCore_Tuner: "` prefix before the actual text.

---

## Lua States

| State ID | Name             | Context                          |
|----------|------------------|----------------------------------|
| 0        | UI               | Frontend / main menu UI scripts  |
| 3        | GameCore_Tuner   | Gameplay — Players[], Cities, etc. |
| 4        | WorldInput       | Input handling                   |
| 5        | StrategicView    | Strategic view layer             |

**State 3 returns empty on `return`** — must use `print()` for output.  
State 3 `print()` output arrives as unsolicited message on sender_id `0xFFFFFFFF`.

---

## Protocol Message Types (from DefaultRequestHandler)

These are the first element of a parsed message from the game to FireTuner2:

| Prefix       | Meaning                                      |
|--------------|----------------------------------------------|
| `"L"`        | LoadLuaStates — triggers panel refresh       |
| `"O"`        | Output — console text to display             |
| `"Closing"`  | Game is disconnecting — client closes socket |
| `"LSQ:"`     | Lua State Query response                     |
| `"APP:"`     | Connected app name info                      |
| `"HELP:"`    | Help request                                 |
| `"LOAD:"`    | Load panel file                              |

---

## Why the TCP Listener Dies After Our Disconnect

**Root cause:** The game is the TCP *server*. When our Python client closes abruptly (socket RST or FIN without the `"Closing"` handshake), the game's listener either:
1. Drops into a bad state and stops accepting new connections, OR
2. The game's listener is *single-instance* — only accepts one connection at a time with no re-listen after abort

**Evidence:** `btnForceDisconnect_Click` just calls `SocketConnection.CloseConnection()` on the client side. It doesn't send any packet. So the "Force Disconnect" button works because it cleanly closes the TCP socket (FIN/ACK), and the game detects the clean close and resets its listener.

Our Python `shutdown(SHUT_RDWR) + close()` should send FIN — but if anything in the recv thread eats the FIN or the buffer state is wrong, it may send RST instead.

**Fix:** Call `socket.shutdown(socket.SHUT_WR)` *only* (not SHUT_RDWR) to send FIN and allow the game to detect EOF, then close after a brief delay to drain any final data from the game.

---

## Fix: Graceful Disconnect in Python Client

```python
def disconnect_gracefully(self):
    """Send graceful disconnect — closes send side, waits for game to acknowledge."""
    if self.sock:
        try:
            # Shutdown write side only (sends FIN to game)
            self.sock.shutdown(socket.SHUT_WR)
            # Give game ~500ms to detect the close and reset its listener
            time.sleep(0.5)
        except OSError:
            pass
        finally:
            self._running = False
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None
```

**Alternative:** Send a `"Closing"` dummy message before disconnecting — but since `DefaultRequestHandler` processes this as a message *from the game*, not from us, the game won't react to us sending it. The clean FIN approach is correct.

---

## Complete Protocol Command Set

All `CMD:` prefixes used in the wire protocol (from #US strings):

| Command Prefix    | Purpose                                      |
|-------------------|----------------------------------------------|
| `CMD:<state>:<lua>` | Execute Lua in given state                 |
| `LOAD:<path>`     | Load a panel .ltp file                       |
| `LSQ:`            | Lua State Query                              |
| `APP:`            | Application info announcement               |
| `HELP:`           | Help request                                 |
| `HELPT:`          | Help topic request                           |
| `TREE:`           | Tree view data                               |
| `LIST:`           | Selection list data                          |
| `MLIST:`          | Multiselect list data                        |
| `LISTSEL:`        | List selection event                         |
| `TABLE:`          | Table data                                   |
| `CUSTOM_TABLE:`   | Custom table data                            |
| `CUSTOM_TABLE_SEL:` | Custom table selection                     |
| `VAL:`            | Value control update                         |
| `SET:`            | Set value                                    |
| `QRY:`            | Query                                        |
| `KILLQRY:`        | Kill query                                   |
| `STRACKERS:`      | Stat trackers list                           |
| `START_TRACKER:`  | Start stat tracker                           |
| `STOP_TRACKER:`   | Stop stat tracker                            |
| `ERR:`            | Error message                                |
| `Closing`         | Game signals connection close                |
| `L`               | Load lua states                              |
| `O`               | Output (console print)                       |

---

## Confirmed Working Patterns

```python
# State 3 print() pattern (WORKS)
ft.lua_state = 3
result = ft.execute("print('hello')", timeout=5)
# Result arrives via 0xFFFFFFFF console channel

# State 3 return (EMPTY — doesn't route back)
result = ft.execute("return 'hello'")  # returns '[empty response]'

# State 0 return (WORKS for some globals)
ft.lua_state = 0
result = ft.execute("return tostring(UI.IsInGame())")

# Multi-line as single line (use ; or space separators)
lua = "local x=1; local y=2; print(tostring(x+y))"
```

---

## Known Issues / Limitations

1. **Single client:** Only one TCP connection at a time. Second connect kills first.
2. **TCP flood:** `print()` heavy operations (e.g. RegisterProcessor hooks) flood the recv buffer. Cap at 3s.
3. **State 3 no-return:** `return` is silently dropped in GameCore state. Use `print()`.
4. **Listener reset:** Abrupt disconnect (RST) kills listener until game restart. Use graceful shutdown.
5. **No auth:** Zero authentication. Anyone on localhost can connect and execute arbitrary Lua.
