# Controlled native Quarter placement trial

This is the fresh implementation after retirement of the old CSC AI tuning.
It uses the shared controller and neutral environment/provenance helpers; it
imports no legacy site-quality, subsidy, resource-purchase or foundation policy.

The current fixture is existing game04 turn250, Sydney P5/city131073, Tailors.
All native targets are pinned to the reviewed Windows XP2 DLL and Frida17.24.3.
Importing the modules performs no game operations.

1. `baseline` observes up to five ordinary intervals and stops at the first
   GetBestDistrict return. No score is changed. Clean loaded rules, original AI
   identity and complete source facts are prerequisites.
2. `--plan-only` reads the closed baseline and exports a preferred alternative.
   It requires a sole Best call/reservation capture and the immediately preceding
   fresh cache calculation; earlier calculation-only passes remain separate.
3. `treatment --baseline ... --plan ...` loads the identical original save and
   adds the measured cache gap plus one utility unit to the preferred site's
   fresh NetValue output. It observes at most turn260, stopping on a completed
   preferred Quarter or construction at a different site.

The plan is an explicit experimental preference. It does not yet say what a
good supply-chain site is. Candidates must be clear, owned, revealed, legal,
unreserved and supported by fresh positive raw/cache scores. No forced orders,
grants, reservation removal, queue clearing or scripted district creation occurs.

`kernel.c` and `live.js` use native callbacks before JavaScript, preserve output
pointer/arguments, and keep zero/sentinel/overflow exclusions. The v2 limit is
1,048,576 Q8 per fresh output,128 changes and512 records per immutable load window.
Budget exhaustion disables the policy and makes the observation incomplete.
The raw output is adjusted afresh; existing cache values are not incremented.

Reservation data is the latest native Best-entry snapshot. The planner accepts
only a sole matching Best/capture and rejects later recalculation or ambiguous
records. Session/window labels are not native generation identifiers.

`run_synthetic.py` tests actual native calls in a disposable owned host, not Civ.
The new tests include candidate capture, reservation handling, a model site
switch, repeated fresh outputs and terminal mutation-budget behavior. The real
reader and orchestration also have separate Lua5.1/pure/mocked evidence.

The daemon freezes before Menu and retains callbacks until the exact held game
process exits. Settings are restored and installed/source hashes are verified.
Disabling is not rollback; treated saves are not clean references. The installed
AI reset is the new baseline and is not reverted to old tuning by test cleanup.

See `project/docs/research/mods/civ6-district-placement-choice-20261103.md` for
actual observations and `project/docs/integrations/csc-ai-reset-20261103.md` for
the archive boundary.

The qualified alternative may change district type at the same tile. A same-type
site switch still requires two qualified sites. The Sydney plan is explicitly
a type switch, not a demonstration that a Quarter moved between sites.

Natural Wonder and project-completion presentation recovery now belongs to the
shared controller and is installed automatically. The later replay records an
exact, archived-source-verified controller presentation revision alongside the
offline planner revision; it does not relax the native input pins or change the
numeric policy. Regenerate a plan after a reviewed provenance revision, and
retain the old plan as evidence of the actual earlier run.

`control.py` performs a fixed no-adjustment 250→254 observation from a qualified
closed baseline. It records scientific failure separately from successful normal
cleanup. Its earlier frozen implementation remains archived with that run.
