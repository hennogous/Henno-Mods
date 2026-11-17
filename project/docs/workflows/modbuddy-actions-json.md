# ModBuddy Action JSON Workflow

Updated 17 November 2026.

ModBuddy stores `ActionCriteriaData`, `FrontEndActionData`, and `InGameActionData` in `Civ Supply Chains/Civ Supply Chains.civ6proj` as minified XML inside CDATA. Editing those blocks directly is error-prone, especially when adding criteria or moving files between action types.

Use the JSON mirror instead:

```powershell
python project\tools\modbuddy\civ6proj_actions.py export
python project\tools\modbuddy\civ6proj_actions.py check
python project\tools\modbuddy\civ6proj_actions.py patch
```

Default paths:

- Project file: `Civ Supply Chains/Civ Supply Chains.civ6proj`
- JSON mirror: `project/modbuddy/CivSupplyChains.actions.json`

## Normal Edit Flow

1. Treat JSON as the editing source. If ModBuddy changed actions, reconcile those changes before using `export`, which overwrites JSON.
2. Edit `project/modbuddy/CivSupplyChains.actions.json`.
3. Run `check` to verify the JSON can regenerate valid CDATA.
4. Run `sort` to order both action lists and regenerate CDATA. Use `patch` when deliberately preserving the existing order.
5. Review the `.civ6proj` diff before building.

## JSON Shape

`blocks.actionCriteria` stores criteria as generic XML-node JSON so uncommon ModBuddy criteria can round-trip safely.

`blocks.frontEndActions` and `blocks.inGameActions` store each action as:

```json
{
  "type": "UpdateDatabase",
  "id": "CSC_Q_ALL",
  "properties": {
    "LoadOrder": "95"
  },
  "criteria": [
    "SomeCriterion"
  ],
  "files": [
    "Data/CSC_Q_ALL_Schema.sql"
  ]
}
```

Multiple `criteria` entries become multiple `<Criteria>` child elements, which ModBuddy treats as AND-gated criteria. File paths in action blocks use forward slashes. Keep MSBuild `<Content Include="...">` paths in the main project file as backslash paths.

## Notes

- The generated CDATA remains minified because ModBuddy already stores it that way.
- The tool patches only `ActionCriteriaData`, `FrontEndActionData`, and `InGameActionData`.
- Adding a new file still requires both a `<Content Include="...">` entry and an action entry in the JSON.
- Each Content copy destination must be unique. When several old files become
  one shared file, keep one Content entry for it. The SDK Copy task otherwise
  batches multiple SourceFiles against one DestinationFiles value and fails.
  Both the action `check` command and Quarter content-wiring validator reject
  duplicate destinations, including Windows case/slash aliases.
- Do not hand-edit the generated `.modinfo`; ModBuddy overwrites it from the `.civ6proj`.

## Ordering and consolidation

Every action must declare a numeric `LoadOrder`. Sort by **LoadOrder, action
type, action ID**, with alphabetical comparisons for the last two keys:

```powershell
python project/tools/modbuddy/civ6proj_actions.py sort
python -m unittest discover -s project/tools/modbuddy -q
```

The shipping-manifest tests compare actual project CDATA against JSON, check
ordering, and check action files exist and are included in the project. `check`
checks JSON round-tripping; the tests also detect an out-of-date project.

Settings database/text actions and icons use 100. The Pedia shared import uses 490
so it is available before UI contexts at 500. Other established phases remain.
File order within an action is dependency order: shared Schema before Common.

`organize_actions.py` is the reviewed consolidation helper. It combines only
UpdateDatabase, UpdateText, UpdateIcons, ImportFiles and DoNothing actions with
identical properties, criteria and additional metadata. New merged cohorts need
a deliberate descriptive action ID. Gameplay scripts, UI contexts and script
replacements keep their own actions and identities. Running `sort` never merges.

The 17 November cleanup reduced the working in-game action list from 109 to 90
(the committed base goes from 105 to 87),
including Quarter/Gold/M&C, text and shared import groups. Existing criteria,
context properties and file coverage were retained. These are authoring actions;
ModBuddy generates the resulting `.modinfo` at build time.
