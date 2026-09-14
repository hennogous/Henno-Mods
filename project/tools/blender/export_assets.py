#!/usr/bin/env python3
"""Discover, export and install all top-level .blend files in --blend-directory.

Run from the repository; helpers live in the adjacent scene_export directory.
Python 3.10+, standard library only. Never connects to another machine.
"""
import argparse
import datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys


def executable(value):
    found = shutil.which(value)
    path = Path(found or value).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f'Executable not found: {value}')
    return str(path)


def run_step(command, log_path):
    print(f'Running {log_path.stem}; log: {log_path}', flush=True)
    with log_path.open('w', encoding='utf-8') as log:
        # Stream while retaining full diagnostics for the local Windows agent.
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, encoding='utf-8', errors='replace') as process:
            for line in process.stdout:
                log.write(line)
                log.flush()
                print(line, end='', flush=True)
            code = process.wait()
    if code:
        raise RuntimeError(f'Export stopped (exit {code}); see {log_path}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blend-directory', type=Path, help='Revision folder containing the final blends and textures')
    parser.add_argument('--mod-root', type=Path)
    parser.add_argument('--library', type=Path)
    parser.add_argument('--blender', default='blender')
    parser.add_argument('--converter', help='Defaults to the mod repository tools/cn6libs converter')
    parser.add_argument('--texconv', help='Defaults to project/tools/directxtex/texconv.exe, then texconv on PATH')
    parser.add_argument('--output', type=Path, help='New empty directory; default export-runs/timestamp')
    parser.add_argument('--defaults', type=Path, help='Override CSC template/material/policy defaults JSON')
    parser.add_argument('--stage-only', action='store_true', help='Decode and build; skip FGX/DDS conversion')
    parser.add_argument('--no-install', action='store_true', help='Convert into the run folder without installing into the mod')
    parser.add_argument('--install', type=Path, metavar='JOB_JSON', help='Explicitly install a previously converted run')
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    helpers = here / 'scene_export'
    engine = helpers / 'export_scene.py'
    if not engine.is_file():
        parser.error(f'Missing helper: {engine}; copy the scene_export folder too')
    if args.install:
        # The engine verifies conversion receipts and destination hashes, backs up
        # replaced files and merges the current XLP before installing.
        return subprocess.call([sys.executable, str(engine), 'install', str(args.install.resolve())])
    if not args.mod_root or not args.library or not args.blend_directory:
        parser.error('Export requires --blend-directory, --mod-root and --library')
    mod = args.mod_root.expanduser().resolve()
    library = args.library.expanduser().resolve()
    blends = args.blend_directory.expanduser().resolve()
    sys.path.insert(0, str(helpers))
    from discovery import find_blends, make_job
    files = find_blends(blends)
    if not mod.is_dir() or not library.is_dir():
        parser.error('--mod-root and --library must be existing local directories')
    blender = executable(args.blender)
    converter = texconv = None
    if not args.stage_only:
        converter = executable(args.converter or str(mod.parent / 'project/tools/cn6libs/CN6ToFGX.exe'))
        local_texconv = here.parent / 'directxtex' / 'texconv.exe'
        texconv = executable(args.texconv or (str(local_texconv) if local_texconv.is_file() else 'texconv'))
    defaults = json.loads((args.defaults or helpers / 'csc.defaults.json').read_text(encoding='utf-8'))
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    out = (args.output or blends / 'export-runs' / stamp).expanduser().resolve()
    if out == mod or mod in out.parents:
        parser.error('Export output must be outside the live mod content directory')
    if out.exists():
        parser.error(f'Output already exists: {out}; choose a fresh directory')
    out.mkdir(parents=True)
    logs = out / 'runner-logs'
    logs.mkdir()
    request = out / 'discovery-request.json'
    request.write_text(json.dumps({'files': [str(p) for p in files]}, indent=2) + '\n')
    inventory = out / 'discovery-inventory.json'
    run_step([blender, '--background', '--factory-startup', '--python-exit-code', '1',
              '--python', str(helpers / 'discover_blends.py'), '--', str(request), str(inventory)],
             logs / 'discover.log')
    catalogue = {a['asset_id']: a for a in json.loads((library / 'catalogue.json').read_text())['assets']}
    job, report = make_job(json.loads(inventory.read_text()), defaults, mod, library, out, catalogue)
    (out / 'discovery-report.json').write_text(json.dumps(report, indent=2) + '\n')
    if report['blockers']:
        raise ValueError('Discovery blocked; see ' + str(out / 'discovery-report.json') +
                         '\n' + '\n'.join(report['blockers']))
    job_path = out / 'job.json'
    job_path.write_text(json.dumps(job, indent=2) + '\n', encoding='utf-8')
    base = [sys.executable, str(engine)]
    run_step(base + ['decode', str(job_path), '--blender', blender], logs / 'decode.log')
    run_step(base + ['build', str(job_path)], logs / 'build.log')
    if not args.stage_only:
        run_step(base + ['convert', str(job_path), '--converter', converter, '--texconv', texconv], logs / 'convert.log')
        if not args.no_install:
            run_step(base + ['install', str(job_path)], logs / 'install.log')
    print(f'\nFinished. Report: {out / "report.json"}\nJob: {job_path}')
    if args.stage_only or args.no_install:
        print('Staged only. Source blends and live mod files were not changed.')
    else:
        print('Installed into the mod project, including XLP entries. Source blends were not changed.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(1)
