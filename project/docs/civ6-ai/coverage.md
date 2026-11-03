# Coverage and provenance

This consolidation covers the AI research available in the CSC workspace on
3 November 2026, including the earlier **AI optimisation** chat and the later
Industrial Zone, future-economy and district-choice investigations.

## Three complementary reviews

| Review | Material | Result |
|---|---|---|
| Engine architecture | Native scoring, city production, Builder consumers, prerequisites, modifier forecasts, symbols and instrumentation reports | Seven maintained topics and AI-N findings with explicit binary/context boundaries |
| CSC experimentation | Baselines, material/map opportunity, placement, research, preservation, producer/customer follow-through, assistance and reference AI mods | Eight mechanism topics, a navigation page, a full source map and AI-C findings |
| Chat reconciliation | All 50 pages / 492 distinct visible turns of AI optimisation, 11 October–1 November | Design-decision provenance, research journey, corrections and AI-H findings |

The [CSC source map](topics/csc/source-map.md) records the full-body research and
integration-document review. The [machine source catalogue](data/source-catalog.json)
adds supporting agent notes and tool references, with original paths, sizes and
content hashes. The [chat review record](data/thread-review.json) retains page
cursors, turn IDs, selected decisions and coverage limits.

The build catalogue normalises document text to UTF-8 without BOM and LF
newlines for Windows/Linux portability. Original reports retain exact-byte
native-artifact identities; the CSC source-map snapshot retains review-time hashes.

## What “consolidated” establishes

The review extracts and reconciles findings from the existing reports. It does
not repeat every experiment or independently re-audit every large evidence store.
Original reports remain responsible for their executed settings, counters,
source pins and raw-artifact locations. Current topic pages distinguish direct
observations, static algorithms, interpretation and unresolved effects.

The chat review inspected visible messages and final answers through the first
turn. It omitted command/tool outputs. Long automation or command bodies may
have been truncated by the chat API. Historical assistant statements are leads,
not standalone verification of engine behaviour. Research decisions are linked
to source reports wherever possible.

## Reconciliation

The [corrections page](topics/history/corrections-and-cautions.md) brings together
the changes that matter to the model: private-yield spillover; corrected plot
handlers and Aqueduct mask; preference units and sign-based consumers; actual
customer gates versus prerequisite forecasts; conditional strategy routes versus
direct preferences; later strategy re-adoption; later startup validation; and
the distinction between measurement failure and AI non-response.

`data/corrections.json` also attaches specific correction notices to affected
original documents in the website. Every original source receives a historical
status banner. This preserves the record while making later qualifications
visible at the point of reading.

## Boundaries

- The emphasis is economic AI and the CSC questions we investigated. Military,
  diplomacy and the complete victory AI are not comprehensively reconstructed.
- Static engine statements are scoped to the named current-build XP2 binary.
  Reference symbols and older-platform exports are supporting leads.
- Historical packages, installed source and the current checkout can differ.
  Later code does not retroactively describe an earlier executed experiment.
- Large native evidence stores, saved games and subscribed mod packages remain
  outside this website. Their report paths and hashes identify them; preservation
  of those external packages remains separate from Git publication.
- Neither compilation nor the website establishes that an experimental tuning
  package improves total empire benefit. The [open questions](topics/history/open-questions.md)
  retain the missing tests and controls.

The catalogue and finding register are rebuilt and checked with the site. See
[maintenance](maintenance.md) for the update and publishing workflow.
