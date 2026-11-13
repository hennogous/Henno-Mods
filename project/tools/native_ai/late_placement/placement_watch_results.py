"""Keep decision, foundation, completion and loaded-world observations distinct."""
import argparse
import json
from pathlib import Path
import re


def parse(log,*,allow_faults=False):
    assert 'CSC_QUARTER_WATCH_INSTALLED'in log,'Observer was not installed'
    faults=re.findall(r'CSC_QUARTER_WATCH_FAULT[^\r\n]*',log)
    assert not faults or allow_faults,'Observer reported a fault'
    rows=[]
    for kind,payload in re.findall(r'CSC_QUARTER_WATCH_([A-Z]+)\t([^\r\n]+)',log):
        if kind in ('INSTALLED','FAULT'):continue
        row=dict(kind=kind)
        for field in payload.split('\t'):
            name,value=field.split('=',1)
            assert name not in row,'Duplicate diagnostic field'
            if value in ('true','false'):value=value=='true'
            elif re.fullmatch(r'-?\d+(?:\.\d+)?',value):value=float(value)if'.'in value else int(value)
            row[name]=value
        rows.append(row)
    sites=[r for r in rows if r['kind']=='SITE']
    events={event:[r for r in sites if r['event']==event]for event in
        ('loaded','foundation','completion','ownership-change','first-observed')}
    summary={event:dict(count=len(group),below3=sum(r['millForecastTotal']<3 for r in group),
        atLeast3=sum(r['millForecastTotal']>=3 for r in group),
        atLeast4=sum(r['millForecastTotal']>=4 for r in group))for event,group in events.items()}
    return dict(rows=rows,summary=summary,measurementComplete=not faults,faults=faults,
        bestCount=sum(r['kind']=='BEST'for r in rows),
        writeCount=sum(r['kind']=='WRITE'for r in rows),
        deferredCount=sum(r['kind']=='DEFERRED'for r in rows),
        limits=['Mill forecast is geometry with one prospective local Mill, not realised output.',
                'Eligible adjacency at foundation is not output from an incomplete Quarter.',
                'Last native write and published bid do not by themselves establish causal selection.',
                'Loaded, captured and first-observed sites are excluded from foundation statistics.'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    parser.add_argument('--partial',action='store_true',help='Preserve readable rows from a failed observation; never mark it complete')
    args=parser.parse_args()
    result=parse((args.run/'Lua.log').read_text(encoding='utf-8-sig'),allow_faults=args.partial)
    (args.run/'placement-watch.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({name:result[name]for name in('measurementComplete','summary','bestCount','writeCount','deferredCount')},indent=2))
