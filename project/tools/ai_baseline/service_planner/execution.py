"""One-shot native purchase through an injected canonical controller instance."""
from dataclasses import replace
import json
import os
from pathlib import Path
from .policy import PROFILES


def lua(value):
    if value is None: return 'nil'
    if isinstance(value,bool): return str(value).lower()
    if isinstance(value,(int,float)): return str(value)
    if isinstance(value,str): return json.dumps(value,ensure_ascii=True)
    if isinstance(value,dict): return '{'+','.join('['+lua(k)+']='+lua(v)for k,v in value.items())+'}'
    raise TypeError(type(value))


class PurchaseExecutor:
    """The driver supplies fresh native facts, not cached legality/treasury values.

    `fresh(decision.candidate)` returns (Candidate, Budget, turn, purchase_parameter,
    venue_type). `readback` returns fresh player/city/owner/gold/turn. Neither is
    implemented with worldbuilder setters or fabricated deductions.
    """
    def __init__(self, planner, runner, journal, *, allow_mutations=False, boundary=None, allow_ai_native_request_probe=False):
        if not __debug__:raise RuntimeError('Run this prototype with Python assertions enabled')
        self.planner=planner;self.runner=runner;self.journal=Path(journal)
        self.allow_mutations=allow_mutations;self.pending={};self.boundary=boundary
        self.allow_ai_native_request_probe=allow_ai_native_request_probe;self.native_authority_confirmed=False;self.authority_probe_used=False
        if self.journal.exists():
            for line in self.journal.read_text(encoding='utf-8').splitlines():
                event=json.loads(line)
                if event['event']=='purchase-begin':
                    self.pending[event['player']]=event
                    if event.get('allow_ai_native_request_probe'):self.authority_probe_used=True
                elif event['event']=='purchase-confirmed':
                    prior=self.pending.pop(event['player'],None)
                    if prior:
                        self.planner.purchases.append((event['player'],prior['city'],event['turn'],event['real_gold_spent']))
                        key=prior.get('site_key',f"{prior['player']}:{prior['city']}:{prior['quarter']}:{prior['source_plot']}")
                        self.planner.site_spend[key]=self.planner.site_spend.get(key,0)+event['real_gold_spent']
                        if prior.get('allow_ai_native_request_probe'):self.native_authority_confirmed=True
            self.planner.pending_players.update(self.pending)

    def record(self,event):
        self.journal.parent.mkdir(parents=True,exist_ok=True)
        with self.journal.open('a',encoding='utf-8')as f:
            f.write(json.dumps(event,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())

    def request(self,decision,needs,fresh):
        assert self.allow_mutations,'Native spending disabled unless explicitly enabled'
        assert decision.action=='purchase'
        c,budget,turn,param,venue=fresh(decision.candidate)
        assert c.key==decision.candidate.key and c.observed_turn==turn
        assert c.purchase_plot==decision.candidate.purchase_plot and c.footprint==decision.candidate.footprint,'Acquisition dependencies changed; replan'
        assert self.boundary is not None,'Driver must supply fresh safe-boundary proof'
        proof=self.boundary()
        assert proof['turn']==turn and proof['autoplay_active']is False,'Do not mutate during active autoplay'
        d=self.planner.evaluate(c,needs,budget,turn)
        assert d.action=='purchase',d.reason
        profile=PROFILES.get(c.service)
        if profile:assert venue in profile.venues
        assert param is not None and c.purchase_plot is not None
        reserve=budget.gold-budget.available(self.planner.policy)
        material=self.planner.policy.objective=='materials'
        if material and self.allow_ai_native_request_probe and not self.native_authority_confirmed:
            assert not self.authority_probe_used,'Unproven native AI request already attempted; investigate, never repeat blindly'
        request={'player':c.player,'city':c.city,'purchase_plot':c.purchase_plot,'source_plot':c.plot,
                 'quarter':c.quarter,'turn':turn,'base':c.purchase_base if material else c.base,
                 'specialty':c.purchase_specialty if material else c.specialty,'service':c.service,
                 'material_first':material,'stepwise':self.planner.policy.stepwise,'established':c.established,'site_key':c.site_key,'plan_connectors':{str(i):True for i in c.plan_connectors},'remaining_tiles':{str(i):True for i in c.missing_tiles},
                 'plan_materials':{str(i):True for i in c.plan_materials},
                 'customer_plot':c.customer_plot,'venue_type':venue,
                 'requires_specialty':profile.requires_specialty if profile else False,
                 'civic':profile.civic if profile else None,
                 'require_research_now':d.tier=='strong_service',
                 'gold':budget.gold,'price':c.price,'max_price':d.max_price,'reserve':reserve,
                 'plot_purchase_parameter':param,'allow_ai_native_request_probe':bool(material and self.allow_ai_native_request_probe)}
        event=dict(request,event='purchase-begin',key=c.key)
        # Mark ambiguity before dispatch. A timeout, a Lua error or process restart
        # cannot make this site/player eligible for an automatic second request.
        self.record(event);self.pending[c.player]=event;self.planner.pending_players.add(c.player)
        if request['allow_ai_native_request_probe']:self.authority_probe_used=True
        code='CSC_SERVICE_PURCHASE_REQUEST='+lua(request)+';\n'+Path(__file__).with_name('native_purchase.lua').read_text(encoding='utf-8')
        raw=self.runner.cmd(code,'PlotInfo','service-purchase-'+str(c.purchase_plot),check=True)
        self.record({'event':'purchase-dispatched','player':c.player,'key':c.key})
        return raw

    def reconcile(self,player,readback):
        event=self.pending[player]
        result=readback(event)
        # Exact ownership and real treasury change are both necessary. An ACK or
        # the purchase-request marker is not proof the purchase actually happened.
        confirmed=(result['city_owner']==player and result['plot_owner']==player
                   and result['gold']==event['gold']-event['price']
                   and result['turn']==event['turn'])
        if not confirmed:return {'confirmed':False,'pending':True,'readback':result}
        self.record({'event':'purchase-confirmed','player':player,'key':event['key'],
                     'real_gold_spent':event['price'],'turn':result['turn']})
        self.planner.purchases.append((player,event['city'],event['turn'],event['price']))
        key=event.get('site_key',f"{player}:{event['city']}:{event['quarter']}:{event['source_plot']}")
        self.planner.site_spend[key]=self.planner.site_spend.get(key,0)+event['price']
        if event.get('allow_ai_native_request_probe'):self.native_authority_confirmed=True
        self.planner.pending_players.discard(player);del self.pending[player]
        self.planner.mark_dirty(player,event['city'])
        # No foundation is placed in the purchase callback. The next safe check
        # must collect fresh owned-land legality and run the existing0% contract.
        return {'confirmed':True,'pending':False,'real_gold_spent':event['price']}
