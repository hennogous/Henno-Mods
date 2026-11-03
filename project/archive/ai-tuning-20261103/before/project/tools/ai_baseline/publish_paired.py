"""Publish a verified completed paired AI baseline as a durable project report."""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def fraction(n,d):return f'{n}/{d} ({n/d:.0%})' if d else '0/0'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output
    data=read(out/'analysis.json');validation=read(out/'validation.json');prefs=read(out/'preferences-restored.json')
    assert data['completed_games']==10 and len(validation['games'])==10 and validation['snapshots']==110
    assert prefs['verified'] and prefs['fresh_native_check'] and prefs['main_menu']
    for sample in [*data['groups'].values(),*data['games']]:
        for q in sample['quarters'].values():
            for key in ('completed','base','both'):q.setdefault(key,0)
    labels={'vanilla-standard':'Vanilla Standard','tar-standard':'TAR + Standard'}
    text=['# CSC AI baseline: five vanilla and five TAR Standard games','',
        '**Complete — 17 October 2026.** All ten real Civ games reached exactly turn 250 on Online speed. The five vanilla worlds reproduce the earlier Standard captures; the other five use Truly Abundant Resources with the same Standard resource setting, seeds and leaders. No AI tuning was applied.','',
        'This is the current baseline for improving AI use of the implemented Bakers’ and Tailors’ Quarters. Material access is especially relevant to Services; Quarters can still earn through goods sales without adjacent materials.','',
        '## Endpoint at turn 250','',
        '| Setup | Major cities | Completed Bakers | Bakers Base-only / Both | Completed Tailors | Tailors Base-only / Both |',
        '|---|---:|---:|---:|---:|---:|']
    for key,g in data['groups'].items():
        b,t=g['quarters']['BAKERS'],g['quarters']['TAILORS']
        text.append(f'| {labels[key]} | {g["totals"]["cities"]} | {b["completed"]} | {b["base"]-b["both"]} / {b["both"]} | {t["completed"]} | {t["base"]-t["both"]} / {t["both"]} |')
    text+=['','Base-only and Both are exclusive. Counts require adjacent revealed materials owned by the same player. They describe completed Quarters at the endpoint, not every placement event or every geographic opportunity. There are 776 completed Quarters across 598 major-city observations; six retain both owned material classes.','',
        '## Placement decisions when materials were available','',
        '| Setup | Quarter | Chose Base when Base was available | Chose Both when Both was available | Chose Base + Sales when that combination was available |',
        '|---|---|---:|---:|---:|']
    for key,g in data['groups'].items():
        for q,v in g['quarters'].items():
            text.append(f'| {labels[key]} | {q.title()} | {fraction(v.get("base_chosen_when_available",0),v.get("base_available",0))} | {fraction(v.get("both_chosen_when_available",0),v.get("both_available",0))} | {fraction(v.get("base_sales_chosen_when_available",0),v.get("base_sales_available",0))} |')
    text+=['','These alternatives were already owned and passed native plot placement checks in the most recent player-turn-start scan, at most one turn old. They do not include future purchases, affordability or every city production restriction. Tile yield, removal costs and other city plans can justify a different choice; these counts expose available material access rather than proving the best overall site.','',
        'Across both setups, the AI chose Base access in 153/287 Bakers placements (53%) and 24/62 Tailors placements (39%) when a Base-bearing alternative was recorded. Both-class Tailor choices had only four such observed opportunities across ten games, so that tiny denominator should not drive tuning.','',
        '## Material improvements and later sales districts','',
        '| Setup | Quarter | Improved adjacent Base plots | Improved adjacent Specialty plots | Later sales district chose Quarter adjacency when available |',
        '|---|---|---:|---:|---:|']
    losses=[]
    for key in labels:
        games=[g for g in data['games'] if g['group']==key]
        for q in ('BAKERS','TAILORS'):
            counts=[]
            for cat in ('base','spec'):
                rs=[r for g in games for r in g['improvement_comparison'] if r['quarter']==q and r['category']==cat and r['adjacent_to_quarter']]
                counts.append(fraction(sum(r['improved'] for r in rs),len(rs)))
            cs=[r for g in games for r in g['customer_choices'] if r['quarter']==q and r['comparable'] and r['adjacency_option']]
            text.append(f'| {labels[key]} | {q.title()} | {counts[0]} | {counts[1]} | {fraction(sum(r["adjacent"] for r in cs),len(cs))} |')
        losses.extend((g['game'],r['resource_plot']) for g in games for r in g['material_retention'] if not r['resource_retained'] and r['final_district'])
    text+=['','Improvement counts deduplicate material plots within each Quarter/player sample and exclude pillaged improvements. A material plot can support several Quarters. Specialty plots were improved much more frequently than Base plots. Some Base plots can also lie outside a city’s workable radius; the CSV retains that distinction and whether the relevant source building existed.','',
        f'{len(set(losses))} distinct originally owned adjacent material plots were later absent beneath a district for surviving same-owner Quarter relationships. The raw ledger distinguishes resource loss, ownership changes and the final district; it does not identify the AI’s reason for clearing the deposit.','',
        'The sales comparison excludes City Centers and requires a previous Quarter plus a fresh native plot-legal adjacency alternative. Repeated capture-related appearances of the same district plot/type are excluded from placement counts.','',
        '## Buildings and Services','',
        '| Setup | Quarter | Stage 2 / 3 / 4 buildings in completed Quarters |',
        '|---|---|---:|']
    for key,g in data['groups'].items():
        for q,v in g['quarters'].items():text.append(f'| {labels[key]} | {q.title()} | {v.get("stage2",0)} / {v.get("stage3",0)} / {v.get("stage4",0)} |')
    text+=['','Native supply activation properties at the endpoint show:','',
        '| Setup | Bakers Growth sources | Bakers Housing sources | Bakers Tourism sources | Tailors supply sources, all stages |',
        '|---|---:|---:|---:|---:|']
    for key,g in data['groups'].items():
        s=g['services'];tailors=sum(v for k,v in s.items() if 'TAILORS' in k)
        text.append(f'| {labels[key]} | {s.get("CSC_BAKERS_STAGE_2_EFFECT_GROWTH",0)} | {s.get("CSC_BAKERS_STAGE_3_EFFECT_HOUSING",0)} | {s.get("CSC_BAKERS_STAGE_4_EFFECT_TOURISM",0)} | {tailors} |')
    text+=['','These are source-city/stage activations at turn 250, not recipient hidden-building counts or a claim that a Service never activated earlier. Snapshot histories retain the intermediate properties. Native flags are authoritative; the service-opportunity CSV is a diagnostic model of civic, source-building, material and venue exposure, rather than a complete native requirement evaluator.','',
        'Base materials alone can support stage 2 and 3 Services. Specialty material and both-class placement are needed for stage 4, whose rarity remains an intentional part of the design. The baseline therefore supports examining Base placement, Base improvements and customer adjacency before trying to make Both-class sites ubiquitous.','',
        '## Individual maps','',
        '| Setup | Seed pair | Major cities | Bakers complete / Base-only / Both | Tailors complete / Base-only / Both |',
        '|---|---:|---:|---:|---:|']
    for g in data['games']:
        b,t=g['quarters']['BAKERS'],g['quarters']['TAILORS']
        text.append(f'| {labels[g["group"]]} | {g["paired_map"]} | {g["totals"]["cities"]} | {b["completed"]} / {b["base"]-b["both"]} / {b["both"]} | {t["completed"]} / {t["base"]-t["both"]} / {t["both"]} |')
    text+=['','## Reproduction and evidence','',
        '- Continents.lua, Small 74×46, six majors and nine city states, Gathering Storm, Online, Prince, ordinary victory conditions.',
        '- CSC production material pass v3, Bakers/Tailors scope, direct Tailor assistance; animals enabled, unused modded resource cleanup enabled, M&C disabled.',
        '- Vanilla Standard (2) in both groups; TAR enabled only in the second. Its separate Truly Abundant preset was not selected. TAR’s resource validity and harvest rules also apply during that group’s games.',
        '- Map seeds: 830102, 830203, 830304, 830405, 830506. Game seeds: 940104, 940207, 940310, 940413, 940516. Leader rosters repeat across the paired setups.',
        '- All five vanilla initial maps match the earlier captures across 13 fields on every one of their 3,404 tiles. TAR comparisons retain per-field differences; resources and resulting start locations may differ.',
        '- Read-only observer v3, complete district/improvement history and owned candidate scans. Continuous autoplay avoids returning human control at intermediate checkpoints.',
        '- Turn 1 plus frozen snapshots every 25 turns through 250: 110 snapshots. Endpoint means the beginning of turn 250 after 249 advances; intermediate snapshots are captured at the first major-player activation.',
        '- Ten initial and ten final native saves have verified SHA-256 checksums. Event prefixes, material counts, zero observer/Gameplay SQL errors and all 115 installed gameplay files passed verification.',
        '- The same observer v3 and installed gameplay were used for all valid games. Controller reconnect, return-player and save-preparation revisions are explicitly retained in controller-revisions.json; exact native commands are archived.',
        '- A fresh native read confirms Civ at its background main menu, all 141 original unique mod preference flags restored and auto-start false. The native API returns one duplicate mod entry, which is accounted for.',
        '',
        'The interrupted first controller trial, which returned human control every 25 turns and stalled on a diplomacy session at 50, is excluded entirely. Game 1 was regenerated from the same exact initial map and rerun continuously. No diplomatic response was submitted by the controller.',
        '',
        'Game 6’s final save was initially blocked by a disaster animation opened on return at 250. Closing that playback completed one capital’s automatic growth from 10 to 11 within the same turn. Quarter, plot, research, Service and event data were unchanged. The standardized benchmark census is retained; a separate settled census describes the saved state. Later final saves also clear visible playback and retain a separate save-state census. No extra turn or AI decision was requested.',
        '',
        'Raw evidence: `C:/Users/Shadow/Desktop/Codex/csc-ai-paired-standard-20261016/`. Key files are analysis.json, validation.json, preferences-restored.json, per-map-quarter-stats.csv, base_placement_choices.csv, choices.csv, customer_choices.csv, improvement_comparison.csv, improvement_timing.csv, material_retention.csv, service_opportunities.csv and the per-game turn snapshots, saves and logs.',
        '',
        'Source tools: [runner](../../../tools/ai_baseline/paired_standard.py), [observer](../../../tools/ai_baseline/paired_observer.lua), [analysis](../../../tools/ai_baseline/paired_analysis.py), [verification/reproduction instructions](../../../tools/ai_baseline/README.md).',
        '',
        'Five games per setup are a descriptive baseline. They do not establish causal AI understanding of CSC adjacency or statistical superiority of either resource setup. The earlier Standard-speed study used a different setup and boundary-neighbour enumeration and is retained as historical evidence. No AI optimisation has been applied yet.']
    target=ROOT/'project/docs/research/mods/csc-ai-paired-standard-20261016.md'
    report='\n'.join(text)+'\n';target.write_text(report,encoding='utf-8');(out/'final-report.md').write_text(report,encoding='utf-8')
    manifest={'status':'complete','completed_at':datetime.now().astimezone().isoformat(),'games':10,'turn':250,'snapshots':110,'native_saves':20,'installed_files_verified':115,'source_observer_version':3,'preferences':prefs,'report':str(target),'report_sha256':digest(target),'distinct_material_plots_replaced_by_district':len(set(losses))}
    (out/'final-verification.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('Published',target);print('Distinct material plots replaced by districts:',len(set(losses)))

if __name__=='__main__':main()
