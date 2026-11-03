"""Review native scrolling overlay artwork without opening or changing the game.

Read shipped Overlay ArtDefs and their matching Windows BLPs. Export original
RGBA pixels, a contact sheet, an illustrative scrolling GIF and source evidence.
The preview does not reproduce the native shader, terrain projection or timing.
"""
import argparse
import hashlib
import json
import math
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


FLOW = ["FormCorpsArrow", "TradeRoutePrimary", "ReligiousPressureIn",
        "LoyaltyPressureIn", "ReligiousPressureOut", "ZombieSense",
        "PS_English_Pointer", "PS_Dowsing_Rod"]
LABELS = {
    "FormCorpsArrow": "Corps formation arrows",
    "TradeRoutePrimary": "Trade route",
    "ReligiousPressureIn": "Religion: incoming waves",
    "LoyaltyPressureIn": "Loyalty pressure waves",
    "ReligiousPressureOut": "Religion: outgoing waves",
    "ZombieSense": "Zombie sensing",
    "PS_English_Pointer": "Pirates: English pointer",
    "PS_Dowsing_Rod": "Pirates: dowsing rod",
    "ART_DEF_OVERLAY_CULTURE_MASK": "Territory border",
    "OVER_Culture_Border_Open": "Open territory border",
    "OVER_Culture_Border_Citystate": "City-state border",
    "OVER_Culture_Border_CityState_Open": "Open city-state border",
    "MoveBorder": "Movement range border",
    "AOEBorder": "Area-of-effect border",
    "CR_border": "Red Death zone border",
    "cr_BarbCamptBorder": "Red Death camp border",
    "CR_Warning_Border": "Red Death warning border",
    "PS_Treasure_border_HexHighlightEdge": "Pirates: treasure-area border",
}


def inventory(game):
    """Keep every material variant, grouped by the texture it actually uses."""
    result = {}
    paths = [game / "Base/ArtDefs/Overlay.artdef"]
    paths += sorted((game / "DLC").glob("*/ArtDefs/Overlay.artdef"))
    for path in paths:
        root = ET.parse(path).getroot()
        for group in root.findall("./m_RootCollections/Element"):
            if group.find("m_CollectionName").get("text") != "Overlays":
                continue
            for material in group.findall("Element"):
                for collection in material.findall("./m_ChildCollections/Element"):
                    if collection.find("m_CollectionName").get("text") != "SplineBorder":
                        continue
                    for style in collection.findall("Element"):
                        values = {v.find("m_ParamName").get("text"): v
                                  for v in style.findall("./m_Fields/m_Values/Element")}
                        texture = values.get("SplineTexture")
                        if texture is None:
                            continue
                        name = texture.find("m_EntryName").get("text")
                        variant = {
                            "artdef": str(path.relative_to(game)),
                            "overlay": material.find("m_Name").get("text"),
                            "style": style.find("m_Name").get("text"),
                        }
                        for key in ["SplineWidth", "SplineSegmentLength", "SplineScrollSpeed", "Color_Alpha"]:
                            value = values.get(key)
                            if value is not None:
                                variant[key] = float(next(c.text for c in value if c.tag != "m_ParamName"))
                        if variant.get("SplineScrollSpeed", 0) == 0:
                            continue
                        result.setdefault(name, {"texture": name, "variants": []})["variants"].append(variant)
    return result


def read_native_textures(package):
    """Read the inspected v2 OverlayTexture serialization; reject other layouts.

    TextureEntry is 104 bytes, starting at 35037 in these shipped packages.
    Its consecutive name slots start at 2. The following string objects have
    two lengths and 16-byte padded storage. Full mip payload sizes and bounds
    are checked before accepting a record; this is not a general BLP decoder.
    """
    data = package.read_bytes()
    assert data[:8] == b"CIVBLP\x02\0", package
    big_data = struct.unpack_from("<I", data, 16)[0]
    records = []
    position = 35037
    while position + 104 < big_data:
        fmt, w, h, depth, layers, mips, flags = struct.unpack_from("<5H2B", data, position + 88)
        if fmt != 29 or depth != 1 or layers != 1 or flags != 0:
            break
        slot = struct.unpack_from("<Q", data, position + 8)[0]
        assert slot == len(records) + 2
        assert w > 0 and h > 0 and w & (w - 1) == h & (h - 1) == 0
        assert 1 <= mips <= 14
        offset, size = struct.unpack_from("<QI", data, position + 32)
        assert size == sum(max(1, w >> n) * max(1, h >> n) * 4 for n in range(mips))
        assert big_data + offset + size <= len(data)
        records.append((position, w, h, offset, size))
        position += 104
    assert records, package
    position += 8
    textures = {}
    for record, w, h, offset, size in records:
        capacity, length = struct.unpack_from("<II", data, position)
        assert capacity == length + 1 and 0 < length < 256
        name = data[position + 8:position + 8 + length].decode("ascii")
        assert data[position + 8 + length] == 0 and name not in textures
        position += ((8 + capacity + 15) // 16) * 16
        pixels = data[big_data + offset:big_data + offset + w * h * 4]
        textures[name] = (Image.frombytes("RGBA", (w, h), pixels), {
            "package": str(package), "package_sha256": hashlib.sha256(data).hexdigest(),
            "record_offset": record, "size": [w, h], "pixel_sha256": hashlib.sha256(pixels).hexdigest(),
            "full_mip_payload_bytes": size,
        })
    return textures


def font(size, bold=False):
    path = Path("C:/Windows/Fonts") / ("segoeuib.ttf" if bold else "segoeui.ttf")
    return ImageFont.truetype(str(path), size)


def checker(size):
    image = Image.new("RGBA", size, (29, 39, 48, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], 12):
        for x in range(0, size[0], 12):
            if (x // 12 + y // 12) % 2:
                draw.rectangle((x, y, x + 11, y + 11), fill=(37, 48, 57, 255))
    return image


def strip(texture, size, phase=0):
    # Texture U is shown left-to-right. Equal display height is a comparison
    # convention, not the game's width/repetition ratio or shader orientation.
    width = max(2, round(texture.width * size[1] / texture.height))
    tile = texture.resize((width, size[1]), Image.Resampling.LANCZOS)
    result = checker(size)
    offset = round((phase % 1) * width)
    for x in range(-width + offset, size[0], width):
        result.alpha_composite(tile, (x, 0))
    return result


def note(row):
    name = row["texture"]
    if name == "ReligiousPressureOut":
        return "Stock width is ZERO: private width needed to display."
    if name.startswith(("PS_", "CR_", "cr_")) or name == "ZombieSense":
        return "Scenario asset: package privately for the normal game."
    if name in FLOW:
        return "Directional candidate; private layer/material recommended."
    return "Scrolling border mask; packed colour channels, not a flow arrow."


def render_sheet(rows, images):
    cw, ch, margin = 660, 350, 28
    width = margin * 2 + cw * 3
    height = 185 + math.ceil(len(rows) / 3) * ch + 65
    sheet = Image.new("RGBA", (width, height), "#101b26")
    d = ImageDraw.Draw(sheet)
    d.text((margin, 20), "CIV VI / NATIVE SCROLLING OVERLAYS", font=font(35, True), fill="#f4e4ba")
    d.text((margin, 70), "18 distinct textures from shipped SplineBorder materials | base game + installed DLC", font=font(23), fill="white")
    d.text((margin, 106), "Actual native RGBA artwork. Repeated strips are texture studies, not captures of the game renderer.", font=font(22), fill="#b7c7d6")
    d.text((margin, 139), "Widths, repeat and scroll are stock ArtDef values. Scenario assets need explicit packaging; all colours remain adjustable.", font=font(20), fill="#b7c7d6")
    for i, row in enumerate(rows):
        x, y = margin + (i % 3) * cw, 185 + (i // 3) * ch
        d.rounded_rectangle((x, y, x + cw - 16, y + ch - 16), radius=12, fill="#1b2b3a", outline="#3e5264")
        name, v = row["texture"], row["variants"][0]
        d.text((x + 16, y + 11), f"{i+1:02}  {LABELS[name]}", font=font(24, True), fill="white")
        d.text((x + 16, y + 47), name, font=font(17), fill="#aac9e6")
        tex = images[name]
        thumb = checker((180, 142))
        art = tex.copy()
        art.thumbnail((174, 136), Image.Resampling.LANCZOS)
        thumb.alpha_composite(art, ((180-art.width)//2, (142-art.height)//2))
        sheet.alpha_composite(thumb, (x + 16, y + 80))
        sheet.alpha_composite(strip(tex, (410, 100)), (x + 212, y + 101))
        d.text((x + 16, y + 226), f"Native {tex.width} x {tex.height}", font=font(17), fill="#bfccd8")
        d.text((x + 212, y + 208), "Repeated texture / equal display height", font=font(17), fill="#bfccd8")
        d.text((x + 16, y + 256), f"Width {v['SplineWidth']:g} | repeat {v['SplineSegmentLength']:g} | scroll {v['SplineScrollSpeed']:+g}", font=font(19), fill="#f4e4ba")
        d.text((x + 16, y + 287), note(row), font=font(16), fill="#d2dce4")
    d.text((margin, height - 53), "01-08: flow candidates. 09-18: border alternatives. Raw colour masks are intentionally preserved; no invented effects.", font=font(21), fill="#b7c7d6")
    return sheet.convert("RGB")


def render_gif(rows, images, output):
    frames = []
    for frame in range(48):
        canvas = Image.new("RGBA", (1240, 1020), "#101b26")
        d = ImageDraw.Draw(canvas)
        d.text((24, 18), "NATIVE ART / SCROLLING STUDY", font=font(30, True), fill="#f4e4ba")
        d.text((24, 64), "Illustrative UV scroll, equal size and cycle time. Not native timing or an in-game capture.", font=font(20), fill="#c2d0dd")
        for i, row in enumerate(rows):
            x, y = 24 + (i % 2) * 608, 112 + (i // 2) * 222
            d.rounded_rectangle((x, y, x+588, y+204), radius=10, fill="#1b2b3a", outline="#3e5264")
            d.text((x+14, y+10), f"{i+1:02}  {LABELS[row['texture']]}", font=font(23, True), fill="white")
            sign = -1 if row["variants"][0]["SplineScrollSpeed"] < 0 else 1
            canvas.alpha_composite(strip(images[row["texture"]], (558, 105), sign*frame/48), (x+14, y+49))
            message = "Stock width 0: shown here with a visible width" if row["texture"] == "ReligiousPressureOut" else row["texture"]
            d.text((x+14, y+168), message, font=font(18), fill="#c2d0dd")
        frames.append(canvas.convert("RGB").quantize(colors=128))
    frames[0].save(output, save_all=True, append_images=frames[1:], duration=80, loop=0, disposal=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", type=Path, required=True)
    parser.add_argument("--sdk", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = inventory(args.game)
    assert set(rows) == set(LABELS), "New or missing native textures: update labels after inspection"
    ordered = [rows[n] for n in FLOW] + [r for n, r in rows.items() if n not in FLOW]
    packages, images = {}, {}
    for row in ordered:
        root = (args.game / row["variants"][0]["artdef"]).parent.parent
        package = root / "Platforms/Windows/BLPs/Overlay.blp"
        if package not in packages:
            packages[package] = read_native_textures(package)
        im, evidence = packages[package][row["texture"]]
        images[row["texture"]] = im
        row.update(evidence)
        # SDK pixel parity is an independent control on extraction/channel order.
        sdk_name = "OVER_Culture_Border_02" if row["texture"] == "ART_DEF_OVERLAY_CULTURE_MASK" else row["texture"]
        controls = list(args.sdk.rglob(sdk_name + ".dds"))
        row["sdk_pixel_controls"] = []
        for path in controls:
            control = Image.open(path).convert("RGBA")
            equal = control.size == im.size and control.tobytes() == im.tobytes()
            row["sdk_pixel_controls"].append({"path": str(path), "equal": equal})
        row["note"] = note(row)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "textures").mkdir(exist_ok=True)
    for name, im in images.items():
        im.save(args.output / "textures" / (name + ".png"))
    render_sheet(ordered, images).save(args.output / "native-animation-contact-sheet.png")
    render_gif(ordered[:8], images, args.output / "native-animation-scrolling-study.gif")
    (args.output / "native-materials.json").write_text(json.dumps(ordered, indent=2) + "\n", encoding="utf-8")
    matches = sum(any(c["equal"] for c in r["sdk_pixel_controls"]) for r in ordered)
    (args.output / "README.txt").write_text(
        "Native overlay material review\n\n"
        "18 unique scrolling textures; every source material variant is listed in native-materials.json.\n"
        "PNG: original native RGBA pixels, plus illustrative repetition.\n"
        "GIF: original artwork scrolling at normalized cycle time; not native shader, orientation or timing.\n"
        "Border textures can encode separate colour masks in their channels. Their raw red/green is not a prescribed lens colour.\n"
        "ReligiousPressureOut has stock width 0; visible use requires a private width override.\n"
        "Scenario art needs explicit packaging for use outside the scenario. Native lens appearance requires in-game review.\n"
        f"Extraction: checked v2 RGBA layout, sequential names, full mip sizes and payload bounds. {matches}/18 match SDK source pixels exactly.\n"
        "No game, installed package, mod source art or player settings were changed.\n", encoding="utf-8")
    print(f"Rendered {len(ordered)} native materials from {len(packages)} packages; {matches} exact SDK pixel controls: {args.output}")


if __name__ == "__main__":
    main()
