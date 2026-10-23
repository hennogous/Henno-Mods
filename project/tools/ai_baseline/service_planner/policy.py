"""Pure policy. No game connection, gold/ownership writer or import side effect."""
from dataclasses import dataclass, field
import math


@dataclass(frozen=True)
class Service:
    quarter: str
    need: str
    stage: int
    civic: str
    venues: tuple[str, ...]
    requires_specialty: bool = False
    naval_era_limit: int | None = None


# These identify actual Service hosts, not all goods-sales customers.
PROFILES = {
    'storekeeper': Service('BAKERS', 'growth', 2, 'CIVIC_FEUDALISM', ('BUILDING_GRANARY',)),
    'innkeeper': Service('BAKERS', 'housing', 3, 'CIVIC_MEDIEVAL_FAIRES', ('BUILDING_MARKET',)),
    'dockmaster': Service('TAILORS', 'naval', 2, 'CIVIC_NAVAL_TRADITION', ('BUILDING_LIGHTHOUSE',), naval_era_limit=3),
    'sacristan': Service('TAILORS', 'religion', 3, 'CIVIC_DIVINE_RIGHT', ('BUILDING_TEMPLE',)),
    'groundskeeper': Service('BAKERS', 'culture', 4, 'CIVIC_URBANIZATION', ('BUILDING_ZOO',), True),
    'ride_technician': Service('BAKERS', 'culture', 4, 'CIVIC_URBANIZATION', ('BUILDING_FERRIS_WHEEL',), True),
    'stage_manager': Service('TAILORS', 'culture', 4, 'CIVIC_OPERA_BALLET', ('BUILDING_AMPHITHEATER',), True),
    'performance_venue': Service('TAILORS', 'culture', 4, 'CIVIC_OPERA_BALLET', ('BUILDING_BOLSHOI_THEATRE', 'BUILDING_BROADWAY', 'BUILDING_SYDNEY_OPERA_HOUSE'), True),
}


@dataclass(frozen=True)
class Need:
    strength: float
    confidence: float
    evidence: str

    def __post_init__(self):
        assert all(math.isfinite(v) and 0 <= v <= 1 for v in (self.strength, self.confidence))
        assert self.evidence, 'An inferred need must name its evidence'


@dataclass(frozen=True)
class Candidate:
    player: int
    city: int
    plot: int
    quarter: str
    base: int
    specialty: int
    service: str | None = None
    venue_ready: bool = False
    research_ready: bool = False
    producer_ready: bool = False
    # Estimates must be supplied from actual chain dependencies, not assumed zero.
    ready_in_turns: int = 999
    confidence: float = 0.5
    dependencies_owned_or_in_purchase: bool = False
    missing_tiles: tuple[int, ...] = ()
    purchase_plot: int | None = None
    price: int = 0
    revealed: bool = False
    material_visible: bool = False
    potential_legal: bool = False
    current_legal: bool = False
    native_purchasable: bool = False
    same_quarter_present: bool = False
    eligible_ai: bool = False
    human: bool = False
    frontier_danger: bool = False
    displacement_cost: float = 0
    natural_border_in_turns: int | None = None
    era: int = 0
    material_plots: tuple[int, ...] = ()
    customer_plot: int | None = None
    observed_turn: int = 0
    # Native collectors set this False if any projection could not be checked.
    native_projection_verified: bool = False
    # Material-first plans retain identity while their missing tiles become owned.
    plan_materials: tuple[int, ...] = ()
    remaining_price: int = 0
    purchase_base: int = 0
    purchase_specialty: int = 0

    established: bool = False
    owned_base: int = 0
    owned_specialty: int = 0
    source_owned: bool = False
    stepwise: bool = False
    plan_connectors: tuple[int, ...] = ()

    @property
    def site_key(self):
        return f'{self.player}:{self.city}:{self.quarter}:{self.plot}'

    @property
    def key(self):
        suffix = ':' + ','.join(map(str,self.plan_materials)) if self.plan_materials else ''
        return f'{self.player}:{self.city}:{self.quarter}:{self.plot}:{self.service or "general"}'+suffix

    @property
    def footprint(self):
        return frozenset((self.plot, *self.material_plots, *self.missing_tiles))


@dataclass(frozen=True)
class Policy:
    stepwise: bool = False
    max_connectors: int = 0
    objective: str = 'services'
    minimum_reserve: int = 150
    deficit_reserve_turns: int = 10
    strong_fraction: float = .25
    general_fraction: float = .08
    strong_cost_cap: int = 200
    general_cost_cap: int = 60
    strong_need: float = .8
    strong_confidence: float = .75
    near_term_horizon: int = 20
    city_purchase_cooldown: int = 10
    player_purchase_window: int = 5
    player_purchase_cap: int = 2
    wide_scan_interval: int = 5

    @classmethod
    def material_first(cls):
        return cls(objective='materials',strong_fraction=.5,strong_cost_cap=300,
                   general_fraction=0,general_cost_cap=0,
                   city_purchase_cooldown=1,player_purchase_cap=3)

    @classmethod
    def material_first_v2(cls,*,max_connectors=0):
        # Opt-in calibrated wallet policy; v1 remains available for provenance.
        assert isinstance(max_connectors,int)and 0<=max_connectors<=2
        return cls(objective='materials',stepwise=True,max_connectors=max_connectors,minimum_reserve=25,
                   strong_fraction=.8,strong_cost_cap=300,general_fraction=0,
                   general_cost_cap=0,city_purchase_cooldown=1,player_purchase_cap=3)


@dataclass(frozen=True)
class Budget:
    gold: int
    net_income: float = 0
    emergency_reserve: int = 0
    maintenance: float = 0
    cashflow_observed: bool = True

    def __post_init__(self):
        assert self.gold >= 0 and self.emergency_reserve >= 0
        assert all(math.isfinite(x)for x in (self.gold,self.net_income,self.emergency_reserve))

    def available(self, policy):
        reserve = max(policy.minimum_reserve, self.emergency_reserve,
                      math.ceil(max(0, -self.net_income) * policy.deficit_reserve_turns))
        return max(0, self.gold - reserve)


@dataclass(frozen=True)
class Decision:
    candidate: Candidate
    action: str
    tier: str
    score: float
    reason: str
    max_price: int = 0


class Planner:
    """Cache plans; events mark cities dirty, safe turn boundaries choose actions."""
    def __init__(self, policy=Policy()):
        self.policy = policy
        self.cache = {}
        self.scan_turn = {}
        self.dirty = set()
        self.purchases = []
        self.pending_players = set()
        self.site_spend = {}

    def mark_dirty(self, player, city):
        self.dirty.add((player, city))

    def wide_due(self, player, city, turn):
        key = (player, city)
        return key not in self.cache or turn - self.scan_turn[key] >= self.policy.wide_scan_interval

    def update(self, player, city, turn, candidates):
        assert all(c.player == player and c.city == city for c in candidates)
        if self.policy.objective=='materials':
            # Mark one preferred site/chain per Quarter at the broad scan. Do
            # not consume its district slot on a weaker owned site while its
            # better Both location is waiting for ownership or purchase range.
            ranked=sorted(candidates,key=self.material_rank)
            marked={}
            for c in ranked:marked.setdefault(c.quarter,c)
            candidates=tuple(marked.values())
        self.cache[player, city] = tuple(candidates)
        self.scan_turn[player, city] = turn
        self.dirty.discard((player, city))

    def evaluate(self, c, needs, budget, turn):
        p = self.policy
        def no(reason): return Decision(c, 'reject', 'none', 0, reason)
        if not c.eligible_ai or c.human or c.player < 0: return no('not an eligible AI')
        if c.same_quarter_present and not(p.stepwise and c.established): return no('same Quarter already placed')
        if c.base < 1: return no('no Base supply in this chain')
        if not c.revealed or not c.material_visible: return no('unrevealed site or undiscovered material')
        if not c.potential_legal: return no('invalid projected site')
        if not c.dependencies_owned_or_in_purchase: return no('unfunded material/customer dependency')
        if p.objective=='materials':return self.evaluate_material(c,budget,turn)
        if not 0 <= c.confidence <= 1: return no('invalid chain confidence')
        service = PROFILES.get(c.service)
        if c.service and service is None: return no('unknown Service')
        if service and service.quarter != c.quarter: return no('Service/Quarter mismatch')
        if service and service.requires_specialty and c.specialty < 1: return no('stage4 lacks Specialty')
        need = needs.get(service.need) if service else None
        if service and service.naval_era_limit is not None and c.era > service.naval_era_limit:
            # Admiral points may remain useful, but the v1 naval-production route
            # no longer qualifies for aggressive purchasing after Renaissance.
            need = None
        fit = need.strength * min(need.confidence, c.confidence) if need else 0
        strong = bool(service and need and need.strength >= p.strong_need
                      and min(need.confidence, c.confidence) >= p.strong_confidence
                      and c.venue_ready and c.research_ready
                      and c.ready_in_turns <= p.near_term_horizon)
        tier = 'strong_service' if strong else 'general'
        # Material ranking is subordinate to a useful Service, not universal Both.
        score = 100 * fit + 4 * c.base + min(c.specialty, 4) - c.displacement_cost
        score -= min(c.ready_in_turns, 50) * .2 if service else 0
        if not c.missing_tiles:
            return Decision(c, 'place' if c.current_legal else 'watch', tier, score,
                            'owned and native-legal' if c.current_legal else 'wait for native legality')
        if len(c.missing_tiles) != 1 or c.purchase_plot != c.missing_tiles[0]:
            return Decision(c, 'watch', tier, score, 'v1 buys only one final missing tile')
        if not c.native_projection_verified:
            return Decision(c, 'watch', tier, score, 'native post-purchase projection unverified')
        if c.frontier_danger: return no('contested or unsafe frontier')
        if c.natural_border_in_turns is not None and c.natural_border_in_turns <= 2:
            return Decision(c, 'watch', tier, score, 'natural border acquisition imminent')
        if not c.native_purchasable: return Decision(c, 'watch', tier, score, 'not native-purchasable now')
        if c.price <= 0: return no('missing native price')
        if c.player in self.pending_players: return no('purchase awaiting readback')
        if any(pid == c.player and city == c.city and turn - t < p.city_purchase_cooldown
               for pid, city, t, amount in self.purchases): return no('city purchase cooldown')
        recent = [(t, cost) for pid, city, t, cost in self.purchases
                  if pid == c.player and 0 <= turn - t < p.player_purchase_window]
        if len(recent) >= p.player_purchase_cap: return no('player purchase cap')
        available = budget.available(p)
        fraction = p.strong_fraction if strong else p.general_fraction
        cap = p.strong_cost_cap if strong else p.general_cost_cap
        # Spend history also consumes the current rolling allowance. This is
        # conservative when the fresh balance already reflects earlier costs.
        limit = max(0, min(cap, math.floor(available * fraction)) - sum(v for _, v in recent))
        action = 'purchase' if c.price <= limit else 'watch'
        return Decision(c, action, tier, score, 'within purchase allowance' if action == 'purchase'
                        else 'price exceeds purchase allowance', limit)

    @staticmethod
    def material_rank(c):
        return (-(c.base>0 and c.specialty>0),-c.base,-c.specialty,
                len(c.missing_tiles),c.remaining_price,c.displacement_cost,
                c.player,c.city,c.plot,c.plan_materials)

    def evaluate_material(self,c,budget,turn):
        p=self.policy
        both=c.base>0 and c.specialty>0
        # The selection key, rather than this diagnostic score, owns the strict
        # lexicographic order: Both, Base count, Specialty count.
        score=10000*int(both)+100*c.base+c.specialty
        def result(action,reason,limit=0):
            return Decision(c,action,'both_materials'if both else 'base_only',score,reason,limit)
        if c.service:return result('reject','Service matching disabled in material-first mode')
        if c.frontier_danger:return result('reject','contested or unsafe frontier')
        if p.stepwise and not c.established and c.current_legal and c.source_owned and c.owned_base>0:
            return result('place','owned source + Base; retain Both material acquisition plan')
        if p.stepwise and c.established and not c.missing_tiles:
            return result('watch','established and fully owned supply; monitor improvements/pillage')
        if not c.missing_tiles:
            return result('place'if c.current_legal else 'watch',
                          'owned and native-legal'if c.current_legal else 'wait for native legality')
        if not both:return result('watch','purchases reserved for Base + Specialty plans')
        if not p.max_connectors and len(c.missing_tiles)>3:return result('watch','more than three acquisition tiles')
        if len(c.plan_connectors)>p.max_connectors or len(c.missing_tiles)>3+p.max_connectors:return result('watch','acquisition route exceeds bounded steps')
        if c.purchase_plot not in c.missing_tiles:return result('watch','wait for native purchase reach')
        if not c.native_projection_verified:return result('watch','native source projection unverified')
        if not c.native_purchasable or c.price<=0:return result('watch','not native-purchasable now')
        if c.natural_border_in_turns is not None and c.natural_border_in_turns<=2:
            return result('watch','natural border acquisition imminent')
        if c.player in self.pending_players:return result('reject','purchase awaiting readback')
        recent=[(t,cost)for pid,city,t,cost in self.purchases
                if pid==c.player and 0<=turn-t<p.player_purchase_window]
        if any(pid==c.player and city==c.city and turn-t<p.city_purchase_cooldown
               for pid,city,t,cost in self.purchases):return result('watch','city purchase cooldown')
        if len(recent)>=p.player_purchase_cap:return result('watch','player purchase cap')
        if p.stepwise:
            if not budget.cashflow_observed:return result('watch','cashflow unobserved')
            available=budget.available(p)
            limit=max(0,min(p.strong_cost_cap-sum(cost for t,cost in recent),math.floor(available*p.strong_fraction),p.strong_cost_cap-self.site_spend.get(c.site_key,0)))
            if c.price>limit:return result('watch','next step exceeds real-wallet allowance',limit)
            # Authorize only this freshly quoted step. Later route prices are
            # observations, not an admission gate or a promise to finish: after
            # each confirmed acquisition, refresh ownership, price and wallet.
            # Unknown quotes remain unknown; future income never funds a buy.
            return result('purchase','responsible step toward Both supply',limit)
        limit=max(0,min(p.strong_cost_cap,math.floor(budget.available(p)*p.strong_fraction))
                  -sum(cost for t,cost in recent))
        # Fund the known remaining chain, not just an attractive first tile.
        if c.remaining_price<=0 or c.remaining_price<c.price:return result('watch','unknown remaining chain cost',limit)
        return result('purchase'if c.remaining_price<=limit else 'watch',
                      'funded Both acquisition step'if c.remaining_price<=limit else 'remaining chain exceeds allowance',limit)

    def select(self, needs_by_city, budgets, turn, refresh, *, allowed_actions=None):
        """Refresh cheap facts before every decision, even when wide plans are cached."""
        choices = []
        allowed = {"purchase", "place"} if allowed_actions is None else set(allowed_actions)
        self.unavailable_decisions = []
        for key, candidates in sorted(self.cache.items()):
            if key[0]not in budgets:continue
            for stale in candidates:
                fresh = refresh(stale)
                if fresh is None: continue
                assert (fresh.player, fresh.city, fresh.plot, fresh.quarter, fresh.service) == (
                    stale.player, stale.city, stale.plot, stale.quarter, stale.service)
                assert fresh.observed_turn == turn, 'No action from stale native facts'
                d = self.evaluate(fresh, needs_by_city.get(key, {}), budgets[fresh.player], turn)
                if d.action in ('purchase', 'place'):
                    if d.action in allowed: choices.append(d)
                    else: self.unavailable_decisions.append(d)
        # Explicit decisions and deterministic ties, not an arbitrary global list.
        if self.policy.objective=='materials':
            choices.sort(key=lambda d:self.material_rank(d.candidate))
        else:choices.sort(key=lambda d: (-d.score, -d.candidate.base, -d.candidate.specialty,
                                    d.candidate.player, d.candidate.city, d.candidate.plot,
                                    d.candidate.service or ''))
        cities, district_tiles, dependencies, out = set(), set(), set(), []
        purchase_players = set()
        for d in choices:
            c = d.candidate
            key = (c.player, c.city)
            # Multiple Quarter types may share materials, but a new district
            # cannot consume another selected plan's supply or customer tile.
            supply = set(c.material_plots)
            if c.customer_plot is not None: supply.add(c.customer_plot)
            if key in cities or c.plot in district_tiles or c.plot in dependencies or supply & district_tiles: continue
            if d.action == 'purchase' and c.player in purchase_players: continue
            cities.add(key);district_tiles.add(c.plot);dependencies.update(supply);out.append(d)
            if d.action == 'purchase': purchase_players.add(c.player)
        self.dirty.clear()
        return out
