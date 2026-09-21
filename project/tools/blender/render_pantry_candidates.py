"""Build temporary candidate blends and render contact views using existing helpers.

Run with Blender --background --factory-startup --python-exit-code 1 --python
this.py -- REVIEW_DIRECTORY [--build-only] [--only ASSET ...]
These files are a review workspace, never the live CSC prop library.
"""
import sys,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
LIB=OUT/'work/CSC_Prop_Library'
source=ROOT/'project/tools/blender/build_prop_library_blends.py'
# Reuse the current importer/material implementation, but select the candidate's
# explicit source state instead of forcing Worked for construction-stock assets.
code=source.read_text(encoding='utf-8').split("for row in data['assets']:")[0]
code=code.replace("s['state']=='Worked'","s['state']==row.get('preview_state','Worked')")
args=sys.argv[:];sys.argv=['candidate-builder','--',str(LIB)]
namespace={'__file__':str(source),'__name__':'candidate_builder'}
exec(compile(code,str(source),'exec'),namespace)
sys.argv=args
data=namespace['data']
if '--only' in args:
 ids=set(args[args.index('--only')+1:]);data['assets']=[r for r in data['assets'] if r['asset_id'] in ids]
for row in data['assets']:
 if (LIB/(row['asset_id']+'.blend')).exists():continue
 try:
  namespace['build'](row)
  print('CANDIDATE_BUILT',row['asset_id'],flush=True)
 except Exception as exc:
  import traceback;traceback.print_exc();row['status']='preview_failed';row['issues'].append(str(exc))
(OUT/'candidate-catalogue.json').write_text(json.dumps(data,indent=2))
if '--build-only' in args:raise SystemExit(0)
render_source=ROOT/'project/tools/blender/render_prop_contact_previews.py'
render_code=render_source.read_text(encoding='utf-8').replace('scene.cycles.samples = 24','scene.cycles.samples = 16').replace('scene.render.resolution_x = 768','scene.render.resolution_x = 480').replace('scene.render.resolution_y = 640','scene.render.resolution_y = 400')
renderer={'__file__':str(render_source),'__name__':'candidate_renderer'}
exec(compile(render_code,str(render_source),'exec'),renderer)
(OUT/'previews').mkdir(exist_ok=True)
results=[]
for row in data['assets']:
 try:
  result=renderer['render_asset'](LIB/(row['asset_id']+'.blend'),LIB,OUT)
  result.update(state=row['preview_state'],category=row['category'],source_pack=row['source_pack'],candidate_note=row['candidate_note'])
  (OUT/'previews'/(row['asset_id']+'.json')).write_text(json.dumps(result,indent=2))
  results.append(result)
 except Exception as exc:
  import traceback;traceback.print_exc();print('CANDIDATE_RENDER_FAILED',row['asset_id'],str(exc),flush=True)
(OUT/'render-run.json').write_text(json.dumps(results,indent=2))
print('CANDIDATE_PREVIEWS_COMPLETE',len(results),flush=True)
