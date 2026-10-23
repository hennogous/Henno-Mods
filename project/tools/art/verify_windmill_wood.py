"""Focused pre/post publication checks for the wooden tower revision."""
import sys,json,hashlib,struct
from pathlib import Path
import xml.etree.ElementTree as E
import numpy as np
from PIL import Image
OUT=Path(sys.argv[1]);installed='--installed' in sys.argv
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains';NAME='CSC_BAKERS_Wind_Mill_Tower';RUIN=NAME+'_CON+PIL'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return E.fromstring(Path(p).read_text().replace('AssetObjects:','AssetObjects.'))
def txt(n,k):
    c=n.find(k);return c.get('text',c.text) if c is not None else None
def canonical(n):return (n.tag,sorted(n.attrib.items()),(n.text or '').strip(),[canonical(c) for c in n])
plan=json.loads((OUT/'install-plan.json').read_text());parents=[]
for suffix in ['', '_2']:
    name='CSC_BAKERS_Wind_Mill'+suffix+'.ast';row=next(r for r in plan if Path(r['destination']).name==name)
    old=read(row['backup']);new=read(row['source']);points=old.find('.//m_attachmentPoints');assert canonical(points)==canonical(new.find('.//m_attachmentPoints'))
    parents.append(next(p for p in points.findall('.//m_Points/Element') if txt(p,'m_Name')=='newAttachmentPoint_11'))
    for state in old.findall('.//m_GroupStates/Element'):
        if txt(state,'m_MeshName')=='Scaffolding':
            for val in state.findall('.//Element'):
                if txt(val,'m_ParamName')=='Visible':val.find('m_bValue').text='false'
    assert canonical(old)==canonical(new),'Unexpected parent assembly change'
assert canonical(parents[0])==canonical(parents[1]),'Base scaffold transform differs between variants'
mask=np.zeros((1024,1024),bool);mask[614:746,512:644]=True
for name in ['CSC_Atlas_B_BAKERS','CSC_Atlas_B_BAKERS_2','CSC_Atlas_B_TAILORS','CSC_Atlas_B_TAILORS_2','CSC_Atlas_N','CSC_Atlas_G','CSC_Atlas_M']:
    old=np.array(Image.open(OUT/'before-textures'/(name+'.dds')).convert('RGBA'));new=np.array(Image.open(OUT/'staged/Textures'/(name+'.dds')).convert('RGBA'))
    if name.endswith(('_G','_M')):old=old[:,:,0];new=new[:,:,0]
    assert np.array_equal(old[~mask],new[~mask]),name+' changed outside slot'
    if '_B_' in name:
        xcf=np.array(Image.open(OUT/'staged-xcf'/(name+'.png')).convert('RGBA'))
        assert np.array_equal(xcf[mask],new[mask]),name+' XCF layer mismatch'
def fnv(s):
    n=2166136261
    for c in s.encode():n=((n^c)*16777619)&0xffffffff
    return n
b=(OUT/'cook-wood/BLPs/WindmillRepairCheck.blp').read_bytes();records={}
for format,h,stride in [('RigidModel',0x315cfcd9,24),('SkinnedModel',0x6679b170,32)]:
    start=0
    while True:
        off=b.find(struct.pack('<I',h),start)
        if off<0:break
        start=off+4
        if off<24:continue
        size=struct.unpack_from('<I',b,off-24)[0];ident=struct.unpack_from('<I',b,off-16)[0];n=struct.unpack_from('<I',b,off+4)[0]
        if n and size==n*stride:records.setdefault(ident,[]).append(dict(format=format,vertices=n,stride=stride))
cooked={}
for name in [NAME,RUIN]:
    assert fnv(name) in records,(name,hex(fnv(name)),records)
    rows=records[fnv(name)];assert all(r['format']=='RigidModel' for r in rows),(name,rows);cooked[name]=rows
if installed:
    for r in plan:
        src=Path(r['source']);dst=Path(r['destination'])
        if sha(src)!=sha(dst):
            assert dst.suffix=='.dds',str(dst)
            scalar=dst.stem.endswith(('_AO','_AO2','_G','_M'))
            a=np.array(Image.open(src).convert('RGBA'));b=np.array(Image.open(dst).convert('RGBA'))
            assert np.array_equal(a[:,:,0] if scalar else a,b[:,:,0] if scalar else b),str(dst)
            if dst.stem.endswith(('_AO','_AO2','_G','_M')):assert struct.unpack('<8I',dst.read_bytes()[76:108])==(32,64,0,8,255,0,0,0)
    lib=Path.home()/'Desktop/Working Files/3D Art/Textures/CSC_Props';release='2026-10-22_Shared_01_r037'
    for p in (OUT/'atlas-release').rglob('*'):
        if p.is_file():assert sha(p)==sha(lib/'Current'/p.relative_to(OUT/'atlas-release'))==sha(lib/'Releases'/release/p.relative_to(OUT/'atlas-release'))
report=dict(installed=installed,parent_placements_preserved=True,parent_only_shared_scaffold_group_hidden=True,wood_slot_outside_pixels_unchanged=True,xcf_wood_pixels_match=True,cooked_tower_formats=cooked,native_export_contract=json.loads((OUT/'native-export-contract.json').read_text()),animation=json.loads((OUT/'native-animation-validation.json').read_text()),clearance=json.loads((OUT/'sail-clearance.json').read_text()))
(OUT/('final-verification.json' if installed else 'prepublication-verification.json')).write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['native_export_contract','animation']},indent=2))
