"""
Probe CE API with a live game at turn 149.
Test: Mem, ObjMem, CityTradeManager, CultureManager, EconomicManager.
Also fix city query and get full picture.
"""
import sys, os, time, threading, struct, math
sys.path.insert(0, os.path.dirname(__file__))
from firetuner_client import FireTuner


class OC(FireTuner):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.lines = []
        self._lock = threading.Lock()
    def _process_buffer(self):
        while len(self._recv_buffer) >= 8:
            ml = struct.unpack_from('<I', self._recv_buffer, 0)[0]
            sid = struct.unpack_from('<I', self._recv_buffer, 4)[0]
            end = 8 + ml
            if len(self._recv_buffer) < end: break
            body = bytes(self._recv_buffer[8:end])
            self._recv_buffer = self._recv_buffer[end:]
            try:
                text = body.decode('utf-8', errors='replace').rstrip('\x00')
                if sid in (0xFFFFFFFF, 4294967295):
                    if len(text)>=2 and text[1]=='\n': text=text[2:]
                    if ': ' in text[:30]: text=text[text.index(': ')+2:]
                    with self._lock: self.lines.append(text.strip())
                elif sid in self._responses:
                    self._responses[sid] = text or '[empty]'
            except: pass
    def q(self, lua, wait=2.5):
        with self._lock: self.lines.clear()
        content = f"CMD:3:{lua}".encode()+b'\x00'
        sid = self._next_sender_id()
        self.sock.sendall(struct.pack('<II', len(content), sid)+content)
        time.sleep(wait)
        with self._lock: return list(self.lines)

ft = OC(timeout=15.0)
ft.connect()
print("Connected.\n")

# --- Cities (fixed query) ---
city_lua = (
    "local p=Players[0]; "
    "for i,c in p:GetCities():Members() do "
    "local ok,err=pcall(function() "
    "local bq=c:GetBuildQueue(); "
    "local tid=bq:CurrentlyBuilding(); "
    "local cur='nothing'; "
    "if tid>=0 then "
    "local u=GameInfo.Units[tid]; local b=GameInfo.Buildings[tid]; local d=GameInfo.Districts[tid]; "
    "if u then cur=u.UnitType elseif b then cur=b.BuildingType elseif d then cur=d.DistrictType "
    "else cur='id_'..tostring(tid) end end; "
    "print('CITY:'..c:GetName()..':pop='..c:GetPopulation()..':bld='..cur..':turns='..bq:GetTurnsLeft()) "
    "end); if not ok then print('CITY_ERR:'..tostring(err)) end end"
)
city_lines = ft.q(city_lua, 3.5)
print("=== CITIES ===")
for l in city_lines:
    if l.startswith("CITY:") or l.startswith("CITY_ERR:"):
        print(" ", l)

# --- CE availability check ---
print("\n=== CE API CHECK ===")
ce_check = ft.q(
    "local apis={'Mem','ObjMem','RegisterProcessor','CityTradeManager','CultureManager','EconomicManager','UnitManager','GovernorManager'}; "
    "for _,name in ipairs(apis) do "
    "local v=_G[name]; "
    "print('CE:'..name..':'..(v~=nil and type(v) or 'nil')) "
    "end",
    wait=2.5
)
for l in ce_check:
    print(" ", l)

# --- CityTradeManager ---
print("\n=== CityTradeManager ===")
ctm = ft.q(
    "local p=Players[0]; "
    "for i,c in p:GetCities():Members() do "
    "local ok,err=pcall(function() "
    "local tm=CityTradeManager(c); "
    "print('CTM:'..c:GetName()..':type='..type(tm)); "
    "-- try to enumerate methods via metatable "
    "local mt=getmetatable(tm); "
    "if mt then print('CTM_MT:has_metatable') else print('CTM_MT:none') end "
    "end); if not ok then print('CTM_ERR:'..tostring(err)) end end",
    wait=3.0
)
for l in ctm:
    print(" ", l)

# --- EconomicManager ---
print("\n=== EconomicManager (player level) ===")
eco = ft.q(
    "local p=Players[0]; "
    "local ok,err=pcall(function() "
    "local em=EconomicManager(p); "
    "print('ECO:type='..type(em)); "
    "local mt=getmetatable(em); "
    "if mt and mt.__index then "
    "for k,v in pairs(mt.__index) do print('ECO_METHOD:'..tostring(k)) end "
    "end "
    "end); if not ok then print('ECO_ERR:'..tostring(err)) end",
    wait=3.0
)
for l in eco:
    print(" ", l)

# --- ObjMem on capital plot ---
print("\n=== ObjMem probe (capital plot) ===")
objmem = ft.q(
    "local cap=Players[0]:GetCities():GetCapitalCity(); "
    "local px=cap:GetX(); local py=cap:GetY(); "
    "local plot=Map.GetPlot(px,py); "
    "print('PLOT:('..px..','..py..')'); "
    "local ok,err=pcall(function() "
    "-- Read appeal (offset 0x4a, FIELD_SHORT) "
    "local appeal=ObjMem(plot, 0x4a, FIELD_SHORT); "
    "print('ObjMem:appeal='..tostring(appeal)); "
    "-- Read terrain type at offset 0x18 "
    "local ter=ObjMem(plot, 0x18, FIELD_INT); "
    "print('ObjMem:terrain_raw='..tostring(ter)) "
    "end); if not ok then print('OBJMEM_ERR:'..tostring(err)) end",
    wait=3.0
)
for l in objmem:
    print(" ", l)

# --- CultureManager ---
print("\n=== CultureManager (player) ===")
cult = ft.q(
    "local p=Players[0]; "
    "local ok,err=pcall(function() "
    "local cm=CultureManager(p); "
    "print('CULT:type='..type(cm)); "
    "local mt=getmetatable(cm); "
    "if mt and mt.__index then "
    "local methods={}; for k,v in pairs(mt.__index) do table.insert(methods,tostring(k)) end; "
    "print('CULT_METHODS:'..table.concat(methods,',')) "
    "end "
    "end); if not ok then print('CULT_ERR:'..tostring(err)) end",
    wait=3.0
)
for l in cult:
    print(" ", l)

ft.close()
print("\nDone.")
