"""Deterministic CSC building export rules and staged XML validation."""
import argparse
import json
from pathlib import Path

QUARTERS = ('BAKERS', 'TAILORS', 'APOTHECARIES', 'STONEMASONS',
            'CARPENTERS', 'BLACKSMITHS', 'GOLDSMITHS', 'BREWERS')
STATES = ('Worked', 'Unworked', 'Pillaged', 'Construction', 'Unbuilt')
COBBLE_MATERIAL = 'CSC_ALL_Cobble_Patch_Decal'


def material_for_mesh(mesh, mat, contract, job):
    """Preserve prop material groups even when authored inside the main mesh."""
    fixed = (mesh['role'] == 'fixed_geometry' or mesh['name'].startswith('CSC_Fixed_')) and \
            'leanto' not in mesh['name'].casefold()
    declared = mat.get('external') or job.get('material_bindings', {}).get(mat['name'])
    if fixed or declared in ('CSC_ALL_Props_01', 'CSC_ALL_Props_02'):
        return contract['prop_material']
    return contract['building_material']


def contract_for(asset_id, metadata, mod):
    """Resolve an explicit scene declaration; never infer the building level from a name."""
    from export_scene import read_xml, txt
    quarter = metadata.get('quarter')
    stage = metadata.get('supply_chain_stage')
    if quarter not in QUARTERS or not asset_id.startswith(f'CSC_{quarter}_'):
        raise ValueError(f'{asset_id}: csc_export.quarter must match a CSC Quarter prefix')
    if type(stage) is not int or stage not in (2, 3, 4):
        raise ValueError(f'{asset_id}: csc_export.supply_chain_stage must be 2, 3 or 4')
    atlas = 1 if QUARTERS.index(quarter) < 4 else 2
    result = {'asset_id': asset_id, 'quarter': quarter, 'supply_chain_stage': stage,
              'building_level': stage - 1, 'building_material': f'CSC_{quarter}_E',
              'ruin_material': f'CSC_{quarter}_NE',
              'prop_material': f'CSC_ALL_Props_{atlas:02}',
              'main_visible': ['Worked'], 'fixed_visible': ['Worked'],
              'new_prop_visible': ['Worked']}
    required = [result['building_material'], result['prop_material'],
                result['ruin_material']]
    if stage == 2:
        ruin_id = metadata.get('construction_geometry')
        if ruin_id not in ('CSC_Level_1_CON+PIL', 'CSC_Level_1_S_CON+PIL'):
            raise ValueError(f'{asset_id}: Stage 2 needs csc_export.construction_geometry (full or small Level 1)')
        result['ruin_geometry'] = ruin_id
        result['ruin_visible'] = ['Construction', 'Pillaged']
    else:
        level = stage - 1
        result.update(ruin_geometry=metadata.get('construction_geometry') or f'CSC_Level_{level}_CON+PIL',
                      cobble_geometry=f'CSC_ALL_Stage_{stage}_Cobble_Decals',
                      ruin_visible=['Construction', 'Pillaged'],
                      cobble_visible=['Worked', 'Construction'])
        required.append(COBBLE_MATERIAL)
    for ident in (result['ruin_geometry'], *([result['cobble_geometry']] if 'cobble_geometry' in result else [])):
        if ident == metadata.get('construction_geometry') and ident not in (
                'CSC_Level_1_CON+PIL', 'CSC_Level_1_S_CON+PIL',
                'CSC_Level_2_CON+PIL', 'CSC_Level_3_CON+PIL'):
            # A source blend in this batch must provide the new GEO/FGX.
            continue
        for suffix in ('.geo', '.fgx'):
            path = mod / 'Geometries' / (ident + suffix)
            if not path.is_file():
                raise ValueError(f'{asset_id}: required shared geometry missing: {path}')
        geo = read_xml(mod / 'Geometries' / (ident + '.geo'))
        if txt(geo, 'm_Name') != ident or not geo.findall('m_Meshes/Element'):
            raise ValueError(f'{asset_id}: shared GEO has wrong identity or no meshes: {ident}')
    for ident in required:
        path = mod / 'Materials' / (ident + '.mtl')
        if not path.is_file():
            raise ValueError(f'{asset_id}: required existing material missing: {path}')
        material = read_xml(path)
        if txt(material, 'm_Name') != ident:
            raise ValueError(f'{asset_id}: material XML identity differs from filename: {path}')
        for value in material.findall('m_CookParams/m_Values/Element'):
            if value.findtext('m_eObjectType') != 'TEXTURE':
                continue
            texture = txt(value, 'm_ObjectName')
            if texture.startswith('CSC_'):
                for suffix in ('.tex', '.dds'):
                    dependency = mod / 'Textures' / (texture + suffix)
                    if not dependency.is_file():
                        raise ValueError(f'{asset_id}: required material texture missing: {dependency}')
    return result


def state_rows(model):
    from export_scene import txt
    rows = {}
    for row in model.findall('m_GroupStates/Element'):
        key = (txt(row, 'm_MeshName'), txt(row, 'm_GroupName'), txt(row, 'm_StateName'))
        values = {txt(v, 'm_ParamName'): v for v in row.findall('m_Values/m_Values/Element')}
        if key in rows or 'Visible' not in values or 'Material' not in values:
            raise ValueError(f'duplicate or incomplete group state {key}')
        rows[key] = (values['Visible'].findtext('m_bValue') == 'true',
                     txt(values['Material'], 'm_ObjectName'))
    return rows


def assert_groups(model, geo, expected):
    """Every GEO mesh/group must have exactly five matching AST rows."""
    from export_scene import txt
    actual = state_rows(model)
    wanted = {}
    for mesh in geo.findall('m_Meshes/Element'):
        mesh_name = txt(mesh, 'm_Name')
        for group in mesh.findall('m_Groups/Element'):
            group_name = txt(group, 'm_Name')
            for state in STATES:
                wanted[(mesh_name, group_name, state)] = expected(mesh_name, group_name, state)
    if actual != wanted:
        missing = sorted(set(wanted) - set(actual))
        extra = sorted(set(actual) - set(wanted))
        wrong = [(key, actual[key], wanted[key]) for key in wanted.keys() & actual.keys()
                 if actual[key] != wanted[key]]
        raise ValueError(f'group-state mismatch: missing={missing[:3]}, extra={extra[:3]}, wrong={wrong[:3]}')


def validate_stage(job, decoded, stage):
    """Check the exact AST/GEO state and material contract before conversion/install."""
    from export_scene import read_xml, txt, MODELS, POINTS, attachment_transform
    mod = Path(job['mod_root'])
    checked = []
    reused_csc = set()
    tilted_attachments = []
    used_new_props = set()
    used_decals = set()
    authored_ruins = {e['geometry_id'] for e in job.get('shared_geometries', [])}
    for entry in job['buildings']:
        contract = entry.get('contract')
        if not contract:
            continue
        ident = entry['asset_id']
        root = read_xml(stage / 'Assets' / (ident + '.ast'))
        models = {txt(m, 'm_Name'): m for m in root.findall(MODELS + '/Element')}
        for model_name, instance in models.items():
            for (mesh_name, group_name, state), (visible, _) in state_rows(instance).items():
                if state in ('Unworked','Unbuilt') and visible:
                    raise ValueError(f'{ident}/{model_name}/{mesh_name}/{group_name}: {state} must be invisible')
        unexpected_ruins = [name for name in models if 'CON+PIL' in name and name != entry['contract']['ruin_geometry']]
        if unexpected_ruins:
            raise ValueError(f'{ident}: unexpected construction/pillage models {unexpected_ruins}')
        main = models[ident]
        geo = read_xml(stage / 'Geometries' / (ident + '.geo'))
        decoded_model = decoded['models'][ident]
        mesh_lookup = {m['name']: m for m in decoded_model['meshes']}
        def main_expected(mesh, group, state):
            source_mesh = mesh_lookup[mesh]
            source_mat = next(m for m in source_mesh['materials'] if m['name'] == group)
            material = material_for_mesh(source_mesh, source_mat, contract, job)
            return (state == 'Worked', material)
        assert_groups(main, geo, main_expected)
        ruin_id = contract['ruin_geometry']
        if contract.get('authored_ruin_geometry') != (ruin_id in authored_ruins):
            raise ValueError(f'{ident}: authored construction geometry declaration differs from source inventory')
        if ruin_id not in models:
            raise ValueError(f'{ident}: missing shared model {ruin_id}')
        ruin_geo = read_xml((stage if contract.get('authored_ruin_geometry') else mod) / 'Geometries' / (ruin_id + '.geo'))
        assert_groups(models[ruin_id], ruin_geo,
                      lambda mesh, group, state: (state == 'Construction' if group == 'Pillage_Construction_01' else state in ('Construction', 'Pillaged'),
                                                  'Pillage_Construction_01' if group == 'Pillage_Construction_01' else contract['ruin_material']))
        if contract['supply_chain_stage'] in (3, 4):
            cobble_id = contract['cobble_geometry']
            if cobble_id not in models:
                raise ValueError(f'{ident}: missing shared model {cobble_id}')
            cobble_geo = read_xml(mod / 'Geometries' / (cobble_id + '.geo'))
            assert_groups(models[cobble_id], cobble_geo,
                          lambda mesh, group, state: (state in ('Worked', 'Construction'), COBBLE_MATERIAL))
        for decal_id in entry.get('decals', []):
            if decal_id not in models:
                raise ValueError(f'{ident}: missing authored PIL decal model {decal_id}')
            decal_geo = read_xml(stage / 'Geometries' / (decal_id + '.geo'))
            assert_groups(models[decal_id], decal_geo,
                          lambda mesh, group, state: (state in entry.get('decal_states', {}).get(decal_id, ['Pillaged']),
                                                      next(m['name'] for m in next(x for x in decoded['models'][decal_id]['meshes'] if x['name']==mesh)['materials'] if m['name']==group)))
            used_decals.add(decal_id)
        attachments = {a['instance_id']: a for a in decoded_model['attachments']}
        points = {txt(p, 'm_Name').removeprefix('CSC_Attach_'): p
                  for p in root.findall(POINTS + '/Element') if txt(p, 'm_Name').startswith('CSC_Attach_')}
        expected_points = set(attachments)
        found_points = set(points)
        if expected_points != found_points:
            raise ValueError(f'{ident}: attachment point mismatch: {expected_points ^ found_points}')
        for instance_id, attachment in attachments.items():
            point = points[instance_id]
            expected, issues = attachment_transform(attachment, job.get('policies', {}))
            if issues:
                raise ValueError(f'{ident}/{instance_id}: invalid transform: {issues}')
            for field, values in (('m_position', expected['position']),
                                  ('m_orientation', expected['rotation'])):
                actual = [float(point.findtext(field + '/' + axis)) for axis in 'xyz']
                if any(abs(a-b)>1e-6 for a,b in zip(actual, values)):
                    raise ValueError(f'{ident}/{instance_id}: {field} differs from Blender')
            if abs(float(point.findtext('m_scale'))-expected['scale'])>1e-6:
                raise ValueError(f'{ident}/{instance_id}: scale differs from Blender')
            if max(abs(v) for v in attachment['rotation_degrees'][:2]) > 1e-4:
                tilted_attachments.append(f'{ident}/{instance_id}')
            asset = attachment['source_asset_id']
            bound = {txt(v, 'm_EntryName') for v in point.findall('m_CookParams/m_Values/Element')
                     if txt(v, 'm_ParamName') == 'Asset'}
            if bound != {asset}:
                raise ValueError(f'{ident}/{instance_id}: attached asset differs from Blender: {bound}')
            if asset.startswith('CSC_') and asset not in decoded['models']:
                reused_csc.add(asset)
            if asset in decoded['models'] and decoded['models'][asset]['kind'] == 'prop':
                used_new_props.add(asset)
                prop_root = read_xml(stage / 'Assets' / (asset + '.ast'))
                prop_model = prop_root.find(MODELS + '/Element')
                actual_materials = {material for visible, material in state_rows(prop_model).values() if visible}
                expected_material = contract['building_material'] if 'leanto' in asset.casefold() else contract['prop_material']
                if actual_materials != {expected_material}:
                    raise ValueError(f'{ident}/{instance_id}: new CSC prop uses {actual_materials}, expected {expected_material}')
        checked.append(ident)
    missing_props = {e['asset_id'] for e in job.get('props', [])} - used_new_props
    missing_decals = {e['geometry_id'] for e in job.get('decals', [])} - used_decals
    if missing_props or missing_decals:
        raise ValueError(f'Unused blend masters: props={sorted(missing_props)}, decals={sorted(missing_decals)}')
    for ident, model in decoded['models'].items():
        if model['kind'] != 'prop':
            continue
        root = read_xml(stage / 'Assets' / (ident + '.ast'))
        prop = root.find(MODELS + '/Element')
        geo = read_xml(stage / 'Geometries' / (ident + '.geo'))
        rows = state_rows(prop)
        if any(visible != (state == 'Worked') for (_, _, state), (visible, _) in rows.items()):
            raise ValueError(f'{ident}: new CSC prop must be Worked-only')
        assert_groups(prop, geo, lambda mesh, group, state: rows[(mesh, group, state)])
    return {'validated_buildings': checked, 'new_props': [i for i,m in decoded['models'].items() if m['kind']=='prop'],
            'reused_csc_props_for_henno': sorted(reused_csc),
            'xy_rotation_ae_review': tilted_attachments,
            'manual_review': 'Existing CSC attachment assets retain their installed state tables; Henno checks those in game.'}


def main():
    from export_scene import load_job, sha
    parser = argparse.ArgumentParser(description='Validate a staged CSC building export contract')
    parser.add_argument('job', type=Path)
    args = parser.parse_args()
    job = load_job(args.job)
    out = Path(job['output'])
    decoded = json.loads((out / 'decoded.json').read_text())
    result = validate_stage(job, decoded, out / 'stage')
    manifest = json.loads((out / 'manifest.json').read_text())
    if manifest.get('converted_files'):
        for rel, expected in manifest['converted_files'].items():
            path = out / 'stage' / rel
            if not path.is_file() or sha(path) != expected:
                raise ValueError(f'Converted output differs from manifest: {rel}')
        for ident in manifest['models']:
            path = out / 'stage' / 'Geometries' / (ident + '.fgx')
            if not path.is_file() or path.stat().st_size < 100:
                raise ValueError(f'Missing or undersized converted FGX: {path}')
        result['converted_files_verified'] = len(manifest['converted_files'])
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
