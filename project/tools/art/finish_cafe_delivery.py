"""Record the Cafe handoff and register its two approved shared masters."""
from cafe_atlas import *
from PIL import Image,ImageDraw
from collections import Counter
def main():
    report=json.loads((OUT/'install-report.json').read_text());assets=report['assets'];counts={a['asset']:a for a in assets};placements=json.loads((OUT/'review-placements.json').read_text());instances=Counter(p['asset'] for p in placements)
    bespoke=1413+sum(counts[k]['vertices']*v for k,v in instances.items() if k.startswith('CSC_BAKERS_'))
    total=1413+sum(counts[k]['vertices']*v for k,v in instances.items());report['review_counts']=dict(base=1413,building_plus_bespoke=bespoke,advisory_target=2200,all_visible_vertices=total,instances=dict(instances));(OUT/'install-report.json').write_text(json.dumps(report,indent=2))
    library=ART/'Props/CSC_Prop_Library';path=library/'catalogue.json'
    if not (OUT/'before-install/prop-catalogue.json').exists():shutil.copy2(path,OUT/'before-install/prop-catalogue.json')
    catalogue=json.loads(path.read_text())
    for ident in ['CSC_ALL_Garden_Wall_Curve','CSC_ALL_Stage_4_Cobble_Decals']:
        exp=json.loads((OUT/(ident+'-export.json')).read_text());lo,hi=exp['bounds'];relative='../Bakers/Cafe_Regular_20261017/'+ident+'.blend'
        record=dict(asset_id=ident,source_pack='CSC',origin='authored_blender',blend_path=relative,blend_file=relative,export_scene='Export',dimensions=[b-a for a,b in zip(lo,hi)],registration_status='installed_native_assets',reuse_scope='shared',reuse_approved=True,status='verified_blender_and_native',blend_sha256=sha(SOURCE/(ident+'.blend')),state_behavior={'Worked':'visible','Unworked':'visible','Construction':'hidden','Pillaged':'hidden','Unbuilt':'hidden'},pivot='Local ground pivot',reuse_notes='30-degree radius96 wall segment, buried4-unit footing; duplicate and rotate in AE.' if 'Wall' in ident else '182-unit circular decal, exact existing square-cobble base colour, geometry-defined footprint.',verification=counts[ident])
        existing=next((a for a in catalogue['assets'] if a['asset_id']==ident),None)
        if existing:assert existing['blend_sha256']==record['blend_sha256'];existing.update(record)
        else:catalogue['assets'].append(record)
    for item in catalogue['assets']:
        if item['asset_id']=='CSC_ALL_Oval_Table':item['registration_status']='installed_native_assets';item['native_verification']=counts[item['asset_id']]
    path.write_text(json.dumps(catalogue,indent=2))
    canvas=Image.new('RGB',(1000,560),(238,233,221));draw=ImageDraw.Draw(canvas)
    for i,ident in enumerate(['CSC_ALL_Garden_Wall_Curve','CSC_ALL_Stage_4_Cobble_Decals']):
        im=Image.open(OUT/(ident+'-preview.png')).convert('RGBA');im.thumbnail((480,480));canvas.paste(im,(i*500+10,10),im);draw.text((i*500+15,510),ident,fill=(35,30,24))
    canvas.save(OUT/'Cafe_Shared_Additions.png')
    lines=['# Cafe regular concept — prop delivery','',f'Editable sources: `{SOURCE}`','',f'Review package: `{OUT}`','','One .blend per independently exported model. Export contains only that model and its static rig; Review supplies lighting/camera. The combined Cafe_Regular_Review.blend is a placement proposal, not an export source.','','## Files','', '| Model | Exported vertices | Triangles |', '|---|---:|---:|']
    lines += [f"| {a['asset']} | {a['vertices']} | {a['triangles']} |" for a in assets]
    lines += ['', '## Reuse and placement','', 'The oval table and closed sack preserve their existing source geometry and UVs. Eight copies of the new 30-degree wall segment form the proposed crescent. Each segment has its own ground pivot. The cobbles reuse the exact square-variant base-colour PNG named by Henno; the existing Stage3 opacity/height sheet is tied to another building layout, so the new circular decal uses a geometry footprint and a new material pointing at the existing B texture. No cobble artwork was generated.', '', 'The brewing set uses the counter ground pivot and has its contents at counter height17.8. The table service and reading set use the table ground pivot and tabletop height13. Apply the same placement/rotation/scale as their support. The pastry tray rests on its own local Z=0 contact plane. Plants and pots remain for Henno to place from existing assets.', '', '## Atlas and validation','',f'Shared atlas {RELEASE}: six ImageGen-painted surfaces in previously vacant slots10–15; seven isolated AO cells in Bakers Stage4. All pre-existing surface pixels, other AO allocations, opacity/emission and sheet02 preserved. Source artwork, companion maps, manifests, hashes and reproducible packer are in the canonical release.', '', 'All ten saved blends pass automated source validation. All ten CN6→FGX→CN6 comparisons preserve geometry, normals, UVs and triangles within5e-6 numeric error. Runtime AST/GEO/MTL and XLP registrations are installed. Props are visible in Worked/Unworked and hidden in Construction/Pillaged/Unbuilt. Existing building ASTs are byte-for-byte preserved; final assembly, duplicates and plants remain in AE. No new base building geometry is exported.', '', f'Geometry accounting for the proposed scene: building plus bespoke props {bespoke:,} exported vertices versus the advisory2,200 target; full scene including reused furniture, sacks, wall copies and decal {total:,}. Counts are reported rather than hidden by the per-file checks. The coffee sets and repeated chairs account for most of the excess.', '', 'The unchanged generic L3 reference retains its inherited static-weight validation issue. That reference is excluded from the new exports. Blender renders are appearance previews; AE decal projection/terrain behavior, cooking and in-game appearance are not yet verified. Final icon/SV work should use the saved AE AST after placement.', '', 'Source and review provenance: source-parity.json in revision-01-base, native-verification.json, individual *-validation.json and *-export.json, cobbles-provenance.json, review-placements.json and install-report.json.']
    text='\n'.join(lines)+'\n'
    text=text.replace('new material pointing at the existing B texture','new material using a colour-identical copy with only the old layout alpha cleared')
    text=text.replace('Existing building ASTs are byte-for-byte preserved','Existing building ASTs were not rewritten')
    text=text.replace('height17.8','height 17.8').replace('height13','height 13').replace('slots10','slots 10').replace('within5e-6','within 5e-6').replace('advisory2,200','advisory 2,200')
    (SOURCE/'README.md').write_text(text,encoding='utf-8');(OUT/'README.md').write_text(text,encoding='utf-8')
    doc=ROOT/'project/docs/art/cafe-regular-prop-delivery.md';doc.write_text(text,encoding='utf-8')
    shutil.copy2(OUT/'Cafe_Prop_Contact_Sheet.png',SOURCE/'Prop_Contact_Sheet.png')
    print(json.dumps(report['review_counts'],indent=2))
if __name__=='__main__':main()
