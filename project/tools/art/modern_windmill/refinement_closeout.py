import json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from modular_v9 import ART,BASE,sha,dump
from refinement_native import O,DESTS,LIBS,RELEASES
# Correct source provenance and freeze matching metadata in both release copies.
for kind,lib in LIBS.items():
 info=json.loads((O/'libraries'/kind/'library.json').read_text());info['source_sha256']=sha(DESTS[BASE]/(BASE+'.blend'))
 for root in (O/'libraries'/kind,lib/'Current',lib/'Releases'/RELEASES[kind]):dump(root/'library.json',info)
report=json.loads((O/'publication-report.json').read_text())
for r in report['files']:r['after']=sha(r['destination'])
dump(O/'publication-report.json',report)
skill=Path.home()/'.codex/skills/civ-supply-chains'
p=skill/'references/art-modern-kit-and-atlases.md';s=p.read_text()
s=s.replace('revision-03-finished-shelter','revision-04-painted-kit').replace('revision-09-modular','revision-10-painted-kit').replace('BAKERS/Props/Modern/revision-01','BAKERS/Props/Modern/revision-02').replace('BAKERS/Water Mill/modern/revision-01','BAKERS/Water Mill/modern/revision-02-painted-kit')
s=s.replace('historical shared 8x8 surface grid','compact material groups within an 8x8 surface grid')
s=s.replace('Current base revision 03','Earlier base revision 03').replace('Current releases are buildings r003 and props r002','Earlier releases were buildings r003 and props r002')
note='''
## Current painted kit and compact atlas — 27 October 2026

Supersedes the scattered historical UV1 slot layout. Buildings r004 and props
r003 are current. Reusable base revision04-painted-kit preserves Henno's mesh
cleanup and has no recess slab/backing wall; its foundation has an entrance
notch down to Z=-30 and remains beneath the walls. Base1496vertices/840triangles;
derived Water2333/1317 excluding reusable props. Wind references the shared base.
Silo revision10-painted-kit and both props revision02 have migrated UV1.

Props occupy a compact4x3 block of128px cells at top-left of the1024 page:
row1 roof/green trim/ivory trim/cream metal; row2 silo/elevator/iron/concrete;
row3 sack/sack ends/pallet wood/stone. The rest is expansion space. Independent
2048 AO allocations are unchanged except the rebaked base/Water coverage.
Do not restore historical surface slot coordinates. Migrate all consumers
together for any future repack; keep local UV sampling scale stable.

Painting follows DIS_COM_Base_B's purposeful material variation and local depth.
Brick/roof relief is stronger and wood normals follow painted grain, not generic
sine waves. Registered surface sources, original generated artwork and provenance
are in each library. Rebuild reads registered_B/N/G/M before the original V8 fallback.
Generic painted texture guidance was already correct; this was an execution gap.

Existing AST assembly/placements, ArtDefs and XLPs are preserved. Source/native
checks and isolated cook passed; live AE/game appearance remains unverified.
Details and all current paths: project/docs/art/modern-building-kit.md.
'''
if '## Current painted kit and compact atlas' not in s:s+=note
p.write_text(s,encoding='utf-8')
p=skill/'SKILL.md';s=p.read_text();s=s.replace('modern props follow the historical\n  shared-prop layout.','modern props use compact material groups in the shared 8x8 surface grid\n  (the original scattered historical slots were superseded).');p.write_text(s,encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',32)
ims=[Image.open(O/'images'/(i+'_Comparison.png')).convert('RGBA') for i in ('CSC_BAKERS_Wind_Mill','CSC_BAKERS_Wind_Mill_Modern')]
canvas=Image.new('RGB',(2048,1100),(239,236,226));d=ImageDraw.Draw(canvas)
for j,(im,label) in enumerate(zip(ims,['Historical Wind Mill','Modern Wind Mill'])):
 canvas.paste(im,(j*1024,60),im);d.text((j*1024+40,20),label,font=font,fill=(52,57,48))
d.line((1024,16,1024,1080),fill=(194,193,181),width=2);canvas.save(O/'images/Historical_Modern_Wind_Mill_SideBySide.png')
print('CLOSEOUT_READY',len(report['files']))
