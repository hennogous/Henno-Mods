"""Publish the completed material survey as durable collaborator documentation."""
import json
from pathlib import Path
from statistics import mean

ROOT=Path(__file__).resolve().parents[3]
OUT=Path.home()/'Desktop/Codex/csc-map-material-opportunities-20261016'
DEST=ROOT/'project/docs/research/mods/csc-map-material-opportunities-20261016.md'
GROUPS=['vanilla-abundant','tar-abundant','tar-truly-abundant']
LABELS=['Vanilla Abundant','TAR with Abundant','TAR with Truly Abundant']

def main():
    a=json.loads((OUT/'analysis.json').read_text());v=json.loads((OUT/'validation.json').read_text())
    assert v['status']=='passed' and v['maps']==15 and len(a['opportunities'])==120
    assert all(r['same_terrain']==r['same_features']==r['same_land_water']==3404 for r in a['paired_terrain_comparisons'])
    defs=json.loads((OUT/'materials.json').read_text());qs=list(defs);rs=a['opportunities']
    def values(q,g,key='land_both'):return [next(r[key] for r in rs if r['quarter']==q and r['group']==g and r['map']==i) for i in range(1,6)]
    def raw_link(name):return (OUT/name).as_posix()
    text=['# CSC material opportunity comparison 16 October 2026','',
    'Fifteen fresh maps compare vanilla Abundant, Truly Abundant Resources (TAR) enabled with the same Abundant setting, and TAR enabled with its Truly Abundant preset. CSC remains enabled in all three groups. The five paired seeds have identical terrain and features across setups; their resource layouts differ.','',
    '**Truly Abundant increases the mean number of both-material sites for all eight Quarters. Enabling TAR while retaining Abundant mostly redistributes sites and does not consistently increase them.** Some zero counts come from an entire material class being absent: Tailors have no specialty resources on maps 1 and 5 in any group; Stonemasons have none on map 5. AI placement guidance cannot produce a connection to a class that the map does not contain.','',
    'Counts below are distinct passable land tiles adjacent to at least one base-material source and one specialty-material source. They measure geography before ownership, city reach, research and improvements. All generated resources count, including unrevealed strategic deposits. A separate filter for ordinary placement blockers appears below.','',
    'Hills count as adjacent base material for Stonemasons and Blacksmiths; Woods/Rainforest count for Carpenters. The Quarter site itself does not supply its own adjacency. One neighboring tile can match both classes through its terrain and resource; the CSV also gives counts requiring two distinct supporting tiles. Nearby candidate tiles can share sources, so these are tile opportunities rather than independent settlements.','']
    for group,label in zip(GROUPS,LABELS):
        text+=['## '+label,'','| Quarter | Map 1 | Map 2 | Map 3 | Map 4 | Map 5 | Mean |','|---|---:|---:|---:|---:|---:|---:|']
        for q in qs:
            nums=values(q,group);text.append('| '+q.title()+' | '+' | '.join(map(str,nums))+f' | {mean(nums):.1f} |')
        text+=['']
    text+=['## Missing material classes','',
    'These absences persist across all three resource settings for the paired seeds. They explain the listed zero counts without relying on AI behaviour.','',
    '| Quarter | Maps | Missing specialty resources |','|---|---|---|',
    '| Tailors | 1 and 5 | Dyes, Silk and Silver |',
    '| Stonemasons | 5 | Gypsum and Marble |',
    '| Goldsmiths using the individual design page | 4 | Diamonds and Jade |','',
    'Other zero counts can occur despite both classes being present, because their sources do not have a common adjacent land tile. Source counts and resource inventories are retained in the data.','',
    '## Effect of terrain and feature materials','',
    'The following means compare the complete definition against resource sources alone. This isolates the contribution of Hills or Woods/Rainforest to the geographic count.','',
    '| Quarter | Vanilla resources only | Vanilla including terrain/features | TAR Abundant resources only | TAR Abundant including terrain/features | Truly Abundant resources only | Truly Abundant including terrain/features |',
    '|---|---:|---:|---:|---:|---:|---:|']
    for q in ('STONEMASONS','CARPENTERS','BLACKSMITHS'):
        cells=[]
        for group in GROUPS:cells.extend([f'{mean(values(q,group,"resource_only_both")):.1f}',f'{mean(values(q,group)):.1f}'])
        text.append('| '+q.title()+' | '+' | '.join(cells)+' |')
    text+=['','## Sites with ordinary placement blockers removed','',
    'The common clearable-site comparison excludes occupied districts, nonremovable features other than Gathering Storm floodplains, and luxury or strategic resources on the candidate tile. Bonus-resource removal and normal feature clearing are allowed after research. The same filter applies to every setup. It remains a geographic estimate rather than a complete native city-specific eligibility check.','',
    '| Quarter | Vanilla Abundant mean | TAR Abundant mean | TAR Truly Abundant mean |','|---|---:|---:|---:|']
    for q in qs:text.append('| '+q.title()+' | '+' | '.join(f'{mean(values(q,g,"common_clearable_both")):.1f}' for g in GROUPS)+' |')
    text+=['',
    'The CSV additionally reports a harvest-aware count using the loaded rules. TAR makes luxury and strategic resources harvestable, so those counts can exceed the common-filter counts. Keeping this variant separate avoids attributing the effect of harvesting rules solely to distribution.','',
    '## Material definitions','',
    'Bakers and Tailors resolve to the actual loaded CSC material tags, including Flax and enabled animal materials. The six unimplemented Quarters use their individual design pages. The complete resource identifiers and feature/terrain rules are in the [material definitions](../../../tools/map_survey/materials.json).','',
    '| Quarter | Definition source | Terrain or feature sources |','|---|---|---|']
    for q,rules in defs.items():
        source=rules['source'];link=source if source.startswith('runtime') else '['+q.title()+' design](../../../../'+source+')'
        terrain='Hills' if rules['base'].get('hills') else 'Woods and Rainforest' if rules['base'].get('features') else 'None'
        text.append('| '+q.title()+' | '+link+' | '+terrain+' |')
    text+=['',
    'Carpenters use Copper and Iron as well as Woods/Rainforest for base materials; Aluminium, Amber, Dyes, Silk and Silver are specialty materials. The overview table and incomplete SQL stub contain older lists.','',
    'Goldsmiths use Diamonds and Jade from their individual page. The overview additionally lists Pearls; including Pearls gives the alternative counts below.','',
    '| Goldsmiths including Pearls | Map 1 | Map 2 | Map 3 | Map 4 | Map 5 |','|---|---:|---:|---:|---:|---:|']
    for group,label in zip(GROUPS,LABELS):
        vals=[next(m['goldsmiths_with_pearls_land_both'] for m in a['maps'] if m['group']==group and m['map']==i) for i in range(1,6)]
        text.append('| '+label+' | '+' | '.join(map(str,vals))+' |')
    text+=['','## Setup and verification','',
    '- Gathering Storm, Small Continents (74×46), six major civilizations, nine city states, Prince difficulty, Online speed and Ancient Era starts. No turns advance after loading turn 1.',
    '- CSC and official content throughout. TAR is disabled for vanilla Abundant, enabled for TAR Abundant, and enabled for TAR Truly Abundant. Resource values are respectively 3, 3 and 45. Other community mods are disabled. CSC animal materials and resource cleanup use their current enabled defaults.',
    '- Each seed pair reuses the same six leader identities across all three setups. All 3,404 terrain and feature values match within every pair.',
    '- All 15 maps and 51,060 tile records passed coverage, coordinate, reciprocal-neighbor, setting and source checks. All 120 Quarter/map rows passed count invariants. Gameplay SQL errors: zero. All 111 recorded CSC gameplay/configuration files and TAR files remain unchanged.',
    '- The initial edge-neighbor export was corrected to enumerate all six native directions. The first map retains its original dump and a normalization record; all non-neighbor fields are unchanged, and the final coordinate graph matches all fourteen other native exports.',
    '- The first two maps were saved before the user chose numbers-only output. Later maps retain tile data, settings, logs and counts without manual game saves. Original mod preferences and native auto-start were restored at the final main menu.','',
    '| Map | Map seed | Game seed |','|---|---:|---:|']
    for i in range(1,6):text.append(f'| {i} | {830001+i*101} | {940001+i*103} |')
    text+=['','## Data and tools','',
    '- [All 120 Quarter/map counts and filters]('+raw_link('quarter-opportunities.csv')+').',
    '- [Individual candidate tiles and material sources]('+raw_link('opportunity-sites.csv')+').',
    '- [Map resource inventories and resolved definitions]('+raw_link('analysis.json')+').',
    '- [Paired terrain comparison]('+raw_link('paired-map-comparison.csv')+') and [validation result]('+raw_link('validation.json')+').',
    '- [Collection and analysis tools](../../../tools/map_survey/README.md).','']
    content='\n'.join(text);DEST.write_text(content,encoding='utf-8');(OUT/'final-report.md').write_text(content,encoding='utf-8')
    compact=['| Quarter | Vanilla Abundant | TAR + Abundant | TAR + Truly Abundant |','|---|---|---|---|']
    for q in qs:compact.append('| '+q.title()+' | '+' | '.join(', '.join(map(str,values(q,g))) for g in GROUPS)+' |')
    (OUT/'compact-table.md').write_text('\n'.join(compact)+'\n',encoding='utf-8')
    print(DEST);print('\n'.join(compact))

if __name__=='__main__':main()
