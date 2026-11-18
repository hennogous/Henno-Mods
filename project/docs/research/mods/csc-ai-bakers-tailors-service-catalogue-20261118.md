# Bakers and Tailors Service forecasts

The Quarter forecast groups loaded modifier bindings by the Service they
deliver. It gets the Service identity from the gameplay presentation anchor
and the other effects from attachments with the same producer and recipient
gates. The catalogue keeps the original root, leaf, producer, recipient and
requirements for each effect. The alternative Mills and the Dockmaster's
unit-class and era cases remain distinct bindings of their respective Services.

| Service | Benefit in Quarter forecast |
| --- | --- |
| Storekeeper | City growth and Great Engineer points |
| Innkeeper | Housing where it relieves a growth constraint, and Great Merchant points |
| Groundskeeper and Ride Technician | Tourism and Great Engineer points |
| Horticulturist with Leugi's Garden District | Tourism and Great Artist points |
| Dockmaster | Production for observed eligible ship work and Great Admiral points |
| Sacristan | Faith based on current city output and Great Prophet points |
| Stage Manager, Ballet Dancer, Musical Actor and Opera Singer | Tourism and Great Artist points at their actual venues |

The catalogue also records Citizen slots from the granted buildings. A slot is
capacity and can persist after Service effects switch off. Pricing it requires
an estimate of who would fill it and what that citizen would otherwise work.
Pricing of staffing, new Wonder construction and separate strategy weights
for the proxies is deferred.

Innkeeper Housing pools the scheduled stacks in the receiving city. The two
comparison worlds share live Housing, population and positive Food surplus.
Already active CSC Housing is removed from the common base and then added back
through the timelines, which lets a delayed or lost stack lower a bid. The
proxy estimates the change in usable surplus using the loaded Housing bands,
caps it at two Food per turn in either direction, and prices that Food through
the same native interval valuation as other yields. This cap is a policy
estimate for holding population and surplus fixed throughout the forecast.
There is no new CE API. Current bands and city reads still need live calibration.

The three Tailors Wonder Service host, hidden building and READY-property
bindings moved from the gameplay Lua list into the Tailors SQL. The gameplay
reconciler and forecast now read the same rows. The forecast recognizes a
working, owned, complete Wonder on the exact adjacent plot and evaluates the
Fashion House, materials and civic requirements in both worlds. The current
READY property can be unset in the comparison where the Quarter has yet to be
built. The reconciler still creates persistent grants on their original plots.

The audit ran the game-loaded SQLite modifier graph against the production Lua
compiler, applying the current host registry to an in-memory copy. It found
10 Services and venue variants, 33 priced-effect bindings and zero omitted
bindings for the standard pair. Overlaying the relevant Leugi gameplay SQL
yielded 11 variants and 35 bindings, including the Horticulturist. The graph
audit does not measure the size or accuracy of live bids. The 156 economy
checks include nonlinear stacking, active Housing loss, delayed Housing and
exact Wonder recipient admission. The 21 Fashion House Lua gameplay tests
cover grant persistence and activation, including several Wonders in one city.
Tailors SQL architecture and Quarter contract checks pass.

Next evidence is a live comparison for Housing relief and Wonder benefits,
followed by changed native selections and full-game processing time.
