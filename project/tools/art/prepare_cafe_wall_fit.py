"""Read saved AE assembly, including decals, for a disposable fitting snapshot."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'blender'))
import render_ae_asset as R
from cafe_atlas import OUT,ROOT
OUT.mkdir(parents=True,exist_ok=True)
resolver=R.Resolver(ROOT/'Civ Supply Chains',R.DEFAULT_SDK)
assembly=R.Assembly(resolver)
assembly.is_decal=lambda ident,near:False
root=assembly.asset(ROOT/'Civ Supply Chains/Assets/CSC_BAKERS_Cafe.ast')
R.prepare_geometry(assembly,OUT/'_cache',OUT)
job=dict(root=root,assets=assembly.assets,geometries=assembly.geometries,materials=assembly.materials,warnings=assembly.warnings,output=str(OUT),inputs=resolver.inputs)
(OUT/'ae-job.json').write_text(json.dumps(job,indent=2))
print('Prepared',len(assembly.assets),'saved assets',len(assembly.geometries),'native geometries')
