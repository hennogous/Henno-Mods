"""Read historical city coordinates or follow a placement rival from a verified save."""
import argparse
import re
import shutil
import time
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

from lightweight_guidance import (HERE, HeldProcess, NativeSession, launch, load, make_probe_controller,
                                 native_inventory, relief_sql, replace, require, restore_preferences, select_stack,
                                 sha, split_relief_sql, write_json)


def observe_teno(c, out, user):
    """Follow the recorded rival and both original sites across the next district decision."""
    query = """
local function sites()
 local city=assert(CityManager.GetCity(3,65536))
 assert(city:GetName()=='LOC_CITY_NAME_TENOCHTITLAN')
 local d=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER
 local y=GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index
 local center=Map.GetPlot(city:GetX(),city:GetY())
 for _,i in ipairs({599,675,750}) do
  local p=Map.GetPlotByIndex(i)
  local legal=p:CanHaveDistrict(d.Index,3,65536)
  local score=p:GetAdjacencyYield(3,65536,d.Index,y)
  print('CSC_TENO_RIVAL',Game.GetCurrentGameTurn(),i,p:GetOwner(),legal,score,
        p:GetDistrictType(),center:GetProperty('CSC_AI_PAIR_ACTIVE_'..d.DistrictType..'1') or '-')
 end
end
sites()
Events.TurnBegin.Add(sites)
"""
    c.cmd(query, 'PlotInfo', 'observe-third-rival')
    deadline = time.monotonic()+240
    while time.monotonic()<deadline:
        row=c.state_read('follow-alternative-site')
        if row['turn']>=39:
            break
        if row['player0_human'] and not row['active'] and row['local_player']==0:
            c.ready(row['turn'],'named-handoff')
            c.play(min(39,row['turn']+3))
        else:
            time.sleep(2)
    else:
        raise TimeoutError('Archived decision did not advance')
    lines=(user/'Logs/Lua.log').read_text(encoding='utf8',errors='replace').splitlines()
    rows=[line.split('CSC_TENO_RIVAL\t',1)[1].split('\t') for line in lines if 'CSC_TENO_RIVAL\t' in line]
    require(rows and min(int(r[0]) for r in rows)<32 and max(int(r[0]) for r in rows)>=38,
            'Third-site observations missed the bid or foundation')
    write_json(out/'rivals.json', rows)


def read_cities(study, receipt, native_save, out, sites=False):
    pins = load(study / 'study.json')['pins']
    checkpoint = load(receipt)
    require(not out.exists() and not native_inventory(), 'Output exists or the game is in use')
    out.mkdir()
    arm = receipt.parent.parent
    protocol = load(arm/'protocol.json')
    package = Path(pins['packages']['csc']['path'])
    staged = {}
    for rel, field in [('Data/CSC_Q_ALL_AI_Connectors.sql','active_sha256'),
                       ('Lua_UI/AI/CSC_AI_BakersGameplay.lua','gameplay_sha256')]:
        path = package/rel
        original = path.read_bytes()
        require(original == (HERE.parents[3]/'Civ Supply Chains'/rel).read_bytes(), 'Installed release differs')
        if rel.endswith('.sql'):
            if protocol.get('layout_floor'):
                candidate = original+b'\n'+(HERE/'no_base_city_rules.sql').read_bytes()+relief_sql(protocol['layout_floor'])
                if protocol.get('split_relief'):
                    candidate+=split_relief_sql()
            else:
                candidate = original+b'\n'+(HERE/'paired_material_rules.sql').read_bytes()
        else:
            candidate = (arm/'local-gameplay.lua').read_bytes()
        require(sha256(candidate).hexdigest() == protocol[field], 'Historical build differs')
        staged[path] = (original,candidate)
    c = make_probe_controller(out, user_root=Path(pins['userdata']))
    if sites:
        c.study_endpoint=39
        c.observer_warning_senders=range(1,6)
        c.allow_observer_warning_dismissal=c.allow_observer_first_meet_dismissal=True
    session = NativeSession(out, c, inventory=native_inventory, hold=HeldProcess, write=write_json)
    try:
        if not native_save.exists():
            source = Path(checkpoint['archive'])
            require(native_save.parent.resolve()==Path(pins['saves']).resolve() and sha(source)==checkpoint['sha256'],
                    'Save staging needs a verified snapshot and its native directory')
            shutil.copy2(source,native_save)
        for path, (_,candidate) in staged.items():
            replace(path,candidate)
        session.start(lambda: launch(SimpleNamespace(binary=Path(pins['binary'])), out))
        session.wait_context('MainMenu')
        select_stack(session, out, [pins['packages']['csc']['id']])
        session.issue_load_once(native_save, sha256=checkpoint['sha256'],
                                native_directory=Path(pins['saves']), turn=checkpoint['turn'])
        session.wait_context('GameCore_Tuner')
        if sites:
            session.wait_context('PlotInfo')
            observe_teno(c, out, Path(pins['userdata']))
            return
        raw = c.cmd("""
for _,player in ipairs(PlayerManager.GetAliveMajors()) do
 for _,city in player:GetCities():Members() do
  print('CSC_AUDIT_CITY',player:GetID(),city:GetID(),Map.GetPlot(city:GetX(),city:GetY()):GetIndex(),city:GetName())
 end
end
""", 'GameCore_Tuner', 'read-fixed-city-centers')
        cities = re.findall(r'CSC_AUDIT_CITY\s+(\d+)\s+(\d+)\s+(\d+)\s+(\S+)', raw)
        require(len(cities) >= 5, 'City locations unavailable')
        write_json(out/'cities.json', dict(source=checkpoint['sha256'], cities=cities))
    finally:
        try:
            if session.owner is not None and session.owner.poll() is None:
                session.close(restore_preferences=lambda: restore_preferences(c, out)
                              if (out/'original-preferences.json').exists() else None)
        finally:
            if not native_inventory():
                for path,(original,candidate) in staged.items():
                    require(path.read_bytes() in (candidate,original), 'Concurrent installed mod edit')
                    replace(path, original)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for field in ('study', 'receipt', 'native_save', 'out'):
        p.add_argument(field, type=Path)
    p.add_argument('--sites',action='store_true',help='Track Tenochtitlan across its archived decision')
    args = p.parse_args()
    read_cities(**vars(args))
