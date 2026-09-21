#!/usr/bin/env python3
"""Discover, export and install all top-level .blend files in --blend-directory.

Run from the repository; helpers live in the adjacent scene_export directory.
Python 3.10+, standard library only. Never connects to another machine.
"""
import argparse
import datetime
import hashlib
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


def latest_installed_job(blend_directory):
    """Resolve the newest installed export recorded under one source folder."""
    runs = blend_directory.expanduser().resolve() / 'export-runs'
    candidates = []
    for job_path in runs.glob('*/job.json'):
        report_path = job_path.parent / 'report.json'
        if not report_path.is_file():
            continue
        try:
            report = json.loads(report_path.read_text(encoding='utf-8'))
            job = json.loads(job_path.read_text(encoding='utf-8'))
            if Path(job['output']).resolve() == job_path.parent.resolve():
                candidates.append((job_path,report.get('status')))
        except (OSError, ValueError, KeyError, TypeError):
            continue
    for job_path,status in sorted(candidates,key=lambda row:row[0].parent.name,reverse=True):
        if status == 'installed_pending_asset_editor_and_game_review':
            return job_path
        if status in ('purged','uninstalled','superseded'):
            break
    raise ValueError(f'No installed export run found under {runs}')


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
    parser.add_argument('--contract', type=Path, help='Building contract JSON; defaults to export-contract.json in blend folder when present')
    parser.add_argument('--include-optional', action='store_true', help='Include all optional blends listed by the building contract')
    parser.add_argument('--stage-only', action='store_true', help='Decode and build; skip FGX/DDS conversion')
    parser.add_argument('--no-install', action='store_true', help='Convert into the run folder without installing into the mod')
    parser.add_argument('--install', type=Path, metavar='JOB_JSON', help='Explicitly install a previously converted run')
    parser.add_argument('--uninstall', type=Path, metavar='JOB_JSON', help='Undo one installed folder export from its run job.json')
    parser.add_argument('--list-purge', type=Path, metavar='JOB_JSON', help='List every file and XLP entry a purge of this run would remove; make no changes')
    parser.add_argument('--list-latest-purge', type=Path, metavar='BLEND_DIRECTORY', help='Preview purge of the newest installed run from this blend folder')
    parser.add_argument('--purge-latest', type=Path, metavar='BLEND_DIRECTORY', help='Purge the newest installed run from this blend folder')
    parser.add_argument('--dry-run', action='store_true', help='With --uninstall, show the plan without changing mod files')
    parser.add_argument('--purge', action='store_true', help='With --uninstall, delete all assets produced by this run instead of restoring prior versions')
    parser.add_argument('--force', action='store_true', help='With purge, also delete run-owned outputs changed or removed since installation')
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    helpers = here / 'scene_export'
    engine = helpers / 'export_scene.py'
    if not engine.is_file():
        parser.error(f'Missing helper: {engine}; copy the scene_export folder too')
    if sum(bool(x) for x in (args.install,args.uninstall,args.list_purge,args.list_latest_purge,args.purge_latest))>1:
        parser.error('Choose only one install, uninstall, or purge operation')
    if args.dry_run and not (args.uninstall or args.purge_latest):
        parser.error('--dry-run requires --uninstall or --purge-latest')
    if args.purge and not args.uninstall:
        parser.error('--purge requires --uninstall')
    if args.force and not (args.list_purge or args.list_latest_purge or args.purge_latest or (args.uninstall and args.purge)):
        parser.error('--force requires a purge operation')
    if args.list_latest_purge or args.purge_latest:
        job_path = latest_installed_job(args.list_latest_purge or args.purge_latest)
        command = [sys.executable, str(engine), 'uninstall', str(job_path), '--purge']
        if args.list_latest_purge or args.dry_run: command.append('--dry-run')
        if args.force: command.append('--force')
        return subprocess.call(command)
    if args.list_purge:
        command = [sys.executable, str(engine), 'uninstall',
                   str(args.list_purge.resolve()), '--purge', '--dry-run']
        if args.force: command.append('--force')
        return subprocess.call(command)
    if args.uninstall:
        command=[sys.executable, str(engine), 'uninstall', str(args.uninstall.resolve())]
        if args.dry_run: command.append('--dry-run')
        if args.purge: command.append('--purge')
        if args.force: command.append('--force')
        return subprocess.call(command)
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
    from discovery import find_blends, select_blends, make_job, apply_contract_file
    files = find_blends(blends)
    contract_path=(args.contract or blends/'export-contract.json').expanduser().resolve()
    if args.contract and not contract_path.is_file():
        parser.error(f'Missing contract file: {contract_path}')
    if args.include_optional and not contract_path.is_file():
        parser.error('--include-optional requires a building contract')
    if contract_path.is_file():
        files=select_blends(files,contract_path,args.include_optional)
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
    rows=json.loads(inventory.read_text())
    if contract_path.is_file():
        rows=apply_contract_file(rows,contract_path,catalogue)
        (out/'contract-source.json').write_text(json.dumps({'path':str(contract_path),
            'sha256':hashlib.sha256(contract_path.read_bytes()).hexdigest()},indent=2)+'\n')
    job, report = make_job(rows, defaults, mod, library, out, catalogue)
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
