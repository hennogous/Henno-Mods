"""Bounded capability query across frames; never a purchasing backend.

SetLocalPlayerAndObserver transfers human control, not merely the camera. This
helper temporarily changes that role only at an inactive boundary, performs
read-only purchase permission queries, and restores the exact original roles.
It never requests a purchase or changes gold/plot ownership. Native testing
proved role restoration CAN advance a turn even without autoplay. This route is
rejected for production and disabled unless a separate unsafe diagnostic opts in.
"""
import json,re,time


def core_state(r,label):
 code="local h={};for id=0,5 do h[#h+1]=Players[id]:IsHuman()and '1'or '0'end;print('CSC_ACTOR_CORE',Game.GetCurrentGameTurn(),AutoplayManager.IsActive(),Game.GetLocalPlayer(),Game.GetLocalObserver(),table.concat(h,','))"
 raw=r.cmd(code,'GameCore_Tuner',label)
 m=re.findall(r'CSC_ACTOR_CORE\s+(\d+)\s+(true|false)\s+(-?\d+)\s+(-?\d+)\s+([01,]+)',raw)[-1]
 return dict(turn=int(m[0]),active=m[1]=='true',local_player=int(m[2]),observer=int(m[3]),human=[x=='1'for x in m[4].split(',')])


def query_ui(r,player,city,decode,label):
 code="""local pid=%d;local city=CityManager.GetCity(pid,%d);assert(city and city:GetOwner()==pid)
local pars={[CityCommandTypes.PARAM_PLOT_PURCHASE]=true};local visible,results=CityManager.CanStartCommand(city,CityCommandTypes.PURCHASE,true,pars,true)
local rows={};local gold=Players[pid]:GetTreasury():GetGoldBalance()
for _,index in ipairs(visible and results and results[CityCommandResults.PLOTS]or {})do
 local plot=Map.GetPlotByIndex(index);local price=city:GetGold():GetPlotPurchaseCost(index)
 if #rows<8 and plot:GetOwner()==-1 and not plot:IsWater()and not plot:IsImpassable()and price>0 and gold>=price then
  local p={[CityCommandTypes.PARAM_PLOT_PURCHASE]=true,[CityCommandTypes.PARAM_X]=plot:GetX(),[CityCommandTypes.PARAM_Y]=plot:GetY()}
  rows[#rows+1]={plot=index,price=price,normal=CityManager.CanStartCommand(city,CityCommandTypes.PURCHASE,p)==true}
 end
end
print('CSC_ACTOR_UI='..CSC_SERVICE_NATIVE.Json({turn=Game.GetCurrentGameTurn(),local_player=Game.GetLocalPlayer(),actor_human=Players[pid]:IsHuman(),gold=gold,rows=rows}))"""%(player,city)
 return decode(r.cmd(code,'PlotInfo',label),'CSC_ACTOR_UI')


def probe_command_actor(r,*,turn,player,city,decode,write,max_samples=5,spacing=1,allow_unsafe_diagnostic=False):
 assert allow_unsafe_diagnostic, "Rejected role-switch route: native test advanced clock; diagnostic opt-in required"
 assert player in range(1,6) and 1<=max_samples<=5 and 0<=spacing<=2
 before=core_state(r,'actor-before');assert before['turn']==turn and not before['active']
 assert before['local_player']==0 and before['human']==[True,False,False,False,False,False]
 report=dict(turn=turn,player=player,city=city,before=before,samples=[],purchase_requests=0,
  AI_turns_to_advance=0,temporary_human_control=True,switch_requests=0,restore_requests=0)
 write(r.root/'actor-probe-started.json',report)
 error=None
 try:
  # Journal before the role switch. A missing ACK never repeats this switch.
  report['switch_requests']=1
  r.cmd('assert(not AutoplayManager.IsActive()and Game.GetCurrentGameTurn()=='+str(turn)+');PlayerManager.SetLocalPlayerAndObserver('+str(player)+');','CSC_AdjacencyGameplay','actor-switch-once')
  for n in range(max_samples):
   if n:time.sleep(spacing)
   core=core_state(r,'actor-current-'+str(n));assert core['turn']==turn and not core['active'],'Native phase moved; restore immediately'
   ui=query_ui(r,player,city,decode,'actor-ui-'+str(n));assert ui['turn']==turn
   report['samples'].append(dict(core=core,ui=ui))
   write(r.root/'actor-probe-latest.json',report)
   if ui['local_player']==player and ui['actor_human'] and any(x['normal']for x in ui['rows']):break
 except BaseException as e:error=e;report['error']=repr(e)
 finally:
  report['restore_requests']=1
  r.cmd('PlayerManager.SetLocalPlayerAndObserver('+str(before['local_player'])+');PlayerManager.SetLocalObserverTo('+str(before['observer'])+');','CSC_AdjacencyGameplay','actor-restore-once')
  after=core_state(r,'actor-after-restore');report['after']=after
  report['roles_restored']=all(after[k]==before[k]for k in ('local_player','observer','human'))
  report['observed_native_turn_delta']=after['turn']-before['turn']
  report['clock_unchanged']=after['turn']==before['turn']and not after['active']
  report['ui_actor_synchronized']=any(s['ui']['local_player']==player and s['ui']['actor_human']for s in report['samples'])
  report['permission_observed']=any(s['ui']['local_player']==player and s['ui']['actor_human']and any(x['normal']for x in s['ui']['rows'])for s in report['samples'])
  write(r.root/'actor-probe-result.json',report)
  assert report['roles_restored'],'Human/AI role restoration failed; preserve native state'
  assert report['clock_unchanged'],'Native clock moved during capability probe; investigate'
 if error:raise error
 r.ready(turn,'actor-restored-final')
 return report
