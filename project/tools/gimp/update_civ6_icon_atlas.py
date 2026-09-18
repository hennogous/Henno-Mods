"""Batch replace one 4x4 Civ VI atlas cell and run the installed DDS exporter.

Set CSC_ICON_ATLAS_XCF, CSC_ICON_OUTPUT_PNG, CSC_ICON_LAYER_NAME and
CSC_ICON_CELL_INDEX in the launching environment. Optionally set
CSC_ICON_UPDATE_REPORT to a writable JSON report path.
"""
import json
import os
import traceback

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp, Gio

atlas_path = os.environ['CSC_ICON_ATLAS_XCF']
icon_path = os.environ['CSC_ICON_OUTPUT_PNG']
layer_name = os.environ['CSC_ICON_LAYER_NAME']
cell_index = int(os.environ['CSC_ICON_CELL_INDEX'])
report_path = os.environ.get('CSC_ICON_UPDATE_REPORT', os.path.join(os.getcwd(), 'icon_atlas_update.json'))
report = {}

try:
    image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, Gio.File.new_for_path(atlas_path))
    if (image.get_width(), image.get_height()) != (1024, 1024) or not 0 <= cell_index < 16:
        raise ValueError('Expected a 1024x1024 atlas and a cell index from 0 to 15')
    x, y = cell_index % 4 * 256, cell_index // 4 * 256
    layers = image.get_layers()
    old = next((item for item in layers if item.get_name() == layer_name), None)
    if old is None:
        if os.environ.get('CSC_ICON_ALLOW_NEW') != '1':
            raise ValueError('Existing atlas layer was not found')
        index = 0
    else:
        if tuple(old.get_offsets()[1:]) != (x, y):
            raise ValueError('Existing layer is in a different atlas cell')
        index = layers.index(old)
    new = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, Gio.File.new_for_path(icon_path))
    if (new.get_width(), new.get_height()) != (256, 256):
        raise ValueError('New icon must be 256x256')
    if old is not None:
        image.remove_layer(old)
    image.insert_layer(new, None, index)
    new.set_offsets(x, y)
    new.set_name(os.environ.get('CSC_ICON_NEW_LAYER_NAME', layer_name))
    image.set_selected_layers([new])
    saved = Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image, Gio.File.new_for_path(atlas_path))
    if not saved:
        raise RuntimeError('GIMP did not save the updated XCF')
    report['xcf_saved'] = True
    procedure = Gimp.get_pdb().lookup_procedure('python-fu-export-civ6-icon-atlas-dds')
    config = procedure.create_config()
    config.set_property('run-mode', Gimp.RunMode.NONINTERACTIVE)
    config.set_property('image', image)
    result = procedure.run(config)
    report['export_status'] = str(result.index(0))
    if result.index(0) != Gimp.PDBStatusType.SUCCESS:
        raise RuntimeError('DDS exporter returned ' + report['export_status'])
except Exception:
    report['error'] = traceback.format_exc()
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)
