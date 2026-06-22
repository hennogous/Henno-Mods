# ModBuddy Action JSON Workflow

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

1. Run `export` before starting if the `.civ6proj` may have changed in ModBuddy.
2. Edit `project/modbuddy/CivSupplyChains.actions.json`.
3. Run `check` to verify the JSON can regenerate valid CDATA.
4. Run `patch` to regenerate the three CDATA blocks in the `.civ6proj`.
5. Review the `.civ6proj` diff before building.

## JSON Shape

`blocks.actionCriteria` stores criteria as generic XML-node JSON so uncommon ModBuddy criteria can round-trip safely.

`blocks.frontEndActions` and `blocks.inGameActions` store each action as:

```json
{
  "type": "UpdateDatabase",
  "id": "CSC_Q_SETUP",
  "properties": {
    "LoadOrder": "95"
  },
  "criteria": [
    "SomeCriterion"
  ],
  "files": [
    "Data/CSC_Q_SETUP.sql"
  ]
}
```

Multiple `criteria` entries become multiple `<Criteria>` child elements, which ModBuddy treats as AND-gated criteria. File paths in action blocks use forward slashes. Keep MSBuild `<Content Include="...">` paths in the main project file as backslash paths.

## Notes

- The generated CDATA remains minified because ModBuddy already stores it that way.
- The tool patches only `ActionCriteriaData`, `FrontEndActionData`, and `InGameActionData`.
- Adding a new file still requires both a `<Content Include="...">` entry and an action entry in the JSON.
- Do not hand-edit the generated `.modinfo`; ModBuddy overwrites it from the `.civ6proj`.
