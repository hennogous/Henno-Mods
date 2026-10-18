"""Publish the native 4/5/6 study with service-stage distinctions."""
import argparse
from pathlib import Path
from statistics import mean
from analyze import read


def report(folder, target):
    data = read(folder / 'analysis.json'); maps = data['maps']
    assert len(maps) == 15
    rows = data['opportunities']; quarters = list(maps[0]['resolved_definitions'])
    lines = ['# CSC native luxury diversity experiment — 16 October 2026', '',
             'Fifteen native turn-1 maps compare 4, 5 and 6 land luxury types per continent, using the same five map/game seed pairs and leader rosters. CSC and official content only; vanilla Abundant, Online, Prince, Continents.lua at Small size (74 × 46), six majors and nine city states. Animal resources enabled; unused modded resources cleaned. No turns advanced and no native saves required.', '',
             'The private test script passes `LuxuriesPerRegion` to the installed GS ResourceGenerator. All other generation decisions use the installed game scripts. Read-only phase captures and RNG traces were added during the batch for offline calibration. The five four-type controls reproduce every earlier vanilla-Abundant terrain, feature and resource tile exactly.', '',
             'Background generation was tested while Henno confirmed Civ was backgrounded and he continued working. FireTuner performed setup, generation, turn-1 export and return to menu without mouse or keyboard input. Window focus could not be independently observed because Computer Use access to Civ was denied; this does not certify that loading can never steal focus on other configurations.', '',
             '## Diversity and continental coverage', '',
             '| Configured types | Named continents | Mean land luxury types / continent | Mean luxury tiles / continent | Mean industries with Base sites / continent | Mean industries with both-class sites / continent |',
             '|---:|---:|---:|---:|---:|---:|']
    for k in (4, 5, 6):
        regions = [c for m in maps if m['luxury_types_per_continent'] == k for c in m['continents'] if c['id'] != -1]
        values = [k, len(regions), f"{mean(c['land_luxury_types'] for c in regions):.2f}", f"{mean(c['land_luxury_tiles'] for c in regions):.1f}",
                  f"{mean(sum(q['common_clearable_base'] > 0 for q in c['quarters']) for c in regions):.2f} / 8",
                  f"{mean(sum(q['common_clearable_both'] > 0 for q in c['quarters']) for c in regions):.2f} / 8"]
        lines.append('| ' + ' | '.join(map(str, values)) + ' |')
    lines += ['', 'Diversity is measured after starting-position adjustment and counts land luxuries. It can differ from the constructor target. More types also divide the luxury occurrence budget among more types; this is not simply an abundance increase. Industry coverage means at least one candidate with ordinary future clearing allowed, not guaranteed service operation.', '',
              '## Material opportunities', '',
              'Mean candidate tiles per whole map, with ordinary future clearing allowed. Base includes both-class sites. Stages 2–3 can use Base supply; Stage 4 requires both classes. Improvements, research, customer districts and other service requirements still apply.', '',
              '| Quarter | Base, 4 | Base, 5 | Base, 6 | Both, 4 | Both, 5 | Both, 6 | Continents with Base, 4 / 5 / 6 | Continents with both, 4 / 5 / 6 |',
              '|---|---:|---:|---:|---:|---:|---:|---|---|']
    for q in quarters:
        vals = [q.title()]
        for key in ('common_clearable_base', 'common_clearable_both'):
            for k in (4, 5, 6): vals.append(f"{mean(r[key] for r in rows if r['quarter'] == q and r['group'] == f'luxuries-{k}'):.1f}")
        for metric in ('common_clearable_base', 'common_clearable_both'):
            coverage = []
            for k in (4, 5, 6):
                regions = [c for m in maps if m['luxury_types_per_continent'] == k for c in m['continents'] if c['id'] != -1]
                count = sum(next(r for r in c['quarters'] if r['quarter'] == q)[metric] > 0 for c in regions)
                coverage.append(f'{count}/{len(regions)}')
            vals.append(' / '.join(coverage))
        lines.append('| ' + ' | '.join(vals) + ' |')
    full_base = []
    for k in (4, 5, 6):
        regions = [c for m in maps if m['luxury_types_per_continent'] == k for c in m['continents'] if c['id'] != -1]
        full_base.append(f"{sum(all(q['common_clearable_base'] > 0 for q in c['quarters']) for c in regions)}/{len(regions)}")
    lines += ['', '## Reading the result', '',
              'Continents with at least one ordinarily clearable Base-supported site for **every** Quarter: ' + ', '.join(f'{k} types: **{n}**' for k, n in zip((4, 5, 6), full_base)) + '.', '',
              'Six types is a promising next candidate for broader seed testing. In this sample Apothecaries gain Base coverage on all fifteen continents, while Goldsmiths still lack Base opportunities on three. Goldsmiths have no both-class sites anywhere in the six-type maps, even under the raw passable-land filter. More luxury diversity improves regional breadth but does not reliably create nearby pairs of the two classes.', '',
              'Keep Stage 4 rarity as a separate design choice. A future light-touch audit could focus on missing Base materials before considering any both-class adjacency repair. No production resource intervention has been installed.', '',
              '## Interpretation limits', '',
              'This is a paired five-seed sample, not a guarantee for every map script, map size or resource pack. Changing the number of types changes subsequent random draws and starting adjustments, so individual resource layouts are not nested additions. The paired-map CSV records any downstream feature differences; terrain and continent IDs are checked separately.', '',
              'A candidate can use material sources across a continent border. Candidate tiles can share sources and are not independent settlements or simultaneous Quarter builds. Hidden strategics and designed Hills/Woods/Rainforest materials count. Bakers/Tailors use runtime material tags; the other six use their individual design pages. Goldsmiths use Diamonds/Jade; the older overview’s additional Pearls are excluded from the main comparison.', '',
              'Rare Stage 4 support is not automatically a defect. This experiment supplies evidence before choosing any production map intervention. CSC’s gameplay and installed game/Workshop files were unchanged.', '',
              '## Viewer and raw results', '',
              '- Open `project/tools/map_lab/viewer.html` or the standalone `project/snapshots/map-lab/index.html`. The viewer retains the original fifteen maps and adds these fifteen native experiments.',
              '- Select a 4/5/6 luxury resource setup, then use Continent, Opportunity supply and Continent comparison. Base/both industry coverage follows the clearing filter.',
              '- Raw evidence: `project/snapshots/map-lab/luxury-study/`; detailed tables: `continent-opportunities.csv`, `continent-inventory.csv`, `paired-map-comparison.csv`; verification: `validation.json`.',
              '- Offline reference captures and measured API/RNG mismatches: `project/snapshots/map-lab/native-calibration/`. Recorded-draw replay is a diagnostic aid, not an implementation of Civ’s RNG or a new-terrain generator.', '']
    target.parent.mkdir(parents=True, exist_ok=True); target.write_text('\n'.join(lines), encoding='utf-8')
    print(target)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True); p.add_argument('--report', type=Path, required=True)
    a = p.parse_args(); report(a.output, a.report)
