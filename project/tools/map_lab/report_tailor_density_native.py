"""Publish the completed six-map native resource census without a game connection."""
import argparse
from collections import defaultdict
import json
from pathlib import Path

def read(path):return json.loads(path.read_text(encoding='utf-8'))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();batch=read(a.input/'batch.json');assert batch['status']=='complete' and batch['maps']==6
    assert read(a.input/'preferences-restored.json')['verified']
    stats=read(a.input/'resource-stats.json');assert len(stats)==12
    worlds=defaultdict(dict)
    for r in stats:worlds[(r['level'],r['map'])][r['quarter']]=r
    lines=['# Tailor density v4 — six fresh native maps, 17 October 2026','',
        'Three vanilla Standard maps and three vanilla Abundant maps, paired on three fresh seed pairs. CSC v4 ran automatically inside Civ during map initialization. Online/Prince, Small Continents (74×46), six majors/nine city states, animals enabled, unused-resource cleanup enabled, M&C off. CSC was the only active community mod; TAR and RH disabled. No autoplay or game saves.','',
        '## Placement opportunities','',
        'Counts are ordinarily clearable land tiles adjacent to mapped Base materials. Base-only excludes Specialty adjacency; both requires both material classes. Ownership, city reach, improvements and research are not filters. Neighbouring sites can share resource deposits.','',
        '| Resources | Map | Map seed / game seed | Bakers Base-only / both | Tailors Base-only / both | CSC copies added |',
        '|---|---:|---|---:|---:|---:|']
    for (level,n),qs in worlds.items():
        b,t=qs['BAKERS'],qs['TAILORS']
        lines.append(f"| {level} | {n} | {b['map_seed']} / {b['game_seed']} | {b['base_only']} / {b['both']} | {t['base_only']} / {t['both']} | {b['all_csc_added_copies']} |")
    lines+=['','## Material copies','',
        'Bakers and Tailors overlap through shared Flax; their totals must not be added together as distinct map resources. Quantity is read from native plots, not inferred from the number of deposits.','',
        '| Resources | Map | Bakers Base / Specialty copies | Tailors Base / Specialty copies | Added Bakers Base / Specialty | Added Tailors Base / Specialty |',
        '|---|---:|---:|---:|---:|---:|']
    for (level,n),qs in worlds.items():
        b,t=qs['BAKERS'],qs['TAILORS']
        lines.append(f"| {level} | {n} | {b['base_resource_copies']} / {b['spec_resource_copies']} | {t['base_resource_copies']} / {t['spec_resource_copies']} | {b['base_copies_added']} / {b['spec_copies_added']} | {t['base_copies_added']} / {t['spec_copies_added']} |")
    lines+=['','## Individual resource inventory','']
    for (level,n),qs in worlds.items():
        lines += [f'### {level} map {n}','']
        for q,r in qs.items():
            for kind in ('base','spec'):
                entries=', '.join(f"{name.removeprefix('RESOURCE_').removeprefix('CSC_').replace('_',' ').title()} {count}" for name,count in r[kind+'_inventory'].items())
                lines.append(f'- {q.title()} {kind}: {entries or "none"}.')
        lines.append('')
    lines+=['## Continental coverage','', '| Resources | Map | Continent instances | Bakers Base / both coverage | Tailors Base / both coverage | Tailor both-site clusters |','|---|---:|---:|---:|---:|---:|']
    for (level,n),qs in worlds.items():
        b,t=qs['BAKERS'],qs['TAILORS']
        lines.append(f"| {level} | {n} | {b['continents']} | {b['continents_with_base']} / {b['continents_with_both']} | {t['continents_with_base']} / {t['continents_with_both']} | {t['both_clusters']} |")
    lines+=['','## Verification and interpretation','',
        'All six maps stayed at turn1. The native audit confirms version4, successful automatic startup before UI, actual resource quantity1 for each addition, and the captured native eligibility for every placement. Original resources/quantities and other plot fields are preserved. Exact offline replay of native pre-pass inputs matches additions, palettes, continental counts and density targets. An independent census agrees with the audit. Installed gameplay/source pins and read-only controller transcripts pass. Original mod preferences and auto-start were restored and freshly verified; diagnostic capture was disabled.','',
        'The new seeds were not used in the previous five-map preview. Same-seed Standard/Abundant landscapes were checked separately; resource distribution and starting decisions may vary between levels. The density target is relative to each map after the original continental repair:2× Tailor Base-only and4× both, with an abundance-scaled minimum for zero both-class counts. Small site-count overshoots can occur because one deposit supports multiple candidate centers. Baker opportunities may benefit from shared Flax.','',
        'This measures material geography, not AI behavior or established Services. No AI tuning coefficients changed during the six-map experiment. Historical v3 worlds and prior AI tests remain separate.','',
        f'Evidence: `{a.input}`. Per-map maps, audits, native eligibility, resource inventories, logs and exact replay checks are retained; aggregate tables are resource-stats.json and resource-stats.csv.']
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'report':str(a.output),'maps':len(worlds),'stats_rows':len(stats)}))

if __name__=='__main__':main()
