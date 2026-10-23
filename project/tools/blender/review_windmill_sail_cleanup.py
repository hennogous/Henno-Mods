"""Reuse saved-assembly clearance and framing for the sail-only correction."""
from pathlib import Path
source=Path(__file__).with_name('review_windmill_ground_states.py').read_text()
source=source.replace("for state in ('Worked','Construction','Pillaged'):","for state in ('Worked',):")
exec(compile(source,str(__file__),'exec'))
