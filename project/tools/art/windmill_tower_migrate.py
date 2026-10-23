"""Stage native storage UV migration without reauthoring native geometry."""
import json,sys,subprocess,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains'
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from render_ae_asset import helper

def region_at(regions,x,y):
    if x<511.9 or y<511.9:return None
    hits=[r for r in regions if r['uv_bounds'][0]-.15<=x<=r['uv_bounds'][2]+.15 and r['uv_bounds'][1]-.15<=y<=r['uv_bounds'][3]+.15]
    assert len(hits)==1,(x,y,[r['id'] for r in hits])
    return hits[0]

def main(out):
    regions=json.loads((out/'atlas-migration.json').read_text())['regions']
    consumers=json.loads((out/'atlas-consumers.json').read_text())['geometries']
    extract,_=helper(out/'cache');bridge=extract.parent;patch=bridge/'PatchAtlasUV.exe'
    cmd=[r'C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe','/nologo','/platform:x64',f'/out:{patch}','/r:System.Windows.Forms.dll','/r:System.Web.Extensions.dll']
    cmd += [f'/r:{bridge/n}' for n in ['Firaxis.IO.dll','Firaxis.Utility.dll','Firaxis.Granny.dll','CivNexus6.exe']]+[str(Path(__file__).with_name('PatchAtlasUV.cs'))]
    subprocess.run(cmd,check=True,capture_output=True)
    stage=out/'staged/Geometries';stage.mkdir(parents=True,exist_ok=True)
    before=out/'before/Geometries';before.mkdir(parents=True,exist_ok=True)
    report={}
    for name,consumer in consumers.items():
        original=MOD/f'Geometries/{name}.fgx'
        assert hashlib.sha256(original.read_bytes()).hexdigest()==consumer['native_hash'],name+' changed since audit'
        raw=json.loads((out/f'native/{name}.json').read_text());edits={}
        meshes={m['name']:m for m in raw['meshes']}
        for rng in consumer['ranges']:
            m=meshes[rng['mesh']]
            for i in {i for tri in m['triangles'][rng['first']:rng['first']+rng['count']] for i in tri[:3]}:
                u,v=m['vertices'][i]['uv'];r=region_at(regions,u*1024,v*1024)
                if r:edits.setdefault(m['name'],{})[str(i)]=[u,v,u+r['delta'][0]/1024,v+r['delta'][1]/1024]
        ep=out/(name+'-uv-edits.json');ep.write_text(json.dumps(edits))
        for ext in ('.fgx','.geo'):
            src=MOD/f'Geometries/{name}{ext}';shutil.copy2(src,before/src.name)
        shutil.copy2(MOD/f'Geometries/{name}.geo',stage/(name+'.geo'))
        result=subprocess.run([str(patch),str(original),str(stage/original.name),str(ep)],cwd=bridge,capture_output=True,text=True)
        (out/(name+'-migration.log')).write_text(result.stdout+result.stderr)
        assert result.returncode==0,result.stdout+result.stderr
        target=out/(name+'-migrated.json')
        subprocess.run([str(extract),str(bridge),str(stage/original.name),str(target)],cwd=bridge,capture_output=True,check=True)
        new=json.loads(target.read_text());assert new['models']==raw['models'],name+' skeleton/placement changed'
        for m,b in zip(raw['meshes'],new['meshes']):
            assert m['triangles']==b['triangles'] and m['boneBindings']==b['boneBindings']
            for i,(v,w) in enumerate(zip(m['vertices'],b['vertices'])):
                assert {k:x for k,x in v.items() if k!='uv'}=={k:x for k,x in w.items() if k!='uv'}
                expected=edits.get(m['name'],{}).get(str(i),[*v['uv'],*v['uv']])[2:]
                assert max(abs(a-b) for a,b in zip(expected,w['uv']))<1e-7
        report[name]={'moved_vertices':sum(map(len,edits.values())),'native_buffers_verified':True,'skeleton_and_placements_unchanged':True}
        print(name,report[name],flush=True)
    (out/'native-migration-validation.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':main(Path(sys.argv[1]))
