"""Publish the timber revision through the established shared-atlas pipeline."""
import sys,json,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(sys.argv[2])
source=(Path(__file__).with_name('integrate_windmill_shared_materials.py')).read_text()
source=source[:source.index('def install():')]
source=source.replace('2026-10-21_Shared_01_r036','2026-10-22_Shared_01_r037').replace("accepted_on='2026-10-21',content_revision=36","accepted_on='2026-10-22',content_revision=37")
start=source.index('            for f in manifest[');end=source.index("            path=ATLAS/",start)
source=source[:start]+'''            allocation=next(a for f in manifest['pages'][0]['quarters'][0]['families'] for a in f.get('allocations',[]) if a['id']==bake['id'])
            assert allocation['cell']==bake['cell']
'''+source[end:]
source=source.replace("family.setdefault('allocations',[]).append(dict(","allocation.update(dict(")
source=source.replace("            occupied=np.array(Image.open(OUT/'AO2-occupied.png'));assert not occupied[y:y1,x:x1].any()","            assert bake['cell'] in [[516,976,580,1020],[584,976,648,1020]]")
source=source.replace('windmill sail and timber AO in unused Bakers Stage2 cells; all other allocations preserved.','wider timber windmill and expanded sails rebaked in their existing cells; all other allocations preserved.')
source=source.replace('Henno requested shared sail AO, Level1 tower material and the authored Level1 scaffold on 21 October 2026.','Henno requested a wider wooden tower, painted diagonal brace, larger cloth and removal of the rear scaffold on 22 October 2026.')
exec(compile(source,str(__file__),'exec'))
def stage():
    prepare()
    # Independent saved-FGX contract: each rigid moving part has exactly its
    # intended real bone, with no synthetic-root padding binding.
    checks=[]
    for name in (NAME,RUIN):
        raw=json.loads((OUT/(name+'-native.json')).read_text());geo=read_xml(STAGE/f'Geometries/{name}.geo')
        assert geo.tag=='AssetObjects..GeometryInstance'
        for mesh in raw['meshes']:
            intended='Sails' if mesh['name'].endswith('_Sails') else 'Root'
            assert mesh['boneBindings']==[intended],(mesh['name'],mesh['boneBindings'])
            node=next(n for n in geo.findall('m_Meshes/Element') if txt(n,'m_Name')==mesh['name'])
            assert int(node.findtext('m_nBoundBoneCount'))==1
            assert all(v['boneIndices'][0]==0 and v['boneWeights'][0]==255 and sum(v['boneWeights'])==255 for v in mesh['vertices'])
            checks.append(dict(mesh=mesh['name'],bindings=mesh['boneBindings'],vertices=len(mesh['vertices']),triangles=len(mesh['triangles']),groups=mesh['groups']))
    (OUT/'native-export-contract.json').write_text(json.dumps(checks,indent=2))
    rows=json.loads((OUT/'install-plan.json').read_text());backup=OUT/'before-installed'
    files=[]
    # The base geometry includes both front and rear scaffolds in one group.
    # Its front section is now embedded at the identical world placement in the
    # windmill CON+PIL. Disable only that shared group in these two assemblies.
    for suffix in ['', '_2']:
        path=STAGE/'Assets'/('CSC_BAKERS_Wind_Mill'+suffix+'.ast');asset=read_xml(path)
        changed=0
        for row in asset.findall('.//m_GroupStates/Element'):
            if txt(row,'m_MeshName')!='Scaffolding':continue
            for value in row.findall('.//Element'):
                if txt(value,'m_ParamName')=='Visible' and value.findtext('m_bValue')=='true':value.find('m_bValue').text='false';changed+=1
        assert changed==1,(suffix,changed)
        save(asset,path);files.append((path,MOD/'Assets'/path.name))
    layout=json.loads((SOURCE/'atlas-migration.json').read_text())
    layout['tower_plaster'].update(surface='wooden planks with painted diagonal brace',replaced_on='2026-10-22',source=str(SOURCE/'wood-revision-20261022/Wood_B.png'),normal_height_source=str(SOURCE/'wood-revision-20261022/Wood_H.png'))
    (OUT/'atlas-migration.json').write_text(json.dumps(layout,indent=2));files.append((OUT/'atlas-migration.json',SOURCE/'atlas-migration.json'))
    for name in ['CSC_Atlas_B_BAKERS','CSC_Atlas_B_BAKERS_2','CSC_Atlas_B_TAILORS','CSC_Atlas_B_TAILORS_2','CSC_Atlas_N','CSC_Atlas_G','CSC_Atlas_M']:
        files.append((STAGE/'Textures'/(name+'.dds'),ART/'Textures'/(name+'.dds')))
        png=ART/'Textures'/(name+'.png')
        if png.exists():files.append((OUT/'staged-textures'/(name+'.png'),png))
    files.extend((p,ART/'Textures'/p.name) for p in (OUT/'staged-xcf').glob('*.xcf'))
    assert len(list((OUT/'staged-xcf').glob('*.xcf')))==4
    for src,dst in files:
        b=backup/(str(len(rows))+'-'+dst.name);shutil.copy2(dst,b);rows.append(dict(source=str(src),destination=str(dst),backup=str(b),before=sha(dst)))
    (OUT/'install-plan.json').write_text(json.dumps(rows,indent=2))
    old=Path.home()/'Desktop/Codex/windmill-tower-20261021/shared-materials'
    for f in ['native-animation-transforms.npz','validate-motion.py']:shutil.copy2(old/f,OUT/f)
    print('WOOD_REVISION_STAGED',len(rows),'files; native real bindings verified')

def install():
    for row in json.loads((OUT/'inspection.json').read_text()):assert sha(row['path'])==row['sha']
    for row in json.loads((OUT/'texture-baseline.json').read_text()):assert sha(row['path'])==row['sha256']
    for row in json.loads((OUT/'xcf-baseline.json').read_text()):assert sha(row['path'])==row['before']
    for p,h in json.loads((OUT/'baseline.json').read_text()).items():assert sha(p)==h,p
    result=json.loads((OUT/'cook-wood/result.json').read_text());log=(OUT/'cook-wood/stdout.log').read_text()
    assert result['exit_code']==0 and 'XLP cook completed with success.' in log and '(ERRORS!!)' not in log and 'Replacing asset:' not in log
    assert json.loads((OUT/'sail-clearance.json').read_text())=={}
    assert json.loads((OUT/'native-animation-validation.json').read_text())['frames_checked']==301
    for name in [NAME,RUIN]:
        v=json.loads((OUT/(name+'-source-validation.json')).read_text());assert v['error_count']==v['warning_count']==0
    rows=json.loads((OUT/'install-plan.json').read_text())
    for r in rows:assert sha(r['destination'])==r['before'],r['destination']
    assert not (LIB/'Releases'/RELEASE).exists()
    shutil.copytree(LIB/'Current',OUT/'before-library');shutil.copy2(LIB/'CURRENT.json',OUT/'before-CURRENT.json')
    shutil.copytree(ATLAS,LIB/'Releases'/RELEASE);shutil.copytree(ATLAS,LIB/'Current',dirs_exist_ok=True)
    (LIB/'CURRENT.json').write_text(json.dumps(dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-22',library_sha256=sha(LIB/'Current/library.json')),indent=2)+'\n')
    for r in rows:
        dst=Path(r['destination']);tmp=dst.with_name(dst.name+'.wood-tmp');shutil.copy2(r['source'],tmp);os.replace(tmp,dst);r['installed_sha256']=sha(dst)
    artwork=SOURCE/'wood-revision-20261022';shutil.copytree(OUT/'artwork',artwork,dirs_exist_ok=True)
    shutil.copy2(OUT/'wood-slot.json',artwork/'slot.json')
    (OUT/'publication-report.json').write_text(json.dumps(dict(installed=True,release=RELEASE,files=rows,brace_geometry=False,UV1_UV3_preserved=True),indent=2));print('WOOD_REVISION_INSTALLED',len(rows))
if __name__=='__main__':globals()[sys.argv[1]]()
