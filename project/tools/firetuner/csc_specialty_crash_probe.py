"""
CSC Specialty Product / CE crash probe via FireTuner.

Default mode is read-only and safe:
    python project/tools/firetuner/csc_specialty_crash_probe.py

Optional mutation probes for a fresh throwaway test game:
    python project/tools/firetuner/csc_specialty_crash_probe.py --ce-add-greatwork
    python project/tools/firetuner/csc_specialty_crash_probe.py --danger-complete-project-effect

The danger flag deliberately invokes the same native product-creation effect path that is
suspected of crashing/failing. Use only when you are ready to collect logs/crash package.
"""
from __future__ import annotations

import argparse
import socket
import struct
import threading
import time
from pathlib import Path

HOST = "127.0.0.1"
PORT = 4318


class FireTunerSession:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.sock: socket.socket | None = None
        self._next_id = 1000
        self._recv_buffer = bytearray()
        self._responses: dict[int, str | None] = {}
        self._lines: list[str] = []
        self._lock = threading.Lock()
        self._reader: threading.Thread | None = None
        self._stop = False

    def connect(self) -> None:
        self.sock = socket.create_connection((HOST, PORT), timeout=self.timeout)
        self.sock.settimeout(0.5)
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    def close(self) -> None:
        self._stop = True
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass

    def _read_loop(self) -> None:
        assert self.sock is not None
        while not self._stop:
            try:
                data = self.sock.recv(65536)
            except socket.timeout:
                continue
            except OSError:
                break
            if not data:
                break
            self._recv_buffer.extend(data)
            self._process_buffer()

    def _process_buffer(self) -> None:
        while len(self._recv_buffer) >= 8:
            msg_len = struct.unpack_from("<I", self._recv_buffer, 0)[0]
            sender_id = struct.unpack_from("<I", self._recv_buffer, 4)[0]
            end = 8 + msg_len
            if len(self._recv_buffer) < end:
                break
            body = bytes(self._recv_buffer[8:end])
            del self._recv_buffer[:end]
            text = body.decode("utf-8", errors="replace").rstrip("\x00")
            if sender_id == 0xFFFFFFFF:
                # Console print line. Civ prefixes some lines with channel metadata.
                if len(text) >= 2 and text[1] == "\n":
                    text = text[2:]
                if ": " in text[:40]:
                    text = text[text.index(": ") + 2:]
                with self._lock:
                    self._lines.append(text.strip())
            else:
                with self._lock:
                    if sender_id in self._responses:
                        self._responses[sender_id] = text or "[empty]"

    def q(self, lua: str, wait: float = 2.5) -> list[str]:
        assert self.sock is not None
        with self._lock:
            self._lines.clear()
        content = f"CMD:3:{lua}".encode("utf-8") + b"\x00"
        sender_id = self._next_id
        self._next_id += 1
        self.sock.sendall(struct.pack("<II", len(content), sender_id) + content)
        time.sleep(wait)
        with self._lock:
            return list(self._lines)


def print_section(title: str, lines: list[str]) -> None:
    print(f"\n=== {title} ===")
    if not lines:
        print("[no console output]")
    for line in lines:
        print(line)


SAFE_LUA = r'''
print('CSC_PROBE:BEGIN')
print('CSC_PROBE:CE:Mem='..tostring(type(Mem)))
print('CSC_PROBE:CE:ObjMem='..tostring(type(ObjMem)))
print('CSC_PROBE:CE:CultureManager='..tostring(type(CultureManager)))
print('CSC_PROBE:CE:EconomicManager='..tostring(type(EconomicManager)))

local function rowExists(tableName, key)
  local t = GameInfo[tableName]
  local row = t and t[key]
  print('CSC_PROBE:ROW:'..tableName..':'..key..':'..tostring(row ~= nil))
  if row then
    for k,v in pairs(row) do
      if k == 'Index' or k == 'GreatWorkObjectType' or k == 'GreatWorkSlotType' or k == 'ResourceType' or k == 'BuildingType' or k == 'ProjectType' or k == 'ModifierType' or k == 'Name' then
        print('CSC_PROBE:FIELD:'..key..':'..tostring(k)..'='..tostring(v))
      end
    end
  end
end

rowExists('GreatWorkObjectTypes', 'GREATWORKOBJECT_PRODUCT')
rowExists('GreatWorkSlotTypes', 'GREATWORKSLOT_PRODUCT')
rowExists('GreatWorks', 'GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_1')
rowExists('Resources', 'RESOURCE_CSC_BAKERS_SPECIALTY')
rowExists('Buildings', 'BUILDING_CSC_ARISTOCRAT')
rowExists('Projects', 'PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY')
rowExists('Modifiers', 'MOD_CSC_PROJECT_COMPLETION_CREATE_BAKERS_SPECIALTY')

local p = Players[0]
if p then
  local cap = p:GetCities():GetCapitalCity()
  print('CSC_PROBE:PLAYER0:alive='..tostring(p:IsAlive()))
  if cap then
    print('CSC_PROBE:CAPITAL:'..cap:GetName()..':id='..tostring(cap:GetID())..':x='..cap:GetX()..':y='..cap:GetY())
    local b = GameInfo.Buildings['BUILDING_CSC_ARISTOCRAT']
    if b then
      local has = cap:GetBuildings():HasBuilding(b.Index)
      print('CSC_PROBE:CAPITAL_HAS_ARISTOCRAT='..tostring(has))
    end
  else
    print('CSC_PROBE:CAPITAL:nil')
  end
end
print('CSC_PROBE:END')
'''

CE_ADD_GW_LUA_TEMPLATE = r'''
print('CSC_PROBE:CE_ADD_GW:BEGIN')
local ok, err = pcall(function()
  assert(CultureManager ~= nil, 'CultureManager nil - CE not loaded')
  local gwType = '__GW_TYPE__'
  local gw = GameInfo.GreatWorks[gwType]
  assert(gw ~= nil, 'great work row missing: '..gwType)
  print('CSC_PROBE:CE_ADD_GW:GreatWorkType='..tostring(gw.GreatWorkType)..':dbIndex='..tostring(gw.Index)..':object='..tostring(gw.GreatWorkObjectType)..':image='..tostring(gw.Image)..':person='..tostring(gw.GreatPersonIndividualType)..':era='..tostring(gw.EraType))
  local p = Players[0]
  assert(p ~= nil, 'Player 0 missing')
  local cap = p:GetCities():GetCapitalCity()
  assert(cap ~= nil, 'Player 0 capital missing')
  local gwIndex = CultureManager.FindOrAddGreatWork(gw.Index)
  print('CSC_PROBE:CE_ADD_GW:gwListIndex='..tostring(gwIndex))
  CultureManager.SetGreatWorkPlayer(gwIndex, 0)
  p:GetCities():AddGreatWork(gwIndex)
  print('CSC_PROBE:CE_ADD_GW:ADDED')

  local function callMethod(obj, methodName, ...)
    if obj == nil then
      return false, 'object nil'
    end
    local f = obj[methodName]
    if type(f) ~= 'function' then
      return false, 'method missing: '..methodName..' type='..tostring(type(f))
    end
    return pcall(f, obj, ...)
  end

  local function inspectCity(city)
    if city == nil then return end
    print('CSC_PROBE:CE_ADD_GW:CITY:'..tostring(city:GetName())..':id='..tostring(city:GetID())..':x='..tostring(city:GetX())..':y='..tostring(city:GetY()))
    local buildings = city:GetBuildings()
    print('CSC_PROBE:CE_ADD_GW:CITY_BUILDINGS_TYPE='..tostring(type(buildings)))
    print('CSC_PROBE:CE_ADD_GW:METHOD:GetNumGreatWorkSlots='..tostring(type(buildings.GetNumGreatWorkSlots)))
    print('CSC_PROBE:CE_ADD_GW:METHOD:GetGreatWorkInSlot='..tostring(type(buildings.GetGreatWorkInSlot)))
    print('CSC_PROBE:CE_ADD_GW:METHOD:HasBuilding='..tostring(type(buildings.HasBuilding)))

    for row in GameInfo.Building_GreatWorks() do
      local building = GameInfo.Buildings[row.BuildingType]
      if building ~= nil then
        local okHas, has = callMethod(buildings, 'HasBuilding', building.Index)
        print('CSC_PROBE:CE_ADD_GW:DB_SLOT_DEF:'..tostring(row.BuildingType)..':slotType='..tostring(row.GreatWorkSlotType)..':numSlots='..tostring(row.NumSlots)..':hasOk='..tostring(okHas)..':has='..tostring(has))
        if okHas and has then
          local okNum, numSlots = callMethod(buildings, 'GetNumGreatWorkSlots', building.Index)
          print('CSC_PROBE:CE_ADD_GW:BUILDING_SLOT_COUNT:'..tostring(row.BuildingType)..':ok='..tostring(okNum)..':value='..tostring(numSlots))
          if okNum and numSlots and numSlots > 0 then
            for slot = 0, numSlots - 1 do
              local okSlot, inSlot = callMethod(buildings, 'GetGreatWorkInSlot', building.Index, slot)
              print('CSC_PROBE:CE_ADD_GW:SLOT:'..tostring(row.BuildingType)..':'..tostring(slot)..':ok='..tostring(okSlot)..':gwListIndex='..tostring(inSlot)..':MATCH='..tostring(inSlot == gwIndex))
            end
          end
        end
      end
    end
  end

  inspectCity(cap)
end)
print('CSC_PROBE:CE_ADD_GW:OK='..tostring(ok)..':ERR='..tostring(err))
print('CSC_PROBE:CE_ADD_GW:END')
'''

DANGER_EFFECT_LUA = r'''
print('CSC_PROBE:DANGER_EFFECT:BEGIN')
print('CSC_PROBE:DANGER_EFFECT:This will invoke the native CSC product completion effect path.')
local ok, err = pcall(function()
  local p = Players[0]
  assert(p ~= nil, 'Player 0 missing')
  local cap = p:GetCities():GetCapitalCity()
  assert(cap ~= nil, 'Player 0 capital missing')
  local mod = GameInfo.Modifiers['MOD_CSC_PROJECT_COMPLETION_CREATE_BAKERS_SPECIALTY']
  assert(mod ~= nil, 'Modifier row missing')
  -- There is no general public Lua API for ApplyModifier in normal state 3.
  -- This marker exists so we can confirm the probe reached the danger step before
  -- using in-game project completion as the actual trigger.
  print('CSC_PROBE:DANGER_EFFECT:READY_FOR_MANUAL_PROJECT_COMPLETION')
end)
print('CSC_PROBE:DANGER_EFFECT:OK='..tostring(ok)..':ERR='..tostring(err))
print('CSC_PROBE:DANGER_EFFECT:END')
'''


def latest_crash_pkg() -> Path | None:
    root = Path.home() / "AppData/Local/Firaxis Games/Sid Meier's Civilization VI/packagedDumps"
    pkgs = sorted(root.glob("**/submission.pkg"), key=lambda p: p.stat().st_mtime, reverse=True)
    return pkgs[0] if pkgs else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--ce-add-greatwork', action='store_true', help='Use CE CultureManager to create/assign one great work.')
    parser.add_argument('--ce-greatwork-type', default='GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_1', help='GreatWorkType to use with --ce-add-greatwork.')
    parser.add_argument('--danger-complete-project-effect', action='store_true', help='Mark readiness for manual native project completion crash repro.')
    args = parser.parse_args()

    before_pkg = latest_crash_pkg()
    print('Latest crash package before probe:', before_pkg)

    ft = FireTunerSession(timeout=15.0)
    try:
        ft.connect()
    except OSError as e:
        print('Could not connect to FireTuner at 127.0.0.1:4318:', e)
        print('Start Civ VI with EnableTuner=1 and load into a game, then rerun this script.')
        return 2

    try:
        print_section('SAFE DATABASE / CE PROBE', ft.q(SAFE_LUA, wait=4.0))
        if args.ce_add_greatwork:
            ce_lua = CE_ADD_GW_LUA_TEMPLATE.replace('__GW_TYPE__', args.ce_greatwork_type)
            print_section('CE GREATWORK INSERT PROBE', ft.q(ce_lua, wait=4.0))
        if args.danger_complete_project_effect:
            print_section('DANGER EFFECT MARKER', ft.q(DANGER_EFFECT_LUA, wait=2.0))
    finally:
        ft.close()

    after_pkg = latest_crash_pkg()
    print('\nLatest crash package after probe:', after_pkg)
    if after_pkg and after_pkg != before_pkg:
        print('NEW_CRASH_PACKAGE:', after_pkg)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
