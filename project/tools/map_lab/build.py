"""Build a self-contained viewer from native CSC map-survey exports."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GROUPS = ["vanilla-abundant", "tar-abundant", "tar-truly-abundant"]
LABELS = ["Vanilla · Abundant", "TAR · Abundant", "TAR · Truly Abundant"]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def render(bundle, target):
    encoded = json.dumps(bundle, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    template = (HERE / "viewer.template.html").read_text(encoding="utf-8")
    html = template.replace("/* MAP_LAB_CSS */", (HERE / "viewer.css").read_text(encoding="utf-8"))
    html = html.replace("/* MAP_LAB_JS */", (HERE / "viewer.js").read_text(encoding="utf-8"))
    html = html.replace("{\"MAP_LAB_DATA\":true}", encoded)
    target.write_text(html, encoding="utf-8")
    return target


def build(survey, output, luxury_survey=None):
    analysis = read(survey / "analysis.json")
    summary = {(m["group"], m["map"]): m for m in analysis["maps"]}
    maps = []
    for group, label in zip(GROUPS, LABELS):
        for folder in sorted((survey / group).glob("map-*/complete.json")):
            folder = folder.parent
            native = read(folder / "map.json")
            settings = read(folder / "settings.json")
            m = summary[group, settings["map_number"]]
            native.pop("neighbor_normalization", None)
            maps.append({"id": f"{group}-{settings['map_number']}", "group": group,
                         "groupLabel": label, "number": settings["map_number"],
                         "settings": settings, "data": native,
                         "definitions": m["resolved_definitions"],
                         "reference": [r for r in analysis["opportunities"]
                                       if r["group"] == group and r["map"] == settings["map_number"]],
                         "source_sha256": hashlib.sha256((folder / "map.json").read_bytes()).hexdigest()})
    assert len(maps) == 15, f"Expected 15 complete maps, got {len(maps)}"
    if luxury_survey:
        study = read(luxury_survey / 'analysis.json')
        for summary in study['maps']:
            group, number = summary['group'], summary['map']
            folder = luxury_survey / group / f'map-{number:02d}'
            maps.append({'id': f'{group}-{number}', 'group': group,
                         'groupLabel': f"Vanilla · Abundant · {summary['luxury_types_per_continent']} luxury types",
                         'number': number, 'settings': read(folder / 'settings.json'),
                         'data': read(folder / 'map.json'), 'definitions': summary['resolved_definitions'],
                         'reference': [r for r in study['opportunities'] if r['group'] == group and r['map'] == number],
                         'continents': summary['continents'],
                         'source_sha256': hashlib.sha256((folder / 'map.json').read_bytes()).hexdigest()})
    bundle = {"version": 1, "title": "CSC material maps", "maps": maps}
    output.mkdir(parents=True, exist_ok=True)
    target = render(bundle, output / "index.html")
    (output / "maps.json").write_text(json.dumps(bundle, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"viewer": str(target), "maps": len(maps), "bytes": target.stat().st_size}))
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--survey", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "project/snapshots/map-lab")
    parser.add_argument('--luxury-survey', type=Path, help='Add completed native 4/5/6 luxury maps and continent census')
    args = parser.parse_args()
    build(args.survey, args.output, args.luxury_survey)
