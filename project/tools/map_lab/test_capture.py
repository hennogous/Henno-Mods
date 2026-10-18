"""Verify observation wrappers preserve RNG/output and respect read-only libraries."""
import argparse
from pathlib import Path
from offline import OfflineWorld, read


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('map','database','game-root','workshop-root','lua-dependencies'): p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();native=read(a.map)
    def new(): return OfflineWorld(native,a.database,a.game_root,a.workshop_root,12345,3,a.lua_dependencies)
    plain=new();expected=plain.run('stock',6)
    observed=new();observed.bootstrap();observed.lua.execute('for _,p in ipairs(OFFLINE_DATA.plots) do p.resource=nil end')
    observed.execute(a.game_root/'DLC/Expansion2/Maps/Utility/ResourceGenerator.lua')
    observed.lua.execute("local original=table;table=setmetatable({},{__index=original,__newindex=function()error('Attempt to modify read-only table')end})")
    observed.lua.execute((Path(__file__).parent.parent/'map_survey/calibration_capture.lua').read_text())
    observed.lua.execute('CSCcalBegin();ResourceGenerator.Create{resources=3,LuxuriesPerRegion=6,START_CONFIG=2};CSCcalResourcesEnd();CSCcalEnd();')
    resources=[observed.lua.globals().OFFLINE_DATA.plots[i+1].resource for i in range(len(native['plots']))]
    assert resources==[p.get('resource') for p in expected['plots']]
    assert observed.rng.getstate()==plain.rng.getstate()
    assert any('CSC_CAL_DATA\tsorts\t' in line for line in observed.logs)
    print('PASS: read-only standard table respected; RNG state and all resource tiles unchanged; sort observations captured')


if __name__=='__main__': main()
