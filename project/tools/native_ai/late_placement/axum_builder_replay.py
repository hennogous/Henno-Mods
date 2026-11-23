"""Observe Axum's Flax/Bamboo jobs in the unchanged saved Continents world."""
import argparse
from pathlib import Path
import sys
from types import SimpleNamespace

from ce_replay import STEAM_26595377_CORE_SHA
from driver import load, parse, require
from material_development_replay import observe_workers
from planning_continue import run


def replay(source, output, frida_directory, at, defer_one_turn, boundary_only):
    protocol = load(source / 'protocol.json')
    require((protocol['map'], protocol['map_seed'], protocol['game_seed']) ==
            ('Continents', 18111120, 29111120)
            and protocol['native_profile']['gamecore_sha256'] == STEAM_26595377_CORE_SHA,
            'Expected the recorded Continents benchmark and Steam GameCore')
    require((frida_directory / 'frida/__init__.py').is_file(), 'Missing existing Frida package')
    sys.path.insert(0, str(frida_directory.resolve()))
    import frida

    def worker_trace(session, controller, out):
        raw = controller.cmd('''
local city=assert(Players[5]:GetCities():FindID(131073))
assert(city:GetName()=='LOC_CITY_NAME_AXUM' or city:GetName()=='Axum')
local flax,bamboo=Map.GetPlotByIndex(1828),Map.GetPlotByIndex(1977)
assert(flax:GetResourceType()==GameInfo.Resources.RESOURCE_CSC_FLAX.Index)
assert(bamboo:GetResourceType()==GameInfo.Resources.RESOURCE_BAMBOO.Index)
print('CSC_AXUM_FARM='..GameInfo.Improvements.IMPROVEMENT_FARM.Index)
''', 'GameCore_Tuner', 'verify-axum-worker-fixture')
        opening = dict(axum=True, snapshotOnly=boundary_only, player=5, city=131073, improvement=parse(raw,'CSC_AXUM_FARM'),
                       plots=[dict(plot=1828,x=52,y=24), dict(plot=1977,x=53,y=26)])
        return observe_workers(frida, session, controller, opening, out)

    # The later checkpoint starts with the chosen worker already travelling.
    # Five turns cover the original Protect failure, fresh reservation and work.
    through = {100: 175, 150: 155}[at]
    run(SimpleNamespace(source=source, output=output, at=at, through=through,
                        dependencies=None, material_only=True), material_observer=worker_trace,
        material_observer_start=at + 1 if defer_one_turn else None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'output', 'frida-directory'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--at', type=int, choices=(100, 150), default=100)
    parser.add_argument('--defer-one-turn', action='store_true',
                        help='Run one ordinary turn before attaching the native observer')
    parser.add_argument('--boundary-only', action='store_true',
                        help='Read native Builder rosters at inactive boundaries without attaching callbacks')
    replay(**vars(parser.parse_args()))
