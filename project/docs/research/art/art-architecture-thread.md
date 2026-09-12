> **Documentation audit — 2026-09-12: Historical.** Raw conversation retains unverified Pile and performance claims. The later art-performance-evidence-review explicitly withdraws Pile-specific guidance. Keep as provenance, not operational instructions.
> Classification: Discussion record. See the [full audit](../../DOCUMENT-AUDIT.md).


Let me ground this in real Firaxis Pile assets rather than describe them abstractly — let me see what's in your Pantry Exports.

Listed Pile and cluster prop asset files in Pantry Exports
Good — it's worth understanding properly, because it's the lever that reconciles "reuse everything" with "respect the asset limit." One honesty note up front: the actual Pile geometry files live in the SDK Pantry on your Windows box (…\SDK Assets\Civ6\pantry\), not in your Mac-side Pantry Exports folder (which only has a handful of files), so I can't crack one open right now. But I can ground this in what your files do show plus the pattern's mechanics — and offer to dissect a real one via the Blender MCP when you import it.

What a Pile actually is
A Pile is a single asset whose geometry is a pre-arranged heap of many small objects — a stack of logs, a mound of stones, a cluster of sacks — modeled and merged into one mesh, given one material, and registered as one asset. It sits on a spectrum between an atomic prop and a full base tile:

Asset entries	Placements	Reuse/instance	Per-item control
Atomic prop (1 sack)	1	many	yes	full
Pile (heap of sacks)	1	1 per heap	yes	none (baked heap)
Baked into building	0	—	no (replicated)	full
The Pile is one of the referenced assets that a base tile or building points at. Recall DIS_PRD_Classical_Base_01 was 83 references — a Pile is a single baked geometry that is one of those references. And your base_02 file literally places DIS_PRD_Pile as one instance. So the hierarchy is: base tile (composition of references) → references → Pile assets (baked heaps) + atomic props + buildings.

What it buys you
Collapses many visual props into one asset entry — kind to the asset limit.
Collapses many placements into one reference — simpler base manifests, fewer attachment points.
Still a referenced asset → reused across buildings and bases, engine-instanced (geometry stored once, batched), sharing the one prop atlas. You keep every performance property that baking-into-buildings would throw away.
Author the "nice heap" once — the internal arrangement (which log sits where) is baked into the asset a single time, then scattered everywhere.
How Firaxis actually uses it (from your catalogue)
They don't make one Pile — they make a small family of variants: Pile, PileA–E, PileBlock, PileWood. A handful of heap variants per material type, then those few get scattered across dozens of tiles. That's the trick for getting visual variety and asset economy: ~5 reused pile variants beat either dozens of unique heaps or hundreds of atomic props. (Harbor does the same with Coal_Pile, Lg_Fish_Bin.) They also keep atomic pieces (PROP_Stone_C–F, PROP_Lumber_B/E, PROP_Boulder) for fine hero placement — so it's piles for bulk dressing, atomic props for accents, not either/or.

The full-circle bit: this is what the Blender join is for
Remember the linked-duplicate + join workflow I demonstrated on the flour sacks? Building a Pile asset is exactly that workflow, used correctly. Link-duplicate the sack six times, arrange a good-looking heap, then join into one mesh — that joined mesh is your CSC_BAKERS_SackPile_A asset. So the join isn't for baking props into a building (which loses reuse); it's for baking a cluster into a reusable asset. Same operation, right target.

Two nice bonuses of authoring it as a pile:

Baked AO across the cluster. Because the whole heap is one mesh with one UV2 AO bake, you get real contact shadows between the stacked items — occlusion that individually-instanced atomic props can never have. Piles look grounded and heavy; scattered instances look floaty. It's a genuine quality win, not just economy.
One placement to art-direct. You tune one good heap instead of fiddling six loose sacks per building.
For CSC, concretely
Look for prop groups that always co-occur: sacks by the mill, a wood stack by the carpenter, crates by the workshop, bottles by the apothecary. Model each as one pile asset, make 2–4 variants so scatter doesn't read as tiled, and place them by reference on buildings and bases. Reserve atomic props for the few hero accents you want to place individually, and reserve building-baking for the truly single-building fixtures (Oven, Loom).

When not to pile: when you genuinely need per-item placement control, or the items appear solo as often as grouped. Then atomic + attachment.

Want me to prototype one — take your flour sack, build a SackPile_A/B/C set in Blender via link-dup + join + a shared-atlas UV + AO bake — so you've got a concrete template for the cluster pattern? And when you're next on the Windows box, point me at a real DIS_PRD_Pile*.geo/.fgx and I'll dissect its island/UV structure so you can match Firaxis's construction exactly.

fwiw, the JNR Urban Complexity mod series has 550 assets

That's a really useful anchor — and it recalibrates the whole 200-vs-300 anxiety.

550 assets in a shipping, widely-used series means the practical working ceiling for a single mod is comfortably north of 550, not somewhere around 300. So for CSC in isolation, ~280–300 has genuine headroom, and the idea of contorting the architecture to force 200 — baking reused props, replicating geometry, losing dedup — was solving a problem that doesn't bind at your scale. Drop that goal. Accept ~280–300 and keep the clean reuse model.

Two caveats keep it from being "asset count is a total non-issue," though:

The limit is a shared, global budget — base game + every active mod. And your co-players are exactly the people who run JNR Urban Complexity: it's thematically adjacent (city/district visual richness), so there's a real scenario where a player stacks CSC (~300) on top of JNR (~550) plus your optional integrations (Sukritact, Resourceful, LAR…). That stack is where the ceiling actually gets tested — not CSC alone. So economy still matters, but as good citizenship in a shared budget, not as a survival constraint for CSC by itself.

That's an argument for the free economy, not the costly one. The moves that cost you nothing — bake single-building fixtures (Oven/Loom), cluster co-placed props into Pile assets — you do anyway; they leave you leaner in the shared stack for zero downside. The moves that cost reuse, quality, or workflow — baking reused props, skimping on pile variants — you don't, because JNR's 550 shows you're nowhere near needing them.

Net adjustment: your binding constraint at this scope is art scope and your own time, not the asset table. Let asset count be something you keep tidy with the free levers, and let it stop being a thing you architect around. If you want visual variety — more pile variants, more prop types — the count budget is not what should stop you.

Let me log the anchor so the recommendation stays calibrated.

Edited
project_art-performance-and-materials.md
+8
-1
Logged. Bottom line: JNR at 550 tells you 300 is safe headroom for CSC alone, so stop treating the asset table as a design constraint — keep it tidy with the free levers (single-building baking, Pile clustering) because the cap is shared with the big art mods your players run, but don't trade reuse, quality, or workflow to chase a number. Your real ceiling is how much art you have time to make.

City Lights has 470... this one I would like to recommend to pair with CSC

That changes the read from "abstract good citizenship" to "a concrete decision you should validate," because now you're not talking about CSC alone — you're deliberately putting ~470 assets on the table before CSC even loads, then stacking ~300 of CSC on top, plus your optional integrations. Call it ~770+ mod assets over the base game.

Here's the honest part: I don't know whether that combined stack fits, and that uncertainty is exactly the point. The Civ6 asset limit is real (your CE README calls it an unfixable bug), global, and murky/version-dependent — and stacking two ~500-asset art mods is precisely the scenario that stresses it. City Lights ships fine alone; CSC will ship fine alone; that tells you nothing about the two together plus base plus integrations. This is the one place in this whole conversation where economy stops being theoretical.

So the actionable thing isn't more analysis — it's a test, before you publish the recommendation:

On Shadow, load base + Gathering Storm + City Lights + CSC + your integration mods together and confirm: game reaches the map clean, districts/buildings actually render (no missing/black models — the classic asset-limit symptom is assets silently failing to load), and no asset-limit errors in the logs. Your run_csc_demo.py FireTuner harness is the natural vehicle; extend it to enable City Lights in the mod set.
If it loads clean → recommend the pairing with confidence, and your free economy levers (single-building baking, Pile clustering) are now a genuine compatibility feature keeping margin for the stack. Keep doing them; still don't sacrifice reuse/quality.
If it breaks → you've found the real ceiling empirically, and then economy becomes a hard requirement: push clustering harder, trim base variants, and reconsider how many integrations you bundle-recommend at once.
One secondary check while you're at it, separate from asset count: functional compatibility. City Lights decorates existing districts; CSC adds custom Quarter districts. Most likely City Lights simply won't touch your Quarters (fine), but confirm it doesn't fight CSC over shared district art or ArtDefs. That's a different failure mode than the asset limit and worth eyeballing in the same combined-load test.

Net: recommending City Lights is a good call aesthetically and the counts probably fit, but "probably" on an unfixable global cap is exactly the thing you verify rather than assume — especially since it's a pairing you'd be putting your name behind. Want me to sketch the extended FireTuner combined-load test (enable City Lights + CSC + integrations, autoplay a few turns, snapshot for missing-asset detection) so it's ready to run next time you're on the Windows box?



