"""Prepare review-only candidate sources, without changing the reusable library."""
import json,sys,re,importlib.util,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(sys.argv[1]).resolve()
GROUPS={
'Timber, logs and planks':'''DIS_PRD_PileWoodA DIS_PRD_PileWoodB DIS_PRD_PileWoodC DIS_PRD_Wood_Plank
IMP_Lumbermill_IND_Beam IMP_Lumbermill_IND_Plank IMP_Lumbermill_IND_PlankStack IMP_Lumbermill_IND_Plankpile IMP_Lumbermill_IND_Plankpile_SM
IMP_Lumbermill_Medieval_Log IMP_Lumbermill_Medieval_Log_Cut IMP_Lumbermill_Medieval_Log_Cut_Stack IMP_Lumbermill_Medieval_Scrap IMP_Lumbermill_Medieval_Scrap_SM IMP_Lumbermill_Medieval_Stump
IMP_QuarryREDO_WoodBeam IMP_QuarryREDO_WoodPile IMP_Camp_IND_Firewood
PROP_Lumber_A PROP_Lumber_B PROP_Lumber_C PROP_Lumber_D PROP_Lumber_E
WON_Woodpiles_Movie_A WON_NewWoodpiles_Movie_A WON_NewWoodpiles_Movie_B''',
'Stone blocks and brick stock':'''DIS_ENC_Blocks DIS_PRD_PileBlockA DIS_PRD_PileBlockB DIS_PRD_PileBlockC DIS_PRD_StoneBlockA DIS_PRD_StoneBlockB DIS_PRD_StonePileA
IMP_QuarryREDO_BlockA IMP_QuarryREDO_BlockB IMP_QuarryREDO_BlockC IMP_Quarry_AN_Block_A IMP_Quarry_AN_Block_B
PROP_Stone_A PROP_Stone_B PROP_Stone_C PROP_Stone_D PROP_Stone_E PROP_Stone_F
WON_DarkerRedBrickPile_A WON_DarkerRedBrickPile_C WON_GreyBrickPile_A WON_GreyBrickPile_C WON_RedBrickPile_A WON_RedBrickPile_C WON_YellowBrickPile_A WON_YellowBrickPile_C WON_GreyBrick_A''',
'Loose material, ore and metal':'''DIS_HBR_Coal_Pile DIS_PRD_Pile DIS_PRD_PileA DIS_PRD_PileB DIS_PRD_PileC DIS_PRD_PileD DIS_PRD_PileE
IMP_QuarryREDO_DirtPileA IMP_QuarryREDO_DirtPileB IMP_QuarryREDO_DirtPileC IMP_QuarryREDO_DirtPileD IMP_QuarryREDO_ResourcePile IMP_QuarryREDO_ResourceA
PROP_Boulderpile_A PROP_BoulderPile_B WON_MetalPile_Movie_A WON_MetalPile_Movie_B WON_IBeamPile_Movie_A
RES_Iron_Rock_Bld_A RES_Copper_Rock_Bld_A RES_Gold_Rock_Bld_A RES_Jade_Rock_Bld_A''',
'Hay, hides and flexible materials':'''PROP_Haypile PROP_IN_Haybale PROP_IN_Haybales_LG PROP_IN_Haybales_SM PROP_MD_Haybales_LG
IMP_Camp_AN_Rack_LG IMP_Camp_AN_Rack_SM_A IMP_Camp_AN_Rack_SM_B IMP_Camp_AN_Rack_SM_C IMP_Camp_IND_Rack_LG
IMP_MINE_IND_Cloth Zimbabwe_cloth petra_RopeA petra_RopeB''',
'Bins, boxes and vessels':'''DIS_COM_Box_Closed DIS_COM_Box_Open DIS_HBR_Lg_Fish_Bin DIS_HBR_SM_Bin
IMP_PLNT_ANC_Bin_A IMP_PLNT_ANC_Bin_B IMP_PLNT_ANC_Bin_C IMP_Camp_IND_Bucket IMP_Camp_AN_Pot
IMP_PLNT_ANC_Barrel_Sm IMP_Fort_BarrelA_Medieval PROP_Crate_Industrial
DIS_COM_OTTO_Pot_A DIS_ENC_Ikanda_Pot DIS_Mbanza_Pot_Blue PROP_Pot_A PROP_Pot_B
DIS_PRD_Metal_Barrel DIS_HBR_Modern_Teal_Crate''',
'Carts, racks and handling equipment':'''IMP_QuarryREDO_Cart IMP_Quarry_AN_Sled_A IMP_Quarry_AN_Sled_B
IMP_PLNT_ANC_Cart IMP_PLNT_IND_Cart DIS_NBH_Market_Cart_A WON_Rhur_Cart IMP_Mine_IND_Car_Rocks
PROP_Ancient_Haycart PROP_IN_Haywagon IMP_Fort_Wagon_Industrial
DIS_PRD_HandCrane IMP_Lumbermill_Medieval_Saw IMP_Lumbermill_IND_Table IMP_Camp_AN_Table
IMP_Pasture_AN_Trough IMP_Pasture_IND_Trough'''
}
spec=importlib.util.spec_from_file_location('source_export',ROOT/'project/tools/blender/export_prop_library.py')
exp=importlib.util.module_from_spec(spec);spec.loader.exec_module(exp)
exp.STAGE=OUT/'work';exp.STAGE.mkdir(exist_ok=True)
discovery=json.loads((OUT/'discovery.json').read_text())
byid={}
for r in discovery['candidates']:
 if not r['excluded']:byid.setdefault(r['asset_id'],r)
selected=[]
for group,names in GROUPS.items():
 for aid in names.split():
  r=byid[aid].copy();r['category']=group
  ast=ET.parse(r['source_ast']).getroot()
  r['models']=[dict(geometry=exp.txt(e,'m_GeoName'),instance=exp.txt(e,'m_Name'),xml=ET.tostring(e,encoding='unicode')) for e in ast.findall('./m_GeometrySet/m_ModelInstances/Element')]
  # Keep native visibility explicit: construction stock often vanishes in Worked.
  visible={}
  for m in r['models']:
   for e in ET.fromstring(m['xml']).findall('m_GroupStates/Element'):
    state=exp.txt(e,'m_StateName')
    if any(exp.txt(v,'m_ParamName')=='Visible' and exp.txt(v,'m_bValue')=='true' for v in e.findall('.//Element')):visible[state]=visible.get(state,0)+1
  r['preview_state']=next((s for s in ['Worked','Unworked','Construction','Unbuilt','Pillaged','Default'] if visible.get(s)),next(iter(visible),'geometry only'))
  r['candidate_note']='Native '+r['preview_state']+' state preview.'
  if r['preview_state'] not in ('Worked','Unworked'):r['candidate_note']+=' Native state visibility needs review before ordinary scene reuse.'
  if '_Movie_' in aid:r['candidate_note']+=' Wonder movie source; check native registration and state use.'
  r['source_behavior_counts']={tag:len(ast.findall(path)) for tag,path in [('attachments','.//m_Points/Element'),('animation_bindings','.//m_animationBindings/m_Bindings/Element')]}
  if any(r['source_behavior_counts'].values()):r['candidate_note']+=' Contains animation/attachment metadata; preview is static geometry.'
  selected.append(r)
(OUT/'selection.json').write_text(json.dumps(selected,indent=2))
index={}
for p in exp.SDK.rglob('*'):
 if p.suffix.lower() in ('.ast','.geo','.fgx','.mtl','.dds','.tex'):index.setdefault(p.name.lower(),[]).append(str(p))
(exp.STAGE/'file_index.json').write_text(json.dumps(index))
print('Selected',len(selected),'review candidates',flush=True)
if '--prepare' in sys.argv:
 prepared=[];materials={};failed=[]
 for row in selected:
  (exp.STAGE/'inventory.json').write_text(json.dumps([row]))
  try:
   exp.prepare()
   d=json.loads((exp.STAGE/'CSC_Prop_Library/catalogue.json').read_text());prepared.extend(d['assets']);materials.update(d['materials'])
  except Exception as exc:failed.append(dict(asset_id=row['asset_id'],error=str(exc)));print('FAILED',row['asset_id'],str(exc),flush=True)
 final=dict(assets=prepared,materials=materials)
 (exp.STAGE/'CSC_Prop_Library/catalogue.json').write_text(json.dumps(final,indent=2))
 (OUT/'preparation-failures.json').write_text(json.dumps(failed,indent=2))
 print('PREPARED',len(prepared),'FAILED',len(failed),flush=True)
