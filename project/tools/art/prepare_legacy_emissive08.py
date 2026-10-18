from bakery_props_atlas import *
from PIL import Image
MOD=ROOT/'Civ Supply Chains';p=MOD/'Textures/CSC_Atlas_E.dds';d=SOURCE/'art-provenance';d.mkdir(exist_ok=True)
im=Image.open(p).convert('RGB');im.save(SOURCE/'textures/CSC_Atlas_E.png');im.save(STAGE/'textures/CSC_Atlas_E.png')
legacy=LIB.parent/'CSC_Atlas_E.png';shutil.copy2(legacy,d/'CSC_Atlas_E-original.png');shutil.copy2(p,d/'CSC_Atlas_E-runtime.dds')
im.crop((192,184,248,232)).resize((448,384),Image.Resampling.NEAREST).save(OUT/'Legacy_Coals_Crop.png')
(OUT/'legacy-emissive-provenance.json').write_text(json.dumps(dict(runtime_dds=str(p),runtime_sha256=sha(p),original_png=str(legacy),original_sha256=sha(legacy),portable_png=str(SOURCE/'textures/CSC_Atlas_E.png'),portable_sha256=sha(SOURCE/'textures/CSC_Atlas_E.png'),crop=[192,184,248,232],transformation='Portable PNG is exact lossless RGB decode of existing runtime DDS; no runtime texture changes; UV3 affine from shared B fire slot to legacy coal crop.'),indent=2))
