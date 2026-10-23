"""Verify saved source UV changes and native animation against authored motion."""
import bpy,sys,json,math
import numpy as np
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'project/tools/art'))
from windmill_tower_migrate import region_at
OUT=Path(sys.argv[sys.argv.index('--')+1]);ART=Path.home()/'Desktop/Working Files/3D Art'
regions=json.loads((OUT/'atlas-migration.json').read_text())['regions']
def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    result={}
    for ob in bpy.data.objects:
        if ob.type!='MESH':continue
        m=ob.data
        result[ob.name]={'position':[list(v.co) for v in m.vertices],'matrix':[list(r) for r in ob.matrix_world],
            'faces':[list(f.vertices) for f in m.polygons],'materials':[mat.name if mat else None for mat in m.materials],
            'uv':[[list(v.uv) for v in layer.data] for layer in m.uv_layers],
            'weights':[[[g.group,g.weight] for g in v.groups] for v in m.vertices]}
    return result
sources=[]
for row in json.loads((OUT/'source-migration.json').read_text()):
    source=Path(row['source']);a=snapshot(OUT/'before-sources'/source.relative_to(ART));b=snapshot(row['staged']);assert a.keys()==b.keys();moved=0
    for name in a:
        x,y=a[name],b[name]
        for k in x:
            if k!='uv':assert x[k]==y[k],(source,name,k)
        assert x['uv'][1:]==y['uv'][1:],(source,name,'UV2/3')
        if not x['uv']:continue
        for old,new in zip(x['uv'][0],y['uv'][0]):
            if old==new:continue
            r=region_at(regions,old[0]*1024,(1-old[1])*1024);assert r
            assert max(abs(new[i]-old[i]-r['delta'][i]/1024*(1 if i==0 else -1)) for i in (0,1))<1e-7
            moved+=1
    assert moved==row['uv1_loops_moved'];sources.append({'source':str(source),'changed_uv1_loops':moved,'all_other_geometry_weights_transforms_and_uvs_unchanged':True})
(OUT/'source-migration-validation.json').write_text(json.dumps(sources,indent=2))

NAME='CSC_BAKERS_Wind_Mill_Tower'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'new-tower'/(NAME+'.blend')),load_ui=False,use_scripts=False)
rig=bpy.data.objects[NAME];scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene
lines=[l.strip() for l in (OUT/'animation-readback/clip.na2').read_text().splitlines() if l.strip() and not l.startswith('//')]
count=int(lines[1].split(':')[1]);tracks={};idx=6
for i in range(3):
    name=lines[idx];idx+=1;tracks[name]=np.array([list(map(float,l.split())) for l in lines[idx:idx+count]]).reshape(count,4,4).transpose(0,2,1);idx+=count
raw=json.loads((OUT/'tower-native.json').read_text());bones={b['name']:b for b in raw['models'][0]['bones']}
transforms={k:ts@np.array(bones[k]['inverseWorld']).reshape(4,4).T for k,ts in tracks.items()}
vertices={}
for mesh in raw['meshes']:
    for v in mesh['vertices']:
        assert v['boneWeights'][0]==255
        bone=mesh['boneBindings'][v['boneIndices'][0]];vertices.setdefault(bone,[]).append([*v['position'],1])
maximum=0;loop_error=0
for bone,vs in vertices.items():
    vs=np.array(vs).T
    loop_error=max(loop_error,float(np.max(np.linalg.norm(((transforms[bone][-1]-transforms[bone][0])@vs)[:3],axis=0))))
    for frame in range(count):
        scene.frame_set(frame+1);authored=np.array(rig.pose.bones[bone].matrix@rig.data.bones[bone].matrix_local.inverted())
        maximum=max(maximum,float(np.max(np.linalg.norm(((authored-transforms[bone][frame])@vs)[:3],axis=0))))
all_points=np.array([v['position'] for m in raw['meshes'] for v in m['vertices']]);span=float(np.max(np.ptp(all_points,axis=0)))
report={'frames_checked':count,'duration_seconds':10,'max_native_vs_authored_vertex_error':maximum,'max_loop_seam_vertex_error':loop_error,
        'max_error_fraction_of_model_span':maximum/span,'loop_error_fraction_of_model_span':loop_error/span,
        'static_root_matrix_error':float(np.max(abs(transforms['Root']-transforms['Root'][0]))),
        'note':'Native FBX/Granny compression: require motion error below 0.05% of model span and loop seam below 0.01%.'}
assert maximum/span<.0005 and loop_error/span<.0001 and report['static_root_matrix_error']<1e-6,report
(OUT/'native-animation-validation.json').write_text(json.dumps(report,indent=2));np.savez(OUT/'native-animation-transforms.npz',**transforms)
print('VERIFIED',len(sources),'saved source files;',report,flush=True)
