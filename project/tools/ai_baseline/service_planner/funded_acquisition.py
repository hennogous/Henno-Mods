"""Own-wallet acquisition with an explicitly enabled donation shortfall.

Uses the explicitly authorized assisted city-assignment/debit backend. Native AI
PURCHASE authority remains unproven. One tile per player per safe turn, exact
receipt before any continuation, and no implicit switch of ordinary defaults.
"""
from dataclasses import asdict
from pathlib import Path
import math,json
from .donation_diagnostic import Diagnostic,budget_snapshot
from .native_adapter import parse


def funding(c,budget,planner,turn):
    decision=planner.evaluate(c,{},budget,turn)
    p=planner.policy
    # available() is clipped at zero. Subtracting it from gold would silently
    # lower the reserve target for a poor wallet, contradicting native checks.
    reserve=max(p.minimum_reserve,budget.emergency_reserve,
                math.ceil(max(0,-budget.net_income)*p.deficit_reserve_turns))
    recent=[cost for pid,city,t,cost in planner.purchases
            if pid==c.player and 0<=turn-t<p.player_purchase_window]
    cap=max(0,min(p.strong_cost_cap-sum(recent),p.strong_cost_cap-planner.site_spend.get(c.site_key,0)))
    out=dict(action='wait',reason=decision.reason,price=c.price,own_gold=0,grant=0,
             reserve=reserve,remaining_cap=cap,donation_cutoff=None,
             ordinary_next_action=decision.action,ordinary_next_reason=decision.reason)
    if decision.action=='purchase':
        out.update(action='acquire',own_gold=c.price,reason='AI wallet passes ordinary one-step policy')
    elif (decision.reason=='next step exceeds real-wallet allowance'
          and c.price<=cap):
        own=min(c.price,max(0,math.floor(.8*budget.available(p))))
        out.update(action='acquire',own_gold=own,grant=c.price-own,
                   reason='Fallback covers only unaffordable step shortfall')
    return out


class FundedDiagnostic(Diagnostic):
    def install(self):
        super().install()
        self.r.cmd(Path(__file__).with_suffix('.lua').read_text(encoding='utf-8'),
                   'CSC_AdjacencyGameplay','install-own-first-acquisition')

    def inherit_confirmed(self,parent):
        result=super().inherit_confirmed(parent)
        rows=[json.loads(x)for x in (Path(parent)/'service-actions.ndjson').read_text().splitlines()]
        begun={};closed={};no_effect={}
        for row in rows:
            if row['event']=='funded-acquisition-begin':begun[row['request']['token']]=row
            if row['event']=='funded-acquisition-confirmed':
                token=row['request']['token'];assert token not in closed;closed[token]=row
            if row['event']=='funded-acquisition-reconciled-no-effect':
                token=row['token'];proof=row['proof']
                assert all(proof.get(k)is True for k in ('verified','ledger_absent','gold_unchanged','owner_unchanged','price_unchanged','read_only_preflight_failure')),'Invalid no-effect proof'
                assert proof['failed_token']==token and token not in no_effect
                no_effect[token]=row
        assert not(closed.keys()&no_effect.keys()),'Closed effect cannot also be cancelled'
        assert begun.keys()==closed.keys()|no_effect.keys(),'Unconfirmed funded acquisition; reconcile separately'
        # Import historic donated spending as well, without reclassifying its
        # grants or retroactively claiming the new policy was active.
        for row in rows:
            if row['event']not in ('donated-acquisition-confirmed','funded-acquisition-confirmed'):continue
            q=row['request'];receipt=row['receipt'];turn=receipt['turn']
            key=f"{q['player']}:{q['city']}:{q['quarter']}:{q['source']}"
            for step in receipt['steps']:
                self.planner.purchases.append((q['player'],q['city'],turn,step['price']))
                self.planner.site_spend[key]=self.planner.site_spend.get(key,0)+step['price']
            if row['event']=='funded-acquisition-confirmed':
                assert receipt['status']=='confirmed'
                assert receipt['final_gold']==receipt['original_gold']+receipt['donated']-receipt['spent']
                assert receipt['own_gold_spent']==receipt['spent']-receipt['donated']
                self.grants+=receipt['donated'];self.spent+=receipt['spent'];self.tiles+=len(receipt['steps'])
        result.update(spent=self.spent,donated=self.grants,tiles=self.tiles,
                      acquisitions=result['acquisitions']+len(closed))
        self.record('funded-history-inherited',**result)
        return result

    def cycle(self,adapter,turn):
        actions=[];catalog=[];used_players=set();used_cities=set()
        for key,city in sorted(adapter.cities.items()):
            if self.planner.wide_due(*key,turn):
                rows=self.city_candidates(adapter,key,turn)
                self.write(self.root/'both-opportunities'/f'{turn:03d}-{key[0]}-{key[1]}.json',
                           dict(turn=turn,candidates=[asdict(c)for c in rows],funding_mode='own_first_shortfall_fallback'))
                self.planner.update(*key,turn,rows)
        # Across cities choose the best material opportunity first. Every action
        # uses this turn's expanded fresh footprint, not cached prices or funds.
        choices=[]
        for key,marks in sorted(self.planner.cache.items()):
            if key not in adapter.cities:continue
            current=self.city_candidates(adapter,key,turn)
            for old in marks:
                c=next((x for x in current if x.key==old.key),None)
                if c is not None:choices.append(c)
        choices.sort(key=self.planner.material_rank)
        for c in choices:
            key=(c.player,c.city);identity=(*key,c.quarter)
            if identity in self.completed:continue
            budget=adapter.budget(c.player);plan=funding(c,budget,self.planner,turn)
            snapshot=budget_snapshot(c,budget,self.planner,turn)
            snapshot['diagnostic_overrides']=['next_step_affordability_shortfall']if plan['grant']else []
            snapshot['funding_mode']='own_first_shortfall_fallback'
            catalog.append(dict(candidate=asdict(c),budget=snapshot,funding=plan))
            if key in used_cities:continue
            if c.missing_tiles:
                if c.player in used_players or plan['action']!='acquire':continue
                if not adapter.cities[key]['district_state'][c.quarter]['can_produce']:continue
                token=f'funded-v13:{turn}:{c.site_key}:{c.purchase_plot}'
                request=dict(enabled=True,token=token,turn=turn,player=c.player,city=c.city,
                    source=c.plot,quarter=c.quarter,plot=c.purchase_plot,materials=list(c.plan_materials),
                    route=list(c.missing_tiles),connectors=list(c.plan_connectors),price=c.price,
                    gold=budget.gold,reserve=plan['reserve'],own_gold=plan['own_gold'],grant=plan['grant'],
                    remaining_cap=plan['remaining_cap'],cashflow_observed=budget.cashflow_observed,
                    net_income=budget.net_income,maintenance=budget.maintenance)
                stem=f'{turn:03d}-{c.player}-{c.city}-{c.quarter}-{c.purchase_plot}'
                self.write(self.root/'funded-acquisitions'/(stem+'-before.json'),dict(request=request,budget=snapshot,funding=plan))
                self.record('funded-acquisition-begin',request=request,budget=snapshot,funding=plan)
                self.planner.pending_players.add(c.player)
                receipt=parse(self.r.cmd('CSC_FUNDED_ACQUISITION.Begin('+self.lua(request)+');',
                    'CSC_AdjacencyGameplay','funded-begin-'+stem),'CSC_FUNDED_RECEIPT')
                for attempt in range(16):
                    if receipt['status']=='confirmed':break
                    receipt=parse(self.r.cmd('CSC_FUNDED_ACQUISITION.Advance('+self.lua({'token':token})+');',
                        'CSC_AdjacencyGameplay','funded-stage-'+stem+'-'+str(attempt)),'CSC_FUNDED_RECEIPT')
                assert receipt['status']=='confirmed','Ambiguous funded acquisition; preserve without resending'
                assert receipt['turn']==turn and receipt['spent']==c.price
                assert receipt['original_gold']==budget.gold and receipt['donated']==plan['grant']
                assert receipt['final_gold']==budget.gold+plan['grant']-c.price
                assert receipt['own_gold_spent']==plan['own_gold']
                self.write(self.root/'funded-acquisitions'/(stem+'-receipt.json'),receipt)
                self.record('funded-acquisition-confirmed',request=request,receipt=receipt,budget=snapshot,funding=plan)
                self.planner.pending_players.discard(c.player)
                self.planner.purchases.append((c.player,c.city,turn,c.price))
                self.planner.site_spend[c.site_key]=self.planner.site_spend.get(c.site_key,0)+c.price
                self.grants+=receipt['donated'];self.spent+=c.price;self.tiles+=1
                used_players.add(c.player);used_cities.add(key)
                actions.append(dict(action='funded_acquisition_confirmed',receipt=receipt,funding=plan))
                self.planner.cache.pop(key,None);self.planner.scan_turn.pop(key,None)
                adapter.collect(turn)
                c=next((x for x in self.city_candidates(adapter,key,turn)
                        if x.plot==c.plot and x.quarter==c.quarter and not x.missing_tiles),None)
                if c is None:continue
            # Keep the Both-only diagnostic foundation rule. Partial routes
            # remain real owned land; later turns discover their remaining steps.
            if c.current_legal and not c.missing_tiles:
                self.record('foundation-begin',player=c.player,city=c.city,quarter=c.quarter,plot=c.plot,turn=turn)
                proof=adapter.place_zero(c)
                assert proof['verified']and proof['progress_before']==proof['progress_after']==0 and proof['native_incomplete']and proof['queue_unchanged']
                self.completed.add(identity);self.foundations+=1;used_cities.add(key)
                self.record('foundation-confirmed',player=c.player,city=c.city,quarter=c.quarter,plot=c.plot,turn=turn,proof=proof,donation_diagnostic=True,funding_mode='own_first_shortfall_fallback')
                actions.append(dict(action='foundation_confirmed',player=c.player,plot=c.plot,quarter=c.quarter))
        self.write(self.root/'decisions'/f'turn-{turn:03d}.json',dict(turn=turn,opportunities=catalog,actions=actions,
            mode='own_first_shortfall_fallback',donation_cutoff=None,strategy_matching=False))
        return actions
