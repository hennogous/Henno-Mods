"""Compare the actual rendered shoulder change and verify its narrow scope."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
O=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout';D=Path.home()/'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads';before=O/'history/before-worn-shoulders'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((before/'delivery-validation.json').read_text());records=json.loads((O/'masters.json').read_text());paths={r['id']:Path(r['blend']) for r in records}
assert all(sha(paths[r['id']])==r['source_sha256'] for r in old['models'])
modern=list((D/'textures').rglob('CSC_Roads_Modern*'));assert all(sha(p)==sha(before/'textures'/p.relative_to(D/'textures')) for p in modern)
assert sha(D/'textures/CSC_Roads_Industrial_01_B.png')==sha(D/'textures/CSC_Roads_Industrial_01_FOW.png')
board=Image.new('RGB',(1400,770),(28,33,37));dr=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
for i,(path,label) in enumerate([(before/'02_First_building.png','Before — clean cut edges'),(O/'02_First_building.png','After — worn paving shoulders')]):
 im=Image.open(path).convert('RGB').crop((390,350,860,820)).resize((700,700),Image.Resampling.LANCZOS);board.paste(im,(700*i,60));dr.text((20+700*i,17),label,font=font,fill='white')
board.save(O/'Worn_Shoulders_Before_After.png')
report={'saved_geometry_sources_unchanged':True,'modern_png_and_dds_unchanged':True,'stone_B_FOW_coverage_match':True,'painted_source_and_prompt':'shoulder-paint-provenance.json','edited_maps':[{ 'path':str(p),'sha256':sha(p)} for p in (D/'textures').glob('CSC_Roads_Industrial*')],'visual_evidence':'Worn_Shoulders_Before_After.png','visual_review':'Original central paving retained; broken stone/dirt visible beyond asphalt and inner island edge; fading within existing card margins. No native shader/terrain verification.'}
(O/'shoulder-validation.json').write_text(json.dumps(report,indent=2));print('SHOULDER_SCOPE_CHECKS_PASS')
