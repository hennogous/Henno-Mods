"""Native directional artwork studies; no game control or mod asset changes."""
import argparse
import hashlib
import json
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
from native_animation_contact_sheet import read_native_textures, inventory as native_inventory

ROOT=Path(__file__).resolve().parents[3]
EXTRAS=['TradeRouteSecondary','MovePath_Valid','MovePath_Queue','MovePath_Invalid',
        'StrategicView_AdjacencyArrow','StrategicView_AdjacencyArrow2','StrategicView_RouteArrowPrimary',
        'ReligionPressureIn','ReligionPressureArrow','ReligionPressureConvert','Lens_PressureHighAnim',
        'Lens_PressureMediumAnim','Lens_PressureLowAnim','PressureHigh','PressureMedium','PressureLow',
        'PressureDown','PressureUp','ReligiousPressureIn_Aqua']

# Source name, title, family, note. The final four are deliberately separated
# from connections: UI flipbooks and static status symbols are not path effects.
CHOICES=[
    ('FormCorpsArrow','Vanilla chevrons','wave','Corps formation; a crisp, thick directional front.'),
    ('ReligiousPressureIn','Religious pressure','wave','Incoming pressure; a rounded front with a soft tail.'),
    ('LoyaltyPressureIn','Loyalty pressure','wave','Rise and Fall; angular front with a fading tail.'),
    ('TradeRoutePrimary','Primary trade route','path','A filled ribbon with a repeating arrowhead.'),
    ('TradeRouteSecondary','Secondary trade route','path','An outlined route with an open arrowhead.'),
    ('MovePath_Valid','Unit movement path','static-path','Rounded gold dashes. Native path, not a moving wave.'),
    ('ZombieSense','Scenario sensing wave','wave','Red Death artwork; a reverse V with a soft wake.'),
    ('ReligiousPressureOut','Outgoing pressure strip','wave','Stock width is zero. Shown here with width enabled.'),
    ('StrategicView_RouteArrowPrimary','Strategic-view route','static-path','Small repeated white arrows; static route artwork.'),
    ('StrategicView_AdjacencyArrow2','Strategic-view adjacency','static-symbol','A simple green arrow; static adjacency symbol.'),
    ('ReligionPressureArrow','Religion direction marker','static-symbol','Arrow-and-disc artwork from a native lens model.'),
    ('ReligionPressureConvert','Conversion halo','static-symbol','A luminous circular edge; native model texture.'),
    ('Religion_PressureHighAnim','High-strength pulse','flip','41-frame ring animation used by Tourism banners.'),
    ('Religion_PressureMediumAnim','Medium-strength pulse','flip','41-frame ring animation; lighter than High.'),
    ('Religion_PressureLowAnim','Low-strength pulse','flip','71-frame ring animation; a subtler local signal.'),
    ('PressureHigh','Pressure-status arrows','status','City-banner strength symbols; static, not flows.'),
]


def load_sources(args):
    materials=native_inventory(args.game)
    packages={}
    sources={}
    base=args.game/'Base/Platforms/Windows/BLPs/Overlay.blp'
    packages[base]=read_native_textures(base)
    for name,_,kind,_ in CHOICES:
        if name in materials:
            row=materials[name]
            package=(args.game/row['variants'][0]['artdef']).parent.parent/'Platforms/Windows/BLPs/Overlay.blp'
            if package not in packages: packages[package]=read_native_textures(package)
            art,evidence=packages[package][name]
            evidence={**evidence,'native_materials':row['variants']}
        elif name in packages[base]:
            art,evidence=packages[base][name]
            evidence={**evidence,'native_materials':[]}
        else:
            path=args.pantry/'Textures'/(name+'.dds')
            art=Image.open(path).convert('RGBA')
            evidence={'sdk_texture':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        sdk=args.pantry/'Textures'/(name+'.dds')
        if sdk.exists():
            control=Image.open(sdk).convert('RGBA')
            evidence['sdk_pixel_equal']=control.size==art.size and control.tobytes()==art.tobytes()
        sources[name]=(art,evidence)
    return sources


def font(size,bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),size)


def centre(canvas,art,xy):
    canvas.alpha_composite(art,(round(xy[0]-art.width/2),round(xy[1]-art.height/2)))


def flip_frame(art,name,phase):
    columns,count=(10,71) if 'Low' in name else (8,41)
    frame=min(count-1,int((phase%1)*count))
    return art.crop(((frame%columns)*80,(frame//columns)*80,(frame%columns+1)*80,(frame//columns+1)*80))


def flow_panel(name,kind,sources,phase=.29,size=(260,108)):
    art,evidence=sources[name]
    canvas=Image.new('RGBA',size,'#142a36')
    d=ImageDraw.Draw(canvas)
    w,h=size
    # A schematic shared tile edge provides direction without inventing a
    # capture of the native renderer, projection, shader colour or game timing.
    d.line((w//2,10,w//2,h-10),fill='#48616a',width=1)
    d.line((12,h//2,w-12,h//2),fill='#203c48',width=1)
    if kind=='wave':
        style=evidence['native_materials'][0]
        width=style.get('SplineWidth',16) or 16
        length=style.get('SplineSegmentLength',8)
        # The pressure quad maps texture V to travel. Keep native width:length
        # proportions, rotate the whole motif for a left-to-right visual study.
        scale=72/width
        motif=art.resize((72,max(8,round(length*scale))),Image.Resampling.LANCZOS)
        motif=motif.transpose(Image.Transpose.ROTATE_270)
        if name=='ZombieSense': motif=ImageOps.mirror(motif)
        for k in range(-1,4):
            t=(k+phase)/3
            if not 0<=t<=1: continue
            fade=1-(2*t-1)**4
            tile=motif.copy()
            tile.putalpha(tile.getchannel('A').point(lambda a:round(a*fade)))
            centre(canvas,tile,(18+t*(w-36),h/2))
    elif kind in ('path','static-path'):
        if name=='MovePath_Valid':
            motif=art.resize((62,31),Image.Resampling.LANCZOS)
        elif name=='StrategicView_RouteArrowPrimary':
            motif=ImageOps.contain(art.crop(art.getchannel('A').getbbox()),(180,23),Image.Resampling.LANCZOS)
        else:
            motif=art.resize((112,46),Image.Resampling.LANCZOS)
        shift=round((phase%1)*motif.width) if kind=='path' else 0
        for x in range(-motif.width+shift,w,motif.width):
            canvas.alpha_composite(motif,(x,(h-motif.height)//2))
    elif kind=='flip':
        centre(canvas,flip_frame(art,name,phase),(w/2,h/2))
    elif kind=='status':
        for i,n in enumerate(['PressureLow','PressureMedium','PressureHigh']):
            source=Image.open(Path(evidence['sdk_texture']).parent/(n+'.dds')).convert('RGBA')
            centre(canvas,ImageOps.contain(source,(30,40),Image.Resampling.LANCZOS),(w/2+(i-1)*65,h/2))
    else:
        motif=art.crop(art.getchannel('A').getbbox())
        motif=ImageOps.contain(motif,(76,76),Image.Resampling.LANCZOS)
        if name=='ReligionPressureArrow': motif=motif.transpose(Image.Transpose.ROTATE_270)
        centre(canvas,motif,(w/2,h/2))
    return canvas


def curated(args):
    sources=load_sources(args)
    cols,cw,ch,gap,margin,header=4,404,316,16,24,144
    width=margin*2+cols*cw+(cols-1)*gap
    height=header+4*ch+3*gap+86
    sheet=Image.new('RGBA',(width,height),'#0c1e2b');d=ImageDraw.Draw(sheet)
    d.text((24,18),'CIV VI  /  DIRECTIONAL EFFECTS & PRESSURE SIGNALS',font=font(29,True),fill='#ecd6a5')
    d.text((24,64),'Actual game artwork: chevrons, religious and loyalty pressure, routes, markers and pulse rings.',font=font(19),fill='#e0e9ed')
    d.text((24,96),'Left: native motif. Right: illustrative flow / symbol study. Neutral source colours; spacing and timing normalised.',font=font(16),fill='#acbfcc')
    evidence=[]
    for i,(name,title,kind,note) in enumerate(CHOICES):
        art,source=sources[name]
        card=Image.new('RGBA',(cw,ch),'#172f42');cd=ImageDraw.Draw(card)
        cd.rounded_rectangle((0,0,cw-1,ch-1),radius=9,outline='#496071')
        cd.text((16,12),f'{i+1:02}  {title}',font=font(19,True),fill='#f1e5ca')
        family={'wave':'MAP WAVE','path':'SCROLLING PATH','static-path':'STATIC PATH',
                'static-symbol':'STATIC SYMBOL / MODEL','flip':'UI FLIPBOOK','status':'STATIC STATUS SYMBOLS'}[kind]
        cd.text((16,42),family,font=font(12,True),fill='#d3bd88')
        cd.rounded_rectangle((12,69,114,177),radius=4,fill='#102330')
        original=flip_frame(art,name,.29) if kind=='flip' else art
        centre(card,ImageOps.contain(original,(94,92),Image.Resampling.LANCZOS),(63,123))
        card.alpha_composite(flow_panel(name,kind,sources),(130,69))
        cd.text((16,185),'NATIVE MOTIF',font=font(11,True),fill='#a9bdca')
        cd.text((136,185),'FLOW STUDY  >' if kind in ('wave','path') else 'DISPLAY STUDY',font=font(11,True),fill='#a9bdca')
        cd.text((16,208),name,font=font(13),fill='#a8c3d6')
        for j,line in enumerate(textwrap.wrap(note,44)):
            cd.text((16,236+j*20),line,font=font(15),fill='#e0e9ed')
        sheet.alpha_composite(card,(margin+(i%4)*(cw+gap),header+(i//4)*(ch+gap)))
        card.convert('RGB').save(args.output/f'{i+1:02}-{name.lower()}.png')
        evidence.append({'number':i+1,'texture':name,'title':title,'family':family,'note':note,
                         'source_size':list(art.size),'source':source})
    y=height-65
    d.text((24,y),'The diagram edge is schematic. These are artwork-based previews, not game captures; terrain, lens tint and native timing can differ.',font=font(15),fill='#b4c6d0')
    d.text((24,y+25),'07 is scenario art; 08 has zero stock width. 09-12 are static artwork/model textures; 13-15 are native 2D ring animations.',font=font(15),fill='#b4c6d0')
    sheet.convert('RGB').save(args.output/'native-directional-effects.png')
    # Animate the moving map families, plus the three actual native flipbooks.
    animated=[0,1,2,3,4,6,12,13,14]
    frames=[]
    for frame in range(48):
        canvas=Image.new('RGBA',(1128,726),'#0c1e2b');gd=ImageDraw.Draw(canvas)
        gd.text((20,15),'NATIVE ART / MOTION COMPARISON',font=font(25,True),fill='#ecd6a5')
        gd.text((20,52),'Illustrative normalised cycles, not native game timing or terrain rendering.',font=font(16),fill='#b4c6d0')
        phase=frame/48
        for n,index in enumerate(animated):
            name,title,kind,_=CHOICES[index]
            x=20+(n%3)*370;y=93+(n//3)*202
            gd.rounded_rectangle((x,y,x+348,y+186),radius=7,fill='#172f42',outline='#496071')
            gd.text((x+12,y+10),f'{index+1:02} {title}',font=font(17,True),fill='#f1e5ca')
            canvas.alpha_composite(flow_panel(name,kind,sources,phase,(324,116)),(x+12,y+47))
        frames.append(canvas.convert('RGB').quantize(colors=160))
    frames[0].save(args.output/'native-directional-motion.gif',save_all=True,append_images=frames[1:],
                   duration=65,loop=0,disposal=2)
    (args.output/'source-evidence.json').write_text(json.dumps({'entries':evidence,
        'preview_limitations':['not native captures','normalised geometry/spacing/cycle time',
            'pressure fronts rotated to travel right','pressure endpoint fade uses documented quartic envelope',
            'no terrain projection, FOW, lighting or native clock simulation','static textures are not presented as native moving effects'],
        'ring_animation_reference':str(args.game/'Base/Assets/UI/WorldView/TourismBannerManager.xml'),
        'wave_shader_evidence':'Desktop/Codex/csc-conveyor-service-lenses-20261101/native-fade-evidence'},indent=2),encoding='utf-8')
    print(json.dumps({'sheet':str(args.output/'native-directional-effects.png'),'size':sheet.size,
                     'cards':len(evidence),'gif_frames':len(frames)}))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game',type=Path,required=True)
    parser.add_argument('--pantry',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--inventory',action='store_true')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    if args.inventory:
        cols,cw,ch=4,330,215
        sheet=Image.new('RGBA',(cols*cw,math.ceil(len(EXTRAS)/cols)*ch),'#142b3d')
        d=ImageDraw.Draw(sheet)
        for i,name in enumerate(EXTRAS):
            image=Image.open(args.pantry/'Textures'/(name+'.dds')).convert('RGBA')
            x,y=i%cols*cw,i//cols*ch
            centre(sheet,ImageOps.contain(image,(310,155),Image.Resampling.LANCZOS),(x+cw/2,y+85))
            d.text((x+8,y+168),name,font=font(14,True),fill='white')
            d.text((x+8,y+190),str(image.size),font=font(13),fill='#d7c39a')
        sheet.convert('RGB').save(args.output/'extra-directional-art-inventory.png')
        print(args.output/'extra-directional-art-inventory.png')
        return
    curated(args)


if __name__=='__main__':
    main()
