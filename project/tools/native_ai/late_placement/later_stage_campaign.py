"""Run the preselected ordinary CSC 1–12 benchmark with the shared controller."""
import argparse
from pathlib import Path
import subprocess
import sys

from ce_replay import DLL, STEAM_26595377_CORE_SHA, native_profile
from driver import HERE, load, manifest, native_inventory, require, sha, write_json
from later_stage_replay import candidate_package


SEEDS = {
    'Continents': (793412556, 1390346751),
    'Fractal': (28111119, 38111119),
    'Pangaea': (27061117, 37061117),
}


def run(args):
    reference = args.reference.resolve(strict=True)
    require(load(reference / 'session-closed.json')['verified'], 'Reference run did not close cleanly')
    require(not native_inventory(), 'A different Civ VI or FireTuner session owns the console')
    protocol = load(reference / 'protocol.json')
    binary = Path(load(reference / 'launch-bootstrap.json')['binary'])
    _, core = native_profile(binary)
    require(core == STEAM_26595377_CORE_SHA and protocol['native_profile']['gamecore_sha256'] == core,
            'The current release does not match the qualified CE binary')
    extras = load(reference / 'extra-mods.json')
    for item in extras.values():
        require(manifest(Path(item['path'])) == item['files'], 'An optional mod changed since reference')
    packages = load(reference / 'packages.json')
    ce, = (Path(path) for path in packages if (Path(path) / 'Binaries/Win64' / DLL).is_file())
    original, = (Path(path) for path in packages if Path(path) != ce)
    require(all(manifest(Path(path)) == item['files'] for path, item in packages.items()), 'Frozen release drift')
    mods = Path(packages[str(ce)]['install']).parent
    saves = mods.parent / 'Saves/Single'
    user_root = Path(load(reference / 'resource-stack-preflight.json')['database']).parent.parent

    output = args.output.resolve()
    frozen = output / 'combined-package'
    lock = output / 'campaign-inputs.json'
    if lock.is_file():
        pins = load(lock)
        require(pins['reference'] == str(reference) and pins['ce'] == manifest(ce)
                and pins['csc'] == manifest(frozen), 'Campaign package or reference changed')
    else:
        require(not output.exists(), 'Choose a new output folder for an unstarted campaign')
        output.mkdir(parents=True)
        payload = candidate_package(original, args.candidate_source.resolve(strict=True), frozen)
        write_json(lock, dict(reference=str(reference), seeds=SEEDS, ce=manifest(ce), csc=payload,
                              gamecore_sha256=core, extras=extras))

    def game(map_name, arm, other=None):
        map_seed, game_seed = SEEDS[map_name]
        destination = output / f'{map_name.lower()}-{arm}'
        if destination.is_dir():
            require((destination / 'full-game-observation-complete.json').is_file()
                    and load(destination / 'session-closed.json')['verified'],
                    'An interrupted arm needs recovery before the campaign can reuse it')
            return destination
        require(not native_inventory(), 'Console already has an owner')
        command = [sys.executable, str(HERE / 'ce_bakers_fresh.py'),
                   '--output', str(destination), '--mods', str(mods), '--user-root', str(user_root),
                   '--binary', str(binary), '--ce', str(ce), '--csc', str(frozen),
                   '--ce-sha256', sha(ce / 'Binaries/Win64' / DLL), '--saves', str(saves),
                   '--map', map_name, '--map-size', 'small', '--map-seed', str(map_seed),
                   '--game-seed', str(game_seed), '--through', '250', '--interval-minutes', '15',
                   '--harmonised-observation', '--planning-observation', '--service-observation', '--main-mod-package']
        if arm == 'stock':
            command += ['--untuned']
        if other:
            command += ['--matched-source', str(other / 'source.json')]
        for item in extras.values():
            command += ['--extra-mod', item['path']]
        print(f'{map_name} {arm} starting', flush=True)
        subprocess.run(command, check=True)
        print(f'{map_name} {arm} reached turn 250', flush=True)
        return destination

    for map_name in args.map or SEEDS:
        stock = game(map_name, 'stock')
        game(map_name, 'combined', stock)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reference', 'output', 'candidate-source'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--map', choices=tuple(SEEDS), action='append')
    run(parser.parse_args())
