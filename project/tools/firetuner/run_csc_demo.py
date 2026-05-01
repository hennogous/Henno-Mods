"""
run_csc_demo.py — Full demo run:
1. Hard relaunch Civ 6
2. Start a new game (CSC active, no CE)
3. Autoplay N turns (observer mode)
4. Print full game state snapshot

Usage: python run_csc_demo.py [turns]
  turns  Number of turns to autoplay (default: 50)

Run from: csc/firetuner/
"""
import sys, os, time, socket, struct, subprocess

# Write output to log file too so we can tail it
_log_path = os.path.join(os.path.dirname(__file__), 'demo_run.log')
_log = open(_log_path, 'w', encoding='utf-8')

class _Tee:
    def __init__(self, *streams): self.streams = streams
    def write(self, data):
        for s in self.streams:
            try: s.write(data)
            except: pass
    def flush(self):
        for s in self.streams:
            try: s.flush()
            except: pass

sys.stdout = _Tee(sys.__stdout__, _log)
sys.stderr = _Tee(sys.__stderr__, _log)

sys.path.insert(0, os.path.dirname(__file__))
from ft_utils import FTSession, snapshot
from firetuner_client import FireTuner

AUTOPLAY_TURNS = int(sys.argv[1]) if len(sys.argv) > 1 else 50

def port_up():
    try:
        s = socket.socket(); s.settimeout(1.0); s.connect(('127.0.0.1', 4318)); s.close()
        return True
    except:
        return False

def wait_for_port(label, timeout=120):
    for i in range(timeout):
        time.sleep(1.0)
        if port_up():
            print(f"  Port up ({label}) after {i+1}s")
            return True
        if i % 15 == 14:
            print(f"  Still waiting ({label})... {i+1}s")
    return False

def fire_with_retry(lua, state=3, max_retries=10):
    """Send Lua and verify it arrived. Retry on connection reset."""
    for attempt in range(max_retries):
        ft = FireTuner(timeout=5.0)
        try:
            ft.connect()
            content = f"CMD:{state}:{lua}".encode() + b'\x00'
            ft.sock.sendall(struct.pack('<II', len(content), ft._next_sender_id()) + content)
            time.sleep(0.3)
            ft.close()
            print(f"  Command sent on attempt {attempt + 1}")
            return True
        except Exception as e:
            try: ft.close()
            except: pass
            if attempt < max_retries - 1:
                time.sleep(1.0)
    print(f"  ERROR: Failed to send command after {max_retries} attempts")
    return False

# ── Step 1: Kill Civ 6 ─────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1: Kill existing Civ 6 process")
print("=" * 60)
subprocess.run(["taskkill", "/F", "/IM", "CivilizationVI.exe"], capture_output=True)
subprocess.run(["taskkill", "/F", "/IM", "CivilizationVI_DX12.exe"], capture_output=True)
subprocess.run(["taskkill", "/F", "/IM", "FiraxisBugReporter.exe"], capture_output=True)
time.sleep(4.0)
print("Killed.")

# ── Step 2: Launch via Steam ────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 2: Launch Civ 6 via Steam")
print("=" * 60)
subprocess.Popen(["cmd", "/c", "start", "steam://rungameid/289070"])
time.sleep(5.0)

print("Waiting for main menu (~60s)...")
if not wait_for_port("main menu", timeout=120):
    print("ERROR: Game didn't open port in time.")
    sys.exit(1)
time.sleep(3.0)

# Verify front end and fire transition on the SAME connection — reconnecting
# too quickly after close causes ConnectionReset on the new connection.
fe_ok = False
ft_fe = None
for attempt in range(10):
    try:
        ft_fe = FTSession(timeout=10.0)
        ft_fe.connect()
        lines = ft_fe.q("print('FE:'..tostring(UI.IsInFrontEnd()))", wait=2.0, state=0)
        fe_ok = any('FE:true' in l for l in lines)
        if fe_ok:
            break
        ft_fe.close()
        ft_fe = None
        print(f"  FE check attempt {attempt+1}: {lines} — waiting...")
        time.sleep(5.0)
    except Exception as e:
        if ft_fe:
            try: ft_fe.close()
            except: pass
            ft_fe = None
        print(f"  FE check attempt {attempt+1} error: {e} — waiting...")
        time.sleep(5.0)

print(f"Front end confirmed: {fe_ok}")
if not fe_ok:
    print("Could not confirm front end after retries.")
    sys.exit(1)

# ── Step 3: Fire new game (reuse same connection) ───────────────────────────
print("\n" + "=" * 60)
print("STEP 3: Fire new game transition")
print("=" * 60)
ft2 = ft_fe  # reuse — no reconnect needed
ft2.q('Options.SetAppOption("Debug", "PlayNowSave", "")', wait=1.0, state=0)
time.sleep(0.3)
try:
    ft2.q('LuaEvents.Raise_State_Transition("MainMenu")', wait=0.5, state=0)
except Exception:
    pass
try:
    ft2.close()
except:
    pass

print("Transition fired. Waiting for port to drop (load screen)...")
for i in range(20):
    time.sleep(1.0)
    if not port_up():
        print(f"  Port dropped at {i+1}s")
        break

print("Waiting for game to come back up...")
if not wait_for_port("in-game", timeout=120):
    print("ERROR: Didn't get port back after load.")
    sys.exit(1)

# Poll until turn >= 1 — port comes back during load screen, 15s timer fires BeginGame
print("Waiting for turn 1 (15s LoadScreen timer + game init)...")
# Wait for MapLabelManager ocean label flood to settle before polling.
# The port comes back during the load screen while ocean labels are printing
# (~30-40s). Connecting into that flood causes immediate ECONNRESET.
# LoadScreen timer fires at +15s; labels settle at +40s; safe to poll at +45s.
print("  Waiting 45s for map label flood to settle...")
time.sleep(45.0)
t_start = -1
civ_info = {}
for attempt in range(30):  # up to ~45s more after the wait
    time.sleep(1.5)
    if not port_up():
        print(f"  [{attempt}] port down, waiting...")
        continue
    try:
        ft3 = FTSession(timeout=8.0)
        ft3.connect()
        t_start = ft3.turn()
        if t_start >= 1:
            civ_info = ft3.civ()
            ft3.close()
            break
        ft3.close()
        if attempt % 5 == 4:
            print(f"  [{attempt}] still turn {t_start}, waiting for BeginGame...")
    except Exception as e:
        print(f"  [{attempt}] error: {e}")

print(f"In-game at turn {t_start}, civ={civ_info}")
if t_start < 1:
    print(f"ERROR: Never reached turn 1. Aborting.")
    sys.exit(1)

# ── Step 4: Autoplay 50 turns ───────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"STEP 4: Autoplay {AUTOPLAY_TURNS} turns (observer mode)")
print("=" * 60)

autoplay_lua = (
    "Automation.SetActive(false); "
    "LuaEvents.AutoPlayEnd.RemoveAll(); "
    "LuaEvents.AutoPlayEnd.Add(function() print('AUTOPLAY_END:t='..Game.GetCurrentGameTurn()) end); "
    "AutoplayManager.SetDisableAssertsForAutoplay(true); "
    f"AutoplayManager.SetTurns({AUTOPLAY_TURNS}); "
    "AutoplayManager.SetReturnAsPlayer(0); "
    "AutoplayManager.SetObserveAsPlayer(0); "
    "AutoplayManager.SetActive(true); "
    "print('STARTED:t='..Game.GetCurrentGameTurn()..'|set='..AutoplayManager.GetTurns())"
)

if not fire_with_retry(autoplay_lua):
    print("ERROR: Could not start autoplay. Aborting.")
    sys.exit(1)

print("Autoplay command confirmed. Waiting for turns to process...")
time.sleep(8.0)

t_wall = time.time()
t_current = t_start
stopped = False

for poll in range(180):  # max 9 min
    time.sleep(3.0)
    if not port_up():
        if poll % 5 == 0:
            print(f"  [{poll*3}s] port down, waiting...")
        continue
    try:
        ft4 = FTSession(timeout=8.0)
        ft4.connect()
        status = ft4.q(
            "print('S:t='..Game.GetCurrentGameTurn()"
            "..'|active='..tostring(AutoplayManager.IsActive())"
            "..'|turns='..tostring(AutoplayManager.GetTurns()))",
            wait=2.0
        )
        ft4.close()

        end_sig = next((l for l in status if 'AUTOPLAY_END:' in l), None)
        s = next((l for l in status if l.startswith('S:')), None)
        active = True
        if s:
            parts = dict(p.split('=', 1) for p in s[2:].split('|') if '=' in p)
            t_current = int(parts.get('t', t_current))
            active = parts.get('active', 'true') == 'true'
            turns_left = parts.get('turns', '?')
            if poll % 4 == 0:
                elapsed = time.time() - t_wall
                print(f"  [{elapsed:.0f}s] turn={t_current} active={active} turns_left={turns_left}")

        if end_sig:
            print(f"  AutoPlayEnd fired: {end_sig}")
            stopped = True
            break
        if not active:
            print(f"  IsActive=false at turn {t_current}")
            stopped = True
            break
        if t_current > t_start + AUTOPLAY_TURNS + 5:
            print(f"  OVERRUN at turn {t_current}, forcing stop")
            ft5 = FTSession(timeout=8.0)
            ft5.connect()
            ft5.q("AutoplayManager.SetActive(false)", wait=1.0)
            ft5.close()
            stopped = True
            break

    except Exception as e:
        print(f"  [{poll}] error: {e}")

elapsed = time.time() - t_wall
actual = t_current - t_start
print(f"\nAutoplay done: turn {t_start} -> {t_current} ({actual} turns in {elapsed:.0f}s)")
print(f"Target: {AUTOPLAY_TURNS} | Actual: {actual} | {'OK' if actual == AUTOPLAY_TURNS else 'MISMATCH'}")

# ── Step 5: Snapshot ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 5: Game state snapshot")
print("=" * 60)
time.sleep(2.0)
snapshot(verbose=True)
print("\nDone.")
