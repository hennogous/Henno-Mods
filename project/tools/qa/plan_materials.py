"""Read-only terrain-aware material fixture search in the current game.

Uses existing resources around owned cities, native district/improvement
eligibility, and distinct adjacent sites. Does not launch or mutate a game.
"""
import argparse
import json
from pathlib import Path
import re
from csc_qa import ROOT, Run, tuner


def parse_plan(text):
    result = {'candidates': [], 'rejections': {}}
    candidates = {}
    for line in text.splitlines():
        match = re.search(r'QA_PLAN_(SUMMARY|FACT|MATERIAL|REJECT)\t(.*)', line)
        if not match:
            continue
        kind, payload = match.groups()
        fields = payload.split('\t')
        if kind == 'SUMMARY':
            result.update(status=fields[0], total_candidates=int(fields[1]), plots_examined=int(fields[2]))
        elif kind == 'REJECT':
            result['rejections'][fields[0]] = int(fields[1])
        else:
            candidate = candidates.setdefault(int(fields[0]), {'materials': {}})
            if kind == 'MATERIAL':
                candidate['materials'].setdefault(fields[1], {}).update(
                    resource=fields[2], improvement=fields[3], state=fields[4])
            else:
                role, key, value = fields[1:]
                target = candidate.setdefault('quarter', {}) if role == 'quarter' else candidate['materials'].setdefault(role, {}).setdefault('plot', {})
                target[key] = {'true': True, 'false': False}.get(value, int(value) if re.fullmatch(r'-?\d+', value) else value)
    assert 'status' in result, 'Native planner summary missing'
    result['candidates'] = [candidates[key] for key in sorted(candidates)]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--quarter', choices=['tailors', 'bakers'], default='tailors')
    parser.add_argument('--materials', choices=['base', 'specialty', 'both', 'stacking'], default='both')
    parser.add_argument('--player', type=int, default=0)
    parser.add_argument('--port', type=int, default=4318)
    parser.add_argument('--limit', type=int, default=10)
    args = parser.parse_args()
    assert args.player >= 0 and args.limit > 0
    tuner.PORT = args.port
    quarter = args.quarter.upper()
    names = {'base': ['BASE'], 'specialty': ['SPEC'], 'both': ['BASE', 'SPEC'], 'stacking': ['BASE', 'BASE', 'SPEC']}[args.materials]
    slots = ','.join('{Name="M%d",Tag="CLASS_CSC_%s_%s",Improvements={"IMPROVEMENT_FARM","IMPROVEMENT_PLANTATION","IMPROVEMENT_PASTURE","IMPROVEMENT_MINE","IMPROVEMENT_CAMP"}}' % (i+1, quarter, kind) for i, kind in enumerate(names))
    request = '{Player=%d,District="DISTRICT_CSC_%s_QUARTER",Slots={%s}}' % (args.player, quarter, slots)
    code = (ROOT/'project/tests/qa/placement.lua').read_text(encoding='utf-8') + '\n'
    code += '''assert(not Game:GetProperty('CSC_TAILORS_QA') and not Game:GetProperty('CSC_QA_MATERIAL_FIXTURE'),
 'QA_PLACEMENT_BLOCKED: use an unmodified map; historical forced-terrain fixtures are untrusted');
local request=%s;local plan=QAPlacement.Find(request);
print('QA_PLAN_SUMMARY',plan.Status,#plan.Candidates,plan.MapPlotsExamined);
for reason,count in pairs(plan.Rejected) do print('QA_PLAN_REJECT',reason,count);end;
for i=1,math.min(#plan.Candidates,%d) do
 local c=plan.Candidates[i];assert(QAPlacement.Recheck(request,c));
 c.Quarter.City=c.City;c.Quarter.Player=c.Player;
 for key,value in pairs(c.Quarter) do print('QA_PLAN_FACT',i,'quarter',key,tostring(value));end;
 for _,m in ipairs(c.Materials) do
  print('QA_PLAN_MATERIAL',i,m.Name,m.Resource,m.Improvement,m.State);
  for key,value in pairs(m.Facts) do print('QA_PLAN_FACT',i,m.Name,key,tostring(value));end;
 end;
end;''' % (request, args.limit)
    text = Run(args.output).execute('read-only terrain-aware candidate scan', code, wait=5)
    plan = parse_plan(text)
    plan['request'] = {'quarter': args.quarter, 'materials': args.materials, 'player': args.player}
    (args.output/'placement-plan.json').write_text(json.dumps(plan, indent=2)+'\n', encoding='utf-8')
    print(f"{plan['status'].upper()}: {plan['total_candidates']} viable layouts; map unchanged.")
    return 0 if plan['status'] == 'candidates' else 20


if __name__ == '__main__':
    raise SystemExit(main())
