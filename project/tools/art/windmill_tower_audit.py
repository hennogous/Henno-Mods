"""Read native atlas consumers before the windmill/storage quadrant migration."""
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'project/tools/blender'))
from render_ae_asset import read_xml, txt, values, texture_bindings, helper, digest

MOD = ROOT / 'Civ Supply Chains'
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
materials = {}
for path in (MOD / 'Materials').glob('*.mtl'):
    bindings = texture_bindings(read_xml(path))
    if bindings.get('BaseColor', '').startswith('CSC_Atlas_B_'):
        materials[path.stem] = bindings
consumers = {}
for path in (MOD / 'Assets').glob('*.ast'):
    root = read_xml(path)
    for model in root.findall('m_GeometrySet/m_ModelInstances/Element'):
        geo = txt(model, 'm_GeoName')
        for state in model.findall('m_GroupStates/Element'):
            mat = values(state).get('Material', '')
            if mat in materials:
                record = consumers.setdefault(geo, {'assets': [], 'groups': []})
                if path.stem not in record['assets']:
                    record['assets'].append(path.stem)
                pair = [txt(state, 'm_MeshName'), txt(state, 'm_GroupName')]
                if pair not in record['groups']:
                    record['groups'].append(pair)
exe, fingerprint = helper(OUT / 'cache')
total = Image.new('L', (1024, 1024))
records = {}
for name, consumer in consumers.items():
    geo_path = MOD / 'Geometries' / (name + '.geo')
    if not geo_path.exists():
        raise FileNotFoundError(geo_path)
    geo = read_xml(geo_path)
    fgx = MOD / 'Geometries' / (name + '.fgx')
    target = OUT / 'native' / (name + '.json')
    target.parent.mkdir(exist_ok=True)
    if not target.exists():
        subprocess.run([str(exe), str(exe.parent), str(fgx), str(target)], cwd=exe.parent,
                       check=True, capture_output=True)
    raw = json.loads(target.read_text())
    meshes = {m['name']: m for m in raw['meshes']}
    mask = Image.new('L', (1024, 1024)); draw = ImageDraw.Draw(mask)
    groups = []
    for mesh in geo.findall('m_Meshes/Element'):
        mesh_name = txt(mesh, 'm_Name')
        for group in mesh.findall('m_Groups/Element'):
            group_name = txt(group, 'm_Name')
            if [mesh_name, group_name] not in consumer['groups']:
                continue
            first = int(txt(group, 'm_nFirstPrim')); count = int(txt(group, 'm_nPrims'))
            src = meshes[mesh_name]
            for tri in src['triangles'][first:first+count]:
                pts = [(src['vertices'][i]['uv'][0]*1024, src['vertices'][i]['uv'][1]*1024) for i in tri[:3]]
                draw.polygon(pts, fill=255)
            groups.append({'mesh': mesh_name, 'group': group_name, 'first': first, 'count': count})
    bbox = mask.crop((512, 512, 1024, 1024)).getbbox()
    if bbox:
        mask.save(OUT / (name + '-uv.png'))
        records[name] = {**consumer, 'native_hash': digest(fgx), 'ranges': groups,
                         'quadrant_bbox': [v+512 for v in bbox]}
        from PIL import ImageChops
        total = ImageChops.lighter(total, mask)
        print(name, records[name]['quadrant_bbox'], flush=True)
total.save(OUT / 'all-uv-coverage.png')
color = Image.open(Path.home() / 'Desktop/Working Files/3D Art/Textures/CSC_Atlas_B_BAKERS.dds').convert('RGB')
overlay = Image.new('RGB', (1024,1024), (255,0,90))
Image.blend(color, Image.composite(overlay, color, total), .35).save(OUT/'coverage-review.png')
(OUT/'atlas-consumers.json').write_text(json.dumps({'materials': materials, 'geometries': records}, indent=2))
print('AUDITED', len(consumers), 'geometries;', len(records), 'use storage quadrant')
