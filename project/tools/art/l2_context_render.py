"""Review saved AE assemblies with flat terrain projection, actual road03 and paving."""
import json,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from ae_asset_render_blender import Builder

class ContextBuilder(Builder):
    def assemble(self,key,transform=None,path=None,root=False):
        super().assemble(key,transform,path,root)
        if not root:return
        for obj,record in zip(self.objects,self.mapping):
            material=next(v for v in self.job['materials'].values() if v['id']==record['material'])
            if 'decal' not in material['shader'].lower():continue
            level=.08 if 'Cobble' in record['material'] else .04 if 'Classical' in record['material'] else .02
            inv=obj.matrix_world.inverted()
            for v in obj.data.vertices:
                p=obj.matrix_world@v.co;p.z=level;v.co=inv@p
            obj.visible_shadow=False
            for mat in obj.data.materials:
                bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
                base=next((n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.label=='BaseColor'),None)
                height=next((n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.label=='Heightmap'),None)
                if base:mat.node_tree.links.new(base.outputs['Alpha'],bs.inputs['Alpha'])
                if height:
                    bump=mat.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.8;bump.inputs['Distance'].default_value=2
                    mat.node_tree.links.new(height.outputs['Alpha'],bump.inputs['Height']);mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
        mesh=bpy.data.meshes.new('Review_Grass');mesh.from_pydata([(-700,-700,-.1),(700,-700,-.1),(700,700,-.1),(-700,700,-.1)],[],[(0,1,2,3)])
        ground=bpy.data.objects.new('Review_Grass',mesh);self.scene.collection.objects.link(ground)
        mat=bpy.data.materials.new('Review_Grass');mat.use_nodes=True
        bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.95
        noise=mat.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=140
        ramp=mat.node_tree.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.075,.12,.025,1);ramp.color_ramp.elements[1].color=(.20,.29,.06,1)
        mat.node_tree.links.new(noise.outputs['Fac'],ramp.inputs[0]);mat.node_tree.links.new(ramp.outputs[0],bs.inputs['Base Color']);mesh.materials.append(mat)

job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
ContextBuilder(job,'sv').render()
