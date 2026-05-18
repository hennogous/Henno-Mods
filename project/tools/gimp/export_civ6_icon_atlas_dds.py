#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
GIMP 3.x Python plug-in: export a Civ VI 4x4 icon atlas to DDS sizes.

Install for GIMP 3.2.x on Windows:
  C:\Users\Shadow\AppData\Roaming\GIMP\3.2\plug-ins\export_civ6_icon_atlas_dds\export_civ6_icon_atlas_dds.py

Use:
  Open e.g. CSC_BAKERS_Icons.xcf, then run:
    Filters > Civ Supply Chains > Export Civ VI Icon Atlas DDS

Outputs, beside the source XCF:
  CSC_BAKERS_256.dds, CSC_BAKERS_128.dds, ... CSC_BAKERS_22.dds

Notes:
  - The original XCF is not modified.
  - The script works from duplicate images only.
  - DDS export uses the verified GIMP settings: Compression=None, Format=RGBA8,
    Save type=All visible layers, No mipmaps.
"""

import os
import re
import sys
import traceback

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio

PROC_NAME = "python-fu-export-civ6-icon-atlas-dds"
MENU_PATH = "<Image>/Filters/Civ Supply Chains/"
MENU_LABEL = "Export Civ VI Icon Atlas DDS"

EXPORT_SPECS = [
    # icon_size, atlas_px, unsharp_radius, amount, threshold
    (256, 1024, None, None, None),
    (128,  512, 1.0, 0.5, 0.0),
    (80,   320, 1.2, 0.5, 0.0),
    (70,   280, 1.3, 0.5, 0.0),
    (50,   200, 1.5, 0.5, 0.0),
    (38,   152, 1.6, 0.5, 0.0),
    (32,   128, 1.7, 0.5, 0.0),
    (22,    88, 1.8, 0.5, 0.0),
]


def _success(procedure):
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


def _failure(procedure, message):
    Gimp.message(message)
    print(message, file=sys.stderr)
    return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error(message))


def _image_path(image):
    """Return the path of the XCF/source image associated with this GIMP image."""
    gfile = image.get_file()
    if gfile is None:
        raise RuntimeError("The image must be saved as an XCF before exporting DDS files.")

    path = gfile.get_path()
    if not path:
        raise RuntimeError("The image file path could not be resolved. Save the XCF locally first.")

    return path


def _derive_prefix_and_folder(image):
    path = _image_path(image)
    folder = os.path.dirname(path)
    base = os.path.basename(path)

    match = re.match(r"^(.*)_Icons\.xcf$", base, re.IGNORECASE)
    if match:
        prefix = match.group(1)
    else:
        prefix = os.path.splitext(base)[0]
        Gimp.message("Filename does not end in _Icons.xcf; using '%s' as the DDS prefix." % prefix)

    return prefix, folder


def _get_layer_name(layer):
    try:
        return layer.get_name()
    except Exception:
        return ""


def _find_layer_by_name(image, name):
    for layer in image.get_layers():
        if _get_layer_name(layer) == name:
            return layer
    return None


def _lower_layer_to_bottom(image, layer):
    try:
        # get_layers() is top-to-bottom; bottom index is len(layers) - 1.
        image.reorder_item(layer, None, max(0, len(image.get_layers()) - 1))
    except Exception:
        # Non-fatal. If this fails, GIMP keeps the existing layer order.
        pass


def _prepare_flattened_master(source_image):
    """Return a duplicate image with visible layers merged into one layer."""
    image = source_image.duplicate()
    image.undo_disable()

    background = _find_layer_by_name(image, "Background")
    if background is not None:
        background.set_visible(True)
        _lower_layer_to_bottom(image, background)

    # Remove hidden non-background root layers so they cannot affect export.
    for layer in list(image.get_layers()):
        if _get_layer_name(layer) != "Background" and not layer.get_visible():
            image.remove_layer(layer)

    visible_layers = [layer for layer in image.get_layers() if layer.get_visible()]
    if not visible_layers:
        image.delete()
        raise RuntimeError("No visible layers found to export.")

    if len(visible_layers) > 1:
        merged = image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
    else:
        merged = visible_layers[0]

    try:
        image.set_selected_layers([merged])
    except Exception:
        pass

    return image


def _apply_unsharp_mask(drawable, radius, amount, threshold):
    """Apply GIMP 3's GEGL unsharp-mask destructively to the drawable."""
    filt = Gimp.DrawableFilter.new(drawable, "gegl:unsharp-mask", "Civ VI icon sharpening")
    if filt is None:
        raise RuntimeError("Could not create GEGL unsharp-mask filter.")

    config = filt.get_config()
    config.set_property("std-dev", float(radius))
    config.set_property("scale", float(amount))
    config.set_property("threshold", float(threshold))

    drawable.merge_filter(filt)


def _save_dds(image, outfile):
    """Export DDS using the verified manual settings from GIMP 3.2.x."""
    layers = image.get_selected_layers()
    if not layers:
        layers = image.get_layers()
    if not layers:
        raise RuntimeError("No drawable layer found for DDS export.")

    # The DDS exporter itself asks image.get_selected_layers()[0], so make sure
    # the visible export layer is selected before running file-dds-export.
    try:
        image.set_selected_layers([layers[0]])
    except Exception:
        pass

    pdb = Gimp.get_pdb()
    proc = pdb.lookup_procedure("file-dds-export")
    if proc is None:
        raise RuntimeError("GIMP procedure file-dds-export was not found. Is DDS export installed/enabled?")

    config = proc.create_config()
    config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
    config.set_property("image", image)
    config.set_property("file", Gio.File.new_for_path(outfile))

    # Verified working settings from the GIMP 3.2.4 DDS export dialog:
    # Compression=None, Format=RGBA8, Save type=All visible layers, No mipmaps.
    config.set_property("compression-format", "none")
    config.set_property("perceptual-metric", False)
    config.set_property("format", "rgba8")
    config.set_property("save-type", "canvas")
    config.set_property("flip-image", False)
    config.set_property("transparent-color", False)
    config.set_property("transparent-index", 0)
    config.set_property("mipmaps", "none")
    config.set_property("mipmap-filter", "default")
    config.set_property("mipmap-wrap", "default")
    config.set_property("gamma-correct", False)
    config.set_property("srgb", False)
    config.set_property("gamma", 0.0)
    config.set_property("preserve-alpha-coverage", False)
    config.set_property("alpha-test-threshold", 0.5)

    result = proc.run(config)
    status = result.index(0)
    if status != Gimp.PDBStatusType.SUCCESS:
        raise RuntimeError("DDS export failed for %s with status %s" % (outfile, status))


def _export_one(master_image, prefix, folder, icon_size, atlas_px, radius, amount, threshold):
    work = master_image.duplicate()
    work.undo_disable()

    try:
        work.scale(atlas_px, atlas_px)
        layers = work.get_layers()
        if not layers:
            raise RuntimeError("No layer found after scaling export image.")

        drawable = layers[0]
        try:
            work.set_selected_layers([drawable])
        except Exception:
            pass

        if radius is not None:
            _apply_unsharp_mask(drawable, radius, amount, threshold)

        outfile = os.path.join(folder, "%s_%s.dds" % (prefix, icon_size))
        _save_dds(work, outfile)
        return outfile
    finally:
        work.delete()


class Civ6IconAtlasExporter(Gimp.PlugIn):
    def do_set_i18n(self, procname):
        return False

    def do_query_procedures(self):
        return [PROC_NAME]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            self.run,
            None,
        )
        procedure.set_image_types("RGB*,GRAY*,INDEXED*")
        procedure.set_menu_label(MENU_LABEL)
        procedure.add_menu_path(MENU_PATH)
        procedure.set_documentation(
            "Export Civ VI icon atlas DDS sizes",
            "Exports 256/128/80/70/50/38/32/22 DDS atlases from the current XCF without modifying it.",
            name,
        )
        procedure.set_attribution("Henno + Bill", "Henno + Bill", "2026")
        return procedure

    def run(self, procedure, run_mode, image, drawables, config, run_data):
        master = None
        exported = []

        try:
            prefix, folder = _derive_prefix_and_folder(image)
            master = _prepare_flattened_master(image)

            for spec in EXPORT_SPECS:
                icon_size, atlas_px, radius, amount, threshold = spec
                exported.append(_export_one(master, prefix, folder, icon_size, atlas_px, radius, amount, threshold))

            Gimp.message("Exported %d DDS icon atlases:\n%s" % (len(exported), "\n".join(exported)))
            return _success(procedure)

        except Exception as exc:
            traceback.print_exc(file=sys.stderr)
            return _failure(procedure, "Civ VI DDS atlas export failed:\n%s" % exc)

        finally:
            if master is not None:
                master.delete()


Gimp.main(Civ6IconAtlasExporter.__gtype__, sys.argv)
