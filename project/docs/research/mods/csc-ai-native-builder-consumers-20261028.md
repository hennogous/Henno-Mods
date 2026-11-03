# Builder / Units consumer review — 28 October 2026

Follow-up: [Units Value adds to native request priority](csc-ai-native-builder-priority-20261028.md). The parser-to-request link described as open below is now traced; final allocation and queue effects remain unresolved.


## Scope and pinned evidence

This is an offline static review of the already copied Windows XP2 GameCore DLL, SHA256 `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`. All new Ghidra work reopened the existing project with `-noanalysis`; no import or automatic reanalysis occurred. No game process, FireTuner, Frida, live memory, settings, installed assets, or gameplay source was accessed or changed. Native type/signature recovery remains approximate; RVAs and assembly are the evidence anchors.

## Confirmed: Units consumes integer Value in this preference path

1. GlobalAi initializer RVA `49c7c0` registers the Units system with `Units`, `UnitType`, at GlobalAi byte offset `+0x31a0` through installer RVA `499310`. The initializer's class/name mapping is inferential (`callgraph-callee`), but the strings and offsets are direct disassembly evidence. See `parser-exports/GlobalAi_Initialize_Inferred_49c7c0.txt` and `builder-exports/Units_Handler_Initialize_Unmapped_499310.txt`.
2. Installer `499310` uses the same four query factories `525af0`, `525a60`, `5259d0`, `525b80`, with System=`Units`. The SQL projection is `indexer.rowid, item.Item, item.Favored, item.Value, ...`. Thus Favored is zero-based column2 and Value is column3. These factories query leader/inherited traits, civilization traits, agendas, and explicit list types respectively; they do not hardcode the list name `UnitPriorityBoosts`. See `favored-query-exports/Lists_QueryFactory_*.txt`.
3. The Units-specific accumulator callback is RVA `4a2360`, installed at handler `+0x120` through vtable RVA `a064c0`, whose third function pointer is `4a2360`. It calls `GetQueryVal<int>` (`525910`), and adds the returned integer for application or subtracts it for removal. Assembly: `4a2372 CALL525910;4a2377 SUB [RBX],EAX` and `4a237f CALL525910;4a2384 ADD [RBX],EAX`.
4. `GetQueryVal<int>` RVA `525910` sets EDX=`3`, then tail-calls the database integer accessor. Therefore this accumulator reads **AiFavoredItems.Value**, not Favored. Correctly named export: `builder-value-exports/UnitsHandler_ValueAccumulator_4a2360.txt`; query accessor: `builder-value-exports/Lists_GetQueryVal_int_525910.txt`.
5. The other Units value callback, RVA `4a2400`, is installed at handler `+0xe0` through vtable `a06490`. It is a two-instruction thunk: `MOV RCX,[RDX]; JMP525910`; it likewise reads Value. It had no analyzed standalone function boundary, so it was inspected as bounded existing instructions rather than creating a function. The handler `+0xa0` callback through vtable `a06460` resolves to no-op `8972d0`. Evidence: `builder-exports/units-offset-references.txt`.

The initial exploratory file name `builder-callback-exports/UnitsHandler_FavoredCallback_4a2360.txt` was provisional and incorrect. Its content is the same integer accumulator; use the corrected `builder-value-exports` file and this report. Neither recovered Units data callback calls `GetQueryVal<bool>`. This does not assert that Favored is unused in every other game system.

## Confirmed aggregation destination; downstream score conversion remains open

RVA `4b39a0` (reference map suggests GrandStrategic::InitArchive, category `callgraph-callee`) passes GlobalAi `+0x31a0` and its own `+0x3f8` vector to generic ExecuteLeaderQuery `4300c0`, with the player's leader, civilization, and difficulty inputs. For players without that leader path, it allocates one integer per unit definition and initializes them to zero. This is direct evidence that the Units integer preferences populate a per-player unit-indexed vector. See `builder-consumer-exports/Units_DirectHandlerConsumer_Unmapped_4b39a0.txt`, especially C around lines136–165 and303–304.

Repository source establishes that CSC's `UnitPriorityBoosts` Builder row is in the Units system (`Civ Supply Chains/Data/CSC_AI_Basic.sql`). Given the system query and integer callback above, changing that row's Value changes its contribution to the Units preference vector when its list applies. The native DLL does not contain the literal list name; the actual active database contents and list applicability were not checked during this offline pass.

**Not yet established:** the exact getter or score calculation that reads GrandStrategic `+0x3f8` and converts it into Builder request, unit-build, or contract value. Do not describe Value50 as a50% multiplier, +50 contract points, or a fixed boost without that link. Values50/900 are not interchangeable boolean flags in this Units parser, but the final score response need not be linear. `UnitProduction::CalculateBestUnits` (`522740`) and `CalculateBestUnitsInCity` (`5236c0`) were exported for context; they do not by themselves establish that missing link. Stopping here avoids an unbounded graph walk.

Existing contract evidence remains separate: `UnitRequestContract::Update` (`3fa5e0`) reads the unit PresentValueOf (`3e8150`), keeps the maximum against the existing contract value field `+0x158`, writes through its archived variable at `+0x148`, and refreshes production turns. `CityBuild::QueueNextBuild` (`3e8190`) compares contract values at `+0x158`. This establishes a contract scoring path, not how Units Value enters it.

## Required City = -1: precise bounded conclusion

`UnitRequestContract::Validate` RVA `3fa8e0` first tests contract `+0x1d8` against `-1`. When it is not `-1`, it compares that field with the candidate city's ID at city `+0xa8` and rejects a mismatch. When it is `-1`, it skips this city-ID restriction and proceeds to the ordinary unit/building/district and city eligibility checks. Assembly starts `CMP [RCX+1d8],-1` and conditionally checks candidate-city identity. See existing `contract-exports/UnitRequestContract_Validate_3fa8e0.txt`.

Thus `-1` means unrestricted by this particular required-city gate, **not** automatic acceptance or immediate recruitment. This does not prove which producer assigns `-1`, what its originating intent was, or why a particular Builder contract was later cancelled. The allocation/contract recruitment loop and all final eligibility conditions remain outside this pass.

## Export status and next useful link

All new exports used the saved copied-binary project with analysis disabled. Native standalone targets decompiled successfully. The planned callback `4a2400` was explicitly skipped by the generic function exporter because no native function start existed; bounded instruction evidence settled its behavior without inventing boundaries. No gameplay files were edited.

The smallest useful next step is a bounded trace of readers of the GrandStrategic per-unit preference vector `+0x3f8` (or its accessor), with a testable formula for how a Units Value reaches the actual build request/contract score. A separate offline trace of the required-city field's setters would identify when unrestricted recruitment is requested. Neither is needed to retain the confirmed parser findings above.

## Related durable references

- [Source/profile audit](csc-ai-profile-source-audit-20261028.md)
- [Archived decision cases](csc-ai-offline-chain-cases-20261028.md)
- [Initial native production analysis](csc-ai-native-production-analysis-20261028.md)
- [Development roadmap (historical)](https://github.com/hennogous/Henno-Mods/blob/819b67c/project/docs/integrations/csc-ai-roadmap.md)

All export-relative paths above resolve under the local analysis root `Desktop/Codex/csc-native-ai-analysis-20261028`, not the repository. Raw reconstructed code remains outside the repository.
