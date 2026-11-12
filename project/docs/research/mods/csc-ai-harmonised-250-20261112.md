# Harmonised main CSC AI: 250-turn test

Henno requests one complete 250-turn game after verifying all ten placement
capabilities in main CSC, then comparison with the existing baseline. For a
native-system solution, verified inputs/consumption and integration suffice;
isolated changed-choice evidence is optional. This supersedes the old 2.1 gate
without turning its unchanged Theater request into a placement win.

## Integration review

Astra independently finds all ten reusable production paths for the implemented
Bakers and Tailors. No fixture city, player or plot controls live policy.

| Capability | Production mechanism |
| --- | --- |
| 1.1 Materials | Shared live supplier/deposit/improvement facts, Base/Specialty distinctions and legal Quarter offers |
| 1.2 Neighbors | Existing and specific future all-stage customer/provider footprints, with actor type/geometry checks |
| 1.3 Rivers | Shared gameplay adjacency rules and one projected local Water/Wind Mill branch |
| 1.4 Combined adjacency | Ordinary 24/48 Q8 utility bands for viable/4+ sites, with supplied-site ranking |
| 1.5 Acquisition | Owned/frontier alternatives, uniquely-cheapest native UI quotes, native savings/payment plus generic ownership acknowledgement; separate supplier purchase/improvement offers |
| 1.6 Follow-through | Ordinary native request, queue, foundation and completion; no direct construction command |
| 1.7 Reconsideration | Known-no-Base typed declines rebuilt and withdrawn from current facts each publication |
| 1.8 Poor sites | Finite material/no-Base/no-host deductions, conservative unknown-state handling |
| 2.1 Customers | Native private-yield adjacency beside completed Quarters; +16 CE preference only for credible future Quarter footprints |
| 2.2 Protection | Shared live material deductions, Builder allowlists, harvest/Wonder guards and supplier exclusions |

The 10th path is not a separate new planner. The central model supplies all
adapters. Stage 2 building, Builder and repair guidance remains integrated as
well; research/strategic preferences are outside this placement review.
Only Bakers and Tailors are implemented; this is not eight finished industries.

## Small harmonisation change

Remove the existing-Quarter +40 customer nomination from the main scanner.
Use the tested native private-yield adjacency for that relationship. Retain
+16 for an evidenced future footprint, which static native adjacency cannot
see. Preserve material protection,24/48 Quarter bands, finite weak deductions,
ownership handling, Builder/building/repair adapters and normal competition.
This avoids stacking two incentives for the same relationship; it does not
claim the old combination was proved harmful. AI-C168 remains the exact
native consumption evidence, including the competing Water Entertainment
decrease and unchanged Theater choice.

## Run protocol

- Normal Small Ancient Prince Continents, Online speed, seeds 18461107/29461107.
- Run to 250; original AI seats 1–5, observer 0. Stock AI, CSC and our pinned CE03
  build only. No RHAI5, external policy, Frida, forced unlocks, subsidies or
  diagnostic world edits. CSC's ordinary map assistance remains active.
- Build current declared gameplay/UI files and native Firaxis manifest;
  retain installed cooked art without performing an unrelated art cook.
  A distinct temporary carrier identity prevents collision with the installed
  CSC. Runtime policy files are unchanged copies of main CSC source.
- Require loaded native SQL and every needed CE capability before play.
  Capture original seats before autoplay, source hashes and current binary IDs.
- Shared controller owns the session and uses guarded 5-turn operations.
  Its existing popup/victory handling remains bounded. Passive Storekeeper
  reads fill otherwise-unobserved inactive handoff clocks; they change no game
  facts. Human/agent outcome check-ins are about every 15 minutes.
- Passive complete census every 25 turns records Quarter/material/customer/
  building/Service-property facts and Production, Gold and Food surplus.
  Preserve the 200 sample for comparison and continue through 250. Main logs
  record every publication, omissions and bounded native receipt readbacks.

Artifact root: `C:/Users/Shadow/Desktop/Codex/csc-ai-harmonised-250-20261112`.
Historical comparator: `csc-ai-integrated-20261108/endpoint-detail-baseline/continents.json`
and `baseline-continents` in the same parent Desktop/Codex store.

The baseline ends at 200 and uses older content/CE. Compare 200 with 200 where
available;250 is the new run's follow-through, not a matched baseline endpoint.
Check initial map/leader/unit signatures. Even matching those cannot make
different gameplay packages a controlled causal AI-only comparison.

## Results

**Completed and independently audited by Astra.** The game reaches the exact
inactive 250 boundary; native exit 0, observer survival, owner absence,
preferences restoration and temporary-package retirement all verify. All ten
25–250 censuses are complete. The main policy publishes 250 times with no
reported policy, industry-scan, observation or Storekeeper failures. Maximum
district entries 632; district-entry, decline and exclusion omissions are zero.
All nine required CE consumers pass their health check at 1 and each milestone.

The initial map signature is 74×46 / −935087381. Leaders, starting plots,
starting units and original AI seats exactly match the historical baseline.
All five studied AI players survive through 250. AI source is at `857fdb4d`;
other gameplay/UI comes from the frozen current worktree, with installed
cooked art. The file manifests identify the complete snapshot rather than
pretending that all content is reproduced by the AI commit alone.

### Placement and material quality

Counts below cover original AI players 1–5; observer 0 and city-states are
excluded. Material counts refer to completed Quarters with currently owned,
visible adjacent mapped deposits. Improved means a compatible, unpillaged
improvement, not necessarily a tile currently worked by a citizen.

| Metric | Baseline 200 | Harmonised 200 | Harmonised 250 |
| --- | ---: | ---: | ---: |
| Completed Quarters | 30 | 29 | 36 |
| With adjacent Base | 6 (20%) | 24 (83%) | 30 (83%) |
| Without adjacent Base | 24 | 5 | 6 |
| With improved Base | 3 | 16 | 24 |
| With Base and Specialty | 0 | 4 | 5 |
| Both materials improved | 0 | 3 | 4 |
| River sites | 2 | 9 | 10 |
| Adjacent mapped sales district, all stages | 10 | 16 | 20 |

At the comparable 200 clock the number of completed Quarters falls by only
one. The substantial change is quality:24 → 5 completed sites without Base,
and 3 → 16 with improved Base. This does not establish that every original
placement was material-aware, that no material was ever lost, or that every
remaining weak site was avoidable.

### Producers, customers and Services

| Metric | Baseline 200 | Harmonised 200 | Harmonised 250 |
| --- | ---: | ---: | ---: |
| Bakers complete | 16 | 14 | 16 |
| Bakers working Stage 2 producer | 7 | 11 | 15 |
| Bakers adjacent Stage 2 customer | 5 | 8 | 9 |
| Bakers working Stage 2 customer building | 1 | 8 | 8 |
| Bakers physical Stage 2 chain | 1 | 6 | 8 |
| Bakers active Stage 2 effect property | 1 | 6 | 8 |
| Tailors complete | 14 | 15 | 20 |
| Tailors working Stage 2 producer | 7 | 10 | 16 |
| Tailors adjacent Stage 2 customer | 0 | 1 | 1 |
| Tailors working Stage 2 customer building | 0 | 0 | 1 |
| Tailors physical Stage 2 chain | 0 | 0 | 0 |
| Tailors active Stage 2 effect property | 0 | 0 | 0 |

A physical Stage 2 chain requires a complete, unpillaged Quarter, improved
Base, working producer and working customer building. The native effect
property is a separate observation, not an inferred building bid.

Independent engine-effect observation confirms **312 Storekeeper chain-turns
versus 39** over the same 2–199 clocks: eight times the baseline's observed
activity. The complete 2–249 window has 248 samples, no gaps or ambiguous
attribution, and **nine distinct Bakers chains with 685 active chain-turns**.
Two chains resume after lapses, across three resumption episodes. Those
effect windows establish resumed operation, not which repair or other action
caused it. Endpoint 250 properties and the through 249 effect history are
different clocks; do not conflate them.

**Tailors customer access remains the clear weakness.** Its sole adjacent
Harbor is next to Quarter 2762, player 5/city 196610. At 200 the Harbor lacks a
Lighthouse; at 250 the Lighthouse works, but that Quarter has no archived
material or producer rows at either clock. The well-supplied Tailors elsewhere
therefore do not become Dockmaster chains. At 250 Tailors has six Stage 3
producers (five working) and three Stage 4 producers, but all observed Bakers
and Tailors Stage 3/4 Service properties remain zero. Better supply is not
general all-stage Service success.

### Economy

These are pooled totals across the same five original AI seats. Gold income
is gross; net Gold subtracts reported total maintenance. Food is surplus
after consumption, not a direct measurement of the Storekeeper growth bonus.

| Metric | Baseline 200 | Harmonised 200 | Harmonised 250 |
| --- | ---: | ---: | ---: |
| Cities | 37 | 35 | 43 |
| Population | 372 | 383 | 489 |
| Production/turn | 946.75 | 873.23 | 1461.94 |
| Gross Gold/turn | 792.09 | 890.83 | 1744.84 |
| Net Gold/turn | 310.09 | 346.83 | 807.84 |
| Food surplus/turn | 226 | 247 | 282 |
| Treasury | 1064.15 | 1475.29 | 2720.02 |

At 200, Production is **−7.8%**, net Gold **+11.9%**, Food surplus **+9.3%**
and population **+3.0%**. There are two fewer cities. Production per city
falls 25.59 → 24.95 (−2.5%); population per city rises 10.05 → 10.94.

| Average per original AI | Baseline 200 | Harmonised 200 | Harmonised 250 |
| --- | ---: | ---: | ---: |
| Production/turn | 189.35 | 174.65 | 292.39 |
| Net Gold/turn | 62.02 | 69.37 | 161.57 |
| Food surplus/turn | 45.2 | 49.4 | 56.4 |

The economy is mixed, despite the stronger Bakers operation. This is not
evidence of a general production increase or a clean tuning-only balance
effect.250 shows further development of this one world; no baseline 250 was
run. The ten 25-turn snapshots provide a new outcome/economy trend, while the
historical baseline provides this detailed 200 endpoint, not a matching full
economy trend.

### Coverage, artifacts and limits

Eight dynamic native ownership acknowledgements are logged; these are not
independently measured payments. No supplier-acquisition offers occur in this
world, and no future-footprint +16 customer receipts occur. Existing-Quarter
customer adjacency is native SQL, so zero CE customer receipts does not mean
that signal was disabled. Capability readiness and source integration do not
prove every conditional mechanism was needed or exercised in this game.
Earlier representative acquisition/protection proofs remain separate evidence.

Astra independently hashes **634 CSC + 6 CE files**, checks the loaded module
identities, reconstructs every full census from raw Lua output, recomputes the
comparison and Storekeeper audit, and verifies normal cleanup. Loaded stock XP2
SHA256: `092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
CE SHA256: `a849eff803d68f7dc4061421c98812ae466b50f0d96a790f884f0f7bcf60eafb`.
Verified 250 save SHA256:
`5b4a41cc16b33a010b87896b3f4accc9084c25ef58da41b6a745b01b8d38bf36`.

The artifact root holds `frozen-package-review.json`, `comparison.json`,
the run's protocol/package/source/module records, all logs and censuses,
50/100/150/200 checkpoints,250 save and closure receipts. The temporary Mods
folders no longer exist; originals were left unchanged. No further games or
matched native-adjacency trials were launched.

Reproduce the aggregation with
`project/tools/native_ai/late_placement/full_game_results.py`, passing the run,
historical detailed baseline census, baseline run and output file. Its tests
cover count units, exact windows/cohorts, missing data, elimination and cityless
seats. The current report is durable; the Desktop artifact path is a locator,
not a portable backup of game binaries or saves.
