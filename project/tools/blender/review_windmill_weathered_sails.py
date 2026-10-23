"""Terrain-clipped preview for a texture-only revision; motion is unchanged."""
import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);ROOT=Path(__file__).resolve().parents[3]
source=Path(__file__).with_name('review_windmill_ground_states.py').read_text()
source=source[source.index("for state in ('Worked','Construction','Pillaged'):"):]
source=source.replace("for state in ('Worked','Construction','Pillaged'):","for state in ('Worked',):")
exec(compile(source,str(__file__),'exec'))
