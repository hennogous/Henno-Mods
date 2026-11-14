"""Closed no-CSC controls versus the completed treated planning campaign.

Native choice quotes are the common comparison phase. Controls additionally
have before-placement CACHE snapshots; neither is a forced fresh forecast.
Report coverage and actual terminal cohorts alongside cumulative foundations.
No claim of identical generated worlds or isolated district-slot causality.
"""
import argparse
import hashlib
import json
from pathlib import Path

from planning_results import analyse
from planning_campaign_results import stock_district


MAPS={'Continents':('continents250-01','continents250-01'),
      'Pangaea':('pangaea250-combined','pangaea250-01'),
      'Fractal':('fractal250-01','fractal250-01')}


def read_arm(root,control):
    root=Path(root)
    closures=[root/'segments'/s for s in('original','continuation')]if(root/'normalized-segments.json').exists()else[root]
    for path in closures:
        for name in('session-closed.json','preferences-restored.json'):
            if not json.loads((path/name).read_text(encoding='utf-8'))['verified']:
                raise ValueError('Unverified closed arm '+str(path))
    if control:
        if json.loads((root/'protocol.json').read_text())['csc_enabled']is not False:
            raise ValueError('Not a no-CSC control')
        if not json.loads((root/'no-csc-database.json').read_text())['verified']:
            raise ValueError('Absent-CSC SQL guard missing')
    summary=analyse(root)
    endpoint=json.loads((root/'full-census-250.json').read_text())
    rows=[(kind,payload.split('\t'))for kind,payload in endpoint['rows']]
    types=summary['district_construction']
    return dict(root=str(root),types=types,
        all_foundations=sum(v['foundations']for v in types.values()),
        stock_foundations=sum(v['foundations']for k,v in types.items()if stock_district(k)),
        stock_slot_foundations=sum(v['foundations']for k,v in types.items()
            if stock_district(k)and v.get('requires_population')is True),
        csc_slot_foundations=sum(v['foundations']for k,v in types.items()if k.startswith('DISTRICT_CSC_')
            and v.get('requires_population')is True),
        slot_metadata_missing=[k for k,v in types.items()if v.get('requires_population')is None],
        terminal_cities=sum(kind=='CITY'for kind,_ in rows),
        terminal_population=sum(int(f[2])for kind,f in rows if kind=='CITY'),
        terminal_alive=[int(f[0])for kind,f in rows if kind=='PLAYER'and f[1]=='true'])


def median_native(v,key):
    d=(v or{}).get(key)or{}
    return '—'if not d.get('n')else f"{d['median']/256:.1f} ({d['n']})"


def adjacency(v):
    if not v:return '—'
    joined=v.get('UI_event_adjacency_joined',0)
    if not joined:return 'unavailable'
    result=', '.join(k.removeprefix('YIELD_').lower()+f" {d['mean']:.2f}"for k,d in
        (v or{}).get('exact_UI_event_adjacency_yields',{}).items()
        if k!='YIELD_CSC_AI_PLACEMENT'and d['mean'])or'0'
    return result+(f" ({joined}/{v['foundations']} UI)"if joined<v['foundations']else'')


def compare(treated,controls,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    arms={name:dict(treated=read_arm(Path(treated)/a,False),control=read_arm(Path(controls)/b,True))
          for name,(a,b)in MAPS.items()}
    lines=['# CSC versus no-CSC district controls','',
        'Three preselected maps, five original AI players per map, through turn250 '
        'on Online speed. Compare newly founded ordinary districts and Quarters, '
        'their placement adjacency, and the native values attached to those sites.', '',
        '| Map | Native-type foundations CSC / control | Slot-consuming native CSC / control | CSC slot foundations | Cities at250 CSC / control | Population at250 CSC / control | Alive AI CSC / control |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for name,a in arms.items():
        t,c=a['treated'],a['control']
        lines.append(f"| {name} | {t['stock_foundations']} / {c['stock_foundations']} | "
            f"{t['stock_slot_foundations']} / {c['stock_slot_foundations']} | {t['csc_slot_foundations']} | "
            f"{t['terminal_cities']} / {c['terminal_cities']} | {t['terminal_population']} / {c['terminal_population']} | "
            f"{len(t['terminal_alive'])} / {len(c['terminal_alive'])} |")
    totals={side:{key:sum(a[side][key]for a in arms.values())for key in
        ('stock_foundations','stock_slot_foundations','csc_slot_foundations',
         'terminal_cities','terminal_population')}for side in('treated','control')}
    t,c=totals['treated'],totals['control']
    lines.append(f"| Total | {t['stock_foundations']} / {c['stock_foundations']} | "
        f"{t['stock_slot_foundations']} / {c['stock_slot_foundations']} | {t['csc_slot_foundations']} | "
        f"{t['terminal_cities']} / {c['terminal_cities']} | {t['terminal_population']} / {c['terminal_population']} | — |")
    lines+=['','Slot totals use the loaded RequiresPopulation rule. City Centers and '
        'Wonder footprints are included in the broader native-type count; City Lights '
        'districts are recorded separately in JSON. Cities and population describe the '
        'turn250 empire, providing context for how much district capacity it developed.', '',
        '## Adjacency and native utility by type','',
        'Adjacency is sampled at the placement event and contains real yields. Native '
        'choice utility is the common score measurement in both groups; the controls also '
        'record the cached total just before placement. Parentheses show matched samples. '
        'A dash means the measurement is unavailable or the district uses another investment '
        'path, such as a Wonder. Detailed timestamps and coverage remain in JSON.', '',
        '| Map | District | Foundations CSC / control | Mean adjacency CSC | Mean adjacency control | Median choice utility CSC (n) | Median choice utility control (n) | Control pre-placement cache (n) |',
        '|---|---|---:|---|---|---:|---:|---:|']
    for name,a in arms.items():
        t,c=a['treated']['types'],a['control']['types']
        for kind in sorted(t.keys()|c.keys()):
            if not stock_district(kind):continue
            x,y=t.get(kind,{}),c.get(kind,{})
            # Wonder footprints follow building investment; their generic
            # district cache can hold the native -9999 sentinel. City Centers
            # are not comparable district-auction investments either. Preserve
            # raw cells in JSON but never present them as forecast calibration.
            comparable=kind not in('DISTRICT_CITY_CENTER','DISTRICT_WONDER')
            quoted_t=median_native(x,'native_choice_total_Q8')if comparable else'—'
            quoted_c=median_native(y,'native_choice_total_Q8')if comparable else'—'
            placement=median_native(y,'native_placement_total_Q8')if comparable else'—'
            lines.append(f"| {name} | {kind.removeprefix('DISTRICT_')} | {x.get('foundations',0)} / {y.get('foundations',0)} | "
                f"{adjacency(x)} | {adjacency(y)} | {quoted_t} | {quoted_c} | {placement} |")
    lines+=['','## Comparison setup','',
        'Small/Prince/Online250, matched selected seeds and leaders, with the same '
        'City Lights, Resourceful2 and Sukritact resource versions. Controls remove '
        'CSC entirely. Its resource and economic effects can change the generated world '
        'and later city growth, so read these results as the overall CSC comparison. '
        'Counts measure foundations; population measures surviving cities at250. '
        'Pangaea with CSC includes the documented turn200-save continuation.']
    payload=dict(arms=arms,totals=totals,analysis_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        limits=['Seed/leader matched, not identical generated worlds.',
                'Cumulative construction and terminal populations are different measures.',
                'Choice-time quote is not a fresh placement-time forecast.',
                'Before-placement matrix snapshot need not be recomputed or consulted at placement.',
                'Factory return flag unused; construction requires physical event.',
                'Pangaea treatment uses labelled continuation with native boundary coverage gap.'])
    (output/'district-controls-comparison.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    (output/'district-controls-comparison.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return payload


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in('treated','controls','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();compare(args.treated,args.controls,args.output)
