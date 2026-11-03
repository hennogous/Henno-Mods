"""User-authorized minimal placement adjustment; no geometry or other AST edits."""
import json,math,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-bakery-display-depth-20261029'
p=ROOT/'Civ Supply Chains/Assets/CSC_BAKERS_Bakery_Modern_2.ast'
before=p.read_bytes();text=before.decode('utf-8')
pattern=r'(<m_position>\s*<x>)(-16.919180)(</x>\s*<y>)(-6.597803)(</y>\s*<z>0.000000</z>\s*</m_position>\s*<m_orientation>.*?<m_Name text="CSC_Attach_Rack" />)'
m=re.search(pattern,text,re.S);assert m,'Expected saved trolley position changed; inspect before editing.'
front=-151.2222;rear=-145.5543212890625;dy=front-1.0-rear
dx_world=math.sin(.626573)*dy;dy_world=math.cos(.626573)*dy
x=-16.919180+dx_world/10;y=-6.597803+dy_world/10
new=text[:m.start()]+m[1]+f'{x:.6f}'+m[3]+f'{y:.6f}'+m[5]+text[m.end():]
O.mkdir(parents=True,exist_ok=True);(O/'Bakery_2_before_trolley_move.ast').write_bytes(before)
p.write_bytes(new.encode('utf-8'))
assert p.read_text().count(f'<x>{x:.6f}</x>')==1
report={'authorization':'User: Move the trolley just clear','attachment':'CSC_Attach_Rack','before':[-16.919180,-6.597803,0],'after':[x,y,0],'district_frame_shift':[0,dy,0],'clearance':1.0,'rotation_scale_and_other_content_preserved':True,'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(O/'trolley-clearance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
