"""Square-tray source bounds against actual saved parent attachment transforms."""
import bpy,sys,math,json,xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
import build_bakery_props as B
B.setup('Bakery_Tray_Fit_Review');scene=B.review;exp=B.export
root=ET.parse(B.ROOT/'Civ Supply Chains/Assets/CSC_BAKERS_Bakery.ast');rows=[]
for point in root.findall('.//m_attachmentPoints/m_Points/Element'):
 name=point.find('m_Name').get('text')
 if not name.startswith('BakeryProp_BAKERS_Bread_Basket_'):continue
 ident=name.replace('BakeryProp_','CSC_');position=Vector([float(point.findtext('m_position/'+a))*10 for a in 'xyz']);angle=-float(point.findtext('m_orientation/z'));scale=float(point.findtext('m_scale'))
 with bpy.data.libraries.load(str(B.SOURCE/(ident+'.blend')),link=False) as (a,b):b.scenes=['Export']
 src=b.scenes[0];meshes=[o for o in src.objects if o.type=='MESH'];coords=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
 rows.append(dict(asset=ident,position=list(position),angle=angle,scale=scale,bounds=bounds))
 for o in meshes:
  matrix=o.matrix_world.copy()
  for col in list(o.users_collection):col.objects.unlink(o)
  scene.collection.objects.link(o);o.parent=None
  for mod in list(o.modifiers):o.modifiers.remove(mod)
  o.matrix_world=Matrix.Translation(position)@Matrix.Rotation(angle,4,'Z')@Matrix.Scale(scale,4)@matrix;o.data.materials.clear();o.data.materials.append(B.mat)
 bpy.data.scenes.remove(src)
gaps=[]
for i,a in enumerate(rows):
 for b in rows[i+1:]:
  assert a['angle']==b['angle'];theta=-a['angle'];dx=b['position'][0]-a['position'][0];dy=b['position'][1]-a['position'][1];delta=[dx*math.cos(theta)-dy*math.sin(theta),dx*math.sin(theta)+dy*math.cos(theta)];sep=[abs(delta[j])-((a['bounds'][j][1]-a['bounds'][j][0])*a['scale']+(b['bounds'][j][1]-b['bounds'][j][0])*b['scale'])/2 for j in range(2)];assert max(sep)>0,sep;gaps.append(dict(pair=[a['asset'],b['asset']],local_axis_gap=sep,separated=True))
(B.OUT/'tray-fit-audit.json').write_text(json.dumps(dict(source='saved independent meshes and actual parent AST transforms',trays=rows,pairs=gaps,overlaps=False),indent=2))
bpy.context.window.scene=scene;center=sum((Vector(r['position']) for r in rows),Vector())/3;scene.camera.location=center+Vector((0,0,60));scene.camera.rotation_euler=(center-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=28;scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.film_transparent=False;scene.render.image_settings.file_format='JPEG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.quality=95;scene.render.filepath=str(B.OUT/'Stand_Trays_Top_Review.jpg');bpy.ops.render.render(write_still=True)
print('STAND TRAY NONOVERLAP',gaps)
