"""Render labelled candidate PNG sheets and a portable searchable HTML gallery."""
from pathlib import Path
import sys,json,math,html,re,collections,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(sys.argv[1]).resolve()
SDK=Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK Assets")
selection=json.loads((OUT/'selection.json').read_text())
catalogue=json.loads((OUT/'candidate-catalogue.json').read_text())
byid={r['asset_id']:r for r in catalogue['assets']}
discovery=json.loads((OUT/'discovery.json').read_text())
FONT='C:/Windows/Fonts/arial.ttf';BOLD='C:/Windows/Fonts/arialbd.ttf'
def font(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def txt(e,p):
 n=e.find(p);return n.get('text',n.text or '') if n is not None else ''
def native_bindings():
 result=collections.defaultdict(list);targets={r['asset_id'].lower() for r in selection}
 seen=set()
 for manifest in ['civ6','expansion1','expansion2']:
  for f in json.loads((SDK/(manifest+'-asset-deps.json')).read_text())['Files']:
   path=SDK/f['Filename']
   if path.suffix.lower()!='.xlp' or str(path).lower() in seen or not path.exists():continue
   seen.add(str(path).lower())
   try:tree=ET.parse(path).getroot()
   except ET.ParseError:continue
   for e in tree.findall('m_Entries/Element'):
    aid=txt(e,'m_ObjectName')
    if aid.lower() in targets:
     result[aid.lower()].append(dict(xlp=str(path.relative_to(SDK)),entry_id=txt(e,'m_EntryID'),asset_class=txt(tree,'m_ClassName'),package=txt(tree,'m_PackageName')))
 return result
bindings=native_bindings()
review_path=OUT/'visual-review-notes.json'
reviews=json.loads(review_path.read_text()) if review_path.exists() else {}
rows=[];blocked=[]
def state_notes(row):
 result={}
 for state in ('Construction','Pillaged'):
  groups=[]
  for model in row['models']:
   for group in ET.fromstring(model['xml']).findall('m_GroupStates/Element'):
    if txt(group,'m_StateName')!=state:continue
    values={txt(e,'m_ParamName'):txt(e,'m_ObjectName') or txt(e,'m_bValue') for e in group.findall('m_Values/m_Values/Element')}
    groups.append(dict(geometry=model['geometry'],mesh=txt(group,'m_MeshName'),group=txt(group,'m_GroupName'),values=values))
  visible=[g for g in groups if g['values'].get('Visible')=='true']
  unspecified=[g for g in groups if 'Visible' not in g['values']]
  materials=sorted({g['values'].get('Material','') for g in visible}-{''})
  burns=sorted({g['values'].get('BurnMaterial','') for g in visible}-{''})
  note=(f"{len(visible)} explicitly visible / {len(groups)} group bindings; materials: {', '.join(materials) or 'none explicitly visible'}." if groups else 'No explicit group-state bindings; fallback behaviour is not established.')
  if unspecified:note+=f' {len(unspecified)} bindings have unspecified visibility.'
  if burns:note+=' Burn bindings: '+', '.join(burns)+'.'
  result[state]=dict(note=note,bindings=groups,verification='Source AST metadata only; not simulated or checked in Asset Editor/in game.')
 return result
for n,r in enumerate(selection,1):
 r['number']=n;r['native_bindings']=bindings.get(r['asset_id'].lower(),[])
 r['state_behaviour']=state_notes(r)
 p=OUT/'previews'/(r['asset_id']+'.json')
 if not p.exists():
  r['reason']=('Source XML namespace parse error needs resolution before a faithful preview.' if r['asset_id']=='DIS_ENC_Ikanda_Pot' else 'Source InitialPlacement scale/shear needs converter support before a faithful preview.')
  blocked.append(r);continue
 row=r.copy();row.update(json.loads(p.read_text()));row['number']=n
 row['vertices']=sum(c['vertices'] for c in byid.get(r['asset_id'],{}).get('components',[]))
 # Build-only metadata can be regenerated; counts also come directly from FGX JSON.
 if not row['vertices']:
  row['vertices']=sum(len(mesh['vertices']) for m in byid[r['asset_id']]['models'] for mesh in json.loads((OUT/'work/CSC_Prop_Library'/m['extracted']).read_text())['meshes'])
 row['flags']=[]
 if r['preview_state'] not in ('Worked','Unworked'):row['flags'].append(r['preview_state'].upper()+'-STATE SOURCE')
 if '_Movie_' in r['asset_id']:row['flags'].append('MOVIE SOURCE')
 if not any(b['asset_class']=='TileBase' and 'fallback' not in b['xlp'].lower() for b in r['native_bindings']):row['flags'].append('CHECK TILEBASE REGISTRATION')
 if r['asset_id'] in reviews:
  row['visual_review_note']=reviews[r['asset_id']]
  row['flags'].append('SEE VISUAL REVIEW NOTE')
 rows.append(row)

def preview(canvas,path,box):
 im=Image.open(OUT/path).convert('RGBA');bounds=im.getbbox()
 if not bounds:raise ValueError('Empty preview '+path)
 if bounds[0]<2 or bounds[1]<2 or bounds[2]>im.width-2 or bounds[3]>im.height-2:print('EDGE_WARNING',path,bounds)
 im=im.crop(bounds);x,y,w,h=box;im.thumbnail((w,h),Image.Resampling.LANCZOS)
 canvas.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2),im)
def wrap(draw,text,width,size=20):
 f=font(size,True)
 words=text.split('_');lines=[];line=''
 for word in words:
  nxt=line+'_'+word if line else word
  if draw.textlength(nxt,font=f)>width and line:lines.append(line+'_');line=word
  else:line=nxt
 lines.append(line)
 return lines,f
def sheet(items,title,filename,detail=True):
 columns=3 if detail else 4;cw=600 if detail else 450;ch=410 if detail else 345;gap=20;pad=40
 width=pad*2+columns*cw+(columns-1)*gap;height=190+math.ceil(len(items)/columns)*(ch+gap)+70
 im=Image.new('RGB',(width,height),'#eceee8');d=ImageDraw.Draw(im)
 d.text((pad,25),'CIV SUPPLY CHAINS  /  PANTRY CANDIDATES',font=font(20,True),fill='#65776a')
 d.text((pad,66),title,font=font(38,True),fill='#233c31')
 d.text((pad,122),'Source geometry + original textures | '+('two angles' if detail else 'overview; two angles in full gallery')+' | each item fitted independently',font=font(21),fill='#65776a')
 for i,r in enumerate(items):
  x=pad+(i%columns)*(cw+gap);y=175+(i//columns)*(ch+gap)
  d.rounded_rectangle((x,y,x+cw,y+ch),radius=13,fill='#fafaf5',outline='#cad3c7',width=2)
  d.text((x+17,y+16),f"{r['number']:03}",font=font(22,True),fill='#355e44')
  pack=r['source_pack'];d.text((x+cw-15,y+17),pack,font=font(18),fill='#65776a',anchor='ra')
  if detail:
   preview(im,r['views'][0]['image'],(x+20,y+56,355,232));preview(im,r['views'][1]['image'],(x+385,y+83,195,173))
  else:preview(im,r['views'][0]['image'],(x+20,y+50,cw-40,195))
  flags=' / '.join(r['flags'])
  if flags:d.text((x+16,y+ch-109),flags,font=font(13,True),fill='#a16a32')
  names,f=wrap(d,r['asset_id'],cw-32,19 if detail else 16)
  for j,line in enumerate(names):d.text((x+16,y+ch-86+j*23),line,font=f,fill='#233c31')
  dims=' x '.join(f'{n:.1f}' for n in r['dimensions'])
  d.text((x+16,y+ch-27),f"{dims} units   |   {r['vertices']:,} source vertices",font=font(16),fill='#65776a')
 d.text((pad,height-60),'Candidates for selection; not added to the library. Native states/registration may constrain reuse.',font=font(19),fill='#65776a')
 d.text((pad,height-33),'Blender studio previews; material effects approximate. This is not an Asset Editor or in-game test.',font=font(18),fill='#65776a')
 target=OUT/'contact-sheets'/filename;target.parent.mkdir(exist_ok=True);im.save(target)
 return target.relative_to(OUT).as_posix()

groups=collections.OrderedDict()
for r in rows:groups.setdefault(r['category'],[]).append(r)
sheets=[]
for gi,(name,items) in enumerate(groups.items(),1):
 for offset in range(0,len(items),12):
  page=offset//12+1;title=name+(f' — {page}' if len(items)>12 else '')
  path=sheet(items[offset:offset+12],title,f'{gi:02}_{re.sub("[^a-z0-9]+","_",name.lower())}_{page}.png')
  sheets.append(dict(title=title,path=path))
first_ids='''DIS_PRD_PileWoodA IMP_Lumbermill_IND_PlankStack IMP_Lumbermill_Medieval_Log_Cut_Stack IMP_Lumbermill_Medieval_Scrap
DIS_PRD_PileBlockA IMP_QuarryREDO_BlockA WON_RedBrickPile_A PROP_Stone_B
DIS_HBR_Coal_Pile IMP_QuarryREDO_ResourcePile WON_MetalPile_Movie_A DIS_PRD_PileA
PROP_Haypile PROP_IN_Haybale IMP_Camp_AN_Rack_SM_A IMP_Camp_IND_Rack_LG
DIS_COM_Box_Open IMP_PLNT_ANC_Bin_A IMP_Camp_IND_Bucket DIS_HBR_Lg_Fish_Bin
IMP_QuarryREDO_Cart IMP_PLNT_ANC_Cart IMP_Mine_IND_Car_Rocks IMP_Lumbermill_Medieval_Saw'''.split()
rowmap={r['asset_id']:r for r in rows};first=[rowmap[x] for x in first_ids if x in rowmap]
sheet(first,'Start here — material and storage shortlist','00_Start_Here.png',False)

def esc(s):return html.escape(str(s),quote=True)
cards=[]
for r in rows:
 imgs=''.join(f'<a href="{esc(v["image"])}"><img loading="lazy" src="{esc(v["image"])}"></a>' for v in r['views'])
 dims=' × '.join(f'{v:.1f}' for v in r['dimensions'])
 native='; '.join(b['package']+' / '+b['entry_id'] for b in r['native_bindings'] if 'fallback' not in b['xlp'].lower()) or 'No standard TileBase registration found in eligible package XLPs.'
 native+=' Construction: '+r['state_behaviour']['Construction']['note']+' Pillage: '+r['state_behaviour']['Pillaged']['note']
 cards.append(f'''<article data-category="{esc(r['category'])}" data-search="{esc((r['asset_id']+' '+r['category']+' '+r['source_pack']).lower())}"><div class="meta">{r['number']:03} · {esc(r['source_pack'])}</div><div class="images">{imgs}</div><h3>{esc(r['asset_id'])}</h3><p>{esc(dims)} source units · {r['vertices']:,} vertices</p><p class="flag">{esc(' / '.join(r['flags']))}</p><details><summary>Source and reuse notes</summary><p>{esc(r['candidate_note'])}</p><p>{esc(r.get('visual_review_note',''))}</p><p>{esc(native)}</p><p>{esc(r['provenance']['manifest'])}<br>{esc(r['provenance']['path'])}</p></details></article>''')
options=''.join(f'<option>{esc(k)}</option>' for k in groups)
links=''.join(f'<a href="{s["path"]}">{esc(s["title"])}</a>' for s in sheets)
blocked_html=''.join(f'<li><code>{esc(r["asset_id"])}</code> — {esc(r["reason"])}</li>' for r in blocked)
document='''<!doctype html><meta charset="utf-8"><title>CSC pantry candidates</title><style>
*{box-sizing:border-box}body{margin:0;background:#eceee8;color:#233c31;font:16px system-ui,sans-serif}header,main{max-width:1600px;margin:auto;padding:30px}h1{font-size:42px;margin:12px 0}p{line-height:1.5}nav{display:flex;gap:12px;flex-wrap:wrap}input,select,nav a{padding:12px;border:1px solid #bdcdbf;border-radius:8px;background:#fafaf5;color:inherit}input{min-width:300px;flex:1}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:18px;margin-top:24px}article{background:#fafaf5;border:1px solid #c9d3c7;border-radius:12px;padding:18px}h3{overflow-wrap:anywhere;font-size:17px}.images{display:flex;align-items:center;height:215px}.images a:first-child{width:66%}.images a{width:34%}.images img{width:100%;max-height:210px;object-fit:contain}.meta{color:#647a68}.flag{font-size:12px;font-weight:700;color:#9c6428}details{font-size:13px}a{color:#315f41}.sheets{display:flex;gap:12px;flex-wrap:wrap}.sheets a{padding:6px}.hidden{display:none}code{overflow-wrap:anywhere}</style><header>
<div>CSC / SOURCE ASSET EXPLORATION</div><h1>Material stock, storage and work props</h1>'''+f'''<p>Indexed <b>{discovery['unique_package_asset_ids']:,}</b> identities in base-game, Rise and Fall and Gathering Storm package manifests. Screened <b>{discovery['unique_matched_ids']:,}</b> semantic matches; selected <b>{len(selection)}</b> candidates; <b>{len(rows)}</b> rendered. Existing library entries are excluded.</p><p>Views use source geometry and original textures, fitted independently. Dimensions are X × Y × Z in source units. Blender shader previews are approximate; native registration/state notes are source metadata, not in-game verification.</p><p><a href="contact-sheets/00_Start_Here.png">Open the 24-item starting shortlist</a> · <a href="candidate-index.json">Machine-readable candidate index</a></p><nav><input id="search" placeholder="Search names or materials…"><select id="category"><option value="">All groups</option>{options}</select><span id="count"></span></nav></header><main><div class="sheets">{links}</div><section class="grid">{''.join(cards)}</section><h2>Not previewed: converter follow-up</h2><ul>{blocked_html}</ul><p>The full semantic search audit is in discovery.json. The live library and mod source files were not changed.</p></main>'''+'''<script>const q=document.querySelector('#search'),cat=document.querySelector('#category'),cards=[...document.querySelectorAll('article')];function filter(){let n=0;for(const c of cards){const show=(!cat.value||c.dataset.category===cat.value)&&c.dataset.search.includes(q.value.toLowerCase());c.classList.toggle('hidden',!show);n+=show}document.querySelector('#count').textContent=n+' candidates'}q.oninput=cat.onchange=filter;filter();</script>'''
(OUT/'index.html').write_text(document,encoding='utf-8')
(OUT/'candidate-index.json').write_text(json.dumps(dict(method='Eligible package manifests + asset/geometry-name semantic filtering + manual family selection + source geometry/texture previews',discovery_counts={k:v for k,v in discovery.items() if isinstance(v,int)},candidates=rows,blocked=blocked,sheets=sheets),indent=2))
print('CONTACT_SHEETS_COMPLETE',len(rows),'candidates',len(sheets)+1,'sheets; blocked',len(blocked))
