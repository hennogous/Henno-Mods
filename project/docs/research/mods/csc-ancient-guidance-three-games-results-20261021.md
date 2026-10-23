# Three Ancient guidance games — final results, 21 October 2026

All three authorized candidate games completed native turn250 from Ancient1. All3,735 player-turn observations are present, with no defeats or censoring. No fourth game, fresh control, reroll or candidate deployment was performed. Version: `ancient-three-natural-guidance200-clean-legacy-v1`.

The new conditional private-yield guidance mechanism is usable in natural games. These runs do not establish that it improves the economy or causes the observed research paths: the user chose three new candidates against historical context, not fresh controls. Removing legacy preferences and adding the new mechanism are combined. Three worlds are three replicates, not fifteen independent player samples.

## Endpoint statistics — AI players1–5

| Game | Seeds map/game | Cities | Population | Quarters B/T | Service flags | Improvements | Builders (charges) | Builders/city | Naval | Opera |
|---|---|---:|---:|---|---:|---:|---|---:|---|---|
| 1 | 830102/940104 | 41 | 642 | 38/22 | 16 | 367 | 21 (50) | 0.51 | 5/5 | 1/5 |
| 2 | 830203/940207 | 50 | 697 | 44/25 | 10 | 384 | 23 (56) | 0.46 | 5/5 | 3/5 |
| 3 | 830304/940310 | 46 | 641 | 41/22 | 13 | 347 | 24 (59) | 0.52 | 5/5 | 2/5 |

Service flags are active source/stage states, not cities or monetary transactions. Across the three independent worlds the endpoint inventories sum to137cities,1,980population,192completedQuarters,39Service flags,1,098improvements and68survivingBuilders with165charges. These sums are descriptive inventories, not effect estimates.

## Research evidence and its bounds

All15 AI completed Feudalism, Medieval Faires, Urbanization, Naval Tradition and Divine Right;6/15 completed Opera and Ballet. Direct Naval strategy adopters numbered1/5,3/5 and2/5 respectively, so nine of the fifteen Naval completions cannot be labeled direct target-guidance successes. There are no static/direct Naval AiFavoredItems rows and no legacy Service strategy/list/condition registrations in any candidate database. Ordinary game research and prerequisite propagation still operate.

Opera illustrates the remaining constraint: Sejong inGame2 adopted its strategy at96 and completed213; Amanitore inGame3 adopted173 but never selected it by249. Five of six Opera completions occurred without direct Opera eligibility. A long gap is not proof that the target was selectable before its prerequisites. Native adoption, observed valuation, progressing-civic selection and completion are distinct; target-guidance-timing-and-valuation.json retains all90 player/target timing rows and native score samples. With no fresh control those samples cannot be interpreted as isolated score uplift or changed paths.

The earlier blanket permanent restart-failure interpretation is superseded. Game1 Germany Feudalism and Faires stopped37, regained eligibility47 and followed57; Greece Urbanization stopped66, regained79 and followed86. Each return was20turns after stopping. This is evidence that re-adoption is possible and suggests delayed reconsideration, not a verified universal cooldown constant or a fix. Games2/3 contain no qualifying post-stop recovery opportunity; their empty episode lists are not failed restarts.

## Services, materials and practical limits

At250 the worlds produced25Growth,9Housing,3TailorFaith,1TailorProduction and1BakersTourism source/stage flags. The lone stage4 effect was Game2 Kristina/Stockholm Café→Zoo. There was no Tailors stage4 Tourism effect. Source-to-venue links are archived, not sales transaction counts.

Only49/123 Bakers Quarters and12/69 Tailors Quarters had owned adjacent Base materials at250. In120/192 completed Quarters neither industry-mapped material class was owned adjacent. Only three Bakers and two Tailors Quarters across the worlds had both classes; the Bakers trio was improved inGame2, while both Tailors sites lacked both improved. The map assistance was active, but sufficient map-level materials did not ensure that the AI placed Quarters beside them, owned them, improved them and assembled the required producer and venue.

This is the dominant observed economic limitation after research unlocks. Each gate table uses marginal counts and must not be added into mutually exclusive failure totals. Pillage and resource replacement also matter. Game3 retained only21/35 adjacent mapped industry plots improved; Game1 22/29 andGame2 24/28. These denominators are per-industry plots, not necessarily unique physical plots across industries. The final source-property states match reconstructed complete Service gates in all three worlds at200/225/250, with zero mismatches.

Late city/population/Builder counts vary by world and are not causal harm or benefit estimates. Game1 historical comparison was worse on Services/cities/population while better on Naval timing. That mixed result is sufficient reason not to automatically promote a winner.

## Historical context — not clean baselines

Game1 compared with19October improvement-owned80 trial: recorded initial world/starts match exactly, but26installed files and policy/adjacency definitions differ. Historical Naval2/5 versus5/5 now; Services21→16,cities49→41,pop755→642. Game2 older16October standard-AI/pass3 world has the same starts/terrain but21resource plots differ from pass4; Naval0/5→5/5,Opera0/5→3/5,cities49→50,pop541→697. These comparisons confound source versions, accepted tuning and legacy guidance.

Game3 older16October standard-AI/pass3: same starts=True; recorded world differences={'terrain': 0, 'feature': 0, 'resource': 35, 'resource_count': 35, 'continent': 0, 'owner': 0}. Historical Naval1/5,Opera1/5,cities57,population588,Quarters75; new5/5,2/5,46,641,63. It is not a controlled comparison. Historical renderer/version differences were not removed. No general improvement claim follows from these counts.

## Verification, restoration and retained limitations

Every run independently passed57source/122installed/46RSTreference/2RHexample archive hashes, eleven primary and six Builder checkpoints, all1,245 research observations, native schema/replay/legacy cleanup, player0 exclusion and zero private city yields. All three full native definition table row multisets, generated SQL overlays and callback byte strings are identical. Differences are the authorized seeds/rosters and natural evolution. Contradictory FutureCivic AND inverseFutureCivic economic requirements prevent actual private-yield grants. Existing Service/prerequisite definitions were not migrated.

Final offline verification confirms both installed AI originals match study/original-installed and the other120 installed archived files are unchanged. Native restoration readback after each run, including the final run, verified all144original mod preferences and autostartfalse. Source worktree edits remain uninstalled/preserved. No native gameplay database or Lua runtime error was accepted; scoped LocalizedText duplicate exceptions remain archived. Worker/supervisor completed without a gameplay retry.

Named endpoint saves forGames2/3 were unconfirmed optional saves; full250exports and archived autosave filename250 remain. Autosave turns are filename metadata, not independently reloaded proof. The original supply probe overestimates some signals (per-Quarter improvement80 and ignoring pillage/completion). Final contextual reviews explain Game2/3 warnings, with UI249 versus primary250 timing caveats. Game1 retains the unfinished-Quarter improvement-collection eligibility edge; no baseline fix was slipped in.

The mechanism is an experimental candidate. DiagnosticAmount200 and strategyValue100 are not validated release weights. UI omission/human recommendation effects and broader balance remain unvalidated. No permanent gameplay code changed, no candidate was deployed, and no additional games are scheduled.

## Detailed evidence

- [Game1](csc-ancient-guidance-game-01-20261021.md)
- [Game2](csc-ancient-guidance-game-02-20261021.md)
- [Game3](csc-ancient-guidance-game-03-20261021.md)
- Desktop/Codex/csc-ai-ancient-guidance-20261021/final-series-audit.json: exact hashes and verification metadata.
- Each study/run-0N: compact-results.json, results.md, post-run-audit.json and archived native data.
