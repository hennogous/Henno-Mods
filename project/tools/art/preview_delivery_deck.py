"""Render the corrected native deck against both runner beams."""
source=__import__('pathlib').Path(__file__).with_name('preview_delivery_runner.py').read_text()
exec(source[:source.index('for side in (-1,1):')])
dest=OUT.parent/'delivery-deck-20261010'
for label,offset in [('Rear',Vector((105,-70,75))),('Top',Vector((12,0,165)))]:
 cam.location=target+direction@offset
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(dest/('Sled-Deck-Aligned-'+label+'.png'));bpy.ops.render.render(write_still=True)
print('DECK_PREVIEW_COMPLETE')
