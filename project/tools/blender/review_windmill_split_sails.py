"""Check the revised rotor through its eight-second native cycle, then preview."""
import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);ROOT=Path(__file__).resolve().parents[3]
source=Path(__file__).with_name('review_windmill_ground_states.py').read_text()
source=source.replace("source=source.replace(\"OUT/'review/sv/\", \"OUT/'review-Worked/sv/\").replace('90.94731','63.74731')", "source=source.replace(\"OUT/'review/sv/\", \"OUT/'review-Worked/sv/\").replace('90.94731','63.74731').replace('range(0,301,5)','range(0,len(ts),1)')")
source=source.replace("for state in ('Worked','Construction','Pillaged'):","for state in ('Worked',):")
exec(compile(source,str(__file__),'exec'))
