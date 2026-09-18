"""Write GIMP XCF layer names, sizes, offsets, and opacity to JSON."""
import json
import os

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gio


image = Gimp.file_load(
    Gimp.RunMode.NONINTERACTIVE,
    Gio.File.new_for_path(os.environ["CSC_XCF_PATH"]),
)
rows = []
for index, layer in enumerate(image.get_layers()):
    offsets = layer.get_offsets()
    rows.append(
        {
            "index": index,
            "name": layer.get_name(),
            "size": [layer.get_width(), layer.get_height()],
            "offset": [offsets[1], offsets[2]],
            "opacity": layer.get_opacity(),
            "visible": layer.get_visible(),
        }
    )
with open(os.environ["CSC_XCF_REPORT"], "w", encoding="utf-8") as handle:
    json.dump(rows, handle, indent=2)
