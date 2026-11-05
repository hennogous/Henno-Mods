# Contribution ledger for the Mill/building study

This is a **source and rules inventory**, prepared 5 November 2026. It defines
what real CSC benefits a read-only native probe should look for. It contains
no new tuning and makes no claim that a particular effect contributed native
utility in this study. The historical phantom Mill result and the new local
unit-step implementation are different versions.

`contributions.json` is the machine-readable inventory: nineteen loaded building
definitions, twenty-two contribution groups, four shared valuation questions,
source hashes, profiles and the seven ordinary producers' active root IDs.
Large City Center bit families have explicit patterns/counts and previews;
their complete attached graph remains in the external raw evidence. No native
index is inferred from SQLite row order. The world collector must capture actual
`GameInfo` indexes before attachment.

## What is implemented

Only Bakers and Tailors Quarter actions use `UpdateDatabase`. The other six
Quarter actions are `DoNothing`. Carpenters contains a parked Joinery definition,
but it is not a loaded building or a completed chain.

| Ordinary producer | Base Production cost / maintenance | Independent intrinsic benefits |
|---|---|---|
| Wind Mill | 80 / 2 Gold | Local hills rule: +1 Quarter Production when functional. Machinery. |
| Water Mill | 80 / 2 Gold | Local river rule: floor(edges/2), max3 Quarter Production. Engineering + River Access. |
| Bakery | 160 / 2 Gold | One local amenity, one specialist slot; specialist yields2Food. Guilds + either Mill. |
| Café | 250 / 3 Gold | One amenity, regional range6; one slot yielding1Food1Culture when staffed. Humanism + either Mill. |
| Textile Workshop | 80 / 2 Gold | Material/local/customer exchanges below. Construction. |
| Tailor | 160 / 2 Gold | One local amenity, one slot yielding2Culture1Gold when staffed. Guilds + Workshop. |
| Fashion House | 250 / 3 Gold | One amenity, regional range6; one slot yielding1Culture2Gold when staffed. Humanism + Workshop. |

These are declared base costs, not Online-speed quotes, remaining work or native
Q8 utility. **All nineteen buildings have zero direct `Building_YieldChanges`
rows** in this snapshot; live modifiers still deliver real building income.
Specialist yields require citizens and are not passive income.

The twelve internal `MustPurchase` buildings are:

- Bakers River Access and No River Access flags.
- Bakers Storekeeper, Innkeeper, Groundskeeper and Ride Technician markers.
- Tailors Dockmaster, Sacristan, Stage Manager and three exact Wonder markers
  for Ballet Dancer/Bolshoi, Musical Actor/Broadway and Opera Singer/Sydney.

These cost/maintain zero and are not ordinary production choices. Source
effects live mainly on their producers; hidden marker slots and grant effects
must not be conflated with independent yield streams. Wonder markers have no
citizen slot; their synchronized placement script chooses the exact host plot
and retains establishment separately from current eligibility.

Optional Leugi Garden support adds a twentieth building, the Horticulturist.
It is absent from this snapshot. M&C adds conditional Industry/Corporation
interactions, not another CSC producer family. Those variants remain explicitly
separate from the core study.

## First questions to answer

1. **New local Mill steps:** confirm bounded contributions for Wind1/Water3,
   local-only gameplay yields, old-bit retirement and source/recipient context.
   Four active +1 children replace the old weighted attachments. Disconnected
   legacy definitions preserve IDs; they are not active candidate roots.
2. **Bakery/Café ordinary benefits:** attribute outgoing local Mill
   Production/Gold, incoming Food, legitimate amenities and later building
   propagation. Test whether the hypothetical absent-recipient capability
   credits both mutually exclusive Mill variants.
3. **Service owner gates:** attribute growth, housing, Tourism, GPP and grants
   separately. The known interpreter can omit owner/property/nested gates;
   positive value does not prove actual supply/civic/customer eligibility.
4. **Tailors as a contrasting family:** record its raw values and root totals
   during the same analysis window. Its Workshop has twenty active roots,
   **not twenty encoding bits**: twelve era×naval-class Dockmaster production
   wrappers plus eight material/local/customer/service/GPP/property roots.
5. **Current-state income channels:** distinguish actual per-building getters
   from City Center population/export consumers. Those consumers are not
   automatically in a proposed producer's own modifier vector.

The active ordinary root counts are Wind10, Water12, Bakery9, Café14,
Workshop20, Tailor7 and FashionHouse16. Hidden buildings have no own attached
building roots in this baseline. These are definitions/attachments, not proof
that all roots compile successfully or contribute nonzero utility.

## Material, customer and service distinctions

Ordinary material exchanges require actual improved matching resources. Mills
receive Food from Base; Café receives Food from Specialty. Tailors equivalents
receive Culture. Producers return Production/Gold to matching improvements.
The reverse wrappers use `PLAYER_IMPROVEMENTS`, unsupported in the inspected
hypothetical collection registry; this is a candidate omission of genuine value.

Ordinary local exchanges do **not** require material supply or Service civics.
Bakery/Café give their actual local Mill Production/Gold and receive Food.
Tailor/Fashion House give Workshop Production/Gold and receive Culture.
Mill–Granary and Workshop–Lighthouse exchanges have their own actual customer
requirements and owned adjacency. They are separate from Services.

Stage3 ordinary population sales use **0.105 per customer citizen** in the
current registry. Bakery–Market gives customer Food and seller Production/Gold;
Tailor–Market/Temple gives customer Culture and seller Production/Gold. Actual
functioning sellers, owned adjacency and functioning customer buildings are
required. No material or Service civic gate applies to these ordinary sales.
The public prose currently says0.1; this ledger records the engine amount and
does not silently amend either source or design.

Stage4 ordinary sales give each eligible customer venue Culture and return
Production/Gold to Café/Fashion House. Each site contributes
`floor(its customer's city population / 5)`; floor each customer before summing.
Several distinct venues in one city can be separate relationships. Actual
seller, district/building and ownership gates apply; these ordinary sales do
not require the additional Service civic/material gates.

Services add their own conditions:

| Producer Service | Source requirements | Beneficiary |
|---|---|---|
| Mill / Storekeeper | Feudalism + improved Base + adjacent Granary | Granary city: +10%growth, +1GreatEngineer point; internal marker. |
| Bakery / Innkeeper | Medieval Faires + improved Base + adjacent Market | Market city: +2Housing, +1GreatMerchant point; slot marker. |
| Café / Groundskeeper, Ride Technician | Urbanization + improved Base AND Specialty + qualified Zoo/Ferris | Customer: +2Tourism, +1GreatEngineer point; slot marker. |
| Workshop / Dockmaster | Naval Tradition + improved Base + adjacent Lighthouse | Customer: +20%eligible naval production, +1GreatAdmiral point; slot marker. Explicit Ancient–Renaissance × melee/ranged/raider matrix. |
| Tailor / Sacristan | Divine Right + improved Base + adjacent Temple | Customer: +10%Faith, +1GreatProphet point; slot marker. |
| Fashion House / Stage Manager and Wonder roles | Opera and Ballet + improved Base AND Specialty + qualified Amphitheater/named Wonder | Customer: +2Tourism, +1GreatArtist point per qualifying Fashion House. Theater marker has a slot; Wonder markers do not. |

Keep exact gate differences: Bakers Granary explicitly uses functioning presence;
its Market/Zoo/Ferris SQL leaves do not declare the same argument. Tailors
Lighthouse/Market/Temple/Amphitheater leaves explicitly do. The population Lua
has its own functioning checks; do not substitute it for SQL Service semantics.

Trade is another channel. Real active routes import Food(Bakers) or
Culture(Tailors), plus an amenity, into an origin without a functioning
same-industry Quarter. Supplied destination producers receive Production/Gold
returns. Domestic and international routes have identical fixed CSC payouts.
The UI scans routes and requests a synchronized gameplay property update;
native district placement is not established to simulate that future process.
Core/Gold companions are additive. M&C returns are marginal additions to core,
so totals2/3 must not be added on top of the ordinary1 again.

## Read the evidence without overclaiming

Use effect admission → component contribution → building total → district
aggregation → selected request → construction → realized returns as separate
steps. Preserve the native utility units, readiness, discounting, prerequisites
and recipient scope for each observation. `Yields.DefaultValue` alone is not a
universal conversion between real yields and native Q8 utility.

Regenerate using the explicit read-only rules DB and artifact output directory:

```text
python -B project/tools/native_ai/mill_building_study/ledger/build_inventory.py --database <DebugGameplay.sqlite> --artifact-dir <Desktop-study-folder>/ledger
```

The full raw evidence lives in
`Desktop/Codex/csc-mill-building-study-20261105/ledger/rules-and-roots.json`.
The machine ledger pins its digest, the cache digest and every inspected source
file. It includes all attached root/child references and recursively reached
requirement sets, rather than inferring active behavior from unused definitions.
Original source and current design remain separate; no native call, policy
change, game launch or source tuning is performed by this builder.
