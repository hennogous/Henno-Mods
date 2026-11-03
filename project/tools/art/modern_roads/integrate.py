"""Install approved road GEO/FGX, decal materials and textures without an assembly.

The private test ASTs/XLP are only for an isolated cook. Henno owns the new
district base and its state/placement choices in Asset Editor.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'project/tools/art/modern_windmill'))
import modular_v9_native as n

MOD = ROOT / 'Civ Supply Chains'
D = Path.home() / 'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'
AUTHOR = Path.home() / 'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout'
OUT = AUTHOR / 'ae-integration-20261029'
STAGE = OUT / 'staged'
PANTRY = n.DEFAULT_SDK / 'Civ6/pantry'
CHANNELS = {'B': 'BaseColor', 'H': 'Heightmap', 'FOW': 'FOWColor', 'S': 'Spec'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2))


def run(args, log, cwd=None):
    p = subprocess.run([str(v) for v in args], cwd=cwd, capture_output=True, text=True)
    log.write_text(p.stdout + p.stderr)
    assert p.returncode == 0, (args, p.stdout[-1200:], p.stderr[-1200:])


def stage():
    assert not (OUT / 'publication-report.json').exists(), 'Already installed; use scoped update'
    for folder in ('Assets', 'Geometries', 'Materials', 'Textures', 'CN6'):
        (STAGE / folder).mkdir(parents=True, exist_ok=True)
    baseline = {p.relative_to(MOD).as_posix(): sha(p)
                for folder in ('Assets', 'ArtDefs', 'XLPs')
                for p in (MOD / folder).glob('*') if p.is_file()}
    dump(OUT / 'assembly-baseline.json', baseline)
    delivery = json.loads((AUTHOR / 'delivery-validation.json').read_text())
    approved = {r['id']: r for r in delivery['models']}
    masters = json.loads((AUTHOR / 'masters.json').read_text())
    reader, _ = n.helper(OUT / 'native-reader')
    converter = ROOT / 'project/tools/cn6libs/CN6ToFGX.exe'
    checks = []
    for row in masters:
        ident = row['id']
        assert sha(row['blend']) == approved[ident]['source_sha256'], ('New source edit', ident)
        model = json.loads((AUTHOR / 'models' / (ident + '.json')).read_text())
        assert model['kind'] == 'decal'
        cn6 = STAGE / 'CN6' / (ident + '.cn6')
        n.exp.write_cn6(cn6, model)
        assert sha(cn6) == sha(Path(row['blend']).with_suffix('.cn6'))
        fgx = STAGE / 'Geometries' / (ident + '.fgx')
        run([converter, cn6, fgx, '2'], OUT / (ident + '-convert.log'), converter.parent)
        decoded = OUT / (ident + '-native.json')
        run([reader, reader.parent, fgx, decoded], OUT / (ident + '-read.log'), reader.parent)
        native = json.loads(decoded.read_text())
        assert len(native['meshes']) == len(model['meshes'])
        error = 0
        for a, b in zip(model['meshes'], native['meshes']):
            assert a['triangles'] == b['triangles'] and len(a['vertices']) == len(b['vertices'])
            assert b['boneBindings'] == ['Bone']
            assert b['materialName'] == a['materials'][0]['name']
            for v, w in zip(a['vertices'], b['vertices']):
                values = w['position'] + w['normal'] + w['tangent'] + w['binormal'] + w['uv'] + w['uv2'] + w['uv3']
                error = max(error, max(abs(x-y) for x, y in zip(v, values)))
                assert w['boneWeights'] == [255,0,0,0,0,0,0,0] and w['boneIndices'] == [0]*8
        assert error < 1e-4
        geo = n.exp.geometry(model, n.read(MOD / 'Geometries/CSC_Level_1_S.geo'))
        n.text(geo, 'm_SourceFilePath', row['blend'])
        n.text(geo, 'm_Description', 'Quarter road module; authored district coordinates; projection Z20')
        assert n.exp.txt(geo, 'm_ClassName') == 'DecalGeometry'
        n.save(STAGE / 'Geometries' / (ident + '.geo'), geo)
        # Private assembly exercises the actual decal state schema and material route.
        ast = n.fresh_asset(ident, model, n.read(MOD / 'Assets/CSC_BAKERS_Wind_Mill_Modern.ast'))
        for state in ast.findall(n.exp.MODELS + '/Element/m_GroupStates/Element'):
            values = state.findall('m_Values/m_Values/Element')
            assert {n.exp.txt(v, 'm_ParamName') for v in values} == {'Material', 'Visible'}
        n.save(STAGE / 'Assets' / (ident + '.ast'), ast)
        checks.append({'id': ident, 'source': row['blend'], 'source_sha256': sha(row['blend']),
                       'native_max_error': error, 'native_bone_material_uv_topology_pass': True})
    texture_checks = []
    for era in ('Industrial', 'Modern'):
        name = 'CSC_Roads_' + era + '_01'
        mat = n.read(PANTRY / 'Materials' / ('Decal_Parts_' + era + '_01.mtl'))
        n.text(mat, 'm_Name', name)
        n.text(mat, 'm_Description', 'Worn stone paving underlay' if era == 'Industrial' else 'Tarmac with pedestrian crossings only')
        for item in mat.findall('m_CookParams/m_Values/Element'):
            param = n.exp.txt(item, 'm_ParamName')
            ch = next((ch for ch, slot in CHANNELS.items() if slot == param), None)
            item.find('m_ObjectName').set('text', name + '_' + ch if ch else '')
        n.save(STAGE / 'Materials' / (name + '.mtl'), mat)
        for ch, slot in CHANNELS.items():
            ident = name + '_' + ch
            source = D / 'textures' / (ident + '.png')
            dds = D / 'textures/native' / (ident + '.dds')
            raw = dds.read_bytes()
            assert struct.unpack_from('<II', raw, 12) == (512,512)
            assert struct.unpack_from('<I', raw, 28)[0] == 10
            a = np.asarray(Image.open(source).convert('RGBA')).astype(int)
            b = np.asarray(Image.open(dds).convert('RGBA')).astype(int)
            delta = int(np.max(np.abs(a-b)))
            assert delta <= 1, (ident, delta)
            template = 'Active_Volcano_S' if ch == 'S' else 'Decals_Parts_' + era + '_01_' + ch
            tex = n.read(PANTRY / 'Textures' / (template + '.tex'))
            n.text(tex, 'm_Name', ident)
            n.text(tex, 'm_SourceFilePath', str(source))
            n.text(tex, 'm_DataFiles/Element/m_RelativePath', ident + '.dds')
            for key, value in [('m_Width','512'), ('m_Height','512'), ('m_NumMipMaps','9'),
                               ('m_ImportedTime','0'), ('m_ExportedTime','0'),
                               ('m_ExportSettings/ePixelformat','PF_R8G8B8A8_UNORM')]:
                tex.find(key).text = value
            assert n.exp.txt(tex, 'm_ClassName') == 'Decal_' + ('Heightmap' if ch == 'H' else slot)
            n.save(STAGE / 'Textures' / (ident + '.tex'), tex)
            shutil.copy2(dds, STAGE / 'Textures' / dds.name)
            texture_checks.append({'id': ident, 'source': str(source), 'source_sha256': sha(source),
                                   'dds_sha256': sha(dds), 'max_pixel_error': delta, 'mips': 10})
    files = [p for folder in ('Geometries','Materials','Textures') for p in (STAGE / folder).iterdir() if p.is_file()]
    assert len(files) == 46
    assert all(not (MOD / p.relative_to(STAGE)).exists() for p in files), 'Existing identity; requires selective update'
    dump(OUT / 'staging-validation.json', {'passed': True, 'geometry': checks, 'textures': texture_checks,
          'publish_files': {p.relative_to(STAGE).as_posix(): sha(p) for p in files},
          'private_test_ASTs_not_for_publication': True})
    print('STAGED: 14 DecalGeometry FGX/GEO pairs, 2 materials, 8 DDS/TEX pairs', flush=True)


def publish():
    checks = json.loads((OUT / 'staging-validation.json').read_text())
    cook = json.loads((OUT / 'cook-check/result.json').read_text())
    assert checks['passed'] and cook['exit_code'] == 0 and cook['blps']
    for row in checks['geometry']:
        assert sha(row['source']) == row['source_sha256']
    for row in checks['textures']:
        assert sha(row['source']) == row['source_sha256']
    rows = []
    for rel, digest in checks['publish_files'].items():
        assert sha(STAGE / rel) == digest and not (MOD / rel).exists(), rel
    for rel, digest in checks['publish_files'].items():
        dest = MOD / rel
        shutil.copy2(STAGE / rel, dest)
        assert sha(dest) == digest
        rows.append({'destination': str(dest), 'after': digest, 'before': None})
    baseline = json.loads((OUT / 'assembly-baseline.json').read_text())
    # User edits to existing assemblies are never overwritten by this installer.
    concurrent = [rel for rel, digest in baseline.items() if sha(MOD / rel) != digest]
    dump(OUT / 'publication-report.json', {'installed': True, 'files': rows,
          'existing_assemblies_artdefs_xlps_written': False, 'concurrent_user_changes_preserved': concurrent,
          'game_deployment': False, 'native_viewport_tested': False})
    print('INSTALLED 46 files; district assembly remains user-owned', flush=True)


def verify():
    report = json.loads((OUT / 'publication-report.json').read_text())
    cache = Path(os.environ['APPDATA']) / 'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
    data = json.loads(cache.read_text(encoding='utf-8-sig'))
    records = {r['Filename'].replace('\\','/'): r for r in data['Files']}
    missing = []
    for row in report['files']:
        path = Path(row['destination'])
        assert sha(path) == row['after'], path
        key = path.relative_to(ROOT).as_posix()
        if key not in records:
            missing.append(key)
            continue
        if path.suffix in ('.geo','.mtl','.tex'):
            xml = n.read(path)
            assert records[key]['EntityClass'] == n.exp.txt(xml,'m_ClassName')
            deps = {s.replace('\\','/') for s in data['Dependencies'][key]}
            expected = {(path.parent / x.get('text')).relative_to(ROOT).as_posix()
                        for x in xml.findall('m_DataFiles/Element/m_RelativePath')}
            for item in xml.findall('m_CookParams/m_Values/Element'):
                name = n.exp.txt(item,'m_ObjectName')
                if name:
                    expected.add((MOD / 'Textures' / (name+'.tex')).relative_to(ROOT).as_posix())
            assert deps == expected, (key,deps,expected)
    dump(OUT / 'final-verification.json', {'installed_files_verified': len(report['files']),
          'missing_browser_entries': missing, 'browser_dependencies_verified': not missing,
          'cook_passed': True, 'native_viewport_and_game_tested': False})
    assert not missing, missing
    print(f"VERIFIED: {len(report['files'])} installed files, browser entries/dependencies and isolated cook", flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'cache':
        n.cache(OUT)
    else:
        globals()[sys.argv[1]]()
