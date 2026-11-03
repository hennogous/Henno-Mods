"""Present unaltered renders on dark side-by-side review sheets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
O=Path.home()/'Desktop/Codex/modern-bakery-placement-20261028';font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25)
report=json.loads((O/'publication-report.json').read_text())
for row in report['files']:assert hashlib.sha256(Path(row['destination']).read_bytes()).hexdigest()==row['after']
for ident,label in [('CSC_BAKERS_Bakery_Modern','Modern Bakery'),('CSC_BAKERS_Bakery_Modern_2','Modern Bakery — delivery variant')]:
 page=Image.new('RGB',(1800,960),(25,29,35));d=ImageDraw.Draw(page)
 for i,mode in enumerate(('day','night')):
  im=Image.open(O/ident/mode/'render.png').convert('RGBA').resize((900,900),Image.Resampling.LANCZOS);page.paste(im,(i*900,45),im);d.text((i*900+24,12),label+' / '+mode.title(),font=font,fill=(235,237,240))
 page.save(O/(ident+'-Day-Night.png'))
print('SHEETS_READY')
