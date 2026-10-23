"""Run in GIMP 3: retain source layers, install editable repacked swatches and paths."""
import gi,json,shutil
from pathlib import Path
gi.require_version('Gimp','3.0')
from gi.repository import Gimp,Gio
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\windmill-tower-20261021')
SOURCE=Path.home()/'Desktop/Working Files/3D Art/Textures'
layout=json.loads((OUT/'atlas-migration.json').read_text())
audit=json.loads((OUT/'xcf-audit.json').read_text())

def clip(poly,rect):
    for axis,bound,greater in [(0,rect[0],True),(0,rect[2],False),(1,rect[1],True),(1,rect[3],False)]:
        result=[]
        if not poly:return []
        old=poly[-1];oldin=old[axis]>=bound if greater else old[axis]<=bound
        for p in poly:
            inside=p[axis]>=bound if greater else p[axis]<=bound
            if inside!=oldin:
                t=(bound-old[axis])/(p[axis]-old[axis]);result.append([old[k]+t*(p[k]-old[k]) for k in (0,1)])
            if inside:result.append(p)
            old=p;oldin=inside
        poly=result
    return poly

def export(im,path):
    proc=Gimp.get_pdb().lookup_procedure('file-png-export');c=proc.create_config()
    for k,v in [('run-mode',Gimp.RunMode.NONINTERACTIVE),('image',im),('file',Gio.File.new_for_path(str(path)))]:c.set_property(k,v)
    proc.run(c)

for item in audit:
    name=item['name'];path=SOURCE/(name+'.xcf')
    backup=OUT/'before-xcf'/path.name;backup.parent.mkdir(exist_ok=True);shutil.copy2(path,backup)
    im=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(path)))
    for layer in im.get_layers():
        if 'Storage' in layer.get_name():layer.set_visible(False);layer.set_name('Legacy v2 / '+layer.get_name())
    group=Gimp.GroupLayer.new(im,'Storage v3 — retained paint + plaster');im.insert_layer(group,None,0)
    # Each supplied PNG is a deterministic crop, with its original paint intact.
    for label,rect in [('Unused storage background',[512,512,1024,1024])]+[(r['id'],r['destination']) for r in layout['regions']]+[('Windmill lime plaster (ImageGen)',layout['tower_plaster']['outer'])]:
        file=OUT/'xcf-patches'/name/(label+'.png')
        layer=Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE,im,Gio.File.new_for_path(str(file)))
        im.insert_layer(layer,group,0);layer.set_name(label);layer.set_offsets(rect[0],rect[1])
    for path in im.get_paths():
        if any(t in path.get_name().lower() for t in ['storage','lean']):path.set_name('Legacy v2 / '+path.get_name())
    for old in item['paths']:
        if not old['name'].startswith('Storage v2'):continue
        path=Gimp.Path.new(im,old['name'].replace('v2','v3'));im.insert_path(path,None,0)
        for stroke in old['strokes']:
            coords=stroke['coords'];poly=[[coords[i+2],coords[i+3]] for i in range(0,len(coords),6)]
            for r in layout['regions']:
                clipped=clip(poly,r['source'])
                if len(clipped)<3:continue
                area=abs(sum(clipped[i][0]*clipped[(i+1)%len(clipped)][1]-clipped[(i+1)%len(clipped)][0]*clipped[i][1] for i in range(len(clipped))))/2
                if area<.1:continue
                points=[]
                for x,y in clipped:points.extend([x+r['delta'][0],y+r['delta'][1]]*3)
                path.stroke_new_from_points(Gimp.PathStrokeType.BEZIER,points,True)
    target=OUT/'staged-xcf'/f'{name}.xcf';target.parent.mkdir(exist_ok=True)
    assert Gimp.file_save(Gimp.RunMode.NONINTERACTIVE,im,Gio.File.new_for_path(str(target)))
    export(im,OUT/'staged-xcf'/f'{name}-composite.png')
    im.delete()
    print('XCF_STAGED',name,flush=True)
