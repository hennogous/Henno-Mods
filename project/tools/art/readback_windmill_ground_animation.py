"""Extract the rebased native clip and build its Blender comparison script."""
import sys,importlib.util
from pathlib import Path
OUT=Path(sys.argv[1]);ROOT=Path(__file__).resolve().parents[3];NAME='CSC_BAKERS_Wind_Mill_Tower'
spec=importlib.util.spec_from_file_location('backend',Path.home()/'.codex/skills/civ6-art/scripts/civ6_animation/backend.py');backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
print(backend.run(r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6','extract',OUT/'staged/Geometries'/(NAME+'.fgx'),OUT/'staged/Animations'/(NAME+'_Turn.fgx'),OUT/'animation-readback',30,0,0))
source=(ROOT/'project/tools/blender/validate_windmill_migration.py').read_text().split("NAME='CSC_BAKERS_Wind_Mill_Tower'",1)[1]
source="import bpy,json,numpy as np\nfrom pathlib import Path\nOUT=Path(__file__).parent\nsources=[]\nNAME='CSC_BAKERS_Wind_Mill_Tower'"+source
source=source.replace("OUT/'new-tower'","OUT/'masters'")
(OUT/'validate-motion.py').write_text(source)
