"""Join real Quarter foundations to the latest city review of their material layout."""
import json
from collections import Counter
from pathlib import Path
import sys


def report(folder):
    seats={str(i) for i in json.loads((folder/'source.json').read_text())['original_ai']}
    reviews={}
    counts=Counter()
    rows=[]
    for line in (folder/'Lua.log').open(encoding='utf-8', errors='replace'):
        if 'CSC_PAIR_REVIEW\t' in line:
            t,p,c,d,n,b,goal,rival,margin=line.split('CSC_PAIR_REVIEW\t')[1].split()
            reviews[p,c,d]=dict(turn=int(t),sites=int(n),with_base=int(n)-int(b),target=int(goal),margin=int(margin))
            counts['quarter_reviews']+=1
            counts['with_cue']+=int(goal!='-1')
        elif 'CSC_FLOOR_REVIEW\t' in line:
            t,p,c,d,n,good,penalty,goal,rule=line.split('CSC_FLOOR_REVIEW\t',1)[1].split()
            reviews[p,c,d]=dict(turn=int(t),sites=int(n),with_base=int(good),target=int(goal),
                                penalty=penalty=='true',rule=rule)
            counts['quarter_reviews']+=1
            counts['with_cue']+=int(goal!='-1')
        elif 'CSC_SPLIT_SIGNAL\t' in line:
            t,p,c,name,d,goal,a,b,delta,*third=line.split('CSC_SPLIT_SIGNAL\t',1)[1].split()
            # This precedes the plain floor review in the gameplay log.
            if third and third[0]!='-':
                counts['three_terrain_reviews']+=1
            else:
                counts['mixed_terrain_reviews' if '__N_' in b else 'two_positive_reviews']+=1
        elif 'CSC_PAIR_SWITCH\t' in line:
            fields=line.split('CSC_PAIR_SWITCH\t')[1].split()
            counts['activate_two' if fields[-1]!='-' else 'activate_one' if fields[-2]!='-' else 'withdraw']+=1
        elif 'CSC_QUARTER_WATCH_SITE\t' in line:
            r=dict(f.split('=',1) for f in line.split('CSC_QUARTER_WATCH_SITE\t')[1].strip().split('\t') if '=' in f)
            if r['event']=='foundation' and r['player'] in seats:
                rows.append(dict(turn=int(r['turn']),player=r['player'],city=r['city'],district=r['quarterType'],
                                 plot=int(r['plot']),owned_base=int(r['base']),river=r['river']=='true',
                                 review=reviews.get((r['player'],r['city'],r['quarterType']))))
    return dict(events=counts,foundations=rows)


if __name__=='__main__':
    for directory in sys.argv[1:]:
        print(Path(directory).name,json.dumps(report(Path(directory))))
