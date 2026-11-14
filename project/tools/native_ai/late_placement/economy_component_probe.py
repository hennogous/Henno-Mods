"""Bounded read-only component audit at shared-controller replay boundaries."""
import json
from pathlib import Path
import re
from driver import lua,read,require,write_json

HERE=Path(__file__).resolve().parent


def targets(values):
    require(len(values)<=8,'At most eight explicit component targets')
    result=[]
    for player,city,plot,key in values:
        p,c,i=map(int,(player,city,plot))
        require(p in range(1,6)and c>=0 and i>=0 and key in('BAKERS','TAILORS'),
                'Expected original AI/city/plot/active Quarter')
        result.append(dict(player=p,city=c,plot=i,key=key))
    return result


def capture(controller,out,selected,turn):
    code='CSC_COMPONENT_TARGETS='+lua(selected)+'\n'+read(HERE/'economy_component_probe.lua')
    raw=controller.cmd(code,'CSC_AI_BakersGameplay','economic-components-'+str(turn))
    (out/('economic-components-'+str(turn)+'.txt')).write_text(raw,encoding='utf-8')
    rows=[json.loads(s)for s in re.findall(r'CSC_ECONOMY_COMPONENT=([^\r\n]+)',raw)]
    require('CSC_ECONOMY_COMPONENT_COMPLETE'in raw and len(rows)==len(selected)
            and all(r['turn']==turn for r in rows),'Incomplete economic component audit')
    write_json(out/('economic-components-'+str(turn)+'.json'),
               dict(diagnostic_only=True,turn=turn,records=rows))
