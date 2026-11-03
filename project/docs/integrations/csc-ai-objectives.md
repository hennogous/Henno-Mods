# CSC AI objective and decision principles

## Profile scope — confirmed clarification, 28 October 2026

Both profiles aim for meaningful CSC supply-chain competence. With RHAI5,
complement the capabilities it already provides and add or improve only what
CSC needs, including Builder behavior where evidence shows a gap. Without RH,
provide the support CSC needs; this is not a general-purpose replacement AI mod.
The RH branch need not forever forbid every Builder adjustment, but a narrow
compatibility change must be justified and must not blindly duplicate or override
RH's existing policy. Shared objectives do not require identical tuning inputs.


Proposed implementation path: [CSC AI development roadmap](csc-ai-roadmap.md).


Confirmed direction from Henno, 28 October 2026. This is the durable objective
for CSC AI development across standalone CSC assistance and the RH compatibility
branch. It describes intended capability, not a claim that current code delivers
it. Historical experiment scorecards and tuning weights are evidence, not the
definition of success. This document does not start a test or automation.

## Main objective — confirmed

Make the AI competent at using CSC's supply-chain mechanics to increase the
total benefit to its empire. Ideally, it should develop the opportunities in
its lands and empire into supply chains that support its overall victory
progress, strategic priorities and current needs.

Quarter count, adjacency score, completed foundations and active Service flags
are intermediate indicators. The objective is worthwhile, functioning supply
chains and their empire benefit. Fewer, better chains can be preferable to
more Quarters with weak follow-through.

## Required capabilities — confirmed

1. **Material-aware Quarter placement.** Prefer sites adjacent to materials
   mapped to the actual Quarter, with Base supply as the minimum planning
   ambition and particular interest in sites with both Base and Specialty
   supply. Use current enabled mappings, including supported modded resources;
   generic bonus-resource presence is not a substitute for matching materials.
2. **River opportunity.** Value river adjacency for the real Production bonus
   it brings to the relevant Quarter.
3. **Customer opportunity.** Value suitable existing adjacent customer
   districts and sites that leave legal, usable space for future customers.
   Quarters often unlock before their customer districts.
4. **Combined site potential.** Evaluate material, river and customer adjacency
   together. Explore graded priorities for combined +3, +4, +5 and stronger
   opportunities. Tile purchases can be worthwhile to secure these sites.
   These numbers are candidate bands, not approved hard thresholds or final
   weights. Earlier Both-or-+4 planning is a candidate implementation within
   this broader objective, not a replacement for it.
5. **Balanced customer placement.** Encourage customer districts beside
   Quarters without overwhelming other good locations. A +4 mountain Campus
   should not routinely become a +1 Campus solely to sit beside an
   Apothecaries' Quarter. Sites serving both purposes are especially attractive;
   compare the complete benefit of the alternatives.
6. **Material development and care.** Improve, retain and repair the mapped
   materials serving Quarters; avoid subsequently covering or removing the
   inputs on which a valuable chain depends.
7. **Building follow-through.** Construct the producer and customer buildings
   needed to realise the chain's benefits, including buildings in customer
   districts rather than counting district shells alone.
8. **Strategic Service selection.** Ultimately favour Service effects aligned
   with the player's priorities, victory direction and needs. This remains a
   longer-term capability; earlier deferral is not a decision to omit it.
9. **Recovery.** Repair pillaged Quarters, customer districts and material
   improvements so that established chains can return to service.

## Planning distinctions to preserve

Henno explicitly accepts credible future development in site assessment. Keep
currently realised adjacency and future potential separate in reports and
planner inputs. An unbuilt customer district or unimproved resource is not an
already functioning chain. Production and Gold components should remain visible
even when a combined score is used; their strategic value need not be equal.

Both supply has particular value because of its later Service potential, but
potential alone does not establish timely construction, available customers or
an actual active Service. Respect each mechanic's own requirements: material
supply, customer-building links and Service activation are different facts.
Do not infer monetary transactions from links or Service flags.

## Additional considerations — proposed, not yet fixed policy

These are recommendations arising from the objective, not newly approved
algorithms, coefficients or gameplay changes.

- **Whole-chain opportunity cost and time to benefit.** Include production,
  tile-purchase Gold, Builder charges/travel, maintenance where applicable,
  lost tile use, district capacity and displaced military/economic investment.
  A stronger paper site may be worse if its chain becomes useful too late.
- **Capacity and sequencing.** Finish or repair valuable existing chains when
  that beats starting another. Check population/unlocks, plausible production,
  reachable Builders and affordable development before crediting future value.
  Builder availability is a means to complete work, not an end in itself.
- **Coordination between sites.** Do not promise the same future plot to two
  incompatible districts or destroy one chain's material for another without
  evaluating the trade-off. Consider useful shared customers and redundant
  supply, while avoiding double-counting shared economic benefits.
- **Resilience and replanning.** Account for pillage, capture, resource loss and
  changed strategic needs. Recover a valuable chain, revise an obsolete plan,
  or abandon a genuinely poor investment; preservation is not an absolute ban
  on every harvest or redevelopment.

## Evidence and evaluation

Use the following as a measurement framework, not a fixed weighted formula:

| Dimension | Evidence to seek |
|---|---|
| Site quality | Mapped Base/Both supply, river benefit, legal customer options; present versus projected adjacency |
| Follow-through | Placement to completion/building times, improvement and repair delays, unfinished commitments |
| Sustained operation | Working supply and customer buildings over time, losses, recovery, realised Service effects |
| Empire benefit | Observed incremental yields/effects and strategic outcomes, alongside investment, subsidies and displaced opportunities |
| AI independence | Native placements versus assisted placements, by Quarter type and comparable opportunity/cohort |

Compare against appropriate untuned/CSC-only/RH references at matched clocks
and settings, with per-city and total context. Do not reward Quarter spam,
denominator changes or subsidy spending as improvement by themselves. Report
subsidised and own-funded costs separately. Unsupported causal attribution,
unobserved transactions and sparse observation intervals remain explicit.

Native input loading, score changes, selected actions, physical completion and
net benefit are separate evidence levels. The
[native control analysis](../research/mods/csc-ai-native-production-analysis-20261028.md)
helps identify mechanisms; it does not turn promising inputs into proven
outcomes. The next planner and tuning design should be chosen against this
objective after examining the working controls, not by preserving every
historical intervention.

## Related documents

- [Basic/RH profiles and settings](csc-ai-profiles.md)
- [Tuning implementation and historical evidence](csc-ai-tuning.md)
- [Mechanism-probe results](../research/mods/csc-ai-mechanism-tests-20261025-results.md)
- [Native production/control analysis](../research/mods/csc-ai-native-production-analysis-20261028.md)
