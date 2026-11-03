"""Pack generated albedo and allocate fixed room-lighting cells independently of UV1."""
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw,ImageFont
import numpy as np,json,shutil,hashlib
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-interior-lighting-20261028';MOD=ROOT/'Civ Supply Chains'
GENERATED=Path.home()/'.codex/generated_images/01a17705-552a-7272-bb5e-272856a3d4c2/exec-0ac6384e-d520-4b95-b556-1cec6df05e8d.png'
shutil.copy2(GENERATED,O/'sources/Interior_Bright_ImageGen.png');g=Image.open(GENERATED).convert('RGB');base=Image.open(O/'sources/CSC_Atlas_Modern_B_BAKERS.png').convert('RGBA');old=np.array(base);patches={};metrics=[]
for i,slot in enumerate((11,12,15)):
 p=g.crop((round(i*g.width/3),0,round((i+1)*g.width/3),g.height)).resize((128,128),Image.Resampling.LANCZOS)
 x=512+slot%4*128;y=slot//4*128;before=base.crop((x,y,x+128,y+128));base.paste(p,(x,y));patches[slot]=p
 metrics.append({'slot':slot,'mean_before':float(np.asarray(before)[:,:,:3].mean()),'mean_after':float(np.asarray(p).mean())})
mask=np.zeros((1024,1024),bool)
for slot in (11,12,15):x=512+slot%4*128;y=slot//4*128;mask[y:y+128,x:x+128]=True
assert np.array_equal(old[~mask],np.array(base)[~mask]);base.save(O/'textures/CSC_Atlas_Modern_B_BAKERS.png')
# Keep all legacy window locations. New generic room slots occupy independent UV3 cells.
legacy=Image.open(O/'textures/CSC_Atlas_Modern_E.png').convert('RGB');emissive=legacy.resize((512,512),Image.Resampling.NEAREST)
allocation={11:8,12:9,15:10}
for surface_slot,e_slot in allocation.items():
 rgb=np.asarray(patches[surface_slot].resize((60,60),Image.Resampling.LANCZOS),float)/255
 # Low radiance, preserving the painted scene's colour and contrast. No visible lamp geometry.
 linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4);linear*=.12 if surface_slot!=15 else .055
 srgb=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)
 tile=Image.fromarray(np.uint8(np.clip(srgb*255,0,255))).filter(ImageFilter.GaussianBlur(.35));tile=Image.fromarray(np.pad(np.asarray(tile),((2,2),(2,2),(0,0)),mode='edge'))
 x=256+e_slot%4*64;y=e_slot//4*64;assert np.asarray(emissive.crop((x,y,x+64,y+64))).max()==0
 emissive.paste(tile,(x,y))
emissive.save(O/'textures/CSC_Atlas_Modern_E_BAKERS.png')
# Historical split is an identity copy of the effective installed DDS, not an older source export.
Image.open(MOD/'Textures/CSC_Atlas_E.dds').convert('RGBA').save(O/'textures/CSC_Atlas_E_BAKERS.png')
shutil.copy2(MOD/'Textures/CSC_Atlas_E.dds',O/'sources/Effective_Historical_E.dds')
plan={'version':1,'quarter':'BAKERS','services':'No Service binding or active-brightness variants in this task','families':{'historical':{'runtime':'CSC_Atlas_E_BAKERS','size':256,'layout':'Existing historical UV3 and effective installed lighting copied exactly; no historical mesh changes'},'modern':{'runtime':'CSC_Atlas_Modern_E_BAKERS','size':512,'quadrants':{'stage2':[0,0,256,256],'stage3':[256,0,512,256],'stage4':[0,256,256,512],'storage':[256,256,512,512]},'grid_per_quadrant':[4,4],'cell_size':64,'UV3_inset_pixels':2,'slot_roles':{'0-7':'Existing facade/window locations retained; currently Stage2 slot7 and Stage3 slot5','8':'room A back scene','9':'room A sides/ceiling','10':'room A floor','11':'reserved room A detail','12':'black sentinel; NEVER paint. Includes existing global dark UV (0.02,0.02)','13':'reserved room B back scene','14':'reserved room B sides/ceiling','15':'reserved room B floor'},'occupied_rooms':{'stage3':{'room_A':{'8':'Bakery shelves','9':'Bakery utensils/tiles','10':'light oak floor'},'geometry':'three room boxes behind ground windows and glazed door share these generic chart locations'}},'policy':'UV3 belongs to reusable geometry and stays fixed across Quarters; paint different room scenes into matching quarter-specific E cells. Non-emissive glass/frames retain black UV3. Future rooms use reserved slots, not per-building private atlases.'}},'current_B_patch_cells':[11,12,15],'current_UV3_from_surface_slot':allocation,'emission_linear_scale':{'back_and_sides':.12,'floor':.055},'historical_shared_fallback':'CSC_Atlas_E retained for un-migrated Quarters','modern_shared_fallback':'CSC_Atlas_Modern_E retained as legacy compatibility map'}
(O/'emissive-plan.json').write_text(json.dumps(plan,indent=2));(O/'paint-checks.json').write_text(json.dumps({'outside_interior_cells_unchanged':True,'cells':metrics,'generated_source':str(GENERATED)},indent=2))
prompt='Brighten the three registered interior B cells with off-white plaster, pale honey timber, light sage tiles and brighter bread; preserve shelf/tool/plank layout and reduce baked darkness. Built-in ImageGen edit of Interior_Paint_Target.png.'
(O/'sources/generation-provenance.json').write_text(json.dumps({'tool':'built-in image_gen','source':str(GENERATED),'target':'Interior_Paint_Target.png','prompt_summary':prompt,'packing':'Equal thirds resized to128 and installed only in Stage3 B cells11,12,15; no procedural albedo repaint'},indent=2))
print('MAPS_READY',metrics,flush=True)
