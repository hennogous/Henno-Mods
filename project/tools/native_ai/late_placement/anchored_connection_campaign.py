"""Compare current CSC district tuning with the anchored planner in three matched games."""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

from anchored_connection_results import run_result
from ce_bakers_fresh import package_identity
from ce_replay import DLL, STEAM_26595377_CORE_SHA, development_package_files, native_profile
from driver import HERE, load, manifest, native_inventory, require, sha, write_json
from later_stage_replay import CONNECTION_FILES, CONNECTION_WONDER_UI


# Selected before observing the new games, using the protocol in the study note.
SEEDS = {
    'Continents': (1457395586, 276090738),
    'Fractal': (1836181160, 641259670),
    'Pangaea': (1094008659, 1112702560),
}
ADAPTER = 'Lua_UI/AI/CSC_AI_EconomyAdapters.lua'
FLAG = b'E.AnchoredConnectionsEnabled=false'
AUDIT = b'E.AnchoredConnectionAuditEnabled=false'


def compare(matrix):
    def outcomes(arms):
        scope = [r['counts'] for r in arms]
        found = sum(sum(counts['completed_district_opportunities'].values()) for counts in scope)
        available = sum(sum(counts['district_opportunities'].values()) for counts in scope)
        physical = sum(sum(counts['completed_physical_pairs'].values()) for counts in scope)
        return dict(completed=found, feasible=available, physical_pairs=physical,
                    conversion=found / available if available else None)

    def gained(control, candidate):
        return (control['feasible'] > 0 and candidate['feasible'] > 0
                and candidate['completed'] * control['feasible'] > control['completed'] * candidate['feasible'])

    seeds, campaign = {}, {}
    for name, arms in matrix.items():
        control, candidate = (outcomes([arms[arm]]) for arm in ('control', 'candidate'))
        seeds[name] = dict(control=control, candidate=candidate, improved=gained(control, candidate))
    for arm in ('control', 'candidate'):
        campaign[arm] = outcomes([arms[arm] for arms in matrix.values()])
    improved = sum(seed['improved'] for seed in seeds.values())
    qualifies = (set(matrix) == set(SEEDS) and improved >= 2
                 and gained(campaign['control'], campaign['candidate'])
                 and campaign['candidate']['physical_pairs'] > campaign['control']['physical_pairs'])
    return dict(arms=matrix, seeds=seeds, aggregate=campaign, improved_seeds=improved, qualifies=qualifies)


def freeze_packages(original, source, packages):
    # Share every cooked asset, action, SQL definition and diagnostic between
    # arms. The private yield remains enabled in the existing CSC SQL.
    control, candidate = packages.values()
    adapter = (source / ADAPTER).read_bytes()
    require(adapter.count(FLAG) == adapter.count(AUDIT) == 1, 'Expected explicit disabled planner and audit switches')
    observed = adapter.replace(AUDIT, AUDIT.replace(b'false', b'true'))
    shutil.copytree(original, control)
    for script in (*CONNECTION_FILES, CONNECTION_WONDER_UI):
        require((control / script).is_file(), f'Unregistered CSC Lua overlay {script}')
        shutil.copy2(source / script, control / script)
    (control / ADAPTER).write_bytes(observed)
    shutil.copytree(control, candidate)
    (candidate / ADAPTER).write_bytes(observed.replace(FLAG, FLAG.replace(b'false', b'true')))


def run(args):
    reference = args.reference.resolve(strict=True)
    ce = args.ce.resolve(strict=True)
    require(load(reference / 'session-closed.json')['verified'], 'Previous package source must be closed')
    protocol = load(reference / 'protocol.json')
    extras = load(reference / 'extra-mods.json')
    for item in extras.values():
        require(manifest(Path(item['path'])) == item['files'], 'An optional mod changed since the previous games')
    garden = args.garden.resolve(strict=True)
    garden_id, _ = package_identity(garden)
    require(garden_id == '1bd6e042-25c3-4584-9bc3-66f1ce3bd249' and garden_id not in extras,
            'Expected Leugi’s Garden as an additional Fractal mod')
    map_extras = {name: dict(extras) for name in SEEDS}
    map_extras['Fractal'][garden_id] = dict(path=str(garden), files=manifest(garden))
    sources = load(reference / 'packages.json')
    old_ce, = (Path(path) for path in sources if (Path(path) / 'Binaries/Win64' / DLL).is_file())
    original, = (Path(path) for path in sources if Path(path) != old_ce)
    require(manifest(original) == sources[str(original)]['files'], 'Previous CSC package has changed')
    require(package_identity(ce)[0] == protocol['ce'], 'Dev CE must retain the qualified mod identity')
    mods = Path(sources[str(old_ce)]['install']).parent
    require(development_package_files(ce) == development_package_files(mods / 'CSC Bakers Development CE'),
            'Installed Dev CE differs from the selected package')
    saves = mods.parent / 'Saves/Single'
    user_root = Path(load(reference / 'resource-stack-preflight.json')['database']).parent.parent
    binary = Path(load(reference / 'launch-bootstrap.json')['binary'])
    exe, core = native_profile(binary)
    require(core == STEAM_26595377_CORE_SHA, 'Civ VI binary has changed')
    output = args.output.resolve()
    packages = {arm: output / f'{arm}-package' for arm in ('control', 'candidate')}
    lock = output / 'campaign-inputs.json'
    pins = dict(reference=str(reference), seeds={name: list(pair) for name, pair in SEEDS.items()},
                ce_path=str(ce), ce=development_package_files(ce), csc_base=str(original),
                executable_sha256=exe, gamecore_sha256=core, extras=map_extras)
    if not lock.is_file():
        require(not output.exists(), 'Use a new directory to freeze this campaign')
        freeze_packages(original, args.candidate_source.resolve(strict=True), packages)
    csc = {arm: manifest(path) for arm, path in packages.items()}
    before, after = csc.values()
    require(set(before) == set(after) and {Path(name).as_posix() for name in before
            if before[name] != after[name]} == {ADAPTER}, 'Matched packages must differ only in the planner switch')
    require((packages['control'] / ADAPTER).read_bytes().replace(FLAG, FLAG.replace(b'false', b'true'))
            == (packages['candidate'] / ADAPTER).read_bytes(), 'Unexpected matched policy change')
    pins['csc'] = csc
    if lock.is_file():
        require(load(lock) == pins, 'Pinned campaign inputs changed')
    else:
        write_json(lock, pins)
    if args.freeze_only:
        return
    require(not native_inventory(), 'Another Civ VI or FireTuner session owns the console')

    def game(map_name, arm, other=None):
        destination = output / f'{map_name.lower()}-{arm}'
        if destination.exists():
            run_result(destination)
            return destination
        require(not native_inventory(), 'Another process took ownership of the game console')
        map_seed, game_seed = SEEDS[map_name]
        command = [sys.executable, str(HERE / 'ce_bakers_fresh.py'),
                   '--output', str(destination), '--mods', str(mods), '--user-root', str(user_root),
                   '--binary', str(binary), '--ce', str(ce), '--csc', str(packages[arm]),
                   '--ce-sha256', sha(ce / 'Binaries/Win64' / DLL), '--saves', str(saves),
                   '--map', map_name, '--map-size', 'small', '--map-seed', str(map_seed), '--game-seed', str(game_seed),
                   '--through', '250', '--interval-minutes', '15', '--main-mod-package',
                   '--harmonised-observation', '--planning-observation', '--service-observation']
        if other:
            command += ['--reference-source', str(other / 'source.json')]
        for item in map_extras[map_name].values():
            command += ['--extra-mod', item['path']]
        print(f'{map_name} {arm} starting', flush=True)
        subprocess.run(command, check=True)
        write_json(destination / 'anchored-connection-result.json', run_result(destination))
        print(f'{map_name} {arm} reached turn 250', flush=True)
        return destination

    matrix = {}
    for map_name in args.map or SEEDS:
        control = game(map_name, 'control')
        candidate = game(map_name, 'candidate', control)
        matrix[map_name] = dict(control=run_result(control), candidate=run_result(candidate))
    write_json(output / 'campaign-comparison.json', compare(matrix))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reference', 'ce', 'garden', 'output', 'candidate-source'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--map', choices=tuple(SEEDS), action='append')
    parser.add_argument('--freeze-only', action='store_true', help='Pin inputs and write both packages without launching Civ VI')
    run(parser.parse_args())
