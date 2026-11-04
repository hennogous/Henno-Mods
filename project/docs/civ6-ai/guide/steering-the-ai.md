# Steering the AI

Our new interface lets a mod change how valuable the AI thinks a specific district-site opportunity is. The AI then chooses and executes work through its own systems. The policy can be sophisticated Lua; the native hook applies a checked numerical adjustment at the identified scoring boundary.

## Why this is useful

An ordinary preference can encourage a district type broadly. A per-site adjustment can express a local relationship:

- This Bakers site has useful materials and customers nearby.
- This alternative destroys material the producer would need.
- This investment could serve an empire need, but needs development first.
- A native forecast credits a benefit whose CSC conditions are missing.

These are possible inputs, not all implemented behaviours. Our current rule is much simpler: promote one good adjacency option per city and softly penalise weak ones.

```mermaid
flowchart TD
  A["CSC Lua evaluates the situation"] --> B["Scoped city, district, tile adjustment"]
  B --> C["CE native scoring interface"]
  C --> D["Ordinary AI forecast and choice"]
  D --> E["Native requests and construction"]
```

The interface changes valuation. It does not directly place a district, clear a production queue, grant Gold or guarantee that a lower-scored option cannot win.

## What we have demonstrated

| Demonstration | What it establishes | What it leaves open |
| --- | --- | --- |
| A small adjustment reached the cache, winner and new request | Delivery through several decision stages | A better choice or construction |
| Sydney switched from Neighborhood to Tailors at the same tile, then naturally completed it | A caused district-type choice change and follow-through in that case | A better site, profitable chain or general improvement |
| Packaged Lua + CE fork completed Online100 with 101 matching policy plans and all four diagnostic families | A bounded development carrier without a Python/Frida policy worker | Release compatibility, economic benefit and historical outcome parity |

The Online100 journal recorded 73 increases and 14,584 deductions with zero reported native API faults. These are implementation counts, not a measure of intelligence. The [parity report](../../research/mods/csc-ce-policy-parity-20261104.md) preserves the conditions and limitations.

## Why Community Extension needs a change

The released CE we tested has memory tools, but lacks this typed scoring interface. Our fork adds the native hook, numeric batch publication, scope and version checks, context reset and diagnostics. Keeping those responsibilities native avoids calling arbitrary Lua from the scoring worker.

The preferred release arrangement is **CSC supplies Lua policy → released CE supplies the native capability**. [Draft PR 9](https://github.com/Wild-W/CivilizationVI_CommunityExtension/pull/9) proposes the generic capability to WildW. Until acceptance and release, we need the development fork. A separate CSC native component is a possible fallback, but running it alongside stock CE has not been qualified. Lua alone cannot add the tested implementation to stock CE.

## Keep steering meaningful

The native forecast already includes useful benefits and costs. Adding our entire economic estimate on top would count some things twice. We need a ledger of what is represented, what is approximated poorly and what is missing. Then we can apply a justified correction and test the decision.

**Continue:** [Teaching it CSC](teaching-it-csc.md).

Technical references: [native extension](../topics/native/native-placement-extension.md), [Workshop and CE delivery](../topics/native/workshop-delivery.md), and [controlled choice and completion](../../research/mods/civ6-district-placement-choice-20261103.md).
