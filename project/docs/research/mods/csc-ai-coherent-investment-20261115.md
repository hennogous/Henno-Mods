# Coherent Quarter investment across selection, acquisition and construction

Henno requests the Pella purchase/follow-through inconsistency be fixed. This
targets Problems1.5/1.6 and keeps current district/production competition intact.
The preceding frozen spatial comparison has completed250, saved, closed with
exit0 and restored preferences. Its continuation is a reload of the same seed;
its outcomes are separate from this new candidate.

## One valuation path

The complete-value adapter now accepts **named supplier-protection costs only**
from the earlier planner. It no longer imports the owned-only no-customer128
heuristic or other old site/readiness deltas. The central model prices the same
current income/cost rules on frontier and owned plots. Missing customer space
loses its layout preference and prospective transactions; ownership itself adds
no customer penalty. Named material losses are combined by maximum, so a later
positive heuristic cannot overwrite protection. Base/+2/profitability and
covering-own-material safeguards remain.

## Native-confirmed intent, rather than every proposal

`CSC_AI_PlanContinuity.lua` is registered inside main CSC. The publisher reads
the full bounded CE journal once before the next publication. A plan requires
a new-district `best` record, the current packet version, and the exact positive
complete bid from the previous accepted packet. Cache writes, proposals,
existing-district comparisons, unmatched prices and stale pages create no plan.
The policy does not depend on top16/top32 diagnostic receipt sampling.

One scalar Game property per player persists primitive plan records. There are
at most256 selected city/Quarter/plot records per player. Records expire40 rounds after the
confirmed choice, or15 after the owned phase begins; already-owned selections
start that phase immediately. These are conservative policy lifetimes, not a
universal native timeout. A new native best does not erase an older fixed-footprint request (AI-N131);
both selected sites retain their bounded memory independently. Customer planning
and offers exclude those retained Quarter footprints. Elsewhere customer cost
excludes the Quarter tile itself, which retains its separate displacement cost;
foundation, occupied footprint, ownership/city loss and physical changes are
handled explicitly. Published bids alone never renew intent.

## Stable footprint baseline, fresh economic forecast

A selected unworked Quarter footprint can be temporarily assigned a citizen
while it waits. For that bounded confirmed plan, keep its selected unworked
footprint-cost baseline instead of charging the newly assigned tile's full
income as a new loss. This applies both to initially owned plots and to native-
selected frontier plots once ownership is observed. The latter does not prove
payment; native Treasury receipts remain separate.

The raw facts remain unchanged. A copied valuation site excludes only its
`displaced:` flows. Current suppliers, customer footprints, building plans,
research, production, native yield prices and all other costs are recomputed.
Resource/improvement/terrain/feature changes disable the old baseline. Lost
Base or insufficient adjacency still withdraw immediately. There is no whole-
bid floor, sunk-Gold bonus or forced queue choice. A purchase invoice disappears
only when the footprint is owned.

The native cost excluded by a baseline is also priced diagnostically (at most
six cached yield quotes), logged as `currentDisplacementQ8`, and never added
back to the bid. This exposes the cost assumption rather than hiding it.

## Missing input and explicit withdrawal

A native-confirmed **owned** plan can use its last committed positive bid for
one missing-price/staffing publication, only with fresh Core quality, Base,
ownership/signature and protection checks. A carried bid is labelled, has no
invented current economic breakdown, offers no stale customer layout, and does
not renew its age or grace. Frontier purchases get no unpriced grace. Known
economic losses and safety failures withdraw immediately.

`CSC_AI_PLAN_EVENT` distinguishes confirmed comparison, observed acquisition,
memory expiry/release and withdrawn support. These are not native cancellation
receipts. `CSC_AI_PLAN_QUOTE_PROPOSED` records selected-plan cost components;
`CSC_AI_QUARTER_WITHDRAWAL_PROPOSED` explains removed offers, including economic,
material, displacement, invoice, legacy and data reasons. All confirmed intents
are covered; ordinary offer withdrawals are capped16/player/publication with
an omitted counter. Game properties update only when their encoded value changes.

Current CE does not expose cancellation of an already submitted PurchasePlot-
Contract. A real map change can therefore invalidate a pending native purchase.
This change fixes our inconsistent ownership transition and makes withdrawal
visible; it does not claim to cancel the native economic contract. Investigate
a purchase-consumption gate if subsequent evidence calls for it.

## Qualification

68 economic/SQL/spatial/lifecycle checks and18 publisher/package/observer checks
pass. Multi-turn tests use the real model and bid path for purchase→owned,
lost future-customer credit, temporary staffing, save/reload, expiry, one-turn
missing prices, real material/feature/ownership loss, foundation completion,
typed protection, complete-journal confirmation and stale-page rejection.
ModBuddy source actions regenerate and import the new module. The frozen test
packager adds reviewed AI modules to the accepted runtime file/import lists.

A saturated16384-record/256-page synthetic journal takes median23.5ms for Lua
parsing in five host samples. This excludes native serialization/crossing cost.
Live journal counts and controller wall times remain the practical overhead data.
No new CE hook, DLL or upstream PR is needed. WildW develop remains2986a746;
use the qualified400e6755 CE with XP2 SHA092abfbb.

Next: a fresh ordinary Continents/Small/Prince/Online50 with seeds18461107 and
29461107, the same CL/R2/Suk stack and only main CSC policy. Check native choice
confirmation, persisted ownership transition and the actual post-purchase
retained score. A positive quote need not beat better production alternatives.
Shared controller owns the game; artifact root is
`C:/Users/Shadow/Desktop/Codex/csc-ai-coherence-20261115/`.

## First live pass: acquisition fixed, signed-ID boundary caught

Candidate39bee15e, frozen01/fresh50-01 completes50, saves and closes/restores
exit0. The same Pella target1123 is selected24, pays30 Gold27 and becomes owned28.
Its complete bid remains positive28–31 (23527 then21195 Q8); the old owned-only
128 deduction is now explicitly ignored. On32 the log attributes withdrawal to
27813 Q8 worked-tile displacement, with one citizen on the footprint.

The new diagnostic identifies a boundary error: FootprintSignature used the
nonnegative cost reader, which rejected native -1 absence IDs. Its unknown
signature prevented baseline continuity from activating. Correct the identity
reader to retain signed integer IDs >=-1; missing/failed/invalid getters still
produce unknown. A direct real-Facts regression covers empty plots, resources,
invalid IDs and native getter failures. Plan events now expose their selected
worker baseline and signature. Repeat the same ordinary50 with frozen02 before
claiming live staffing continuity. No native score band or bonus is increased.
