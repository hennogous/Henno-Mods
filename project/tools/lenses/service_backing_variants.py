"""Preview the requested native Service backing variants without changing CSC UI."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from native_ui_inspiration_sheet import sliced_panel

ROOT=Path(__file__).resolve().parents[3]


def font(size,bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),size)


def centre(canvas,art,xy):
    canvas.alpha_composite(art,(round(xy[0]-art.width/2),round(xy[1]-art.height/2)))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pantry',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    textures=args.pantry/'Textures'
    plaque_path=textures/'CityPanel_YieldBacking.dds'
    circle_path=textures/'ActionPanel_Notification2.dds'
    plaque=sliced_panel(Image.open(plaque_path).convert('RGBA'),(46,44),(6,12))
    circle=Image.open(circle_path).convert('RGBA').resize((60,60),Image.Resampling.LANCZOS)
    service_path=ROOT/'Civ Supply Chains/Textures/CSC_BAKERS_50.dds'
    glyph=Image.open(service_path).convert('RGBA').crop((50,100,100,150)).resize((38,38),Image.Resampling.LANCZOS)
    screenshot=Path('C:/Users/Shadow/AppData/Local/Temp/codex-clipboard-798702cf-d8a3-4fb9-9661-e87ea38365d5.png')
    scene=Image.open(screenshot).convert('RGBA').crop((1010,300,1530,700))
    scene=ImageOps.fit(scene,(528,255),Image.Resampling.LANCZOS)
    sheet=Image.new('RGBA',(1200,866),'#0c1e2b');d=ImageDraw.Draw(sheet)
    d.text((26,20),'SERVICE BACKINGS / TWO NATIVE DIRECTIONS',font=font(29,True),fill='#ecd6a5')
    d.text((26,64),'Same 38px Service icon in both. Illustrative composites; no in-game changes.',font=font(18),fill='#b4c6d0')
    variants=[
        ('A  /  22: compact yield plaque',plaque,'46 x 44px  |  was 92 x 58px',
         '50% narrower; 25% shorter, rounded to pixels.',plaque_path),
        ('B  /  20: notification circle',circle,'60 x 60px  |  hinge-free native variant',
         'Uses ActionPanel_Notification2 directly.',circle_path),
    ]
    entries=[]
    for i,(title,frame,size_note,explanation,path) in enumerate(variants):
        x=24+i*588
        card=Image.new('RGBA',(564,712),'#172f42');cd=ImageDraw.Draw(card)
        cd.rounded_rectangle((0,0,563,711),radius=10,outline='#496071')
        cd.text((18,15),title,font=font(23,True),fill='#f1e5ca')
        cd.text((18,53),size_note,font=font(17),fill='#aac4d4')
        cd.text((18,83),explanation,font=font(16),fill='#e0e9ed')
        composite=Image.new('RGBA',(100,100))
        centre(composite,frame,(50,50))
        centre(composite,glyph,(48,50))
        large=composite.resize((300,300),Image.Resampling.NEAREST)
        centre(card,large,(282,270))
        cd.text((18,126),'3x DETAIL',font=font(12,True),fill='#b4c6d0')
        cd.text((18,394),'SCREEN-SIZE STUDY',font=font(12,True),fill='#b4c6d0')
        card.alpha_composite(scene,(18,420))
        # The image box is 100px; frame/glyph keep their exact authored size.
        centre(card,composite,(282,530))
        cd.text((18,688),path.stem,font=font(13),fill='#a9c0d1')
        sheet.alpha_composite(card,(x,116))
        card.convert('RGB').save(args.output/('A-compact-plaque.png' if i==0 else 'B-hinge-free-circle.png'))
        composite.save(args.output/('A-preview-marker.png' if i==0 else 'B-preview-marker.png'))
        entries.append({'option':title,'source':str(path),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'frame_size':list(frame.size),'service_size':[38,38],'glyph_offset':[-2,0],
                        'method':'native nine-slice corners 6,12' if i==0 else 'unchanged native hinge-free variant, resampled'})
    d.text((26,842),'Gold rail and corner artwork are preserved. The circle uses the game\u2019s own matching hinge-free texture.',font=font(16),fill='#b4c6d0')
    sheet.convert('RGB').save(args.output/'service-backing-comparison.png')
    (args.output/'source-evidence.json').write_text(json.dumps({'variants':entries,'not_native_capture':True,
        'source_option_22_size':[92,58],'target_option_22_size':[46,44],
        'service_icon':str(service_path),'screenshot':str(screenshot),'mod_changes':False},indent=2),encoding='utf-8')
    print(args.output/'service-backing-comparison.png')


if __name__=='__main__':
    main()
