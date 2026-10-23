"""Independent archived-renderer review; no game client or changes to a running collector."""
import argparse,datetime,gzip,hashlib,json,re,time
from pathlib import Path

PATTERNS={
 'missing_pipeline_state':r'Unable to locate appropriate Pipeline State Object',
 'pipeline_creation_failure':r'(?:CreateGraphicsPipelineState|CreateComputePipelineState).*(?:fail|error)|(?:fail|error).*Pipeline.?State',
 'shader_failure':r'(?:shader.*(?:compil|creat).*(?:fail|error))|(?:failed.*shader)',
 'device_removed':r'DXGI_ERROR_DEVICE_(?:REMOVED|HUNG|RESET)|device.?removed|device.?hung',
}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def extract(data,base=0):
 lines=data.splitlines(keepends=True);out=[];offset=base
 for i,raw in enumerate(lines):
  line=raw.decode('utf-8',errors='replace').rstrip('\r\n')
  for kind,pattern in PATTERNS.items():
   if not re.search(pattern,line,re.I):continue
   stamp=re.search(r'\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\]',line)
   fields=re.search(r'SP:\s*(\d+)\s+SM:\s*(\d+)\s+Vertex Format:\s*(\d+)\s+Topology:\s*(\d+)',line)
   row={'kind':kind,'line':line,'absolute_log_byte_offset':offset,'timestamp_local':stamp[1]if stamp else None,'context':[x.decode('utf-8',errors='replace').rstrip('\r\n')for x in lines[max(0,i-1):min(len(lines),i+3)]]}
   if fields:row['signature']=dict(zip(('shader_package','shader_method','vertex_format','topology'),map(int,fields.groups())))
   out.append(row)
  offset+=len(raw)
 return out

def review(root):
 events={};segments=[];run=read(root/'run-start.json');start=run['time']
 folders=list((root/'diagnostics').iterdir())
 timeline=root/'timeline.ndjson'
 if timeline.exists():
  labels=[json.loads(x)['label']for x in timeline.read_text(encoding='utf-8').splitlines()if json.loads(x).get('event')=='checkpoint']
  folders=[root/'diagnostics'/name for name in dict.fromkeys(labels)]
 for folder in folders:
  # The collector writes this manifest after closing the compressed log stream.
  manifest=folder/'log-segments.json';p=folder/'Renderer.log.gz'
  if not manifest.exists():continue
  m=next((x for x in read(manifest)if x.get('file')=='Renderer.log'and 'start'in x),None)
  if m is None or 'error'in m:continue
  if not p.exists():
   # A closed checkpoint can observe a valid zero-byte delta. It is not a
   # missing stream and not a graphics error; the prior prefix stays archived.
   if m.get('bytes')==0 and m['end']==m['start']:
    segments.append({'capture':folder.name,'start':m['start'],'end':m['end'],'bytes_read':0,'hits':0,'observed_empty_delta':True})
   continue
  data=gzip.decompress(p.read_bytes());hits=extract(data,m['start'])
  segments.append({'capture':folder.name,'start':m['start'],'end':m['end'],'sha256_compressed':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes_read':len(data),'hits':len(hits)})
  for event in hits:
   event['captures']=[folder.name];event['archived_log']=str(p)
   key=(event['kind'],event['timestamp_local'],event['line'],event['absolute_log_byte_offset'])
   if key in events:events[key]['captures'].append(folder.name)
   else:
    local=event['timestamp_local']
    try:event['timestamp_vs_run_start']='at_or_after_run_start'if datetime.datetime.strptime(local,'%Y-%m-%d %H:%M:%S').timestamp()>=start-1 else'predates_run'
    except(TypeError,ValueError):event['timestamp_vs_run_start']='UNOBSERVED'
    events[key]=event
 rows=list(events.values());recent=[x for x in rows if x['timestamp_vs_run_start']=='at_or_after_run_start']
 return {'version':'incremental-renderer-review-v2','reviewed_unix':time.time(),'source_run_start':start,'archived_renderer_available':bool(segments),'segments':segments,'events':rows,'unique_events':len(rows),'at_or_after_run_start_events':len(recent)if segments else None,'renderer_error_gate':'FAIL: explicit graphics errors require investigation'if recent else'No matched archived errors'if segments else'UNOBSERVED: no closed archived renderer segments','limits':['Closed archived segments only; active current tail may not yet be captured','No matched error does not prove renderer safety','Timestamp comparison uses this Windows host local timezone','Error signatures identify failed pipeline combinations, not a named asset','No native commands, installed files or running collector changed']}


def assert_no_errors(report):
 """Raise only on positive native graphics evidence; preserve unknown as unknown."""
 count=report.get('at_or_after_run_start_events')
 if count is not None and count>0:raise RuntimeError('Explicit archived renderer errors require investigation')
 return report.get('renderer_error_gate')
