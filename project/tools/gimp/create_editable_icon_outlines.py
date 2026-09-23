"""Build an editable GIMP 3 XCF from a render and authored SVG-path manifest.

Run using GIMP's python-fu-eval batch interpreter. Environment:
CSC_OUTLINE_SOURCE, CSC_OUTLINE_MANIFEST, CSC_OUTLINE_XCF.
Keeps one unpainted GIMP path per semantic shape plus an alpha-derived silhouette
path. Set CSC_OUTLINE_STROKE_PREVIEW=1 only to explicitly request painted preview
layers. Saves and reloads the XCF to verify the paths.
"""
import json
import os
import traceback
from collections import OrderedDict
from pathlib import Path
from xml.sax.saxutils import escape

import gi
gi.require_version("Gimp", "3.0")
gi.require_version("Gegl", "0.4")
from gi.repository import Gimp, Gio, Gegl


def require_ok(value, message):
    if not value:
        raise RuntimeError(message)


def path_inventory(image):
    return [{"name": path.get_name(), "strokes": [
        {"id": int(sid), "points": list(path.stroke_get_points(sid)[1]),
         "closed": bool(path.stroke_get_points(sid)[2])}
        for sid in path.get_strokes()]} for path in image.get_paths()]


def run():
    source = Path(os.environ["CSC_OUTLINE_SOURCE"])
    manifest = Path(os.environ["CSC_OUTLINE_MANIFEST"])
    output = Path(os.environ["CSC_OUTLINE_XCF"])
    paint_preview = os.environ.get("CSC_OUTLINE_STROKE_PREVIEW") == "1"
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path = output.with_suffix(".verification.json")
    report = {"source": str(source), "manifest": str(manifest), "xcf": str(output)}
    try:
        data = json.loads(manifest.read_text(encoding="utf-8-sig"))
        image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, Gio.File.new_for_path(str(source)))
        width, height = image.get_width(), image.get_height()
        require_ok([width, height] == data["canvas"], "Render and path dimensions differ")
        base = image.get_layers()[0]
        base.set_name("Original Blender render - locked")
        base.set_lock_content(True)
        base.set_lock_position(True)
        Gimp.context_push()
        Gimp.context_set_foreground(Gegl.Color.new("black"))
        Gimp.context_set_opacity(100.0)
        Gimp.context_set_stroke_method(Gimp.StrokeMethod.LINE)
        Gimp.context_set_line_cap_style(Gimp.CapStyle.ROUND)
        Gimp.context_set_line_join_style(Gimp.JoinStyle.ROUND)
        Gimp.context_set_line_width_unit(Gimp.Unit.pixel())
        Gimp.context_set_line_dash_pattern([])

        # Derive only the outside silhouette from source alpha, not interior edges.
        require_ok(image.select_item(Gimp.ChannelOps.REPLACE, base), "Alpha selection failed")
        procedure = Gimp.get_pdb().lookup_procedure("plug-in-sel2path")
        config = procedure.create_config()
        config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
        config.set_property("image", image)
        result = procedure.run(config)
        require_ok(result.index(0) == Gimp.PDBStatusType.SUCCESS, "Silhouette path conversion failed")
        silhouette = image.get_paths()[0]
        outer_width = data["outer_radius"] + data["inner_radius"]
        silhouette.set_name(f"00 | Outer silhouette - {outer_width:g} px")
        silhouette.set_visible(False)
        Gimp.Selection.none(image)

        def stroke_layer(name, path, line_width, parent=None):
            layer = Gimp.Layer.new(image, name, width, height,
                                  Gimp.ImageType.RGBA_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
            require_ok(image.insert_layer(layer, parent, 0), "Layer insertion failed")
            layer.fill(Gimp.FillType.TRANSPARENT)
            Gimp.context_set_line_width(float(line_width))
            require_ok(layer.edit_stroke_item(path), "Path stroke failed: " + name)
            return layer

        group = None
        if paint_preview:
            stroke_layer(f"Outer silhouette - {outer_width:g} px", silhouette, outer_width)
            group = Gimp.GroupLayer.new(image, f"Interior outlines - {data['interior_width']:g} px")
            image.insert_layer(group, None, 0)
        grouped = OrderedDict()
        for item in data["paths"]:
            grouped.setdefault(item["shape"], []).append(item["d"])
        internal_paths = []
        layers = []
        for number, (name, parts) in enumerate(grouped.items(), 1):
            name = f"{number:02d} | {name}"
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
                   f'viewBox="0 0 {width} {height}">'
                   + ''.join(f'<path d="{escape(d)}" fill="none"/>' for d in parts) + '</svg>')
            success, paths = image.import_paths_from_string(svg, len(svg.encode("utf-8")), True, False)
            require_ok(success and len(paths) == 1, "SVG import failed: " + name)
            path = paths[0]
            path.set_name(name)
            path.set_visible(False)
            internal_paths.append(path)
            if paint_preview:
                layers.append(stroke_layer(name, path, data["interior_width"], group))

        Gimp.context_pop()
        image.set_selected_paths([internal_paths[0]])
        image.set_selected_layers([layers[0] if layers else base])
        before = path_inventory(image)
        require_ok(Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image,
                   Gio.File.new_for_path(str(output))), "XCF save failed")
        reopened = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, Gio.File.new_for_path(str(output)))
        after = path_inventory(reopened)
        require_ok([p['name'] for p in before] == [p['name'] for p in after],
                   "Path names/order changed during XCF save/reload")
        max_delta = 0.0
        for first, second in zip(before, after):
            require_ok(len(first['strokes']) == len(second['strokes']), "Path stroke count changed")
            for left, right in zip(first['strokes'], second['strokes']):
                require_ok(left['closed'] == right['closed'] and len(left['points']) == len(right['points']),
                           "Path structure changed during save/reload")
                max_delta = max(max_delta, max(abs(a-b) for a, b in zip(left['points'], right['points'])))
        # XCF may round control coordinates to float32 and reassign stroke IDs.
        require_ok(max_delta < 0.001, f"Path positions changed by {max_delta} px on reload")
        groups = [layer for layer in reopened.get_layers() if isinstance(layer, Gimp.GroupLayer)]
        if paint_preview:
            require_ok(len(groups) == 1 and len(groups[0].get_children()) == len(grouped),
                       "Per-shape raster layers did not survive the XCF save")
        else:
            require_ok(len(reopened.get_layers()) == 1 and not groups,
                       "Paths-only XCF must contain only the source render layer")
        proc = Gimp.get_pdb().lookup_procedure("file-png-export")
        config = proc.create_config()
        config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
        config.set_property("image", reopened)
        config.set_property("file", Gio.File.new_for_path(str(output.with_suffix(".png"))))
        res = proc.run(config)
        require_ok(res.index(0) == Gimp.PDBStatusType.SUCCESS, "XCF preview export failed")
        report.update({"saved_and_reopened": True, "path_count": len(after),
                       "interior_shape_layers": len(layers), "path_coordinates_preserved": True,
                       "max_coordinate_roundtrip_error_px": max_delta,
                       "paths": [{"name": p["name"], "strokes": len(p["strokes"])} for p in after],
                       "layers": [layer.get_name() for layer in reopened.get_layers()]})
        print(json.dumps({k: v for k, v in report.items() if k not in ("paths", "layers")}))
    except Exception:
        report["error"] = traceback.format_exc()
        print(report["error"])
        raise
    finally:
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


run()
