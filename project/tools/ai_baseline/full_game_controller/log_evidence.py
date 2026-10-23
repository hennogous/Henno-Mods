"""Strict archived Lua boundary review; no native client or live log changes.

Only an immediately preceding exact false ACK from an independently reviewed
read-only diagnostic can explain a traceback. Arbitrary Runtime Error lines,
unknown/truncated traces and missing evidence are never relabeled as clean.
"""
from pathlib import Path
import gzip,json,re

def review_lua_boundary(folder,known_readonly_failed_acks=()):
    folder=Path(folder);known=frozenset(known_readonly_failed_acks)
    report={'evidence_observed':False,'coverage':'UNOBSERVED','events':[],
            'blocking_errors':None,'known_diagnostic_errors':0,'native_controls_issued':0}
    path=folder/'log-segments.json'
    if not path.exists():return report
    m=next((x for x in json.loads(path.read_text(encoding='utf-8-sig'))if x.get('file')=='Lua.log'and 'start'in x),None)
    if not m or 'error'in m:return report
    p=folder/'Lua.log.gz'
    if not p.exists():
        if m.get('bytes')==0 and m.get('start')==m.get('end'):
            report.update(evidence_observed=True,coverage='observed empty delta',blocking_errors=0)
        return report
    lines=gzip.decompress(p.read_bytes()).decode('utf-8',errors='replace').splitlines()
    for i,line in enumerate(lines):
        if not re.search(r'Runtime Error|stack traceback',line,re.I):continue
        previous=lines[i-1]if i else ''
        ack=re.search(r'\b(CSC_FULL_ACK_\d+_\d+)\s+false\b',previous)
        diagnostic=line.strip()=='stack traceback:'and ack is not None and ack[1]in known
        report['events'].append({'line_number':i+1,'line':line,'previous_line':previous,
                                 'classification':'reviewed read-only diagnostic'if diagnostic else'unreviewed Lua error',
                                 'failed_ack':ack[1]if ack else None})
    report.update(evidence_observed=True,coverage='closed archived Lua segment',
                  blocking_errors=sum(e['classification']=='unreviewed Lua error'for e in report['events']),
                  known_diagnostic_errors=sum(e['classification']=='reviewed read-only diagnostic'for e in report['events']))
    return report
