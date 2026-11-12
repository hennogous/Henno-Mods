"""Read existing CE receipts for archived host-aware Quarter candidates.

Diagnostic only: no score, policy enable/disable, gameplay or ownership write.
The main publisher still runs normally. Capture an immutable trace PREFIX in
one generation before its next publication, not an allegedly frozen full window.
Concurrent native callbacks may append; generation changes invalidate the read.
"""
from driver import lua


def candidate_scope(previous, expanded):
    """Old surveys nominate leads; they do not qualify today's eligibility."""
    before={tuple(row[:6]):row for row in previous['sites']}
    result=[]
    for row in expanded['sites']:
        old=before.get(tuple(row[:6]))
        if old and int(row[6])>0 and row[6]!=old[6]:
            result.append(dict(player=int(row[0]),city=int(row[1]),name=row[2],
                profile=row[3],district=int(row[4]),plot=int(row[5]),
                previousDelta=int(old[6]),expandedDelta=int(row[6])))
    assert 0<len(result)<=64
    assert len({(r['player'],r['city'],r['district'],r['plot'])for r in result})==len(result)
    return result


PREFIX="""-- Diagnostic native prefix reader, before main CSC publication resets counters.
local hostScope=__SCOPE__
local hostCities,hostPairs={},{}
local hostPlayers=__PLAYERS__
local hostQuarterTypes={}
local hostArmed=false
for _,r in ipairs(hostScope)do
 local city=r.player..':'..r.city
 hostCities[city]=true;hostPairs[city..':'..r.district..':'..r.plot]=true
end
function CSC_HOST_DIAG_Snapshot()
 assert(hostArmed,'Host reader has not been armed after initial qualification')
 local turn=Game.GetCurrentGameTurn()
 if turn<__START__ or turn>__END__ then return end
 local initial=CE_AIDistrictScoresStatus()
 local generation=assert(tonumber(initial:match('"generation":(%d+)')))
 local version=assert(tonumber(initial:match('"version":(%d+)')))
 local count=assert(tonumber(initial:match('"trace_count":(%d+)')))
 assert(initial:match('"ready":1') and initial:match('"enabled":1')
  and initial:match('"faults":0') and count<16384,'Host trace policy is unhealthy')
 print('CSC_HOST_PREFIX_BEGIN',turn,generation,version,count)
 local offset=0
 while offset<count do
  local limit=math.min(64,count-offset)
  local page=CE_AIDistrictScoresTraceRead(offset,limit,generation)
  assert(type(page)=='string' and page:match('"stale":false'),'Host trace generation changed')
  assert(tonumber(page:match('"generation":(%d+)'))==generation
   and tonumber(page:match('"version":(%d+)'))==version
   and tonumber(page:match('"offset":(%d+)'))==offset
   and tonumber(page:match('"next":(%d+)'))==offset+limit
   and tonumber(page:match('"total":(%d+)'))>=count,'Incomplete host trace prefix')
  local records=assert(page:match('"records":%[(.*)%]}'))
  local readCount=0
  -- CE emits flat numeric records with a short kind string. Preserve the
  -- exact native record plus its stable index; do not reconstruct score values.
  for raw in records:gmatch('{[^{}]+}')do
   local player=assert(tonumber(raw:match('"player":(%d+)')))
   local cityID=assert(tonumber(raw:match('"city":(%d+)')))
   local district=assert(tonumber(raw:match('"district":(-?%d+)')))
   local plot=assert(tonumber(raw:match('"plot":(-?%d+)')))
   local city=player..':'..cityID
   if hostPairs[city..':'..district..':'..plot]
    or hostCities[city] and raw:match('"k":"best"')
    or hostPlayers[player] and (hostQuarterTypes[district] or raw:match('"k":"best"'))then
    print('CSC_HOST_NATIVE',turn,generation,offset+readCount,raw)
   end
   readCount=readCount+1
  end
  assert(readCount==limit,'Host trace record count differs')
  offset=offset+limit
 end
 local final=CE_AIDistrictScoresStatus()
 assert(tonumber(final:match('"generation":(%d+)'))==generation
  and final:match('"enabled":1') and final:match('"faults":0'),'Host trace changed during read')
 print('CSC_HOST_PREFIX_END',turn,generation,version,count)
end
function CSC_HOST_DIAG_Arm()
 assert(not hostArmed,'Host reader was already armed')
 if next(hostPlayers)then
  for _,profile in ipairs(CSC_AI_QuarterPlacement.StageTwoProfiles())do
   hostQuarterTypes[profile.district.Index]=true
  end
 end
 hostArmed=true
 print('CSC_HOST_DIAG_ARMED',Game.GetCurrentGameTurn())
 CSC_HOST_DIAG_Snapshot()
end
GameEvents.OnGameTurnStarted.Add(function()
 -- A load boundary can precede the first successful UI-backed publication.
 -- The controller explicitly arms only after the active main packet qualifies.
 -- Once armed, an inactive or faulted policy is a diagnostic failure.
 if not hostArmed then print('CSC_HOST_DIAG_NOT_ARMED',Game.GetCurrentGameTurn());return end
 local ok,error=pcall(CSC_HOST_DIAG_Snapshot)
 if not ok then print('CSC_HOST_DIAG_FAILED',tostring(error))end
end)
"""


def stage(source,scope,*,start=200,end=207,players=(),window_limit=8):
    # Ordinary matched windows retain their eight-turn guard. The explicit
    # early1.7 scout may read up to18 turns with sparse saved boundaries;
    # each generation still has the same trace/page/capacity checks above.
    # The longer opportunity continuation is restricted to three exact pairs
    # in one city so ordinary native planning can resume without a forced reset.
    opportunity_scope={(r['player'],r['city'],r['district'],r['plot'])for r in scope}
    assert (window_limit==8 or window_limit==18 and start==22 and end<=40 and not scope
        or window_limit==54 and start==200 and end<=254 and not players and opportunity_scope=={
            (1,524295,36,397),(1,524295,36,398),(1,524295,36,472)})
    assert 0<=start<end<=start+window_limit
    assert len(set(players))==len(players) and all(0<p<64 for p in players)
    prefix=PREFIX.replace('__SCOPE__',lua(scope)).replace('__PLAYERS__',lua({p:True for p in players}))
    prefix=prefix.replace('__START__',str(start)).replace('__END__',str(end))
    return prefix.encode('utf-8')+source
