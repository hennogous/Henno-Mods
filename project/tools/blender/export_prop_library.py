"""Inventory and package the initial CSC source-asset Blender library."""
import json
import pathlib
import xml.etree.ElementTree as ET
import shutil
import subprocess
import re

ROOT = pathlib.Path(__file__).resolve().parents[3]
SDK = pathlib.Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK Assets")
MOD = ROOT / 'Civ Supply Chains'
STAGE = ROOT / 'project/prop-library-export'
def txt(e, path, default=''):
    n=e.find(path)
    return n.get('text', n.text or default) if n is not None else default
def main():
    STAGE.mkdir(exist_ok=True)
    inventory=ET.parse(MOD/'Assets/CSC_ALL_Prop_Library.ast').getroot()
    ids=sorted({e.get('text') for e in inventory.findall('.//m_EntryName')})
    packs={}
    for fn,pack in [('civ6','Base game'),('expansion1','Rise and Fall'),('expansion2','Gathering Storm'),('shared','Shared (unresolved)')]:
        d=json.loads((SDK/(fn+'-asset-deps.json')).read_text())
        for f in d['Files']:
            packs.setdefault(pathlib.Path(f['Filename']).name.lower(),[]).append((pack,f['Filename']))
    index={}
    for root in [SDK,MOD]:
        for ext in ['*.ast','*.geo','*.fgx','*.mtl','*.tex','*.dds']:
            for p in root.rglob(ext):
                if 'Archive' not in p.parts: index.setdefault(p.name.lower(),[]).append(str(p))
    rows=[]
    for aid in ids:
        candidates=index.get((aid+'.ast').lower(),[])
        p=next((p for p in candidates if str(MOD) in p),candidates[0] if candidates else None)
        evidence=packs.get((aid+'.ast').lower(),[])
        row=dict(asset_id=aid,source_ast=p,provenance=evidence,source_pack='CSC' if aid.startswith('CSC_') else next((x[0] for x in evidence if x[0]!='Shared (unresolved)'),'UNRESOLVED'))
        if p:
            ast=ET.parse(p).getroot()
            row['models']=[dict(geometry=txt(e,'m_GeoName'),instance=txt(e,'m_Name'),xml=ET.tostring(e,encoding='unicode')) for e in ast.findall('./m_GeometrySet/m_ModelInstances/Element')]
        rows.append(row)
    (STAGE/'inventory.json').write_text(json.dumps(rows,indent=2))
    (STAGE/'file_index.json').write_text(json.dumps(index))
    for r in rows: print(r['asset_id'],r['source_pack'],[(m['geometry'],m['instance']) for m in r.get('models',[])])
def prepare():
    rows=json.loads((STAGE/'inventory.json').read_text())
    index=json.loads((STAGE/'file_index.json').read_text())
    out=STAGE/'CSC_Prop_Library'
    out.mkdir(exist_ok=True)
    def resolve(name,ext):
        paths=index.get((name+ext).lower(),[])
        # Prefer CSC for CSC names; prefer the asset's package directory otherwise.
        paths=sorted(paths,key=lambda p: (0 if str(MOD) in p else 1,len(p)))
        if not paths: raise FileNotFoundError(name+ext)
        return pathlib.Path(paths[0])
    def copy(p,folder):
        target=out/folder/p.name;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=p.read_bytes(): raise ValueError('Name collision '+str(target))
        shutil.copy2(p,target)
        return target.relative_to(out).as_posix()
    def values(e):
        return {txt(v,'m_ParamName'):txt(v,'m_ObjectName') for v in e.findall('.//Element') if txt(v,'m_eObjectType')=='TEXTURE' and txt(v,'m_ObjectName')}
    materials={}
    for row in rows:
        row['issues']=[]
        if row['source_pack']=='UNRESOLVED': row['status']='blocked';continue
        ast=ET.parse(row['source_ast']).getroot()
        row['source_ast_copy']=copy(pathlib.Path(row['source_ast']),'sources/assets')
        row['asset_texture_overrides']=values(ast.find('m_CookParams'))
        row['material_ids']=sorted({txt(e,'m_ObjectName') for e in ast.findall('.//Element') if txt(e,'m_eObjectType')=='MATERIAL' and txt(e,'m_ParamName')=='Material' and txt(e,'m_ObjectName')})
        for name in row['material_ids']:
            if name not in materials:
                mtl=resolve(name,'.mtl');m=ET.parse(mtl).getroot()
                materials[name]=dict(source=copy(mtl,'sources/materials'),textures=values(m),shader=txt(m,'m_ClassName'))
        texnames=set(row['asset_texture_overrides'].values())
        for name in row['material_ids']: texnames.update(materials[name]['textures'].values())
        row['textures']={}
        for name in sorted(texnames):
            try:
                p=resolve(name,'.dds');rel=copy(p,'textures');row['textures'][name]=rel
                try: copy(resolve(name,'.tex'),'sources/textures')
                except FileNotFoundError: pass
            except FileNotFoundError as e: row['issues'].append(str(e))
        for model in row['models']:
            geo=resolve(model['geometry'],'.geo');g=ET.fromstring(re.sub(r'(<\/?)([\w.]+):',r'\1\2.',geo.read_text(encoding='utf-8-sig')))
            model['geo_copy']=copy(geo,'sources/geometries')
            fgx=geo.parent/txt(g,'m_DataFiles/Element/m_RelativePath')
            if not fgx.exists(): fgx=resolve(model['geometry'],'.fgx')
            model['fgx_copy']=copy(fgx,'sources/geometries')
            dest=out/'sources/geometries'/(model['geometry']+'.json')
            if not dest.exists():
                subprocess.run([str(STAGE/'ExtractPropFgx.exe'),str(ROOT/'project/tools/cn6libs'),str(fgx),str(dest)],check=True,cwd=ROOT/'project/tools/cn6libs')
            model['extracted']=dest.relative_to(out).as_posix()
        row['status']='prepared'
    copy(MOD/'Assets/CSC_ALL_Prop_Library.ast','sources/inventory')
    # A refreshed pantry export must not erase locally authored reusable assets.
    previous=json.loads((out/'catalogue.json').read_text()) if (out/'catalogue.json').is_file() else {}
    authored=[r for r in previous.get('assets',[]) if r.get('origin')=='authored_blender']
    conflicts={r['asset_id'] for r in rows}&{r['asset_id'] for r in authored}
    if conflicts: raise ValueError('Authored/source identity collision; reconcile explicitly: '+', '.join(sorted(conflicts)))
    combined_materials=dict(previous.get('materials',{}));combined_materials.update(materials)
    previous.update(assets=rows+authored,materials=combined_materials)
    (out/'catalogue.json').write_text(json.dumps(previous,indent=2))
    print('Prepared',len(rows),'assets;',len(materials),'materials')
if __name__=='__main__':
    import sys
    prepare() if '--prepare' in sys.argv else main()
