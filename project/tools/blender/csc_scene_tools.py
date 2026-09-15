"""Small Blender UI for editing CSC building Export scenes without property bookkeeping.

Install this file as a Blender add-on. It changes only the open .blend; save normally.
The Windows exporter remains the authority for material/asset/state validation.
"""
bl_info = {
    'name': 'CSC Scene Tools', 'author': 'CSC', 'version': (1, 2, 0),
    'blender': (4, 0, 0), 'location': '3D View > Sidebar > CSC',
    'description': 'Place, duplicate and exclude reusable CSC scene props',
    'category': 'Object',
}

import bpy
import json
import re
import shutil
import hashlib
from pathlib import Path
from mathutils import Matrix
from bpy.app.handlers import persistent
from bpy.props import EnumProperty, StringProperty


# Blender's dynamic EnumProperty callback needs string storage to survive redraws.
_LIBRARY_ENUM_ITEMS = []
_SYNCING_NAMES = False


def export_scene():
    scene = bpy.data.scenes.get('Export')
    if not scene:
        raise ValueError('This file has no Export scene')
    return scene


def attachment_root(obj):
    while obj:
        if obj.type == 'EMPTY' and obj.get('instance_id'):
            return obj
        obj = obj.parent
    return None


def instance_label(label):
    label = str(label).removeprefix('Attach_')
    label = re.sub(r'\.\d{3}$', '', label)  # Blender's collision suffix is not an ID.
    base = re.sub('[^A-Za-z0-9_]+', '_', label).strip('_')
    if not base:
        raise ValueError('Give the attachment a nonempty name')
    return base


def same_object(a, b):
    return a is not None and b is not None and a.as_pointer() == b.as_pointer()


def instance_available(scene, ident, root=None):
    if any(not same_object(o, root) and o.type == 'EMPTY' and o.get('instance_id') == ident
           for o in scene.objects):
        return False
    existing = bpy.data.objects.get('Attach_' + ident)
    return existing is None or same_object(existing, root)


def next_instance(scene, label, root=None):
    base = instance_label(label)
    i = 1
    while ((root is not None and f'{base}_{i:02d}' == root.get('instance_id'))
           or not instance_available(scene, f'{base}_{i:02d}', root)):
        i += 1
    return f'{base}_{i:02d}'


def duplicate_base(label):
    # Strip all tool-generated numeric tails, not just the last duplicate step.
    return re.sub(r'(?:_\d{2,})+$', '', instance_label(label))


def next_duplicate_instance(scene, label, root=None):
    base = duplicate_base(label)
    letter = re.fullmatch(r'(.+)_([A-Z])', base)
    if letter:
        family, previous = letter.groups()
        for code in range(ord(previous) + 1, ord('Z') + 1):
            candidate = family + '_' + chr(code)
            if (root is None or candidate != root.get('instance_id')) and instance_available(scene, candidate, root):
                return candidate
    return next_instance(scene, base, root)


def mesh_component_name(mesh):
    # Object/data .001 suffixes arise from Blender append; they are not geometry IDs.
    base = mesh.data.name.split('__', 1)[0]
    return re.sub(r'\.\d{3}$', '', base)


def child_name_plan(root, ident):
    children = sorted((o for o in root.children if o.type == 'MESH'), key=lambda o: o.name)
    planned = []
    for i, child in enumerate(children):
        if child.get('source_asset_id') and child.get('source_asset_id') != root.get('source_asset_id'):
            raise ValueError(f'{child.name}: asset identity differs from {root.name}')
        suffix = f'_{i}' if len(children) > 1 else ''
        expected = mesh_component_name(child) + '__' + ident + suffix
        existing = bpy.data.objects.get(expected)
        if existing is not None and not same_object(existing, child):
            raise ValueError(f'{root.name}: mesh name {expected} is already in use')
        planned.append((child, expected))
    return planned


def sync_attachment_children(root):
    planned = child_name_plan(root, root['instance_id'])
    ident = root['instance_id']
    for child, expected in planned:
        if child.get('source_asset_id') != root['source_asset_id']:
            child['source_asset_id'] = root['source_asset_id']
        if child.get('instance_id') != ident:
            child['instance_id'] = ident
        if child.name != expected:
            child.name = expected
        if child.name != expected:
            raise ValueError(f'{root.name}: mesh name {expected} is already in use')
    return [child for child, _ in planned]


def rename_attachment(root, label, *, resolve_collision=False):
    scene = export_scene()
    if root is None:
        raise ValueError('Select an attachment Empty or its mesh child')
    if not same_object(scene.objects.get(root.name), root) or root.type != 'EMPTY' or not root.get('instance_id'):
        raise ValueError('Select an attachment Empty in Export')
    requested = instance_label(label)
    if not instance_available(scene, requested, root):
        if not resolve_collision:
            raise ValueError(f'{requested}: another attachment already uses this name')
        requested = next_duplicate_instance(scene, requested, root)
    old = root['instance_id']
    child_name_plan(root, requested)
    if old != requested and sum(o.type == 'EMPTY' and o.get('instance_id') == old for o in scene.objects) > 1:
        if any(o.type == 'EMPTY' and o.get('support') == old for o in scene.objects):
            raise ValueError(f'{old}: multiple roots share this ID; support references are ambiguous')
    if root.name != 'Attach_' + requested:
        root.name = 'Attach_' + requested
    if root.name != 'Attach_' + requested:
        raise ValueError(f'{requested}: Blender object name is already in use')
    if old != requested:
        root['instance_id'] = requested
    sync_attachment_children(root)
    if old != requested:
        for other in scene.objects:
            if not same_object(other, root) and other.type == 'EMPTY' and other.get('support') == old:
                other['support'] = requested
    return requested


def reconcile_attachment_names(*, clean_generated=False):
    """Make controller names, IDs, child names/IDs and support links agree."""
    scene = export_scene()
    roots = [o for o in scene.objects if o.type == 'EMPTY' and o.get('instance_id')]
    changed = []
    for root in sorted(roots, key=lambda o: o.name):
        old = root['instance_id']
        desired = root.name
        if (clean_generated and desired == 'Attach_' + old and
                re.search(r'(?:_\d{2,})+$', old) and
                re.fullmatch(r'(.+)_([A-Z])', duplicate_base(old))):
            desired = next_duplicate_instance(scene, old, root)
        if desired != 'Attach_' + old:
            new = rename_attachment(root, desired, resolve_collision=True)
            if new != old:
                changed.append((old, new))
        else:
            sync_attachment_children(root)
    return changed


@persistent
def _attachment_name_change(scene, depsgraph=None):
    global _SYNCING_NAMES
    # Add-on registration runs with restricted data; handlers sync after loading.
    if not hasattr(bpy.data, 'scenes'):
        return
    if _SYNCING_NAMES or bpy.data.scenes.get('Export') is None:
        return
    _SYNCING_NAMES = True
    try:
        reconcile_attachment_names()
    except ValueError as error:
        print('CSC attachment naming:', error)
    finally:
        _SYNCING_NAMES = False


def active_collections(scene):
    preferred = bpy.data.collections.get('Reusable_Attachments')
    if preferred and preferred in {c for o in scene.objects for c in o.users_collection}:
        return (preferred,)
    roots = [o for o in scene.objects if o.type == 'EMPTY' and o.get('instance_id')]
    if not roots:
        raise ValueError('The Export scene has no attachment collection to use')
    return tuple(roots[0].users_collection)


def duplicate_attachment(root):
    scene = export_scene()
    reconcile_attachment_names()
    if not same_object(scene.objects.get(root.name), root):
        raise ValueError('Selected attachment is not in Export')
    source_children = [c for c in root.children if c.type == 'MESH']
    if not source_children:
        raise ValueError('Attachment has no mesh children')
    ident = next_duplicate_instance(scene, root['instance_id'])
    copy = root.copy()
    copy.name = 'Attach_' + ident
    copy['instance_id'] = ident
    for coll in root.users_collection:
        coll.objects.link(copy)
    copy.matrix_world = root.matrix_world.copy()
    children = []
    for original in source_children:
        child = original.copy()
        # Repeated placements deliberately share one source mesh definition.
        child.data = original.data
        child.name = mesh_component_name(original) + '__' + ident
        child['instance_id'] = ident
        child['source_asset_id'] = root['source_asset_id']
        child.parent = copy
        child.matrix_parent_inverse = Matrix.Identity(4)
        child.matrix_basis = Matrix.Identity(4)
        for coll in original.users_collection:
            coll.objects.link(child)
        children.append(child)
    sync_attachment_children(copy)
    return copy, children


def duplicate_fixed(obj):
    if export_scene().objects.get(obj.name) is not obj or not (
            obj.get('export_role') == 'fixed_geometry' or obj.name.startswith('CSC_Fixed_')):
        raise ValueError('Select a CSC_Fixed_ mesh in Export')
    copy = obj.copy()
    copy.data = obj.data.copy()
    copy.name = obj.name + '_Copy'
    for coll in obj.users_collection:
        coll.objects.link(copy)
    copy.matrix_world = obj.matrix_world.copy()
    return copy


def set_export_visible(obj, enabled):
    root = attachment_root(obj)
    target = root or obj
    if export_scene().objects.get(target.name) is not target:
        raise ValueError('Selected object is not in Export')
    if not root and not (target.type == 'MESH' and (
            target.get('export_role') == 'fixed_geometry' or target.name.startswith('CSC_Fixed_'))):
        raise ValueError('Select an attachment or CSC_Fixed_ mesh')
    targets = [target] + ([o for o in target.children if o.type == 'MESH'] if root else [])
    for item in targets:
        item.hide_render = not enabled
        item['csc_export_exclude'] = not enabled
    return target


def remove_prop(obj):
    scene = export_scene()
    root = attachment_root(obj)
    target = root or obj
    if scene.objects.get(target.name) is not target:
        raise ValueError('Selected object is not in Export')
    name = target.name
    if root:
        dependents = [o.name for o in scene.objects if o.type == 'EMPTY' and
                      o.get('instance_id') != root.get('instance_id') and
                      o.get('support') == root.get('instance_id')]
        if dependents:
            raise ValueError(f'{root.name}: other attachments use it as support: {dependents}')
        if any(child.type != 'MESH' for child in root.children):
            raise ValueError(f'{root.name}: has non-mesh children; inspect before removing')
        for child in list(root.children):
            bpy.data.objects.remove(child, do_unlink=True)
        bpy.data.objects.remove(root, do_unlink=True)
    elif target.type == 'MESH' and (
            target.get('export_role') == 'fixed_geometry' or target.name.startswith('CSC_Fixed_')):
        bpy.data.objects.remove(target, do_unlink=True)
    else:
        raise ValueError('Select an attachment or CSC_Fixed_ mesh')
    return name


def catalogue(library):
    path = Path(bpy.path.abspath(library)).expanduser().resolve()
    file = path / 'catalogue.json'
    if not file.is_file():
        raise ValueError(f'Choose the CSC_Prop_Library folder; catalogue missing: {file}')
    records = {a['asset_id']: a for a in json.loads(file.read_text())['assets']
               if a.get('asset_id') and a.get('blend_path') and
               not a['asset_id'].startswith('CSC_Attached_')}
    return path, records


def library_items(self, context):
    global _LIBRARY_ENUM_ITEMS
    try:
        _, records = catalogue(context.scene.csc_prop_library)
        _LIBRARY_ENUM_ITEMS = [(a, a, str(records[a].get('source_pack', '')), i)
                               for i, a in enumerate(sorted(records))]
    except (ValueError, OSError):
        _LIBRARY_ENUM_ITEMS = [('NONE', 'Choose library folder', '', 0)]
    return _LIBRARY_ENUM_ITEMS


def texture_source(image, library_path):
    source = Path(bpy.path.abspath(image.filepath)).resolve()
    if source.is_file():
        return source
    art_root = next((p for p in (library_path, *library_path.parents)
                     if p.name == '3D Art'), None)
    # Some CSC masters were saved on Windows with absolute paths to the synced
    # Working Files/3D Art tree. Match that exact relative tail on this host.
    normalized = image.filepath.replace('\\', '/')
    marker = 'Working Files/3D Art/'
    if marker in normalized:
        tail = normalized.split(marker, 1)[1]
        if art_root:
            candidate = (art_root / tail).resolve()
            if candidate.is_file():
                return candidate
    # Older CSC prop masters use a relative path that lands one directory above
    # 3D Art. Resolve only the known shared CSC texture-tree suffix.
    csc_marker = 'Textures/CSC_Props/'
    if csc_marker in normalized:
        tail = normalized.split(csc_marker, 1)[1]
        if art_root:
            candidate = (art_root / csc_marker / tail).resolve()
            if candidate.is_file():
                return candidate
    # Masters saved with a local //textures directory sometimes lose that
    # directory when copied into the shared Props tree. Resolve only the known
    # CSC production-map names, never an arbitrary image with the same basename.
    basename = Path(normalized).name
    if art_root and re.fullmatch(r'CSC_Props_Shared_0[12]_(?:AO|B|E|G|M|N)\.png', basename):
        candidate = art_root / 'Textures/CSC_Props/Current/textures' / basename
        if candidate.is_file():
            return candidate
    raise ValueError(f'Texture missing on this host: {image.filepath}')


def localize_images(before_images, source_folder):
    local_textures = Path(bpy.data.filepath).parent / 'textures'
    pending = []
    for image in set(bpy.data.images) - before_images:
        if image.source != 'FILE':
            continue
        source = texture_source(image, source_folder)
        dest = local_textures / source.name
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() != source_hash:
            if source.stem.endswith('_AO'):
                raise ValueError(f'AO atlas differs from scene textures: {source.name}; reconcile the shared AO release before import')
            dest = local_textures / (source.stem + '_' + source_hash[:12] + source.suffix)
        pending.append((image, source, dest))
    if pending:
        local_textures.mkdir(exist_ok=True)
    for image, source, dest in pending:
        if not dest.exists():
            shutil.copy2(source, dest)
        image.filepath = '//textures/' + dest.name


def import_prop(library, ident, location):
    scene = export_scene()
    if not bpy.data.filepath:
        raise ValueError('Save the building .blend once before importing portable library textures')
    path, records = catalogue(library)
    if ident not in records:
        raise ValueError(f'{ident}: absent from active prop catalogue')
    record = records[ident]
    blend = path / record['blend_path']
    if not blend.is_file():
        raise ValueError(f'{ident}: source blend missing: {blend}')
    components = record.get('components')
    selected = {c['object'] for c in components if c.get('default_visible', True)} if components else None
    declared_meshes = {m['geometry'] for m in record.get('models', []) if m.get('geometry')}
    before_images = set(bpy.data.images)
    before_objects = set(bpy.data.objects)
    with bpy.data.libraries.load(str(blend), link=False) as (src, dst):
        available = list(src.objects)
        if selected is not None:
            names = [name for name in available if name in selected]
        else:
            names = [name for name in available if name in declared_meshes]
            if not names:
                names = [name for name in available if name == ident or name.startswith(ident + '_')]
        if not names:
            raise ValueError(f'{ident}: no visible master mesh components in {blend.name}')
        dst.objects = names
    imported = [o for o in dst.objects if o is not None]
    meshes = [o for o in imported if o.type == 'MESH']
    if not meshes:
        raise ValueError(f'{ident}: source has no matching mesh components')
    try:
        localize_images(before_images, path)
    except ValueError as error:
        raise ValueError(f'{ident}: {error}') from error
    collections = active_collections(scene)
    instance = next_instance(scene, ident)
    root = bpy.data.objects.new('Attach_' + instance, None)
    root['instance_id'] = instance
    root['source_asset_id'] = ident
    root['export_role'] = 'reused_attachment'
    root['support'] = 'ground'
    root.location = location
    for coll in collections:
        coll.objects.link(root)
    for i, mesh in enumerate(meshes):
        # Keep the library geometry/UVs and asset-local pivot exactly. The Empty is
        # the only place for scene placement. Native rig modifiers are not exported.
        for mod in list(mesh.modifiers):
            if mod.type != 'ARMATURE':
                raise ValueError(f'{ident}: unsupported master modifier {mod.type}')
            mesh.modifiers.remove(mod)
        mesh.name = mesh_component_name(mesh) + '__' + instance + (f'_{i}' if len(meshes) > 1 else '')
        mesh['instance_id'] = instance
        mesh['source_asset_id'] = ident
        mesh.parent = root
        mesh.matrix_parent_inverse = Matrix.Identity(4)
        mesh.matrix_basis = Matrix.Identity(4)
        for coll in collections:
            coll.objects.link(mesh)
    # Blender may append a rig as an implicit dependency even if only its mesh
    # was requested. After static binding removal and reparenting, discard any
    # newly appended, unlinked non-mesh object. Leave existing scene objects alone.
    for extra in set(bpy.data.objects) - before_objects:
        if extra.type != 'MESH' and not extra.users_collection and not extra.children:
            bpy.data.objects.remove(extra, do_unlink=True)
    return root, meshes


def import_asset_master(master_file, location, library=None):
    """Place a prepared CSC prop; retain one portable master beside the building."""
    scene = export_scene()
    if not bpy.data.filepath:
        raise ValueError('Save the building .blend before importing an asset master')
    source = Path(bpy.path.abspath(master_file)).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != '.blend':
        raise ValueError(f'Choose an existing .blend asset master: {source}')
    collections = active_collections(scene)
    before_images, before_objects = set(bpy.data.images), set(bpy.data.objects)
    with bpy.data.libraries.load(str(source), link=False) as (src, dst):
        if len(src.scenes) != 1:
            raise ValueError(f'{source.name}: expected one asset-master scene, found {src.scenes}')
        dst.scenes = list(src.scenes)
    master_scene = dst.scenes[0]
    if master_scene is None:
        raise ValueError(f'{source.name}: could not load asset-master scene')
    try:
        return _finalize_asset_master(source, master_scene, location, library,
                                      scene, collections, before_images, before_objects)
    except Exception:
        if bpy.data.scenes.get(master_scene.name) is master_scene:
            bpy.data.scenes.remove(master_scene)
        for extra in set(bpy.data.objects) - before_objects:
            bpy.data.objects.remove(extra, do_unlink=True)
        raise


def _finalize_asset_master(source, master_scene, location, library,
                           scene, collections, before_images, before_objects):
    source_objects = list(master_scene.objects)
    meshes = [o for o in source_objects if o.type == 'MESH']
    arms = [o for o in source_objects if o.type == 'ARMATURE']
    raw_meta = master_scene.get('csc_export')
    meta = json.loads(raw_meta) if raw_meta else {}
    if not isinstance(meta, dict) or (meta and meta.get('kind') != 'prop'):
        raise ValueError(f'{source.name}: csc_export must identify a prop master')
    if not meta and len(arms) != 1:
        raise ValueError(f'{source.name}: expected one named armature or csc_export prop metadata')
    ident = meta.get('asset_id') or (arms[0].name if len(arms) == 1 else None)
    if not isinstance(ident, str) or not re.fullmatch(r'CSC_[A-Za-z0-9_]+', ident):
        raise ValueError(f'{source.name}: invalid CSC asset identity {ident!r}')
    if not meshes:
        raise ValueError(f'{ident}: master contains no mesh')
    if library:
        try:
            _, records = catalogue(library)
        except (OSError, ValueError):
            records = {}
        if ident in records:
            raise ValueError(f'{ident}: already catalogued; use Add library prop instead')
    for mesh in meshes:
        if mesh.get('source_asset_id') and mesh['source_asset_id'] != ident:
            raise ValueError(f'{mesh.name}: source_asset_id differs from {ident}')
        if len(mesh.data.uv_layers) != 3:
            raise ValueError(f'{mesh.name}: asset master needs UV1, UV2 and UV3')
        if any(m.type != 'ARMATURE' for m in mesh.modifiers):
            raise ValueError(f'{mesh.name}: resolve non-armature modifiers in the master')
        if max(abs(a-b) for row, ref in zip(mesh.matrix_world, Matrix.Identity(4))
               for a,b in zip(row,ref)) > 1e-4:
            raise ValueError(f'{mesh.name}: master mesh placement is not identity; reconcile its pivot before attaching')
    destination = Path(bpy.data.filepath).parent / (ident + '.blend')
    if source.parent == destination.parent and source != destination:
        raise ValueError(f'{source.name}: already in revision folder under another name; rename it to {destination.name} before import')
    if destination != source and destination.exists():
        raise ValueError(f'{ident}: master already exists in revision folder; select {destination} or duplicate its existing attachment')
    if destination == source and not meta:
        raise ValueError(f'{ident}: in-folder master lacks csc_export prop metadata; prepare its master first')
    try:
        localize_images(before_images, source.parent)
    except ValueError as error:
        raise ValueError(f'{ident}: {error}') from error
    if destination != source:
        master_scene['csc_export'] = json.dumps({'kind': 'prop', 'asset_id': ident})
        bpy.data.libraries.write(str(destination), {master_scene}, path_remap='NONE')
    instance = next_instance(scene, ident)
    root = bpy.data.objects.new('Attach_' + instance, None)
    root['instance_id'] = instance
    root['source_asset_id'] = ident
    root['export_role'] = 'custom_attachment'
    root['support'] = 'ground'
    root.location = location
    for coll in collections:
        coll.objects.link(root)
    for i, mesh in enumerate(meshes):
        for mod in list(mesh.modifiers):
            mesh.modifiers.remove(mod)
        mesh.name = mesh_component_name(mesh) + '__' + instance + (f'_{i}' if len(meshes) > 1 else '')
        mesh['instance_id'] = instance
        mesh['source_asset_id'] = ident
        mesh.parent = root
        mesh.matrix_parent_inverse = Matrix.Identity(4)
        mesh.matrix_basis = Matrix.Identity(4)
        for coll in collections:
            coll.objects.link(mesh)
    bpy.data.scenes.remove(master_scene)
    for extra in set(bpy.data.objects) - before_objects:
        if extra.type != 'MESH' and extra is not root and not extra.children:
            bpy.data.objects.remove(extra, do_unlink=True)
    return root, meshes, destination


def select_root(context, root):
    for obj in context.view_layer.objects:
        obj.select_set(False)
    root.select_set(True)
    context.view_layer.objects.active = root


class CSC_OT_duplicate(bpy.types.Operator):
    bl_idname = 'csc_scene.duplicate'
    bl_label = 'Duplicate selected prop'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            obj = context.active_object
            root = attachment_root(obj)
            result = duplicate_attachment(root)[0] if root else duplicate_fixed(obj)
            select_root(context, result)
            self.report({'INFO'}, f'Duplicated {result.name}; place the selected controller')
            return {'FINISHED'}
        except (ValueError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}


class CSC_OT_rename(bpy.types.Operator):
    bl_idname = 'csc_scene.rename'
    bl_label = 'Rename selected prop'
    bl_options = {'REGISTER', 'UNDO'}

    placement_name: StringProperty(name='Placement name')

    def invoke(self, context, event):
        root = attachment_root(context.active_object)
        if root is None:
            self.report({'ERROR'}, 'Select an attachment Empty or its mesh child')
            return {'CANCELLED'}
        self.placement_name = root['instance_id']
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        try:
            root = attachment_root(context.active_object)
            name = rename_attachment(root, self.placement_name)
            select_root(context, root)
            self.report({'INFO'}, f'Renamed placement to {name}; mesh and support IDs updated')
            return {'FINISHED'}
        except (ValueError, AttributeError, KeyError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}


class CSC_OT_repair_names(bpy.types.Operator):
    bl_idname = 'csc_scene.repair_names'
    bl_label = 'Clean up attachment names'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            changed = reconcile_attachment_names(clean_generated=True)
            summary = ', '.join(f'{old} → {new}' for old, new in changed)
            self.report({'INFO'}, summary or 'Attachment names and mesh IDs are consistent')
            return {'FINISHED'}
        except ValueError as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}


class CSC_OT_visibility(bpy.types.Operator):
    bl_idname = 'csc_scene.visibility'
    bl_label = 'Include / exclude from export'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            item = attachment_root(context.active_object) or context.active_object
            enabled = bool(item.hide_render or item.get('csc_export_exclude'))
            target = set_export_visible(item, enabled)
            self.report({'INFO'}, f'{target.name}: {"included" if enabled else "excluded"} from Export')
            return {'FINISHED'}
        except (ValueError, AttributeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}


class CSC_OT_import(bpy.types.Operator):
    bl_idname = 'csc_scene.import_prop'
    bl_label = 'Add library prop at cursor'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            ident = context.scene.csc_library_asset
            root, meshes = import_prop(context.scene.csc_prop_library, ident,
                                       context.scene.cursor.location.copy())
            select_root(context, root)
            self.report({'INFO'}, f'Added {ident} ({len(meshes)} meshes); move the selected Empty')
            return {'FINISHED'}
        except (ValueError, OSError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}


class CSC_OT_remove(bpy.types.Operator):
    bl_idname = 'csc_scene.remove_prop'
    bl_label = 'Remove selected prop'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            name = remove_prop(context.active_object)
            self.report({'INFO'}, f'Removed {name} from Review and Export')
            return {'FINISHED'}
        except (ValueError, AttributeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}


class CSC_OT_import_master(bpy.types.Operator):
    bl_idname = 'csc_scene.import_asset_master'
    bl_label = 'Add non-library asset master'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            root, meshes, master = import_asset_master(
                context.scene.csc_custom_master, context.scene.cursor.location.copy(),
                context.scene.csc_prop_library)
            select_root(context, root)
            self.report({'INFO'}, f'Added {root["source_asset_id"]} ({len(meshes)} meshes); master: {master.name}')
            return {'FINISHED'}
        except (ValueError, OSError, TypeError, json.JSONDecodeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}


class CSC_PT_scene(bpy.types.Panel):
    bl_label = 'CSC props'
    bl_idname = 'CSC_PT_scene'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CSC'

    def draw(self, context):
        layout = self.layout
        layout.label(text='Edit placements on Attach_ Empties')
        layout.label(text='Move / Z rotate / uniform scale; save')
        layout.operator('csc_scene.duplicate')
        layout.operator('csc_scene.rename')
        layout.operator('csc_scene.repair_names')
        layout.operator('csc_scene.visibility')
        layout.operator('csc_scene.remove_prop')
        layout.separator()
        layout.prop(context.scene, 'csc_prop_library', text='Library')
        layout.prop(context.scene, 'csc_library_asset', text='Asset')
        layout.operator('csc_scene.import_prop')
        layout.separator()
        layout.prop(context.scene, 'csc_custom_master', text='Asset master')
        layout.operator('csc_scene.import_asset_master')
        layout.separator()
        layout.label(text='Fixed meshes: Edit Mode edits export')
        layout.label(text='CSC prop geometry: same mesh in all copies')
        layout.label(text='Pantry geometry: source must stay verbatim')


CLASSES = (CSC_OT_duplicate, CSC_OT_rename, CSC_OT_repair_names,
           CSC_OT_visibility, CSC_OT_import, CSC_OT_remove,
           CSC_OT_import_master, CSC_PT_scene)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.csc_prop_library = StringProperty(name='CSC prop library', subtype='DIR_PATH')
    bpy.types.Scene.csc_library_asset = EnumProperty(name='CSC asset', items=library_items)
    bpy.types.Scene.csc_custom_master = StringProperty(name='Non-library asset master', subtype='FILE_PATH')
    if _attachment_name_change not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_attachment_name_change)
    if _attachment_name_change not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_attachment_name_change)
    _attachment_name_change(None)


def unregister():
    for handlers in (bpy.app.handlers.depsgraph_update_post, bpy.app.handlers.load_post):
        if _attachment_name_change in handlers:
            handlers.remove(_attachment_name_change)
    del bpy.types.Scene.csc_custom_master
    del bpy.types.Scene.csc_library_asset
    del bpy.types.Scene.csc_prop_library
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
