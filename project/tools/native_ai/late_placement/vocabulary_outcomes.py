"""Join signed site hints to UI previews, subsequent native contracts and Quarter foundations."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path


def read(folder):
    seats=set(json.loads((folder/'source.json').read_text())['original_ai'])
    active={}
    by_review={}
    records=[]
    foundations=[]
    with (folder/'Lua.log').open(encoding='utf-8-sig',errors='replace') as stream:
        for line in stream:
            if 'CSC_FLOOR_REVIEW\t' in line:
                t,p,c,d,_,_,_,_,_=line.split('CSC_FLOOR_REVIEW\t',1)[1].split()
                old=active.pop((p,c,d),None)
                if old is not None:
                    old['until']=int(t)
            elif 'CSC_VOCAB_SITE\t' in line:
                t,p,c,name,d,plot,gain,margin,floor,rules,*rival=line.split('CSC_VOCAB_SITE\t',1)[1].split()
                if int(p) not in seats:
                    continue
                row=dict(turn=int(t),player=p,city=c,name=name,district=d,plot=int(plot),gain=int(gain),
                         margin=int(margin),rules=rules.split(','),until=None,bids=[])
                active[p,c,d]=row
                by_review[t,p,c,d]=row
                records.append(row)
            elif 'CSC_VOCAB_NATIVE\t' in line:
                ui,t,p,c,name,d,plot,preview,rival,other,can,used,allowed=line.split('CSC_VOCAB_NATIVE\t',1)[1].split()
                row=by_review.get((t,p,c,d))
                if row and row['plot']==int(plot):
                    row['ui']=dict(turn=int(ui),preview=int(preview),rival=int(rival),
                                   other=int(other) if other!='-' else None,can=can=='true',
                                   used=int(used),allowed=int(allowed))
            elif 'CSC_QUARTER_WATCH_SITE\t' in line:
                fields=dict(item.split('=',1) for item in line.split('CSC_QUARTER_WATCH_SITE\t',1)[1].split() if '=' in item)
                if fields['event']!='foundation' or int(fields['player']) not in seats:
                    continue
                row=active.pop((fields['player'],fields['city'],fields['quarterType']),None)
                event=dict(turn=int(fields['turn']),plot=int(fields['plot']),base=int(fields['base']),
                           district=fields['quarterType'],player=fields['player'],city=fields['city'])
                if row:
                    row['foundation']=event['plot']
                    row['until']=event['turn']+1
                    event.update(target=row['plot'],name=row['name'])
                foundations.append(event)
    with (folder/'AI_CityBuild.csv').open(encoding='utf-8-sig',errors='replace') as stream:
        for fields in csv.reader(stream,skipinitialspace=True):
            if len(fields)<10 or fields[5]!='SUBMITTED' or 'DISTRICT_CSC_' not in fields[8]:
                continue
            t=int(fields[0])
            for row in records:
                if (row['player'],row['name'],row['district'])==(fields[1],fields[2],fields[8]) and (
                        row['turn']<=t and (row['until'] is None or t<row['until'])):
                    row['bids'].append((t,fields[9]))
    families=Counter()
    for row in records:
        families.update({rule.split('_')[1] for rule in row['rules']})
    return dict(reviews=len(records),site_count=len({(r['district'],r['plot']) for r in records}),
                families=dict(families),native_previews=sum('ui' in r for r in records),
                eligible=sum(r.get('ui',{}).get('can',False) for r in records),
                reviews_with_submissions=sum(bool(r['bids']) for r in records),
                exact_foundations=sum(e.get('target')==e['plot'] for e in foundations),
                foundations=foundations,records=records)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path)
    parser.add_argument('--details',action='store_true')
    args=parser.parse_args()
    report=read(args.folder)
    if not args.details:
        report.pop('records')
    print(json.dumps(report,indent=2))
