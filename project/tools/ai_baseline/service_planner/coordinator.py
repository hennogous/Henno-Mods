"""Small integration boundary for wide scans, cheap checks and existing0% placement."""
from .execution import PurchaseExecutor
from .policy import Planner


class Coordinator:
    def __init__(self, runner, journal, *, allow_mutations=False, boundary=None, policy=None, allow_ai_native_request_probe=False, purchase_capability=None):
        self.planner=Planner()if policy is None else Planner(policy)
        self.executor=PurchaseExecutor(self.planner,runner,journal,
                                       allow_mutations=allow_mutations,boundary=boundary,allow_ai_native_request_probe=allow_ai_native_request_probe)
        self.allow_mutations=allow_mutations
        # A reviewed unavailable execution path must not consume a city choice,
        # create a pending mutation, or prevent an independently legal foundation.
        self.purchase_capability = purchase_capability
        self.attempted_foundations=set()
        if self.executor.journal.exists():
            import json
            for line in self.executor.journal.read_text(encoding='utf-8').splitlines():
                e=json.loads(line)
                if e['event']=='foundation-begin':
                    self.attempted_foundations.add((e['player'],e['city'],e['quarter']))

    def event(self, player, city):
        # Do not purchase or place inside ownership/research/UI callbacks.
        self.planner.mark_dirty(player,city)

    def cycle(self, player, cities, turn, adapter):
        """Called at a safe player boundary, never by a raw UI event.

        Adapter methods: wide_candidates(player,city,turn), refresh(candidate),
        needs(player,city), budget(player), purchase_facts(candidate),
        purchase_readback(event), place_zero(candidate).
        wide_candidates may inspect revealed beyond-border land; refresh MUST
        return current native ownership, supply, customer, price and legality.
        place_zero is the validated driver's native/UI transaction, not a new
        production/grant mechanism. No game is launched by this coordinator.
        """
        if player in self.executor.pending:
            result=self.executor.reconcile(player,adapter.purchase_readback)
            if result['pending']:return [{'action':'pending_purchase','result':result}]
        for key in list(self.planner.cache):
            if key[0]==player and key[1]not in cities:
                self.planner.cache.pop(key);self.planner.scan_turn.pop(key,None)
        for city in cities:
            if self.planner.wide_due(player,city,turn):
                self.planner.update(player,city,turn,adapter.wide_candidates(player,city,turn))
        needs={(player,city):adapter.needs(player,city)for city in cities}
        blocked = self.purchase_capability is not None and self.purchase_capability.get('available') is False
        decisions=self.planner.select(needs,{player:adapter.budget(player)},turn,adapter.refresh,
                                      allowed_actions={'place'} if blocked and self.allow_mutations else None)
        results=[{'action':'purchase_unavailable','decision':d,'capability':self.purchase_capability}
                 for d in self.planner.unavailable_decisions]
        for d in decisions:
            c=d.candidate
            if not self.allow_mutations:
                results.append({'action':'proposal','decision':d});continue
            if d.action=='purchase':
                self.executor.request(d,needs[player,c.city],adapter.purchase_facts)
                results.append({'action':'pending_purchase','decision':d});continue
            identity=(c.player,c.city,c.quarter)
            if identity in self.attempted_foundations:
                results.append({'action':'already_attempted_foundation','decision':d});continue
            # Recheck after any earlier action; never act on stale selection.
            fresh=adapter.refresh(c)
            if fresh is None or fresh.key!=c.key or fresh.observed_turn!=turn:continue
            recheck=self.planner.evaluate(fresh,needs[player,c.city],adapter.budget(player),turn)
            if recheck.action!='place':continue
            assert self.executor.boundary is not None
            phase=self.executor.boundary()
            assert phase['turn']==turn and phase['autoplay_active']is False
            self.executor.record({'event':'foundation-begin','player':c.player,'city':c.city,
                                  'quarter':c.quarter,'plot':c.plot,'turn':turn})
            self.attempted_foundations.add(identity)
            result=adapter.place_zero(fresh)
            assert result['verified']and result['owner']==c.player and result['plot']==c.plot
            assert result['quarter']==c.quarter and result['progress_before']==result['progress_after']==0
            assert result['cost_before']==result['cost_after']and result['cost_after']>0
            assert result['native_incomplete']and result['queue_unchanged']
            self.executor.record({'event':'foundation-confirmed','player':c.player,'city':c.city,
                                  'quarter':c.quarter,'plot':c.plot,'turn':turn})
            self.planner.mark_dirty(c.player,c.city)
            results.append({'action':'foundation_confirmed','decision':d})
        return results
