"""Filename-independent classification and template resolution for saved scenes."""
from pathlib import Path
import xml.etree.ElementTree as ET
from export_scene import identifier, read_xml, txt, MODELS


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
    own = mod / 'Assets' / (entry['asset_id'] + '.ast')
    paths = [mod / explicit] if explicit else ([own] if own.is_file() else sorted((mod / 'Assets').glob('*.ast')))
    for path in paths:
        root = read_xml(path)
        for model in root.findall(MODELS + '/Element'):
            if meta.get('replace_model') and txt(model, 'm_Name') != meta['replace_model']:
                continue
            names = {txt(g, 'm_MeshName') for g in model.findall('m_GroupStates/Element')}
            match = {meta['state_template_mesh']} & names if meta.get('state_template_mesh') else meshes & names
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
    job.update(mod_root=str(mod), library=str(library), output=str(output), buildings=[], props=[], decals=[])
    report = {'files': [], 'blockers': []}
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
            entry = {'blend': row['path'], 'scene': row['scene'], 'source_sha256': row['sha256'],
                     ('geometry_id' if kind == 'decal' else 'asset_id'): ident}
            if kind == 'building':
                auxiliary[ident] = resolve_building(entry, row, mod)
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
        template = read_xml(Path(entry['template_asset']))
        replaced_names = {txt(m, 'm_Name') for m in template.findall(MODELS + '/Element')
                          if txt(m, 'm_GeoName') in requested}
        entry['preserve_models'] = [n for n in entry['preserve_models'] if n not in replaced_names]
    if not any(job[k] for k in ('buildings', 'props', 'decals')):
        report['blockers'].append('No exportable assets discovered')
    report['status'] = 'blocked' if report['blockers'] else 'ready_to_decode'
    return job, report
