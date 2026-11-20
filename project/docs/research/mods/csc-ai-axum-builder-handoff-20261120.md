# Axum’s missing Builder and delayed Tailors supply

## Original Continents game

Ethiopia’s Axum lost its working Flax Farm on turn 115. The city immediately
reserved a Sawmill on nearby Bamboo as an alternative. Its first reservation
already used the desired improvement and tile. Twenty-five failed Builder
searches and four failed Protect Unit checks followed across the retries.
Axum built the Sawmill on turn 154. The next census showed working supply
again on turn 155, forty turns after the outage.

| Turn | Native behavior in the original run |
| --- | --- |
| 115–117 | Axum reserved Bamboo, recruited a Builder on 116, then failed Protect Unit on 117. |
| 130–132 | Axum recruited another Builder. Move Unit reported success on 131. Build Improvement showed `IMPROVEMENT_BARBARIAN_CAMP` while running, then failed on 132. |
| 134–135 | Axum recruited a Builder for Bamboo again and failed Protect Unit the next turn. |
| 136–142 | Axum reserved a Flax repair. Contract 2919 was submitted at value 323 and marked complete on 142. On the same turn, Axum failed to recruit and failed Protect Unit. |
| 143–152 | Axum reserved Bamboo. It recruited on 147 and stayed in Move Unit through 151. Ethiopia’s Builder 9502730 logged move requests each of those turns, then skipped on 152, when Axum failed Protect Unit. |
| 153–155 | A fresh Bamboo reservation recruited on 153. Builder 9502730 logged a Build Improvement operation on 154, the same turn Axum logged successful Sawmill construction. Supply was working at the 155 census. |

Native logs for the scheduler-off and finishing-scheduler games show the same
Axum sequence. On 154, 9502730 was the only Ethiopian Builder with a build
operation. The CSC material observer recorded plot 1977 changing from bare to
a working `IMPROVEMENT_RES2_SAWMILL` on that turn. On 132 Ethiopia had two
Builder IDs with build operations, including one with `Can’t Start`. Those
lines omit the target and improvement type, so they cannot identify the
operation, if any, that Axum’s failed action submitted.

The Flax training completion on 142 coincided with another city-improvement
contract, 2948 at value 422, also completing. The city logs repeat each contract
across participating cities. Use the new unit and its controller before and
after the creation handler to establish who received the Builder.

## Same Builder resumed the Bamboo job

The turn-150 replay reproduced Axum’s failed protection check, new reservation
and completed Sawmill. The shared controller ran one turn at a time. Native
readback recorded the same Builder at each inactive boundary. Each row lists
the **completed AI turn**. The inactive boundary is one turn higher.

| AI turn | Axum’s behavior | Builder 9502730 after the turn |
| --- | --- | --- |
| 150 | Continue toward Bamboo. | `(52,23)`, controller `53805100`, 3 charges. |
| 151 | Continue toward Bamboo. | `(52,25)`, same controller, 3 charges. |
| 152 | Protect Unit fails. Move Unit and Build Improvement remain ready. | Still `(52,25)`, controller `-1` (unassigned), 3 charges. Native operation log says `SKIP_TURN`. |
| 153 | Reserve the same plot and recruit a Builder. | `(53,26)` on Bamboo, new controller `61669427`, 3 charges. |
| 154 | Confirm arrival and build the Sawmill. | Still `(53,26)`, controller released, 2 charges. CSC records a working supplier. |

The site entered planning immediately at the start of the outage. The final
handoff cost one idle turn at a time when the Builder still had charges and
could reach the site. The earlier failed searches account for much more of
the wait. A turn-end controller read establishes custody at that boundary.
It leaves the exact release trigger and any intervening same-turn transfer
open. The route worked with the same unit after Axum made a fresh reservation.
Kish gives a separate case where a stronger equal-priority job did take the
worker. [Kish controller trace](csc-ai-material-development-matched-20261118.md#kishs-worker-was-reassigned-to-umma).

Keep evaluating job admission, access to a charged Builder, and assignment
over time separately. A larger placement bid alone would have little effect
on Axum’s late interruption. The current scheduler covers finishing an
already assigned worker on a qualifying repair plot. Axum’s Builder was
travelling to build an alternative supplier when the assignment ended.

## Reading the improvement log

On Steam build 26595377, Windows Gathering Storm GameCore SHA-256
`4de40abf7c739f53c1f3f825863ace84dc220e5a42d87620e56fceaf3fbd4dc8`,
the Build Improvement description at RVA `551890` formats the improvement
index already stored at node offset `0x54`. It uses byte `0x58` to pick
the building or repairing wording. This description can be printed while the
node waits. Build Improvement Update (`551ac0`) chooses the action’s worker,
checks charges and arrival or reachability, then resolves the improvement for
the target. A path that returns before that point can leave the improvement
index unchanged. Build Improvement Execute (`5513a0`) reads the selected
worker and improvement before any build or repair request is constructed.
The operation constructor or a matching operation log is the useful witness
when the behavior description names an unexpected improvement.

The same separation matters for training contracts. The Builder creation
handler (`3f9f80`) first records contract completion and then conditionally
assigns custody. That assignment requires a live requested controller and
the contract’s keep-control flag. A Protect Unit failure can mean the node
has no units to protect. Its ordinary fallback at `5588b0` tests the list
returned for the tree’s controller before it evaluates protection needs.

## Inputs and evidence

- Small Online Continents, map seed `18111120`, game seed `29111120`,
  Ethiopia player 5, Axum city ID `131073`, Flax plot `1828` at `(52,24)`,
  Bamboo plot `1977` at `(53,26)` and Tailors at plot `1902`.
- Frozen scheduler-off benchmark packages and matching dev CE DLL SHA-256
  `783e976b114aa5a4dda0541986cd60591bdd7aea2fc8382f418ff95c7a3b3082`.
  The original milestones and both policy arms are in the
  [Steam 26595377 port report](csc-ce-steam-26595377-port-20261120.md#continents-benchmark).
- Local evidence root `Desktop/Codex/csc-ce-steam-26595377`. Compare the
  archive’s `AI_Behavior_Trees.csv`, `AI_CityBuild.csv`, `UnitOperations.log`
  and material census. REA evidence for descriptions, Update, Execute,
  Protect Unit, recruitment and Builder creation is in `axum-worker-rea.json`.
- First replay from the verified turn-100 checkpoint (SHA-256
  `b9b16888a17bbe5f42c09da5e34d004216dec9d2244aead1149a14d3e12a3f65`)
  stalled at turn 104, before the outage. The direct turn-150 replay
  stalled at the source clock. Deferring the callbacks let the turn-150
  replay reach 151. It stalled again in the next window, after the callbacks
  were active. The console stayed responsive and the shared controller closed
  Civ and restored preferences after each timeout. The callback runs captured
  no matching worker events. These runs suggest an observer interaction;
  the blocking call remains unidentified.
- The turn-150 checkpoint SHA-256 is
  `8f12238a596acc39f888d5ad0682658cc3e0e8276920370fcc30e97b58dd8a70`.
  It reached turn 155 using an observer that reads the Builder roster without
  callbacks. In `axum-builder-boundaries`, see `worker-boundary-150.json`
  through `worker-boundary-155.json`, the game logs, and the verified endpoint
  SHA-256 `d80bcd0430c5a348b9796354ec9127878528fc11acf8e5bbc27d3b61343e205e`.
  In this binary the player lookup starts at `44f00` and reads the player
  array via `63d100`. Unit custody is the controller at unit offset `0x300`.
  The callback-only failures and the clean boundary run support retaining
  boundary sampling for future worker traces before adding finer hooks.
- The replay folders retain their diagnostics. Four package copies from the
  first two failed replays were removed after verifying that every file matched
  the frozen benchmark. The source packages and saves remain available.
