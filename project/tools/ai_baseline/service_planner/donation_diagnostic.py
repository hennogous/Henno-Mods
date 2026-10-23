"""Opt-in donated-gold Both-site experiment, separate from ordinary policy.

The normal wallet is measured before any grant. Budget rules are observed, not
applied to this diagnostic. Assisted assignment is never reported as a native
CityManager purchase command. Only the maintained adapter places foundations.
"""
from dataclasses import asdict,replace
from pathlib import Path
import heapq,itertools,json,math,os
from .observations import build_material_candidates
from .policy import Planner,Policy
from .native_adapter import parse

def route(tiles,player,required):
    """Join up to three required plots to owned land, including connectors.

    Only revealed, unowned, quoted plots in the city's actual three-tile range
    may be added. The runtime bridge independently checks native purchase reach
    at each step. Foreign land and unknown costs cannot become free connectors.
    """
    required=set(required)
    if not required:return ()
    nodes={i:p for i,p in tiles.items()if p.get('revealed')and p.get('owner')in(-1,player)
           and(p['owner']==player or p.get('within_city_reach'))}
    if not required<=nodes.keys():return None
    owned={i for i,p in nodes.items()if p['owner']==player}
    if not owned:return None
    def path(target,added):
        if target in owned|added:return ()
        heap=[(0,0,(),i)for i in sorted(owned|added)];heapq.heapify(heap);seen={}
        while heap:
            cost,n,seq,i=heapq.heappop(heap)
            if i in seen:continue
            seen[i]=(cost,n)
            if i==target:return seq
            for j in nodes[i].get('neighbors',()):
                if j not in nodes or j in seen:continue
                extra=j not in owned|added
                if extra and not seq and not added and not nodes[j].get('native_purchasable'):continue
                # Missing future native prices are a route-ranking penalty,
                # never zero gold or an invented quote. Requote after each buy.
                quoted=nodes[j].get('price',0)
                heapq.heappush(heap,(cost+((quoted if quoted>0 else 10000)if extra else 0),n+extra,seq+((j,)if extra else()),j))
        return None
    options=[]
    for order in itertools.permutations(sorted(required)):
        added=set();sequence=[]
        for target in order:
            seq=path(target,added)
            if seq is None:break
            for i in seq:
                if i not in added:sequence.append(i);added.add(i)
        else:
            if sequence and(tiles[sequence[0]].get('price',0)<=0 or not tiles[sequence[0]].get('native_purchasable')):continue
            options.append((sum(tiles[i].get('price',0)<=0 for i in added),sum(max(0,tiles[i].get('price',0))for i in added),len(added),tuple(sequence)))
    return min(options)[3]if options else None

def candidates(city):
    out=[];tiles={p['index']:p for p in city['tiles']}
    for c in build_material_candidates(city,stepwise=False):
        if c.base<1 or c.specialty<1 or c.frontier_danger:continue
        seq=route(tiles,c.player,c.missing_tiles)
        # An unrouteable Both opportunity stays a visible watch, never a grant.
        if seq is None:out.append(replace(c,purchase_plot=None,native_purchasable=False,remaining_price=0));continue
        required=set(c.missing_tiles);price=sum(tiles[i]['price']for i in seq)if all(tiles[i].get('price',0)>0 for i in seq)else 0
        out.append(replace(c,missing_tiles=seq,plan_connectors=tuple(i for i in seq if i not in required),
                           purchase_plot=seq[0]if seq else None,price=tiles[seq[0]]['price']if seq else 0,
                           remaining_price=price,stepwise=True,source_owned=tiles[c.plot]['owner']==c.player,
                           native_purchasable=bool(seq and tiles[seq[0]].get('native_purchasable'))))
    return out

def budget_snapshot(c,budget,planner,turn):
    p=planner.policy;reserve=max(p.minimum_reserve,budget.emergency_reserve,math.ceil(max(0,-budget.net_income)*p.deficit_reserve_turns))
    d=planner.evaluate(c,{},budget,turn)
    total=c.remaining_price if not c.missing_tiles or c.remaining_price>0 else None
    return dict(original_gold=budget.gold,quoted_total=total,quoted_total_known=total is not None,quoted_first_step=c.price,
                net_income=budget.net_income,maintenance=budget.maintenance,cashflow_observed=budget.cashflow_observed,
                reserve=reserve,spendable=budget.available(p),raw_total_affordable=budget.gold>=total if total is not None else None,
                complete_route_preserves_reserve=budget.gold-total>=reserve if total is not None else None,
                whole_route_within_80pct_surplus=total<=math.floor(.8*budget.available(p))if total is not None else None,
                whole_route_within_300cap=total<=300 if total is not None else None,
                ordinary_next_action=d.action,ordinary_next_reason=d.reason,ordinary_next_max_price=d.max_price,
                ordinary_policy=asdict(p),scope='Same-boundary shadow budget, not a no-assistance counterfactual game',
                diagnostic_overrides=['affordability','reserve','spending caps','one-step-per-turn scheduling'],
                route=list(c.missing_tiles),connectors=list(c.plan_connectors))

class Diagnostic:
    def __init__(self,runner,root,write,lua):
        self.r=runner;self.root=Path(root);self.write=write;self.lua=lua
        self.planner=Planner(Policy.material_first_v2(max_connectors=2));self.attempted=set();self.completed=set()
        self.grants=0;self.spent=0;self.tiles=0;self.foundations=0
        self.journal=self.root/'service-actions.ndjson'
        assert not self.journal.exists(),'Fresh diagnostic only; recovery must reconcile its exact ledger'
    def record(self,event,**data):
        with self.journal.open('a',encoding='utf-8')as f:
            f.write(json.dumps(dict(event=event,**data))+'\n');f.flush();os.fsync(f.fileno())
    def inherit_confirmed(self,parent):
        """Warm same-process continuation: retain receipts, never replay actions.

        The caller separately proves the native world/treasury/ledger unchanged.
        An unconfirmed economic or foundation begin blocks this simple handoff.
        """
        parent=Path(parent);text=(parent/'service-actions.ndjson').read_text(encoding='utf-8')
        rows=[json.loads(x)for x in text.splitlines()];begins=set();confirmed=set();sites=set();placed=set()
        for row in rows:
            event=row['event']
            if event=='donated-acquisition-begin':begins.add(row['request']['token'])
            if event=='donated-acquisition-confirmed':
                q=row['request'];token=q['token'];receipt=row['receipt']
                assert token not in confirmed and receipt['status']=='confirmed'
                assert receipt['original_gold']==receipt['final_gold']and receipt['spent']==receipt['donated']
                confirmed.add(token);self.attempted.add((q['player'],q['city'],q['quarter']))
                self.grants+=receipt['donated'];self.spent+=receipt['spent'];self.tiles+=len(receipt['steps'])
            if event=='foundation-begin':sites.add((row['player'],row['city'],row['quarter'],row['plot']))
            if event=='foundation-confirmed':
                key=(row['player'],row['city'],row['quarter'],row['plot'])
                assert key not in placed and row['proof']['verified'];placed.add(key)
                self.completed.add(key[:3]);self.foundations+=1
        assert begins==confirmed,'Unconfirmed acquisition: reconcile separately before continuation'
        assert sites==placed,'Unconfirmed foundation: reconcile separately before continuation'
        self.journal.write_text(text,encoding='utf-8')
        result=dict(parent=str(parent),acquisitions=len(confirmed),foundations=len(placed),tiles=self.tiles,donated=self.grants,spent=self.spent,replayed_native_actions=0)
        self.record('confirmed-history-inherited',**result)
        return result
    def install(self):
        self.r.cmd(Path(__file__).with_name('donation_bridge.lua').read_text(encoding='utf-8'),'PlotInfo','install-donation-UI-bridge')
        self.r.cmd(Path(__file__).with_name('donation_transaction.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','install-donation-transaction')
    def city_candidates(self,adapter,key,turn):
        city=adapter.cities[key]
        if not getattr(adapter,'delta_mode',False):return candidates(dict(city,turn=turn))
        if not hasattr(self,'_delta_candidates'):self._delta_candidates={}
        cached=self._delta_candidates.get(key)
        if cached is None or cached[0]is not city['tiles']:
            cached=(city['tiles'],candidates(dict(city,turn=turn)));self._delta_candidates[key]=cached
        return [replace(c,observed_turn=turn)for c in cached[1]]
    def cycle(self,adapter,turn):
        results=[]
        for key,city in sorted(adapter.cities.items()):
            if self.planner.wide_due(*key,turn):
                rows=self.city_candidates(adapter,key,turn)
                self.write(self.root/'both-opportunities'/f'{turn:03d}-{key[0]}-{key[1]}.json',dict(turn=turn,candidates=[asdict(x)for x in rows],budgets=[budget_snapshot(x,adapter.budget(key[0]),self.planner,turn)for x in rows]))
                usable=[x for x in rows if not x.missing_tiles or(x.purchase_plot is not None and x.price>0)]
                self.planner.update(*key,turn,usable or rows)
        catalog=[]
        for key,marks in sorted(self.planner.cache.items()):
            if key not in adapter.cities:continue
            for old in marks:
                # Earlier Quarter actions in this same city can acquire a
                # shared connector/material; never reuse their old cost/owner.
                freshrows=self.city_candidates(adapter,key,turn)
                c=next((x for x in freshrows if x.plot==old.plot and x.quarter==old.quarter and x.plan_materials==old.plan_materials),None)
                if c is None:continue
                snapshot=budget_snapshot(c,adapter.budget(c.player),self.planner,turn)
                catalog.append(dict(candidate=asdict(c),budget=snapshot))
                identity=(c.player,c.city,c.quarter)
                if identity in self.completed:continue
                if c.missing_tiles:
                    if identity in self.attempted or c.purchase_plot is None or c.price<=0:continue
                    # A capacity/prerequisite failure is observed, not bypassed.
                    if not adapter.cities[key]['district_state'][c.quarter]['can_produce']:continue
                    token=f'donated-both-v5:{turn}:{c.site_key}'
                    tiles={x['index']:x for x in adapter.cities[key]['tiles']}
                    unknown=[i for i in c.missing_tiles if tiles[i].get('price',0)<=0]
                    known=sum(max(0,tiles[i].get('price',0))for i in c.missing_tiles)
                    request=dict(enabled=True,token=token,turn=turn,player=c.player,city=c.city,source=c.plot,
                                 quarter=c.quarter,materials=list(c.plan_materials),route=list(c.missing_tiles),
                                 initial_total=known,initial_quote_complete=not unknown,unknown_quote_tiles=unknown,original_gold=snapshot['original_gold'])
                    self.write(self.root/'acquisitions'/f'{turn:03d}-{c.player}-{c.city}-{c.quarter}-before.json',dict(request=request,budget=snapshot))
                    self.record('donated-acquisition-begin',request=request,budget=snapshot)
                    self.attempted.add(identity)
                    raw=self.r.cmd('CSC_DONATION.Begin('+self.lua(request)+');','CSC_AdjacencyGameplay','donated-begin-'+str(turn)+'-'+c.site_key)
                    receipt=parse(raw,'CSC_DONATION_RECEIPT');waits=0
                    for step in range(len(c.missing_tiles)*5+20):
                        if receipt['status']=='confirmed':break
                        raw=self.r.cmd('CSC_DONATION.Advance('+self.lua({'token':token})+');','CSC_AdjacencyGameplay','donated-stage-'+str(turn)+'-'+str(step)+'-'+c.site_key)
                        receipt=parse(raw,'CSC_DONATION_RECEIPT')
                        waits=waits+1 if receipt['status']in('awaiting_UI','awaiting_ownership')else 0
                        assert waits<6,'Staged acquisition did not become observable; preserve, never resend assignment'
                    else:raise RuntimeError('Bounded acquisition stages exhausted')
                    self.write(self.root/'acquisitions'/f'{turn:03d}-{c.player}-{c.city}-{c.quarter}-receipt.json',receipt)
                    assert receipt['status']=='confirmed',receipt
                    assert receipt['original_gold']==receipt['final_gold'] and receipt['turn']==turn
                    # A native price for a disconnected tile may become known
                    # only after a connector. Compare the realized complete cost
                    # against the frozen PREGRANT wallet, never the donated one.
                    snapshot['realized_total']=receipt['spent']
                    snapshot['realized_total_affordable_from_original_gold']=snapshot['original_gold']>=receipt['spent']
                    snapshot['realized_total_preserves_reserve']=snapshot['original_gold']-receipt['spent']>=snapshot['reserve']
                    snapshot['realized_total_within_80pct_surplus']=receipt['spent']<=math.floor(.8*snapshot['spendable'])
                    self.write(self.root/'acquisitions'/f'{turn:03d}-{c.player}-{c.city}-{c.quarter}-completed-budget.json',snapshot)
                    self.grants+=receipt['donated'];self.spent+=receipt['spent'];self.tiles+=len(receipt['steps'])
                    self.record('donated-acquisition-confirmed',request=request,receipt=receipt,budget=snapshot)
                    # Existing placement transport/legality/progress checks are
                    # reused after every acquired source and material is real.
                    self.planner.cache.pop(key,None);self.planner.scan_turn.pop(key,None)
                    adapter.collect(turn)
                    c=next((x for x in candidates(dict(adapter.cities[key],turn=turn))if x.plot==c.plot and x.quarter==c.quarter and not x.missing_tiles),None)
                    assert c is not None and c.base>0 and c.specialty>0,'Acquired Both plan not present'
                    results.append(dict(action='donated_acquisition_confirmed',receipt=receipt))
                if c.current_legal and not c.missing_tiles:
                    self.record('foundation-begin',player=c.player,city=c.city,quarter=c.quarter,plot=c.plot,turn=turn)
                    proof=adapter.place_zero(c)
                    assert proof['verified']and proof['progress_before']==proof['progress_after']==0 and proof['native_incomplete']and proof['queue_unchanged']
                    self.completed.add(identity);self.foundations+=1
                    self.record('foundation-confirmed',player=c.player,city=c.city,quarter=c.quarter,plot=c.plot,turn=turn,proof=proof,donation_diagnostic=True)
                    results.append(dict(action='foundation_confirmed',plot=c.plot,player=c.player,quarter=c.quarter))
        self.write(self.root/'decisions'/f'turn-{turn:03d}.json',dict(turn=turn,opportunities=catalog,actions=results,mode='donated_gold_both_diagnostic',strategy_matching=False))
        return results
