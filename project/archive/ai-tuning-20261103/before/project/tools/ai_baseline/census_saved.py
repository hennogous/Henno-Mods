"""Read complete map terrain from original turn-200 saves, without advancing."""
import argparse
import json
from pathlib import Path
import re
from run import Runner, write
from continue_saved import read, sha

LUA='''local a={};local w,h=Map.GetGridSize();for i=0,w*h-1 do local p=Map.GetPlotByIndex(i);local t=GameInfo.Terrains[p:GetTerrainType()];local f=GameInfo.Features[p:GetFeatureType()];local r=GameInfo.Resources[p:GetResourceType()];a[#a+1]=string.format('{"index":%d,"x":%d,"y":%d,"terrain":"%s","feature":"%s","resource":"%s","owner":%d,"water":%s,"impassable":%s}',i,p:GetX(),p:GetY(),t and t.TerrainType or '',f and f.FeatureType or '',r and r.ResourceType or '',p:GetOwner(),tostring(p:IsWater()),tostring(p:IsImpassable()));end;print('CSCMAP_JSON={"turn":'..Game.GetCurrentGameTurn()..',"plots":['..table.concat(a,',')..']}');'''

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=Runner(a.output);r.config()
    try:
        for i in range(1,6):
            folder=a.source/f'game-{i:02d}';meta=read(folder/'save.json');path=folder/Path(meta['path']).name
            assert sha(path)==meta['sha256']
            r.say(f'Map census {i}: loading original turn200 save')
            r.cmd(f'Automation.SetAutoStartEnabled(true);Network.LoadGame({json.dumps(str(path))},ServerType.SERVER_TYPE_NONE);','MainMenu',f'load-{i}',wait=3,check=False)
            r.wait('CSC_AdjacencyGameplay',300)
            text=r.cmd(LUA,'CSC_AdjacencyGameplay',f'map-{i}',wait=5)
            data=json.loads(re.search(r'CSCMAP_JSON=([^\r\n]+)',text).group(1));assert data['turn']==200
            assert len(data['plots'])==74*46
            write(a.output/f'game-{i:02d}'/'map.json',data)
            r.say(f'Map census {i}: all3404 plots read at200')
            r.menu()
        r.restore();write(a.output/'complete.json',{'status':'complete','games':5,'turns_advanced':0})
    except BaseException as exc:
        write(a.output/'error.json',{'error':str(exc)});raise

if __name__=='__main__':main()
