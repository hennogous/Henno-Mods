"""Generate an offline comparison and readable report from copied site facts."""
import argparse
import hashlib
import json
from pathlib import Path

from evaluator import review

HERE = Path(__file__).resolve().parent
PROFILES = {'balanced': dict(production=1, gold=0.5, culture=1),
            'culture': dict(production=1, gold=0.5, culture=2),
            'production': dict(production=1, gold=0.25, culture=0.5)}


def bundle(plan, site):
    if plan is None:
        return 'Quote/readiness needed'
    stages = [str(s) for s in plan if not site['existing_buildings'].get(str(s))]
    names = {'2': 'Workshop', '3': 'Tailor', '4': 'Fashion House'}
    result = ([] if site['quarter']['exists'] else ['Quarter']) + [names[s] for s in stages]
    return ', '.join(result) or 'Retain'


def summarize(result, site):
    best = result['best']
    return dict(id=site['id'], score=best['review_utility'] if best else None,
        plan=bundle(best['plan'] if best else None, site),
        action=result['preferred_action'], base_goal=result['base_goal_status'], cost=best['construction_cost'] if best else None,
        yields=best.get('incremental_modelled_yields', {}) if best else {},
        materials=best['materials'] if best else {}, unknowns=best['unknowns'] if best else result['plans'][0]['unknowns'],
        services=best['services'] if best else [])


def generate(packet):
    cases, rules = packet['sites'], packet['rules']
    results = [review(s, rules) for s in cases]
    scenarios = {}
    for horizon in (40, 80, 120):
        for profile, weights in PROFILES.items():
            for scale in (0.5, 1, 1.5):
                key = f'{horizon}:{profile}:{scale:g}'
                scenarios[key] = [summarize(review(s, rules, horizon=horizon, weights=weights, cost_scale=scale), s) for s in cases]
    future = []
    target = next(s for s in cases if s['id'].startswith('shadow110:') and s['identity']['plot'] == 2189)
    for horizon in (80, 120):
        for cost in (120, 200, 320):
            branch = dict(key='conditional:3:131073:2188:harbor', owner=3, city=131073, plot=2188,
                district='DISTRICT_HARBOR', building='BUILDING_LIGHTHOUSE', functioning=True, district_functioning=True,
                population=7, ready_turn=20, cost=cost, maintenance=1, ordinary_yields={'gold': 3}, conflict=False)
            result = review(target, rules, horizon=horizon, future=branch)
            future.append(dict(horizon=horizon, customer_cost=cost, result=summarize(result, target)))
    return dict(schema=1, scope=packet['scope'], rules=rules, sources=packet['sources'],
                cases=cases, default_results=results, scenarios=scenarios, conditional_harbor=future,
                native_adjustments_produced=False)


def markdown(data):
    cases = {s['id']: s for s in data['cases']}
    summaries = data['scenarios']['80:balanced:1']
    out = ['# First offline Tailors site review', '', '3 November 2026. First implementation of the fresh site planner.', '',
        '**44 captured Tailors cases: six new-site alternatives in one city and 38 existing Quarters.** '
        '41 support a partial numerical review; three unfinished Quarters need remaining-production information. '
        'No game, native hook, installed mod or gameplay rule was changed.', '',
        'The first mechanics profile is Tailors only. The engine supports explainable investment bundles; '
        'Bakers and the other Quarters need separately checked profiles. It imports no retired planner or tuning policy.', '',
        '## What the numbers mean', '',
        'These are **partial scenario values**, not actual profit, native Q8 utility or calibrated empire value. '
        'Default: 80 future turns, Production1 / Gold0.5 / Culture1. Captured district quotes are used where present; '
        'unquoted building costs use current nominal costs. The CSC Gold companion is assumed enabled. '
        'Construction is serial at constant captured city production, '
        'with no additional queue delay. Future unlock availability is an explicit assumption.', '',
        'Existing Quarter benefits are subtracted before scoring upgrades. Retain/defer has value0. '
        'Population, materials and customers remain fixed in this first forecast. Positive and negative missing terms '
        'mean this is neither an upper nor lower bound. No review value can be sent to the native bridge.', '',
        '```mermaid', 'flowchart TD', '  F["Copied facts with source hashes"] --> L["Separate yield and cost ledgers"]',
        '  A["Declared horizon, timing and weights"] --> L', '  L --> P["Compare building bundles with retain or defer"]',
        '  P --> U["Show unpriced effects and conditional branches"]', '```', '',
        '## Six new sites: a genuine tie on observed current relationships', '',
        'All six belong to captured AI3/city131073 at turn110. None has owned matching Base or Specialty '
        'supply or an existing matching customer. Dyes beside2114/2116/2189 belong to another player; they '
        'are not credited. Plot2338 has one river edge, below the two-edge Production step. '
        'All six cover a Farm; lost worked yields and alternative land use remain unpriced.', '',
        '| Plot | Base / Specialty | River edges | Distinct future customer footprints | Best reviewed bundle | Partial value |',
        '|---|---|---:|---|---|---:|']
    for s, r in zip(data['cases'], summaries):
        if s['quarter']['exists']:
            continue
        harbor = sum(f['native_potential'].get('DISTRICT_HARBOR') is True for f in s['future_footprints'])
        land = sum(any(f['native_potential'].get(k) is True for k in ('DISTRICT_COMMERCIAL_HUB','DISTRICT_HOLY_SITE','DISTRICT_THEATER'))
                   for f in s['future_footprints'])
        out.append(f'| {s["identity"]["plot"]} | 0 / 0 | {s["river_edges"]} | {harbor} Harbor, {land} land | {r["plan"]} | {r["score"]:.2f} |')
    out += ['', 'Retain/defer beats starting all six under the quantified present-relationship scenario. '
        'That is not a verdict that these cities should never build a Quarter. Exports, Services, future customers '
        'and alternative uses need their own estimates. Different district types on the same future plot are '
        'alternatives, not multiple guaranteed customers. Native plot potential is not immediate city permission.', '',
        '## Existing Quarters: best local upgrade under the default assumptions', '',
        'Each row compares building bundles with retaining that same observed Quarter. Rows are sorted by identity, '
        '**not ranked across different cities or historical worlds**. Only additional buildings appear in the bundle. '
        'Fashion House requires Workshop, not Tailor. A zero value means retain; missing repair quotes remain unscored.', '',
        '| Capture | Player / city | Plot | Best additional bundle | Partial incremental value |', '|---|---|---:|---|---:|']
    for r in summaries:
        s = cases[r['id']]
        if not s['quarter']['exists']:
            continue
        i = s['identity']; value = 'Unpriced' if r['score'] is None else f'{r["score"]:.2f}'
        out.append(f'| {i["world"]} | {i["player"]} / {i["city"]} | {i["plot"]} | {r["plan"]} | {value} |')
    out += ['', '## Sensitivity: the assumptions can change the preferred investment', '',
        'These are different evaluations of the same copied facts. They are not simulated or observed AI outcomes. '
        'Culture emphasis changes its weight from1 to2. The cost multiplier affects unquoted building costs; '
        'a captured district quote stays fixed.', '',
        '| Case | 40 turns | 80 turns | 120 turns | Culture emphasis,80 | 1.5x unquoted costs,80 |', '|---|---|---|---|---|---|']
    ids = ['candidate150:p1:c393221:TAILORS:2165', 'reference150:p3:c65536:TAILORS:2562',
           'reference150:p5:c65536:TAILORS:1683']
    for identity in ids:
        s = cases[identity]; cells = []
        for key in ('40:balanced:1','80:balanced:1','120:balanced:1','80:culture:1','80:balanced:1.5'):
            r = next(r for r in data['scenarios'][key] if r['id'] == identity)
            cells.append(r['plan'] + (f' ({r["score"]:.1f})' if r['score'] is not None else ''))
        out.append('| '+s['name'].removeprefix('LOC_CITY_NAME_').replace('_',' ').title()+' | '+' | '.join(cells)+' |')
    out += ['', '## A priced conditional customer branch', '',
        'At actual new-site2189, the capture records Harbor plot potential at2188. This branch **assumes** '
        'Harbor/Lighthouse completion at relative turn20, ordinary customer Gold3/turn, maintenance1/turn and '
        'total customer investment120/200/320 Production. Those are review estimates, not captured quotes, '
        'commitments, available capacity or confirmed unlocks. The branch pays its customer cost and maintenance '
        'once and adds its declared ordinary yields alongside the CSC relationships. '
        'Even when this partial value becomes positive, the site still lacks the owned Base path '
        'required by our planning ambition; that unresolved goal is shown separately.', '',
        '| Horizon | Customer cost assumption | Best bundle | Partial value | Choice versus defer |', '|---:|---:|---|---:|---|']
    for entry in data['conditional_harbor']:
        r = entry['result']; out.append(f'| {entry["horizon"]} | {entry["customer_cost"]} | {r["plan"]} | {r["score"]:.2f} | {r["action"]} |')
    out += ['', 'Future materials have a separate conditional work-cost/completion input. They require an owned '
        'mapped footprint and explicit conflict assessment; illegal or resource-covering customer promises are '
        'rejected. Unspecified future work gets no free improvement or Service credit.', '',
        '## Mechanics and unresolved value', '',
        '- Ordinary customer transactions remain separate from material-gated Services. Base+customers can beat '
        'Both without useful customers; there is no Both-or-+4 admission rule.',
        '- Working supply is independent of whether a citizen works the material tile. Producer supply benefits '
        'can apply while the extra tile income is unworked or unknown; the latter is not counted as realised income.',
        '- Market and Temple are separate sales even in one city. Stage4 rounds each customer city’s population '
        'before adding branches. Current SQL uses Stage3 engine coefficient0.105; this profile does not substitute '
        'the design display0.1 or claim exact displayed-yield reproduction.',
        '- Service paths are shown, but their strategic value is unpriced by default. Specialist allocation, '
        'trade demand, amenities, growth feedback, policies, competing military/economic work and native-score '
        'overlap are also unpriced. The review cannot establish overall empire benefit.',
        '- Historical captures include earlier treatments. These are current-mechanics re-evaluations of copied '
        'facts, not clean current-rules games or causal comparisons. Source worlds and player/city identities stay separate.',
        '- The Sydney native mechanism capture lacks a resource-type catalogue, customer buildings and river-edge '
        'counts. It is not silently joined to a different world to manufacture a site-quality result.', '',
        '## Implementation and verification', '',
        '`project/tools/ai_site_planner/` contains the independent evaluator, fact extractor, copied fixtures and '
        'report generator. Focused tests cover ordinary sales without Base, distinct customer branches, per-customer '
        'rounding, unworked supply, industry intensity, future investment costs/timing, footprint conflicts, '
        'retaining sunk benefits, missing repair/production data and all44 captured cases.', '',
        'The tool produces JSON, this Markdown and an [interactive comparison](https://hennogous.github.io/Henno-Mods/ai/static/site-planner-review.html). The HTML selects '
        'among27 evaluations computed by the same Python model; it does not implement a second scoring engine.', '',
        'The next review should decide which missing effects or assumptions can change a choice, then extend the '
        'mechanics coverage and collect the specific missing facts. Native utility conversion and deployment '
        'remain the next roadmap phase.', '', '## Source records', '']
    for source in data['sources']:
        out.append(f'- `{source["id"]}`: SHA-256 `{source["sha256"]}`; locator `{source["locator"]}`.')
    out += ['', 'Current mechanics source snapshots (LF-normalized UTF-8 SHA-256):', '']
    for source in data['rules']['primary_sources']:
        out.append(f'- `{source["path"]}`: `{source["sha256_lf"]}`.')
    out += ['', '[Planner topic](../../civ6-ai/topics/csc/site-planner.md) · [Current roadmap](../../civ6-ai/roadmap.md)', '']
    return '\n'.join(out)


def standalone(data):
    payload = json.dumps(dict(cases=data['cases'], scenarios=data['scenarios']), ensure_ascii=False).replace('<', '\\u003c')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="ai-handbook" content="1"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tailors site review</title><style>body{font:16px system-ui;margin:2rem auto;max-width:1150px;padding:0 1rem;background:#faf8f2;color:#24302d}h1{font-size:2rem}label{display:inline-grid;margin:0 1rem 1rem 0;gap:.3rem}select{font:inherit;padding:.4rem}table{border-collapse:collapse;width:100%;background:white}td,th{text-align:left;border-bottom:1px solid #ddd;padding:.6rem}button{font:inherit;background:none;border:0;text-decoration:underline;color:#16635c;cursor:pointer}.scroll{overflow:auto}.note{background:#ece6d7;padding:1rem;border-radius:.5rem}pre{white-space:pre-wrap;font-size:14px}#facts{padding:1rem;background:white}small{color:#54675e}</style>
<h1>Tailors site and investment review</h1><p>44 copied historical cases. Explore how declared assumptions change a partial comparison.</p>
<p class="note">These values are review estimates, not native AI scores or full profit. Services, trade, growth, competing work and other unpriced effects can change the result. Retain/defer is 0. No game is controlled by this page.</p>
<label>Horizon<select id="h"><option>40</option><option selected>80</option><option>120</option></select></label>
<label>Value emphasis<select id="p"><option value="balanced">Production 1 / Gold 0.5 / Culture 1</option><option value="culture">Culture 2</option><option value="production">Production focus</option></select></label>
<label>Unquoted building costs<select id="c"><option>0.5</option><option selected>1</option><option>1.5</option></select></label>
<label>Cases<select id="g"><option value="all">All cases (identity order)</option><option value="new">Six new sites</option><option value="existing">Existing Quarters</option></select></label>
<p><small>Compare alternatives within the same world/player/city. Cross-city rows are not a global ranking.</small></p>
<div class="scroll"><table><thead><tr><th>Case</th><th>Plot</th><th>Best additional bundle</th><th>Partial value</th><th>Modeled action</th></tr></thead><tbody id="rows"></tbody></table></div><h2>Selected case facts</h2><div id="facts">Select a case to inspect its materials, customers and missing information.</div>
<script>const data=DATA;const {h,p,c,g,rows,facts}=Object.fromEntries(['h','p','c','g','rows','facts'].map(id=>[id,document.getElementById(id)]));
const byId=Object.fromEntries(data.cases.map(s=>[s.id,s]));let current=[],selected=null;
const actionNames={retain_or_defer:'Retain / defer',review_upgrade:'Review upgrade',review_investment:'Review investment',review_only_missing_base_path:'Base path still missing'};
function visible(s){return !(g.value==='new'&&s.quarter.exists||g.value==='existing'&&!s.quarter.exists)}
function draw(){current=data.scenarios[h.value+':'+p.value+':'+c.value];rows.replaceChildren();for(const r of current){const s=byId[r.id];if(!visible(s))continue;const tr=document.createElement('tr');const td=document.createElement('td');const b=document.createElement('button');b.textContent=s.identity.world+' / P'+s.identity.player+' / C'+s.identity.city;b.onclick=()=>show(r.id);td.append(b);tr.append(td);for(const v of [s.identity.plot,r.plan,r.score===null?'Needs information':r.score.toFixed(2),actionNames[r.action]]){const cell=document.createElement('td');cell.textContent=v;tr.append(cell)}rows.append(tr)}if(selected&&visible(byId[selected]))show(selected);else{selected=null;facts.textContent='Select a case to inspect its materials, customers and missing information.'}}
function append(tag,text,parent=facts){const e=document.createElement(tag);e.textContent=text;parent.append(e);return e}
function list(title,items){append('h4',title);const ul=append('ul','');for(const text of items)append('li',text,ul)}
function show(id){selected=id;const s=byId[id],r=current.find(x=>x.id===id);facts.replaceChildren();append('h3',s.name.replace('LOC_CITY_NAME_','')+' · plot '+s.identity.plot);
 append('p','Best additional bundle: '+r.plan+'. Partial value: '+(r.score===null?'not priced':r.score.toFixed(2))+'. '+actionNames[r.action]+'.');
 if(r.cost!==null)append('p','Additional construction cost in this estimate: '+r.cost+' Production. Horizon: '+h.value+' turns.');
 const materials=s.materials.filter(m=>m.base||m.specialty);list('Materials',materials.length?materials.map(m=>m.resource.replace('RESOURCE_CSC_','').replace('RESOURCE_','')+' at '+m.plot+': '+(m.owned?'owned':'another owner')+', '+(m.working?'working supply':'not working supply')+', '+(m.worked===null?'citizen work unknown':m.worked?'worked by a citizen':'not worked by a citizen')):['No matching material observed.']);
 list('Customers',s.customers.length?s.customers.map(c=>c.district.replace('DISTRICT_','').replaceAll('_',' ')+' at '+c.plot+': '+(c.building?c.building.replace('BUILDING_','').replaceAll('_',' '):'required building absent')+', population '+(c.population??'unknown')+'.'):['No matching adjacent customer district observed.']);
 list('Service paths',r.services.map(s=>s.name.replaceAll('_',' ')+': '+({missing_path:'material/customer path incomplete',conditional_unlock:'unlock not established',available_in_plan:'available under the stated plan assumptions'}[s.state])));
 list('Unpriced or unresolved',r.unknowns);const details=append('details','');append('summary','Copied facts and model details',details);append('pre',JSON.stringify({materials:s.materials,customers:s.customers,possibleFutureFootprints:s.future_footprints,additionalBundle:r.plan,incrementalModelledYields:r.yields,constructionCost:r.cost,baseGoal:r.base_goal,services:r.services},null,2),details)}
for(const id of ['h','p','c','g'])document.getElementById(id).addEventListener('change',draw);draw();</script></html>'''.replace('DATA', payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path, default=HERE/'fixtures/captured_sites.json')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--markdown', type=Path)
    args = parser.parse_args()
    packet = json.loads(args.fixture.read_text(encoding='utf-8'))
    data = generate(packet)
    data['fixture_sha256'] = hashlib.sha256(args.fixture.read_bytes()).hexdigest()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/'review.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    text = markdown(data)
    (args.output/'review.md').write_text(text, encoding='utf-8')
    (args.output/'review.html').write_text(standalone(data), encoding='utf-8')
    if args.markdown:
        args.markdown.write_text(text, encoding='utf-8')
    print(json.dumps(dict(cases=len(data['cases']), scenarios=len(data['scenarios']),
                          conditional_branches=len(data['conditional_harbor']), output=str(args.output))))


if __name__ == '__main__':
    main()
