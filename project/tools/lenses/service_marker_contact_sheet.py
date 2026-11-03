"""Compare supported camera-facing Service-marker layouts using native UI art.

Creates illustrative composites, not native renderer captures. Does not edit
mod/game files or connect to a running game. Native controls/frames are recorded
alongside output so proposed layouts cannot be confused with shipped presets.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[3]


def font(size, bold=False):
    return ImageFont.truetype(str(Path('C:/Windows/Fonts') / ('segoeuib.ttf' if bold else 'segoeui.ttf')), size)


def tint(image, colour):
    result = ImageChops.multiply(image.convert('RGB'), Image.new('RGB', image.size, colour)).convert('RGBA')
    result.putalpha(image.getchannel('A'))
    return result


def nine_slice(image, size, corner=10):
    result = Image.new('RGBA', size)
    sx, sy = [0, corner, image.width-corner, image.width], [0, corner, image.height-corner, image.height]
    dx, dy = [0, corner, size[0]-corner, size[0]], [0, corner, size[1]-corner, size[1]]
    for y in range(3):
        for x in range(3):
            piece = image.crop((sx[x],sy[y],sx[x+1],sy[y+1]))
            piece = piece.resize((dx[x+1]-dx[x],dy[y+1]-dy[y]), Image.Resampling.LANCZOS)
            result.alpha_composite(piece,(dx[x],dy[y]))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--pantry', type=Path, required=True)
    parser.add_argument('--screenshot', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    source_textures = args.pantry / 'Textures'
    ui = args.game / 'Base/Assets/UI'
    references = {
        'billboard': ('WorldViewIconsManager.xml', 'Billboard="1"'),
        'position': ('WorldViewIconsManager.lua', 'SetWorldPositionVal'),
        'map_pin': ('MapPinManager.xml', 'Texture="MapPin"'),
        'pin_backing': ('MapPinManager.xml', 'Texture="MapPinFlag"'),
        'flag': ('UnitFlagManager.xml', '<ZoomAnchor'),
        'status': ('WorldView/DistrictPlotIconManager.xml', 'Style="DistrictBonusBack"'),
        'status_frame': ('Civ6_Styles.xml', '<DistrictBonusBack Texture="Controls_FrameInfo"'),
        'pulse': ('MapPinManager.xml', 'Cycle="Bounce"'),
    }
    evidence = {}
    for name,(relative,snippet) in references.items():
        path = ui/relative
        text = path.read_text(encoding='utf-8-sig')
        assert snippet in text, (name,path)
        line = next(i for i,value in enumerate(text.splitlines(),1) if snippet in value)
        evidence[name] = {'path': str(path), 'line': line, 'snippet': snippet,
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    def native(name):
        path = source_textures/(name+'.dds')
        return Image.open(path).convert('RGBA')

    service_path = ROOT/'Civ Supply Chains/Textures/CSC_Lens_Service_BAKERS.dds'
    service = Image.open(service_path).convert('RGBA')
    def glyph(size):
        return service.resize((size,size),Image.Resampling.LANCZOS)
    def base():
        return Image.new('RGBA',(230,150))

    markers = {}
    raw = base();raw.alpha_composite(glyph(82),(74,25));markers['bare'] = raw

    dark = base()
    pin_flag = native('MapPinFlag')
    # Exact native MapPinManager base cell, without its bright selection rim.
    dark.alpha_composite(tint(pin_flag.crop((150,0,200,50)).resize((76,76)),(25,46,59)),(77,24))
    dark.alpha_composite(glyph(68),(81,28));markers['dark'] = dark

    gold = base();gold.alpha_composite(native('CityBannerProdCircle').resize((80,80)),(75,22))
    gold.alpha_composite(glyph(63),(84,30));markers['gold'] = gold

    pin = base();pin.alpha_composite(native('MapPin').resize((71,95)),(80,13))
    pin.alpha_composite(glyph(49),(91,28));markers['pin'] = pin

    flag = base()
    frame = native('UnitFlagBase_Combo').crop((0,0,64,64)).resize((84,84))
    flag.alpha_composite(tint(frame,(69,94,72)),(73,19))
    flag.alpha_composite(glyph(58),(86,26));markers['flag'] = flag

    banner = base();banner.alpha_composite(nine_slice(native('Controls_FrameInfo'),(218,56)),(6,36))
    banner.alpha_composite(glyph(49),(13,39))
    ImageDraw.Draw(banner).text((64,53),'Service active',font=font(17,True),fill='#f5eacf')
    markers['banner'] = banner

    options = [
        ('bare','01  Floating icon','Resource-icon approach',
         'Your Service artwork, upright and unobstructed.',
         'Least visual clutter. Height can clear the roof.',
         ['billboard','position']),
        ('dark','02  Dark round badge','Native map-pin backing',
         'A dark backing keeps the white symbol readable.',
         'Compact; works over light and busy buildings.',
         ['billboard','pin_backing']),
        ('gold','03  Gold medallion','Native production-circle frame',
         'Gold rim gives the Service a finished badge look.',
         'More prominent; adds a second ring to the icon.',
         ['billboard']),
        ('pin','04  Map pin','Native map-pin artwork',
         'A pointed base makes the tile attachment clear.',
         'Strong location cue; a larger visual footprint.',
         ['billboard','map_pin']),
        ('flag','05  Unit-style flag','Native unit-flag frame',
         'A raised pennant with a configurable backing colour.',
         'Very legible, but can resemble an actual unit.',
         ['flag','position']),
        ('banner','06  Compact status banner','Native district-info frame; custom layout',
         'Service icon plus a short label above the district.',
         'Most explicit; takes more horizontal space.',
         ['billboard','status','status_frame']),
    ]
    width,height = 1512,1292
    sheet = Image.new('RGB',(width,height),'#101f29');draw=ImageDraw.Draw(sheet)
    draw.text((36,25),'SERVICE MARKERS / UPRIGHT UI OPTIONS',font=font(39,True),fill='#f0dfb7')
    draw.text((38,84),'Same Service icon, six supported layouts above the customer district.',font=font(23),fill='#edf2f5')
    draw.text((38,121),'Illustrative composites using native Civ VI frames. These are not in-game captures.',font=font(20),fill='#b9cbd4')
    screenshot=Image.open(args.screenshot).convert('RGB')
    # A real customer tile without an existing Service mark, so the previews do
    # not paint over or erase a previous marker. Crop/scale only, no scene edits.
    crop=(1010,300,1530,700)
    backdrop=screenshot.crop(crop).resize((448,345),Image.Resampling.LANCZOS)
    bounds=[]
    for i,(key,title,kind,description,tradeoff,refs) in enumerate(options):
        col,row=i%3,i//3;x,y=32+col*496,174+row*486
        card=Image.new('RGB',(472,464),'#1b2e3a');cd=ImageDraw.Draw(card)
        cd.text((13,10),title,font=font(25,True),fill='white')
        cd.text((14,46),kind,font=font(17),fill='#c6b580')
        card.paste(backdrop,(12,75))
        # Equal baseline for the UI layouts. Markers face the camera rather than
        # being perspective-squashed onto the ground like the current sprite.
        card.paste(markers[key],(134,131),markers[key])
        cd.rectangle((12,354,460,420),fill='#162933')
        cd.text((23,363),description,font=font(17),fill='#edf2f5')
        cd.text((23,390),tradeoff,font=font(16),fill='#b6cbd4')
        cd.text((15,435),'Native controls + original Service artwork',font=font(15),fill='#97b6c6')
        card.save(args.output/f'{i+1:02}-{key}.png')
        sheet.paste(card,(x,y));bounds.append((x,y,x+472,y+464))

    draw.text((38,1168),'All six can stay camera-facing, float above the roof and appear only for a working Service.',font=font(21),fill='#edf2f5')
    draw.text((38,1205),'Size can be fixed on screen or scale with zoom. Native AlphaAnim also supports an optional soft pulse.',font=font(20),fill='#b9cbd4')
    draw.text((38,1243),'Chrome and layouts are feasible from shipped UI code; final height, scale and overlap need in-game tuning.',font=font(18),fill='#a1bbc9')
    sheet.save(args.output/'service-marker-contact-sheet.png')
    manifest = {
        'type':'UI layout preview; not native gameplay capture',
        'scope':'No mod/game changes; selected-Quarter functional-Service filtering would be retained',
        'screenshot':str(args.screenshot),'crop':crop,
        'screenshot_sha256':hashlib.sha256(args.screenshot.read_bytes()).hexdigest(),
        'service_art':str(service_path),'service_sha256':hashlib.sha256(service_path.read_bytes()).hexdigest(),
        'native_textures': {name: {'path':str(source_textures/(name+'.dds')),
            'sha256':hashlib.sha256((source_textures/(name+'.dds')).read_bytes()).hexdigest()}
            for name in ['MapPin','MapPinFlag','CityBannerProdCircle','UnitFlagBase_Combo','Controls_FrameInfo']},
        'references':evidence,
        'options':[{'id':k,'title':t,'native_art_or_layout':n,'references':r} for k,t,n,_,_,r in options],
        'not_yet_implemented':'These custom combinations are not installed/native-tested CSC markers',
        'renderer':'WorldAnchor/ZoomAnchor UI controls, not terrain SpriteOverlay',
    }
    (args.output/'source-evidence.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('Created six-card contact sheet and individual cards:',args.output)


if __name__=='__main__':
    main()
