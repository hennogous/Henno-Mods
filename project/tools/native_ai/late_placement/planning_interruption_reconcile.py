"""Restore an abruptly ended test's preferences without inventing a clean exit.

This is shared-controller lifecycle recovery, not gameplay policy. Require no
native/Tuner owner, pin both installed test packages, launch only a menu session,
restore exact subscription preferences, close it normally, then archive the
installed copies. Original logs/checkpoint/unknown exit remain separate evidence.
No world is loaded and no AI turn is advanced here.
"""
import argparse
from pathlib import Path
from types import SimpleNamespace

from driver import (HeldProcess, NativeSession, launch, load, make_probe_controller,
                    manifest, native_inventory, require, restore_preferences, sha, write_json)
from ce_replay import HOTFIX_EXE_SHA, HOTFIX_SHA, native_profile


def run(source):
    source = Path(source).resolve(strict=True)
    require(not native_inventory(), 'Native/Tuner owner remains; do not reconcile')
    require(not (source/'interruption-reconciled.json').exists(), 'Cleanup already recorded')
    identity = load(source/'session-owner.json')
    binary = Path(identity['executable_path']).resolve(strict=True)
    # Restore from the same qualified DX11 profile as the interrupted run.
    # Older records predate the profile field and used the original hotfix.
    protocol_path = source/'protocol.json'
    protocol = load(protocol_path) if protocol_path.is_file() else {}
    expected = protocol.get('native_profile', {
        'executable_sha256': HOTFIX_EXE_SHA,
        'gamecore_sha256': HOTFIX_SHA,
    })
    require(native_profile(binary) == (expected['executable_sha256'], expected['gamecore_sha256']),
            'Unexpected game executable/profile for the interrupted run')
    require((source/'original-preferences.json').is_file(), 'Missing original preferences')
    packages = load(source/'packages.json')
    installs = []
    for path, row in packages.items():
        package, installed = Path(path).resolve(strict=True), Path(row['install']).resolve(strict=True)
        require(installed.parent.name == 'Mods' and installed.name in
                ('CSC Bakers Development CE', 'CSC Bakers Development Mod'), 'Unexpected installed target')
        require(manifest(package) == row['files'] == manifest(installed), 'Test package changed')
        archive = source/installed.name
        require(not archive.exists(), 'Package archive already exists')
        installs.append((installed, archive, row['files']))
    require(len(installs) == 2, 'Expected exact CE/CSC test copies')
    out = source/'interruption-cleanup'
    require(not out.exists(), 'Preserve earlier cleanup attempt')
    out.mkdir()
    controller = make_probe_controller(out, user_root=Path(load(source/'resource-stack-preflight.json')['database']).parent.parent)
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    def archive_packages():
        require(not native_inventory(), 'Owner appeared before package archive')
        for installed, archive, files in installs:
            require(manifest(installed) == files, 'Installed package changed during cleanup')
            # Both absolute targets are verified above: move only these two
            # named test copies from Mods into this original evidence folder.
            installed.rename(archive)
    session.start(lambda: launch(SimpleNamespace(binary=binary), out))
    try:
        session.wait_context('MainMenu')
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(controller, source),
                          restore_package=archive_packages)
    require(session.closed, 'Menu cleanup did not close successfully')
    write_json(source/'interruption-reconciled.json', dict(
        verified=True, source=str(source), source_sha256=sha(source/'source.json'),
        original_native_identity=identity, original_exit_unknown=True,
        owners_absent=True, preferences_verified=True,
        cleanup_session=str(out/'session-closed.json'),
        gameplay_loaded=False, AI_turns_advanced=0,
        package_archives=[str(archive) for _, archive, _ in installs]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    run(parser.parse_args().source)
