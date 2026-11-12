"""Load a closed measured world and read Quarter adjacency without advancing.

The maintained shared controller owns launch, save load, console and cleanup.
Packages are exact archived inputs; this reader never edits them or submits
gameplay actions. Active CSC property amounts, geometry-only Mill alternatives
and native adjacency are separate observations. No new game is started.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
from types import SimpleNamespace
import traceback
from ce_bakers_fresh import package_identity
from ce_replay import DLL,HOTFIX_EXE_SHA,verify_modules
from driver import (HERE,HOTFIX_SHA,HeldProcess,NativeSession,configure,flags,launch,load,lua,
    make_probe_controller,manifest,native_inventory,read,restore_preferences,sha,write_json)

NAMES=('CSC Bakers Development CE','CSC Bakers Development Mod')


def parse_rows(raw):
    rows=[json.loads(r)for r in re.findall(r'CSC_QUARTER_ADJ_ROW\t([^\r\n]+)',raw)]
    footer=re.findall(r'CSC_QUARTER_ADJ_END\s+(\d+)\s+(\d+)\s+(\d+)',raw)
    assert len(footer)==1
    turn,sites,count=map(int,footer[0])
    assert count==len(rows)and sites==sum(r['kind']=='site'for r in rows),'Incomplete adjacency census'
    assert len({r['plot']for r in rows if r['kind']=='site'})==sites
    return dict(turn=turn,sites=sites,rows=rows)


def run(a):
    quarters=getattr(a,'quarter',None)or ['BAKERS','TAILORS']
    source=a.source.resolve(strict=True);out=a.output.resolve();home=a.my_games.resolve(strict=True)
    assert load(source/'result.json')['closed']and load(source/'session-closed.json')['verified']
    checkpoint=load(source/'checkpoint.json');turn=checkpoint['turn']
    assert turn==250 and checkpoint['verified']and checkpoint['save_complete_event']
    save=Path(checkpoint['native_save']).resolve(strict=True)
    assert save.parent==(home/'Saves/Single').resolve()and sha(save)==checkpoint['sha256']==sha(source/'endpoint.Civ6Save')
    original=load(source/'source.json');expected=[]
    for kind,value in load(source/'full-census-250.json')['rows']:
        fields=value.split('\t')
        if kind=='QUARTER'and fields[0]in quarters:
            expected.append((int(fields[1]),int(fields[2]),int(fields[3]),fields[4]=='true',fields[5]=='true'))
    packages={source/name:home/'Mods'/name for name in NAMES}
    assert not out.exists()and not native_inventory()and not any(p.exists()for p in packages.values())
    ledger=load(source/'packages.json');pins={p:manifest(p)for p in packages}
    for p in packages:
        proof,=[row for row in ledger.values()if Path(row['install']).name==p.name]
        assert pins[p]==proof['files'],'Archived input changed'
    ce,csc=packages;ce_id,_=package_identity(ce);csc_id,_=package_identity(csc)
    binary=Path(load(source/'launch-bootstrap.json')['binary']);assert sha(binary)==HOTFIX_EXE_SHA
    scope=dict(turn=turn,players=original['original_ai'],quarters=quarters)
    out.mkdir(parents=True)
    write_json(out/'inputs.json',dict(source=str(source),save_sha256=checkpoint['sha256'],scope=scope,
        expected=expected,packages={p.name:pin for p,pin in pins.items()},turns_advanced=0))
    for name in('quarter_adjacency_snapshot.py','quarter_adjacency_read.lua'):
        shutil.copyfile(HERE/name,out/name)
    controller=make_probe_controller(out,user_root=a.user_root)
    session=NativeSession(out,controller,inventory=native_inventory,hold=HeldProcess,write=write_json)
    copied=[]
    def verify():
        assert all(manifest(packages[p])==pins[p]for p in copied),'Runtime package changed'
    try:
        for p,target in packages.items():shutil.copytree(p,target);copied.append(p)
        verify();session.start(lambda:launch(SimpleNamespace(binary=binary),out))
        session.wait_context('MainMenu');configure(controller,out,csc_id=ce_id)
        session.issue_once('enable-csc',"""local selected
for _,m in ipairs(Modding.GetInstalledMods())do if m.Id=='"""+csc_id+"""'then assert(not selected);selected=m end end
assert(selected and Modding.CanEnableMod(selected.Handle)=='OK');Modding.EnableMod(selected.Handle,true)
""",'MainMenu')
        assert {k for k,v in flags(controller,'verify-exact-pair')['mods'].items()if v}=={ce_id,csc_id}
        def capture():
            verify_modules(session,(packages[ce]/'Binaries/Win64'/DLL).resolve(),out,HOTFIX_SHA)
            before=controller.state_read('before-adjacency-read');assert before['turn']==turn and not before['active']
            code=read(out/'quarter_adjacency_read.lua').replace('__SCOPE__',lua(scope))
            raw=controller.cmd(code,'CSC_AI_BakersGameplay','read-quarter-adjacency')
            (out/'adjacency-raw.txt').write_text(raw,encoding='utf-8')
            result=parse_rows(raw);assert result['turn']==turn
            actual=sorted((r['player'],r['city'],r['plot'],r['complete'],r['pillaged'])for r in result['rows']if r['kind']=='site')
            assert actual==sorted(expected),'Quarter identities or lifecycle changed'
            write_json(out/'adjacency.json',result)
            ui="local sites="+lua([r for r in result['rows']if r['kind']=='site'])+"""
local count=0
for _,s in ipairs(sites)do
 local plot=assert(Map.GetPlotByIndex(s.plot));local city=assert(CityManager.GetCity(s.player,s.city))
 local p=plot:GetAdjacencyYield(s.player,s.city,GameInfo.Districts['DISTRICT_CSC_'..s.quarter..'_QUARTER'].Index,GameInfo.Yields.YIELD_PRODUCTION.Index)
 local g=plot:GetAdjacencyYield(s.player,s.city,GameInfo.Districts['DISTRICT_CSC_'..s.quarter..'_QUARTER'].Index,GameInfo.Yields.YIELD_GOLD.Index)
 print('CSC_QUARTER_ADJ_UI',s.plot,p,g,Locale.Lookup(city:GetName()));count=count+1
end
print('CSC_QUARTER_ADJ_UI_END',Game.GetCurrentGameTurn(),count)
"""
            raw=controller.cmd(ui,'PlotInfo','read-native-adjacency-and-city-names')
            (out/'adjacency-ui.txt').write_text(raw,encoding='utf-8')
            uirows=re.findall(r'CSC_QUARTER_ADJ_UI\s+(\d+)\s+([-\d.]+)\s+([-\d.]+)\t([^\r\n]+)',raw)
            assert len(uirows)==len(expected)and re.search(r'CSC_QUARTER_ADJ_UI_END\s+250\s+'+str(len(expected)),raw)
            write_json(out/'native-adjacency.json',[dict(plot=int(i),production=float(p),gold=float(g),name=name)for i,p,g,name in uirows])
            after=controller.state_read('after-adjacency-read');assert after['turn']==turn and not after['active']
            assert after['local_player']==before['local_player']==0 and after['player0_human']and before['player0_human']
            write_json(out/'read-phase.json',dict(before=before,after=after,turns_advanced=0))
            return True
        session.load_once(save,sha256=checkpoint['sha256'],native_directory=home/'Saves/Single',turn=turn,
            contexts=('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay'),eligibility=capture)
    except Exception as error:
        write_json(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()));raise
    finally:
        if session.owner is not None and session.owner.poll()is None:
            session.close(restore_preferences=lambda:restore_preferences(controller,out)
                if(out/'original-preferences.json').exists()else None,restore_package=verify)
        if session.closed:
            for p in copied:packages[p].rename(out/p.name)
    assert session.closed and sha(save)==checkpoint['sha256']
    write_json(out/'complete.json',dict(verified=True,turn=turn,turns_advanced=0,quarters=quarters,sites=len(expected)))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in('source','output','my-games','user-root'):parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--quarter',choices=('BAKERS','TAILORS'),action='append')
    run(parser.parse_args())
