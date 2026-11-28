"""Measure whether a legal unbuilt improvement contributes to a Quarter preview."""
import argparse
import re
import shutil
from pathlib import Path
from types import SimpleNamespace

from lightweight_guidance import (HERE, HeldProcess, NativeSession, launch, load, make_probe_controller,
    native_inventory, replace, require, restore_preferences, select_stack, sha, verify_modules, write_json)


# Pick an unimproved, owned Base with a legal adjacent Quarter footprint. Use
# the same stable iteration order in both branches of the same turn-50 save.
SEARCH = """
for _,key in ipairs({'TAILORS','BAKERS'}) do
 local imp=GameInfo.Improvements['IMPROVEMENT_CSC_PROBE_'..key]
 local district=GameInfo.Districts['DISTRICT_CSC_'..key..'_QUARTER']
 local materials={}
 for row in GameInfo.Improvement_ValidResources() do
  if row.ImprovementType==imp.ImprovementType then materials[GameInfo.Resources[row.ResourceType].Index]=true end
 end
 for pid=1,5 do
  for i=0,Map.GetPlotCount()-1 do
   local p=Map.GetPlotByIndex(i)
   if p:GetOwner()==pid and materials[p:GetResourceType()] and p:GetImprovementType()==-1 then
    for dir=0,5 do
     local s=Map.GetAdjacentPlot(p:GetX(),p:GetY(),dir)
     local city=s and Cities.GetPlotPurchaseCity(s)
     if city and city:GetOwner()==pid and s:CanHaveDistrict(district.Index,pid,city:GetID()) then
      print('CSC_MARKER_SITE',pid,city:GetID(),s:GetIndex(),p:GetIndex(),imp.Index,district.Index,
            GameInfo.Resources[p:GetResourceType()].ResourceType,key)
     end
    end
   end
  end
 end
end
"""


def measure(study, checkpoint, folder, weight):
    pins = load(study / 'study.json')['pins']
    package = pins['packages']['csc']
    saves = Path(pins['saves'])
    source = Path(checkpoint['archive'])
    local = saves / (checkpoint['unique_name'] + '.Civ6Save')
    require(sha(source) == checkpoint['sha256'] and not native_inventory(), 'Changed source or game in use')
    if not local.exists():
        shutil.copy2(source, local)
    connector = Path(package['path']) / 'Data/CSC_Q_ALL_AI_Connectors.sql'
    original = connector.read_bytes()
    require(original == (HERE.parents[3] / 'Civ Supply Chains/Data/CSC_Q_ALL_AI_Connectors.sql').read_bytes(),
            'Installed connector differs from release')
    template = (HERE / 'possible_supplier.sql').read_bytes()
    trial = original + b'\n' + template.replace(b'__PROBE_WEIGHT__', str(weight).encode())
    folder.mkdir(parents=True)
    controller = make_probe_controller(folder, user_root=Path(pins['userdata']))
    session = NativeSession(folder, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    try:
        replace(connector, trial)
        session.start(lambda: launch(SimpleNamespace(binary=Path(pins['binary'])), folder))
        session.wait_context('MainMenu')
        select_stack(session, folder, [package['id']])
        session.load_once(local, sha256=checkpoint['sha256'], native_directory=saves, turn=checkpoint['turn'],
                          contexts=('GameCore_Tuner','PlotInfo'), eligibility=lambda: True)
        verify_modules(session, None, folder, pins['core_sha256'])
        raw = controller.cmd(SEARCH, 'PlotInfo', 'select-legal-base')
        candidates = re.finditer(r'CSC_MARKER_SITE\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\w+)\s+(\w+)', raw)
        # District placement is exposed to the UI context. Builder legality
        # is exposed to gameplay. Check both before accepting the fixture.
        for found in candidates:
            legal = controller.cmd(f"print('CSC_MARKER_LEGAL',ImprovementBuilder.CanHaveImprovement("
                                   f"Map.GetPlotByIndex({found[4]}),{found[5]},{found[1]}))",
                                   'GameCore_Tuner','check-builder-eligibility')
            if 'CSC_MARKER_LEGAL\ttrue' in legal:
                break
        else:
            raise ValueError('Missing legal material/Quarter pair: ' + raw[-500:])
        player, city, site, deposit, marker, district = map(int, found.groups()[:6])
        context = f'local p=Map.GetPlotByIndex({deposit});local s=Map.GetPlotByIndex({site});'
        result = dict(site=site, player=player, city=city, deposit=deposit, quarter=found[8],
                      resource=found[7], source=checkpoint['sha256'], weight=weight)
        for phase, change in [('unbuilt', None), ('built', marker), ('removed', -1)]:
            if change is not None:
                controller.cmd(context + f'ImprovementBuilder.SetImprovementType(p,{change},{player})',
                               'GameCore_Tuner', phase + '-diagnostic-marker')
            raw = controller.cmd(context + f"print('CSC_MARKER_READ',p:GetImprovementType(),"
                                 f"s:GetAdjacencyYield({player},{city},{district},GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index))",
                                 'PlotInfo', phase + '-private-adjacency')
            readback = re.search(r'CSC_MARKER_READ\s+(-?\d+)\s+(-?[\d.]+)', raw)
            require(readback and int(readback[1]) == (marker if phase == 'built' else -1),
                    'Unexpected improvement readback: ' + raw[-300:])
            result[phase] = float(readback[2])
        write_json(folder / 'preview.json', result)
    finally:
        try:
            if session.owner and session.owner.poll() is None:
                session.close(restore_preferences=lambda: restore_preferences(controller, folder)
                              if (folder/'original-preferences.json').exists() else None)
        finally:
            if not native_inventory():
                require(connector.read_bytes() in (original, trial), 'Concurrent connector edit')
                replace(connector, original)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study', type=Path)
    parser.add_argument('checkpoint', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    arms = []
    for weight in (0,12):
        folder = args.output / str(weight)
        if folder.exists() and not (folder/'preview.json').exists():
            folder.rename(folder.with_name(f'{weight}-attempt-{len(list(args.output.glob(f"{weight}-attempt-*")))+1}'))
        if (folder/'session-closed.json').is_file() and (folder/'preview.json').is_file():
            arms.append(load(folder/'preview.json'))
            continue
        arms.append(measure(args.study, load(args.checkpoint), folder, weight))
    control, trial = arms
    for field in ('source','site','player','city','quarter','resource','deposit'):
        require(control[field] == trial[field], 'Different matched fixture: ' + field)
    write_json(args.output / 'pair.json', dict(control=control, treatment=trial))


if __name__ == '__main__':
    main()
