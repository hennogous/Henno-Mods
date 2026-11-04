# RH5 placement incentives versus the CSC native extension

Read-only source review,4 November2026. Finding **AI-C051**.

The installed RH5.097 package clearly implements the general idea of steering
native district choices with extra positive and negative site incentives. It
does not supply evidence that its author uses, or knows about, our direct native
district-site hook. Code can establish implemented techniques, not the author's
complete private knowledge.

## What the installed code establishes

Source root:
`C:/Program Files (x86)/Steam/steamapps/workshop/content/289070/3792072489/`.
`RHAI_V5_Beta.modinfo:4` identifies5.097 Patreon Beta; lines701–719 register the
supporting district SQL in UpdateDatabase RH_AI_VICT at load order630.

| Source | Visible technique |
|---|---|
| `core/Strategies/Supporting_Systems/RH_Improvements.sql:7–14` | Registers custom yield `RH_YIELD_LAST_RESORT`, DefaultValue0.5, plus a DefaultYieldBias item Value5/Favored0. These are declarations, not a measured conversion to native utility. |
| `core/Strategies/Supporting_Systems/RH_Districts.sql:6–17,168–181` | Defines negative natural-wonder/volcano adjacency and positive selected-wonder rules, then attaches broad rules to district definitions. |
| Same district file:38–63,193–209 | Defines and attaches reciprocal Industrial Zone/infrastructure incentives: IZ near Aqueduct+3 or Dam+4; Aqueduct/Dam near IZ+12; Canal near IZ+25. IZ also receives a river signal. Numbers are custom-yield amounts, not Production or Q8 score additions. |
| Same district file:519–545 | Observatory luxury-class and flat Plains/Grassland proxies illustrate incentives expressed using native adjacency selectors. They do not encode exact CSC material tags or a Base+Specialty conjunction. |

This is intentional score steering through data the native evaluator can read.
It supports the general principle behind our intervention. It is not evidence of
an arbitrary Lua callback supplying a different score for every city/district/plot.

## What distinguishes our current method

RH's reviewed route encodes incentives as custom yield/adjacency definitions.
Our prototype calculates CSC-specific placement facts independently and adds a
signed adjustment at the identified native district-site valuation consumer.
That permits exact material matching, conditional first-Mill calculations and
arbitrary per-pair policy without expressing the whole calculation as adjacency
SQL. Both routes feed a native competition; neither alone guarantees the final
proposal, queue selection or completion.

Package inventory contained67 Lua,168 SQL,26 XML,2 ArtDef,2 DEP,1 Markdown,
1 modinfo and1 text file. No DLL/EXE/ASI/Python/JavaScript/C/C++/header file was
found. Searches of Lua/SQL for NetValue, CalculateDistrictValues,
GetBestDistrict, Frida, pointer/memory writes and placement-score wording found
no direct native district-score implementation. Ordinary GameCore playback event
references are not native hooks. This is bounded negative evidence about this
installed package; it cannot exclude external tooling or unpublished work.

The custom yield identifier here differs from `YIELD_RH_PLACEMENT` in older
public-source research. Do not mix those versions. No RH code was changed or
copied into CSC, no native process was attached and no game was run. This review
does not measure the efficacy or side effects of RH's incentives.

See the [earlier5.097 review](csc-rh-v5097-ai-review-20261018.md),
[native extension](../../civ6-ai/topics/native/native-placement-extension.md)
and [district-score anatomy](../../civ6-ai/topics/native/district-score-anatomy.md).

## Reviewed source identity

Exact-byte SHA-256 hashes at review time:

- `RHAI_V5_Beta.modinfo`: `be4a4e4ef1bad904224cb0a307547c84e4beaf1f86a90c97b152c3429fb67739`
- `core/Strategies/Supporting_Systems/RH_Districts.sql`: `c5dc76ae721b4de196a948761181c1958fd72d81a7b0363dc26efd70a1bb33b6`
- `core/Strategies/Supporting_Systems/RH_Improvements.sql`: `f45108cdbbf454d5fcc290d147d477bff973f82ababaf6c0a633659353853361`
