# Draft CE feature request: district-site score adjustments

Prepared locally; **not sent or published**.

Custom districts can have material/customer rules that the native AI cannot
express through ordinary adjacency predicates. We would like a Workshop mod's
Lua to supply bounded numeric district-site incentives while native AI retains
placement legality, competing investments, requests and production.

The proposed CE capability accepts batches of
`player, city, district index, plot index, signed Q8 adjustment`, plus original
AI identities and a monotonic publication version. Native code performs the
lookup at ordinary district NetValue's output/cache boundary. It does not call
Lua from per-plot analysis jobs. Invalid/zero results are protected, the returned
output pointer is preserved, and context retirement disables the table.

An independent experimental carrier proved that the game can load a proxy from
a mod package selected through frontend GameCores. Packaged Lua supplied42
captured+256Q8 adjustments during an Online1–6 diagnostic. A second game context
in the same process reset to disabled/version0/entries0. This is mechanism
evidence, not an AI-quality or release-readiness claim.

We would prefer CE to own the native capability, allowing CSC to distribute only
Lua/SQL and declare CE as a dependency. The preparation tool produces a focused
unapplied patch and C/assembly module. Its AMD64 objects compile, but the complete
CE build has not been linked or tested. The proposed globals are absent from
stock CE1.3; the general RegisterCallEvent is not used as a substitute.

Review points include initialization/hook coexistence, game-context lifecycle,
original-human exclusion, publication timing, numerical limits, target build
identity and diagnosis. Existing cached values/requests can retain influence
after a policy is withdrawn; this interface does not promise request rollback.

Details and evidence: `project/docs/research/mods/csc-native-workshop-delivery-20261104.md`.
Candidate generator: `prepare_ce_contribution.py`.
