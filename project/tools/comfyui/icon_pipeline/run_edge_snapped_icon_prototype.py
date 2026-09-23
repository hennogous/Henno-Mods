"""Run guide-based edge snapping and create an unstroked editable GIMP XCF.

Requires Python with Pillow, numpy, and OpenCV-contrib (IntelligentScissorsMB),
plus GIMP 3 with the Python batch interpreter. Does not modify the source render
or any installed icon asset.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
GIMP_SCRIPT = HERE.parents[1] / 'gimp' / 'create_editable_icon_outlines.py'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='RGBA Blender render')
    parser.add_argument('guides', type=Path, help='JSON with selected major boundaries and coarse anchors')
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--gimp-console', type=Path, default=None)
    parser.add_argument('--overwrite', action='store_true', help='replace an earlier prototype in output-dir')
    args = parser.parse_args()
    source, guides, out = args.source.resolve(), args.guides.resolve(), args.output_dir.resolve()
    if not source.is_file() or not guides.is_file():
        parser.error('source render and guides JSON must exist')
    gimp = args.gimp_console or os.environ.get('GIMP_CONSOLE_PATH') or shutil.which('gimp-console-3.exe')
    if not gimp or not Path(gimp).is_file():
        parser.error('GIMP 3 console not found; pass --gimp-console')
    gimp = Path(gimp).resolve()
    xcf = out / 'Editable_Snapped_Paths.xcf'
    if xcf.exists() and not args.overwrite:
        parser.error(f'{xcf} exists; choose another output directory or pass --overwrite')
    out.mkdir(parents=True, exist_ok=True)
    snap = HERE / 'snap_icon_paths.py'
    subprocess.run([sys.executable, '-B', str(snap), str(source), str(guides), '--output-dir', str(out)], check=True)
    env = os.environ.copy()
    env.update({'CSC_OUTLINE_SOURCE': str(source),
                'CSC_OUTLINE_MANIFEST': str(out / 'snapped_paths.json'),
                'CSC_OUTLINE_XCF': str(xcf)})
    env.pop('CSC_OUTLINE_STROKE_PREVIEW', None)
    code = "exec(open(r'" + str(GIMP_SCRIPT) + "', encoding='utf-8').read())"
    subprocess.run([str(gimp), '--new-instance', '--no-interface', '--no-splash',
                    '--batch-interpreter=python-fu-eval', '--batch=' + code, '--quit'],
                   cwd=str(gimp.parent), env=env, check=True)
    report = json.loads(xcf.with_suffix('.verification.json').read_text(encoding='utf-8'))
    if not report.get('saved_and_reopened') or report.get('interior_shape_layers') != 0:
        raise RuntimeError('GIMP did not verify an unstroked paths-only XCF')
    expected = len(json.loads((out / 'snapped_paths.json').read_text(encoding='utf-8'))['paths']) + 1
    if report['path_count'] != expected:
        raise RuntimeError(f'Expected {expected} editable paths, found {report["path_count"]}')
    print(json.dumps({'xcf': str(xcf), 'path_count': expected,
                      'preview': str(out / 'Snapped_Paths_Review.png'),
                      'original_render_only': True, 'outlines_stroked': False}))


if __name__ == '__main__':
    main()
