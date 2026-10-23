"""GIMP 3: replace the existing plaster layer, retaining all other layers/paths."""
import gi,json,shutil,hashlib
from pathlib import Path
gi.require_version('Gimp','3.0')
from gi.repository import Gimp,Gio
OUT=Path.home()/'Desktop/Codex/windmill-wood-20261022';SOURCE=Path.home()/'Desktop/Working Files/3D Art/Textures'
rows=[]
def walk(layers):
    for l in layers:
        yield l
        if l.is_group():yield from walk(l.get_children())
for name in ['CSC_Atlas_B_BAKERS','CSC_Atlas_B_BAKERS_2','CSC_Atlas_B_TAILORS','CSC_Atlas_B_TAILORS_2']:
    p=SOURCE/(name+'.xcf');shutil.copy2(p,OUT/'before-xcf'/p.name)
    im=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(p)))
    hits=[l for l in walk(im.get_layers()) if l.get_name()=='Windmill lime plaster (ImageGen)'];assert len(hits)==1
    old=hits[0];parent=old.get_parent();index=im.get_item_position(old)
    layer=Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE,im,Gio.File.new_for_path(str(OUT/'artwork/Wood_B_slot.png')))
    im.insert_layer(layer,parent,index);layer.set_offsets(512,614);layer.set_name('Windmill timber + diagonal brace (ImageGen)');layer.set_visible(old.get_visible());im.remove_layer(old)
    parent.set_name(parent.get_name().replace('plaster','timber'))
    assert not any('plaster' in l.get_name().lower() for l in walk(im.get_layers()))
    target=OUT/'staged-xcf'/p.name;assert Gimp.file_save(Gimp.RunMode.NONINTERACTIVE,im,Gio.File.new_for_path(str(target)))
    proc=Gimp.get_pdb().lookup_procedure('file-png-export');c=proc.create_config()
    for k,v in [('run-mode',Gimp.RunMode.NONINTERACTIVE),('image',im),('file',Gio.File.new_for_path(str(OUT/'staged-xcf'/(name+'.png'))))]:c.set_property(k,v)
    proc.run(c);im.delete();rows.append(dict(path=str(p),before=hashlib.sha256(p.read_bytes()).hexdigest()));print('REPLACED_PLASTER_LAYER',name,flush=True)
(OUT/'xcf-baseline.json').write_text(json.dumps(rows,indent=2))
