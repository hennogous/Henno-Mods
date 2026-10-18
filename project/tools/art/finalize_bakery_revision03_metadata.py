from bakery_props_atlas import *
for p in OUT.glob('*-export.json'):
 r=json.loads(p.read_text());src=SOURCE/(r['asset_id']+'.blend');r['source']=str(src);r['source_sha256']=sha(src);p.write_text(json.dumps(r,indent=2))
prov=STAGE/'atlas/sources/imagegen-r027'
record={'generator':'OpenAI ImageGen','accepted_basecolour_images':['exec-95a84664-e738-41d2-b00a-4b31f98f5d59.png','exec-08d8436a-3e56-4b31-8fab-83ca21ebcb23.png'],'unused_reference_images':['exec-cca92f43-0d69-4428-8c42-f406629b819d.png','Bakery_Alternate_Concept_02_Bread_Cart.png'],'unused_panel':'materials bottom-right brick; oven unchanged','files':{p.name:sha(p) for p in prov.iterdir() if p.is_file() and p.name!='generation-manifest.json'}}
(prov/'generation-manifest.json').write_text(json.dumps(record,indent=2));shutil.copytree(prov,SOURCE/'art-provenance',dirs_exist_ok=True)
