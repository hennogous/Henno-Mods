"""Read archived logs only through an exact outcome checkpoint's byte boundary."""
import gzip,json
from pathlib import Path

def reconstruct_checkpoint(root,name,turn):
    root=Path(root);checkpoint=root/'diagnostics'/f'outcome-{turn}'/'log-segments.json'
    rows=json.loads(checkpoint.read_text(encoding='utf-8-sig'));matches=[r for r in rows if r['file']==name]
    if len(matches)!=1:raise AssertionError('Missing/ambiguous closed checkpoint log boundary')
    limit=matches[0]['end'];segments=[]
    for manifest in(root/'diagnostics').glob('*/log-segments.json'):
        for row in json.loads(manifest.read_text(encoding='utf-8-sig')):
            archive=manifest.parent/(name+'.gz')
            if row['file']==name and row.get('bytes',0)>0 and row['start']<limit and archive.exists():segments.append((row['start'],row['end'],archive))
    data=bytearray();used=0
    for start,end,path in sorted(segments,key=lambda x:(x[0],x[1],str(x[2]))):
        chunk=gzip.decompress(path.read_bytes())
        if len(chunk)!=end-start:raise AssertionError('Archived segment byte size differs')
        end=min(end,limit);chunk=chunk[:end-start]
        if start>len(data):raise AssertionError('Gap before exact checkpoint boundary')
        overlap=max(0,min(len(data),end)-start)
        if overlap and data[start:start+overlap]!=chunk[:overlap]:raise AssertionError('Conflicting checkpoint log segments')
        data.extend(chunk[overlap:]);used+=1
    if len(data)!=limit:raise AssertionError('Incomplete exact checkpoint log')
    return data.decode('utf-8',errors='replace'),dict(bytes=len(data),checkpoint=str(checkpoint),closed_byte_end=limit,segments=used,gaps=[],conflicting_segments=[],same_numeric_turn_future_records_excluded=True)
