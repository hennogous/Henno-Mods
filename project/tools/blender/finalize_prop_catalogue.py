"""Add readable source-state notes and package documentation, without altering assets."""
import json,pathlib,sys,collections,xml.etree.ElementTree as ET
LIB=pathlib.Path(sys.argv[1]).resolve()
d=json.loads((LIB/'catalogue.json').read_text())
lines=['# Initial CSC prop library','', 'Construction and Pillaged behavior below is read from the source AST. It has not been tested in Asset Editor or in game. Blends open in Worked state; all alternate components and material bindings are retained.','', '| Asset | Pack | Construction | Pillaged |','|---|---|---|---|']
for r in d['assets']:
    if r.get('origin') == 'authored_blender':
        lines.append('| '+r['asset_id']+' | CSC | Hidden by owner (planned) | Hidden by owner (planned) |')
        continue
    r['state_behavior']={}
    for state in ['Construction','Pillaged']:
        groups=[]
        for m in r['models']:
            for s in m['states']:
                if s['state']==state: groups.append(dict(geometry=m['geometry'],mesh=s['mesh'],group=s['group'],**s['values']))
        visible=[g for g in groups if g.get('Visible')=='true']
        hidden=[g for g in groups if g.get('Visible')=='false']
        if not groups: note='No explicit state entries; runtime fallback not verified.'
        elif not visible and len(hidden)==len(groups): note='All components hidden.'
        else:
            note='; '.join(g['geometry']+' / '+g['group']+' visible'+(' with '+g['Material'] if g.get('Material') else ' (material inherited/unspecified)')+(' + burn overlay '+g['BurnMaterial'] if g.get('BurnMaterial') else '') for g in visible)+'.'
            if hidden: note+=' Hidden: '+', '.join(g['geometry']+' / '+g['group'] for g in hidden)+'.'
        r['state_behavior'][state]=dict(note=note,groups=groups,evidence='Source AST GroupStates; not runtime verified')
    lines.append('| '+r['asset_id']+' | '+r['source_pack']+' | '+r['state_behavior']['Construction']['note']+' | '+r['state_behavior']['Pillaged']['note']+' |')
    r['material_conversion_notes']=['Original DDS and MTL/AST bindings retained; PNGs decoded at original resolution. Blender Principled preview approximates the Firaxis shader; burn, snow, FOW, tint-mask and decal height behavior are not implemented in the preview. Normal-map orientation has not been verified in Asset Editor.']+r['issues']
    r['pivot']=[0,0,0]
    r['dimension_units']='Source geometry units; identical Blender units; visible Worked-state asset-local bounds'
    r['source_model_transforms']={m['geometry']:json.loads((LIB/m['extracted']).read_text())['models'] for m in r['models']}
    # Source AST declares no attachments/animations for these simple props; record exceptions honestly.
    ast=ET.parse(LIB/r['source_ast_copy']).getroot()
    r['source_behavior_counts']={tag:len(ast.findall(path)) for tag,path in [('attachments','.//m_Points/Element'),('animation_bindings','.//m_animationBindings/m_Bindings/Element'),('timelines','.//m_Timelines/Element')]}
d['import_contract']={'geometry':'Vertex XYZ preserved exactly within float precision. One Blender unit equals one FGX geometry unit. No location/rotation/scale applied and no preview-scene placement imported.','uv':'Source V converted to Blender 1-V, same as the inspected CN6 importer; source UV values and original FGX retained. No atlas remapping.','pivot':'Asset-local origin is retained. FGX InitialPlacement belongs to source authoring scene, recorded in source_model_transforms and object metadata, not used to place the reusable asset.','skeleton':'Original bone hierarchy, local transforms, inverse bind matrices and vertex weights retained. Hidden source_skeleton collections contain bind transform references, not export geometry or animated armatures. Static bind-pose meshes remain in source model space.','placement':'Future scene placements: Blender XYZ / 10, reversed Z rotation for AE. Preserve scale and parent transforms; not destructively applied here.','roles':'Reused assets use source_asset_id and export_role=reused_asset. Future new attachments CSC_Attached_; incorporated custom geometry CSC_Fixed_. Classify terrain following by physical support, not distance.','target':'Around 300 unique CSC assets is a flexible design goal; repeated placements reference shared assets.'}
(LIB/'catalogue.json').write_text(json.dumps(d,indent=2))
(LIB/'STATE_BEHAVIOR.md').write_text('\n'.join(lines)+'\n')
counts=collections.Counter(r['source_pack'] for r in d['assets'])
readme='''# CSC Prop Library

Individual reusable blends, with external portable textures and source records.
Discover the current count from catalogue.json. Authored Blender entries have
origin=authored_blender and a registration_status; their Windows assets and state
wiring may still be pending. The source converter preserves these blends.
Open any blend, or append its asset collection/mesh into a building scene. Multi-component
assets have an asset-ID root; preserve the component hierarchy and metadata. Hidden
source skeleton references are not placement geometry. The scene opens in Worked state.

Files:
- `catalogue.json`: asset IDs, package provenance, relative blend paths, dimensions,
  source transforms, component mapping, materials, state behavior and verification.
- `STATE_BEHAVIOR.md`: concise per-asset Construction/Pillaged behavior.
- `verification.json`: saved-file geometry, transforms, normals, UVs and texture checks.
- `textures/`: shared original DDS plus full-resolution decoded PNGs used in Blender.
- `sources/`: original AST, GEO, FGX, MTL, TEX and extracted geometry records.

Geometry is source-local and unchanged. UV V uses the documented 1-V import convention.
No object transforms were applied. FGX authoring-scene InitialPlacement is recorded as
metadata, separate from the reusable local asset. Library preview placements are excluded.
Future AE placement conversion is Blender XYZ / 10 with reversed Z rotation; keep scale
and parent transforms. Do not apply this conversion to the library's mesh vertices.

All game assets were checked against SDK package file manifests, not inferred from
pantry presence. Counts: '''+str(dict(counts))+'''. No Gathering Storm assets happened
to be present in this starting inventory. No excluded-pack or unresolved asset was exported.

Blender 5.1.2 verification covers saved geometry, topology, UVs, identities, transforms,
group material assignments, custom normals and decoded texture dimensions. Original
material bindings and asset AO overrides are retained. Blender previews approximate
Firaxis shaders: burn/snow/FOW/tint/decal-height effects are source metadata only. For
assets lacking UV3, emissive textures remain bound but preview emission is disabled
pending verification of the source shader's UV routing. See per-asset notes.

No Asset Editor, cook, terrain-following or in-game verification was performed.
Construction/Pillaged notes describe source AST declarations, not tested runtime results.
No geometry exports are blocked; shader-preview limitations remain explicitly recorded.
'''
(LIB/'README.md').write_text(readme)
print(dict(counts));print('Behavior notes added:',len(d['assets']));print('Behavior extras:',[(r['asset_id'],r.get('source_behavior_counts',{})) for r in d['assets'] if any(r.get('source_behavior_counts',{}).values())])
