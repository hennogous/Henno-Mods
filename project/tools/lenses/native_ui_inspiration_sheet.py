"""Native Civ VI UI artwork studies, not new game rendering or shipped layouts.

Read SDK DDS pixels and native XML references. Output only review images and
provenance; never modifies mod assets or connects to a running game.
"""
import argparse
import hashlib
import json
import math
import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[3]
INVENTORY = [
    'CityPanel_ProductionSlot', 'CompletedPopup_IconSlot', 'Civilopedia_IconSlot50',
    'Religion_IconButton', 'Religion_PantheonSlot', 'CityState_HeaderCircle',
    'Controls_CircleCompass', 'Controls_CircleCallout', 'Controls_CircleRim',
    'Controls_YieldBacking', 'UnitFlagReligionTag', 'UnitFlagReligion_Combo',
    'HUDActionsPanelPromotionBanner', 'IconFrame32Check', 'CityPanel_YieldBacking',
    'Controls_KeySwatchHex', 'HexCallout', 'ActionPanel_Notification',
    'Controls_MetalFrame', 'Banner_TypeSlot', 'SelectionPanel_UniqueActionFrame',
    'CivicPanel_ChooserBoostSlot', 'ProductionPanel_MeterSlot', 'UnlockFrames',
    'Controls_Circle', 'Controls_CircleButton', 'CircleBacking64',
    'UnitPanel_PromotionBanner', 'CityStateQuest42', 'Status_CityStateQuest',
    'Controls_CircleBacking68', 'Controls_CircleRim50', 'Circle80_Lighter',
    'DestinationChooser_CurrentSlot', 'Controls_ConfirmFrame',
    'SelectionPanel_PortraitFrame', 'Banner_ProductionCircle',
    'Controls_KeySwatchHexEmpty', 'Controls_FrameDeco', 'Controls_TeamButtonFrame',
    'Circle44_Lighter', 'CityPanel_MeterSmallBacking', 'ProductionPanel_MeterFrame',
    'AdditionalContent_IconBacking50', 'Controls_OptionFrame',
]

# label, source, crop, display size, source context, adaptation idea, optional tint
SELECTION = [
    ('District unlock','UnlockFrames',(76,0,114,38),(80,80),'Tech / civic tree','A compact gold hex; strongly tied to districts.',None),
    ('Building unlock','UnlockFrames',(38,0,76,38),(80,80),'Tech / civic tree','An arched top with a square, plaque-like base.',None),
    ('Wonder unlock','UnlockFrames',(0,0,38,38),(80,80),'Tech / civic tree','A seal with small outward-pointing corners.',None),
    ('Hollow hex','Controls_KeySwatchHexEmpty',None,(72,81),'SDK / lens-style swatch','Open centre, thin outline; tint by Quarter.',(218,180,104)),
    ('Faith crest','UnitFlagReligion_Combo',(0,0,64,64),(86,86),'SDK / religious-unit flag','A small shield with wing-like side points.',(109,139,140)),
    ('Hanging pennant','UnitFlagReligionTag',None,(57,80),'SDK / religious-unit tag','A dark hanging tab; add a narrow gold trim.',None),
    ('Heraldic frame','Controls_TeamButtonFrame',None,(45,82),'SDK / team-button frame','A tall shield with clipped, decorative corners.',None),
    ('Pantheon lozenge','Religion_PantheonSlot',None,(100,86),'SDK / pantheon slot','A horizontal seal with small diamond accents.',None),
    ('Engraved bronze','Controls_MetalFrame',None,(83,83),'SDK / metal frame','Carved metal corners; a more crafted material.',None),
    ('Inset gold frame','Controls_OptionFrame',None,(91,75),'Options / GoldFrame style','A square frame with a round inner aperture.',None),
    ('Ink corner ornament','Controls_FrameDeco',None,(86,86),'Event-popup effects panel','Blue ink and corner curls; quieter than gold.',None),
    ('Diplomatic cartouche','Controls_ConfirmFrame',None,(106,84),'City-state confirmation panel','A light outline with ornamental shoulders.',None),
    ('Thin gold seal','Controls_CircleBacking68',None,(82,82),'Leader icons / diplomacy','A restrained gold edge around a dark disc.',None),
    ('Compass ring','Controls_CircleCompass',None,(82,84),'Setup / options menus','Four small cardinal points; an open centre.',(219,187,123)),
    ('Pedia compass','Civilopedia_IconSlot50',None,(82,82),'Civilopedia icon slots','A compass motif as a subtle backing watermark.',None),
    ('Soft event disc','CompletedPopup_IconSlot',None,(82,82),'Tech / civic completion popup','A soft shadowed disc with almost no metal rim.',None),
    ('Gold pendant','SelectionPanel_UniqueActionFrame',None,(72,84),'SDK / unique-action frame','Small top and bottom ornaments frame the icon.',None),
    ('Portrait flourish','SelectionPanel_PortraitFrame',None,(55,84),'City-panel portrait','An open gold sweep; avoids a heavy closed badge.',None),
    ('Open progress ring','ProductionPanel_MeterFrame',None,(84,84),'Production chooser','A partial gold arc with lighter visual weight.',None),
    ('Notification hinge','ActionPanel_Notification',None,(82,84),'Native notification button','An off-centre clasp adds a directional detail.',None),
    ('Promotion ribbon','UnitPanel_PromotionBanner',None,(114,63),'Unit-panel promotion banner','A folded ribbon; keep it short and icon-only.',(190,160,104)),
    ('Yield plaque','CityPanel_YieldBacking',None,(92,58),'City-panel yield strip','A blue plaque with a bronze rail above it.',None),
    ('Status lozenge','CityPanel_MeterSmallBacking',None,(111,43),'Production chooser status','A low horizontal capsule for a compact symbol.',None),
    ('Quest bubble','CityStateQuest42',None,(94,74),'City-state quest marker','A short pointer without a full map-pin stem.',(65,108,133)),
]


def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/' + ('segoeuib.ttf' if bold else 'segoeui.ttf'), size)


def centre(image, art, xy):
    image.alpha_composite(art, (round(xy[0]-art.width/2), round(xy[1]-art.height/2)))


def tinted(art, colour):
    from PIL import ImageChops
    result=ImageChops.multiply(art.convert('RGB'),Image.new('RGB',art.size,colour)).convert('RGBA')
    result.putalpha(art.getchannel('A'))
    return result


def sliced_panel(art, size, corner):
    """Native Grid-style resizing: preserve corners instead of stretching them."""
    cx,cy=corner
    result=Image.new('RGBA',size)
    sx,sy=[0,cx,art.width-cx,art.width],[0,cy,art.height-cy,art.height]
    dx,dy=[0,cx,size[0]-cx,size[0]],[0,cy,size[1]-cy,size[1]]
    for y in range(3):
        for x in range(3):
            cell=art.crop((sx[x],sy[y],sx[x+1],sy[y+1]))
            cell=cell.resize((dx[x+1]-dx[x],dy[y+1]-dy[y]),Image.Resampling.LANCZOS)
            result.alpha_composite(cell,(dx[x],dy[y]))
    return result


def curated(args):
    # Actual white Bakers' Stage 3 Service artwork, not the notification checkmark.
    service_path=ROOT/'Civ Supply Chains/Textures/CSC_BAKERS_50.dds'
    atlas=Image.open(service_path).convert('RGBA')
    assert atlas.size==(200,200)
    glyph=atlas.crop((50,100,100,150)).resize((38,38),Image.Resampling.LANCZOS)
    ui=args.game/'Base/Assets/UI'
    references={name:[] for _,name,*_ in SELECTION}
    for path in ui.rglob('*.xml'):
        lines=path.read_text(encoding='utf-8-sig',errors='replace').splitlines()
        for name in references:
            pattern=re.compile(r'Texture="'+re.escape(name)+r'(?:\.dds)?"',re.I)
            for line_no,line in enumerate(lines,1):
                if pattern.search(line):
                    references[name].append({'path':str(path),'line':line_no,'snippet':line.strip()})
    packages={name:[] for name in references}
    for path in (args.game/'Base/Platforms/Windows/BLPs/UI').glob('*.blp'):
        data=path.read_bytes().lower()
        for name in packages:
            if name.lower().encode()+b'\0' in data: packages[name].append(str(path))
    # Busy map context without a pre-existing Service medallion in this crop.
    screenshot=Path('C:/Users/Shadow/AppData/Local/Temp/codex-clipboard-798702cf-d8a3-4fb9-9661-e87ea38365d5.png')
    backdrop=Image.open(screenshot).convert('RGBA').crop((1010,300,1530,700))
    backdrop=ImageOps.fit(backdrop,(166,116),Image.Resampling.LANCZOS)
    backdrop=Image.alpha_composite(backdrop,Image.new('RGBA',backdrop.size,(9,21,29,62)))
    cw,ch,gap,margin,header,footer=404,282,16,24,140,78
    width=margin*2+cw*4+gap*3
    height=header+ch*6+gap*5+footer
    sheet=Image.new('RGBA',(width,height),'#0c1e2b')
    draw=ImageDraw.Draw(sheet)
    draw.text((margin,20),'NATIVE CIV VI  /  SERVICE MARKER INSPIRATION',font=font(30,True),fill='#ecd6a5')
    draw.text((margin,67),'24 different pieces of the game\u2019s UI language, beyond the previous badge and pin options.',font=font(20),fill='#e0e9ed')
    draw.text((margin,101),'Left: original artwork.  Right: illustrative assembly with your actual Service icon.  Tints are noted.',font=font(17),fill='#a9bbc6')
    evidence=[]
    for i,(title,name,crop,size,context,idea,tint) in enumerate(SELECTION):
        path=args.pantry/'Textures'/(name+'.dds')
        original=Image.open(path).convert('RGBA')
        art=original.crop(crop) if crop else original
        raw=ImageOps.contain(art,size,Image.Resampling.LANCZOS)
        sample=raw
        if name=='CityPanel_YieldBacking': sample=sliced_panel(art,size,(6,12))
        if name=='CityPanel_MeterSmallBacking': sample=sliced_panel(art,size,(10,10))
        if tint: sample=tinted(sample,tint)
        card=Image.new('RGBA',(cw,ch),'#172f42')
        d=ImageDraw.Draw(card)
        d.rounded_rectangle((0,0,cw-1,ch-1),radius=9,outline='#496071',width=1)
        d.text((16,12),f'{i+1:02}  {title}',font=font(21,True),fill='#f1e5ca')
        d.text((16,43),context,font=font(14),fill='#b9cbd3')
        d.rounded_rectangle((16,69,182,185),radius=6,fill='#102330')
        card.alpha_composite(backdrop,(220,69))
        centre(card,raw,(99,127))
        centre(card,sample,(303,127))
        # Existing service artwork stays 38px in every example for comparison.
        glyph_y=119 if name=='CityStateQuest42' else 127
        centre(card,glyph,(303,glyph_y))
        d.text((26,168),'ORIGINAL',font=font(11,True),fill='#b5c1c6')
        d.text((230,168),'WITH SERVICE'+(' / TINT' if tint else ''),font=font(11,True),fill='white')
        status='BASE UI' if references[name] else 'SDK ART'
        d.text((16,197),name,font=font(13),fill='#a5c2d6')
        d.text((cw-79,45),status,font=font(10,True),fill='#dcc58d')
        for j,line in enumerate(textwrap.wrap(idea,width=47)):
            d.text((16,222+j*20),line,font=font(15),fill='#e0e8eb')
        x=margin+(i%4)*(cw+gap);y=header+(i//4)*(ch+gap)
        sheet.alpha_composite(card,(x,y))
        card.convert('RGB').save(args.output/f'{i+1:02}-{name.lower()}.png')
        evidence.append({'number':i+1,'title':title,'source':str(path),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'original_size':list(original.size),'crop':crop,'shown_size':size,'context_label':context,
            'adaptation_idea':idea,'demo_tint':tint,'native_xml_references':references[name],
            'base_ui_package_entries':packages[name],
            'original_art_transform':'cell crop where specified, proportional resampling; no repainting',
            'demo_note':'same native element with optional multiplicative UI tint; yield/status panels use nine-slice resizing; unchanged 38px CSC service glyph'})
    y=height-footer+20
    draw.text((margin,y),'BASE UI = exact texture reference found in native UI XML.  SDK ART = source artwork; no exact base-XML reference found.',font=font(15),fill='#b4c5cf')
    draw.text((margin,y+25),'All 24 textures were found in base UI packages. These assemblies are design studies, not in-game captures. No mod changes.',font=font(15),fill='#b4c5cf')
    sheet.convert('RGB').save(args.output/'native-ui-service-inspiration.png')
    (args.output/'source-evidence.json').write_text(json.dumps({'entries':evidence,
        'service_icon':{'path':str(service_path),'crop':[50,100,100,150],'definition':'ICON_BUILDING_CSC_BAKERS_STAGE_3_SERVICE','display_size':38},
        'background_screenshot':str(screenshot),'not_runtime_capture':True,
        'not_new_assets':True},indent=2),encoding='utf-8')
    print(json.dumps({'sheet':str(args.output/'native-ui-service-inspiration.png'),'size':sheet.size,
        'candidates':len(evidence),'native_xml':sum(bool(x['native_xml_references']) for x in evidence),
        'base_package_names':sum(bool(x['base_ui_package_entries']) for x in evidence)}))


def inventory(args):
    cols, cw, ch = 5, 300, 205
    sheet = Image.new('RGBA', (cols*cw, math.ceil(len(INVENTORY)/cols)*ch), '#132b3d')
    d = ImageDraw.Draw(sheet)
    for i, name in enumerate(INVENTORY):
        p = args.pantry/'Textures'/(name+'.dds')
        art = Image.open(p).convert('RGBA')
        x, y = i%cols*cw, i//cols*ch
        sample = ImageOps.contain(art, (270,140), Image.Resampling.LANCZOS)
        centre(sheet, sample, (x+150,y+80))
        d.text((x+8,y+152),f'{i+1:02} {name}',font=font(12,True),fill='white')
        d.text((x+8,y+174),str(art.size),font=font(13),fill='#c3b38d')
        d.rectangle((x,y,x+cw-1,y+ch-1),outline='#38536a')
    sheet.convert('RGB').save(args.output/'native-ui-inventory.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pantry',type=Path,required=True)
    parser.add_argument('--game',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--inventory',action='store_true')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    if args.inventory:
        inventory(args)
        print(args.output/'native-ui-inventory.png')
        return
    curated(args)


if __name__=='__main__':
    main()
