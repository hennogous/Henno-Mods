"""Summarise ordinary main-mod timing records; no game or native calls.

Whole Lua-publication wall time is the direct synchronous computation/wait added
by guidance. Per-player records partition its work. CE's managed-cell refresh
counter is separate native overhead; it excludes ordinary engine routines.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re


def distribution(values):
    ordered=sorted(values.items(),key=lambda item:(-item[1],item[0]))
    return {'turns':len(values),'total_ms':sum(values.values())/1000,
            'average_ms':sum(values.values())/1000/len(values)if values else None,
            'max_ms':max(values.values())/1000 if values else None,
            'slowest':[{'turn':turn,'ms':micros/1000}for turn,micros in ordered[:5]]}


def summarise(text,*,first=1,last=250):
    wall,lua_clock=defaultdict(int),defaultdict(int)
    player_wall,player_lua_clock=defaultdict(lambda:defaultdict(int)),defaultdict(lambda:defaultdict(int))
    native_packets={};attempts=successful=failures=missing=0
    observed_turns,missing_wall_turns=set(),set()
    for match in re.finditer(r'\bCSC_AI_(PROCESSING|PLAYER_PROCESSING|NATIVE_PROCESSING)\s+([^\r\n]+)',text):
        kind,payload=match.groups()
        fields={key:int(value)for key,value in re.findall(r'([A-Za-z][A-Za-z0-9]*)=(-?\d+)',payload)}
        turn=fields.get('turn')
        if turn is None or not first<=turn<=last:continue
        if kind=='PROCESSING':
            observed_turns.add(turn)
            attempts+=1;successful+=fields.get('published')==1;failures+=fields.get('ok')==0
            if fields.get('wallMicros',-1)>=0:wall[turn]+=fields['wallMicros']
            else:missing+=1;missing_wall_turns.add(turn)
            if fields.get('luaClockMicros',-1)>=0:lua_clock[turn]+=fields['luaClockMicros']
        elif kind=='PLAYER_PROCESSING'and 'player'in fields:
            if fields.get('wallMicros',-1)>=0:player_wall[fields['player']][turn]+=fields['wallMicros']
            if fields.get('luaClockMicros',-1)>=0:player_lua_clock[fields['player']][turn]+=fields['luaClockMicros']
        elif kind=='NATIVE_PROCESSING'and fields.get('managedMicros',-1)>=0 and 'version'in fields:
            # A failed refresh can report the same still-live packet again.
            # Its cumulative counter contributes its maximum, not a second sum.
            key=turn,fields['version']
            native_packets[key]=max(native_packets.get(key,0),fields['managedMicros'])
    native=defaultdict(int)
    for (turn,version),micros in native_packets.items():native[turn]+=micros
    # A retry without a clock makes that turn's total incomplete. Exclude its
    # partial sum from the headline distribution rather than understate cost.
    for turn in missing_wall_turns:wall.pop(turn,None)
    return {'schema':'csc-ai-processing-time-v1','first_turn':first,'last_turn':last,
            'publication_attempts':attempts,'published_packets':successful,'failed_attempts':failures,
            'unobserved_turns':sorted(set(range(first,last+1))-observed_turns),
            'incomplete_wall_turns':sorted(missing_wall_turns),
            'missing_wall_attempts':missing,'publisher_wall':distribution(wall),'publisher_lua_clock':distribution(lua_clock),
            'players':{str(pid):{'wall':distribution(player_wall[pid]),'lua_clock':distribution(player_lua_clock[pid])}
                       for pid in sorted(set(player_wall)|set(player_lua_clock))},
            'native_managed_cell_wall':distribution(native),
            'scope':'All logged publication attempts summed per turn; native managed-cell work is reported separately.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--first',type=int,default=1);parser.add_argument('--last',type=int,default=250)
    args=parser.parse_args()
    result=summarise(args.log.read_text(encoding='utf-8-sig',errors='replace'),first=args.first,last=args.last)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
