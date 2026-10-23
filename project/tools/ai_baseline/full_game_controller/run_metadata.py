"""Required warm-run metadata before native work, shared with reporter/watchdog."""
from pathlib import Path
import json

def validate(root):
    root=Path(root)
    required=('run-start.json','game-process.json','original-preferences.json',
              'original-installed-manifest.json','installed-original-hashes.json',
              'settings.json','log-offsets.json')
    missing=[name for name in required if not(root/name).exists()]
    assert not missing,('Missing run metadata before native work',missing)
    read=lambda name:json.loads((root/name).read_text(encoding='utf-8-sig'))
    assert isinstance(read('run-start.json')['time'],(int,float))
    assert read('game-process.json')['pid']>0
    return required
