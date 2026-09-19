"""Filename-independent classification and template resolution for saved scenes."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
from export_scene import identifier, read_xml, txt, MODELS, STATES


TEMPLATE_PROFILES = {
    'tilebase': 'tilebase.ast',
    'level1_small': 'level1_small.ast',
}
# Migration of shipped scene metadata, regardless of whether the old output exists.
# Do not silently substitute a generic template for arbitrary missing custom ASTs.
LEGACY_TEMPLATE_PROFILES = {
    'assets/csc_tailors_tailor.ast': 'tilebase',
    'assets/csc_tailors_tailor_2.ast': 'tilebase',
    'assets/csc_tailors_textile_workshop.ast': 'level1_small',
}


def prior_run_owns_installed_prop(output, mod, row, ident):
    """Allow an export source to update only an installed output it previously created."""
    installed = mod / 'Assets' / (ident + '.ast')
    if not installed.is_file():
        return False
    installed_sha = hashlib.sha256(installed.read_bytes()).hexdigest()
    runs = output.parent
    if not runs.is_dir():
        return False
    for receipt_path in sorted(runs.glob('*/install-receipt.json'), reverse=True):
        job_path = receipt_path.parent / 'job.json'
        if receipt_path.parent == output or not job_path.is_file():
            continue
        try:
            receipt = json.loads(receipt_path.read_text())
            prior = json.loads(job_path.read_text())
            if Path(prior['mod_root']).resolve() != mod.resolve():
                continue
            owned = any(item.get('asset_id') == ident and
                        Path(item.get('blend', '')).resolve() == Path(row['path']).resolve()
                        for item in prior.get('props', []))
            expected = receipt.get('installed_sha256', {}).get(f'Assets\\{ident}.ast')
            if owned and expected == installed_sha:
                return True
        except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
            continue
    return False


def find_blends(directory):
    files = sorted((p.resolve() for p in directory.iterdir()
                    if p.is_file() and p.suffix.lower() == '.blend'), key=lambda p: p.name.casefold())
    if not files:
        raise ValueError(f'No .blend files in {directory} (top level only)')
    return files


def unique(values, label):
    values = {v for v in values if v}
    if len(values) != 1:
        raise ValueError(f'{label}: expected one identity, found {sorted(values)}; set csc_export explicitly')
    return next(iter(values))


def classify(row, catalogue):
    meta = row['metadata']
    kind = meta.get('kind')
    base = [m for m in row['meshes'] if m['role'] == 'building_geometry']
    if not kind:
        if base:
            kind = 'building'
        elif row.get('handoff_role') == 'Shared PIL export':
            kind = 'decal'
        elif len(row['armatures']) == 1 and row['armatures'][0] in catalogue:
            kind = 'prop'
        else:
            raise ValueError('Cannot classify scene; set csc_export.kind to building, prop, decal or ignore')
    if kind == 'ignore':
        return kind, None
    if kind not in ('building', 'prop', 'decal'):
        raise ValueError(f'Unsupported csc_export.kind: {kind}')
    ident = meta.get('asset_id') or meta.get('geometry_id')
    if not ident:
        ident = unique([m['asset_id'] for m in base], 'Building source_asset_id') if kind == 'building' else unique(row['armatures'], 'Armature identity')
    identifier(ident)
    return kind, ident


def resolve_building(entry, row, mod):
    meta = row['metadata']
    meshes = {m['name'] for m in row['meshes'] if m['role'] == 'building_geometry'}
    candidates = []
    explicit = meta.get('template_asset')
    legacy_profile = LEGACY_TEMPLATE_PROFILES.get(str(explicit).replace('\\', '/').casefold())
    profile = meta.get('template_profile') or legacy_profile or ('tilebase' if not explicit else None)
    if profile:
        if profile not in TEMPLATE_PROFILES:
            raise ValueError(f'Unknown template_profile {profile!r}; choose {sorted(TEMPLATE_PROFILES)}')
        if explicit and not legacy_profile:
            raise ValueError('Choose template_profile or template_asset, not both')
        paths = [Path(__file__).resolve().parent / 'templates' / TEMPLATE_PROFILES[profile]]
        model_selector, mesh_selector = 'Building', 'BuildingMesh'
        entry['template_profile'] = profile
    else:
        paths = [mod / explicit]
        model_selector, mesh_selector = meta.get('replace_model'), meta.get('state_template_mesh')
    for path in paths:
        root = read_xml(path)
        for model in root.findall(MODELS + '/Element'):
            if model_selector and txt(model, 'm_Name') != model_selector:
                continue
            names = {txt(g, 'm_MeshName') for g in model.findall('m_GroupStates/Element')}
            match = {mesh_selector} & names if mesh_selector else meshes & names
            if len(match) == 1:
                candidates.append((path, root, model, next(iter(match))))
    if len(candidates) != 1:
        raise ValueError(f'Found {len(candidates)} building template/model matches; set csc_export.template_asset, replace_model and state_template_mesh')
    path, root, main, mesh = candidates[0]
    entry.update(template_asset=str(path.resolve()), replace_model=txt(main, 'm_Name'), state_template_mesh=mesh,
                 preserve_models=[txt(m, 'm_Name') for m in root.find(MODELS) if m is not main],
                 replace_owned_attachments=True)
    for key in ('preserve_models', 'replace_attachment_assets', 'replace_owned_attachments'):
        if key in meta:
            entry[key] = meta[key]
    return {txt(m, 'm_GeoName') for m in root.find(MODELS) if m is not main}


def make_job(rows, defaults, mod, library, output, catalogue):
    import copy
    job = copy.deepcopy(defaults)
    job.update(mod_root=str(mod), library=str(library), output=str(output), buildings=[], props=[], decals=[],
               references=[{'asset_id': ident} for ident in job.get('reuse_existing_assets', [])])
    report = {'files': [], 'blockers': []}
    xlp = mod / 'XLPs' / 'CSC_Tilebases.xlp'
    installed = read_xml(xlp).findall('m_Entries/Element') if xlp.is_file() else []
    for ref in job['references']:
        ident = ref['asset_id']
        ast = mod / 'Assets' / (ident + '.ast')
        required = [ast]
        if ast.is_file():
            root = read_xml(ast)
            geos = {txt(model, 'm_GeoName') for model in root.findall(MODELS + '/Element')}
            if not geos or '' in geos or txt(root, 'm_Name') != ident:
                report['blockers'].append(f'{ident}: installed AST has an invalid name or geometry binding')
            if ident in geos:
                required += [mod / 'Geometries' / (ident + '.geo'),
                             mod / 'Geometries' / (ident + '.fgx')]
        missing = [str(path) for path in required if not path.is_file()]
        if missing or not any(txt(e, 'm_EntryID') == ident and txt(e, 'm_ObjectName') == ident
                              for e in installed):
            report['blockers'].append(f'{ident}: existing asset needs its AST, own GEO/FGX when used, '
                                      f'and CSC TileBase registration; missing {missing}')
    known, records, auxiliary = {}, {}, {}
    for row in rows:
        result = {'path': row['path']}
        report['files'].append(result)
        try:
            if row.get('error'):
                raise ValueError(row['error'])
            kind, ident = classify(row, catalogue)
            result.update(kind=kind, asset_id=ident)
            if kind == 'ignore':
                result['status'] = 'explicitly_ignored'
                continue
            folded = ident.casefold()
            if folded in known:
                raise ValueError(f'Duplicate asset identity {ident}, also in {known[folded]}')
            known[folded] = row['path']
            source = catalogue.get(ident)
            if kind == 'prop' and source and source.get('origin') != 'authored_blender':
                raise ValueError('Existing pantry/library asset is reference-only; use as an attachment or explicitly ignore its source blend')
            if (kind == 'prop' and (mod / 'Assets' / (ident + '.ast')).is_file()
                    and ident not in job.get('reuse_existing_assets', [])
                    and ident not in job.get('replace_existing_assets', []) and not source
                    and not prior_run_owns_installed_prop(output, mod, row, ident)):
                raise ValueError(f'{ident}: an installed CSC asset already has this ID; add it to reuse_existing_assets to reference it without replacement')
            entry = {'blend': row['path'], 'scene': row['scene'], 'source_sha256': row['sha256'],
                     ('geometry_id' if kind == 'decal' else 'asset_id'): ident}
            if kind == 'prop' and ident in job.get('reuse_existing_assets', []):
                result['status'] = 'existing_asset_reference'
                continue
            if kind == 'building':
                auxiliary[ident] = resolve_building(entry, row, mod)
                result['template_asset'] = entry['template_asset']
                result['template_profile'] = entry.get('template_profile')
            job[{'building': 'buildings', 'prop': 'props', 'decal': 'decals'}[kind]].append(entry)
            records[ident] = row
            result['status'] = 'resolved'
        except (ValueError, KeyError, OSError, TypeError, ET.ParseError) as error:
            result['status'] = 'blocked'
            result['error'] = str(error)
            report['blockers'].append(f'{row["path"]}: {error}')
    decals = {e['geometry_id']: e for e in job['decals']}
    for entry in job['buildings']:
        row = records[entry['asset_id']]
        meta = row['metadata']
        requested = meta.get('decals')
        if requested is None:
            requested = sorted(auxiliary[entry['asset_id']] & decals.keys())
            # Legacy file link is only a fallback. New metadata links by asset ID;
            # template GEO identity still works when every file has been renamed.
            if row.get('legacy_decal'):
                linked = (Path(row['path']).parent / row['legacy_decal']).resolve()
                requested = sorted(set(requested) | {i for i,e in decals.items() if Path(e['blend']).resolve() == linked})
                if not requested:
                    report['blockers'].append(f'{row["path"]}: unresolved PIL geometry; set csc_export.decals to discovered geometry IDs')
        if not isinstance(requested, list) or any(not isinstance(i, str) for i in requested):
            report['blockers'].append(f'{row["path"]}: csc_export.decals must be a list of geometry IDs')
            continue
        missing = set(requested) - decals.keys()
        if missing:
            report['blockers'].append(f'{row["path"]}: missing decal blends for {sorted(missing)}')
        entry['decals'] = sorted(set(requested))
        state_map = meta.get('decal_states', {})
        if (not isinstance(state_map, dict) or set(state_map) - set(requested) or any(
                not isinstance(states, list) or not states or
                any(state not in STATES for state in states)
                for states in state_map.values())):
            report['blockers'].append(f'{row["path"]}: invalid decal_states mapping')
            continue
        entry['decal_states'] = state_map
        template = read_xml(Path(entry['template_asset']))
        replaced_names = {txt(m, 'm_Name') for m in template.findall(MODELS + '/Element')
                          if txt(m, 'm_GeoName') in requested}
        entry['preserve_models'] = [n for n in entry['preserve_models'] if n not in replaced_names]
    if not any(job[k] for k in ('buildings', 'props', 'decals')):
        report['blockers'].append('No exportable assets discovered')
    report['status'] = 'blocked' if report['blockers'] else 'ready_to_decode'
    return job, report
