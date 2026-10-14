# Bakers material contract

`materials.yaml` is a materials-only design declaration transcribed from the
canonical Bakers design page. It defines expected resources and their material
roles. It is not a full Quarter implementation contract or phase approval.
The canonical source hash protects the transcription from unnoticed source drift;
reconcile design changes before updating it.

`material-validation.yaml` supplies engine file and loading-condition bindings
by category. Resource identities and roles must not be repeated there.

The shared resource-pedia assertion reads this declaration and the existing
Tailors design/implementation contracts. It verifies gameplay mappings, matching
loading conditions, Quarter material lists, and reciprocal resource chapters.
Missing resources are failures even if absent from both gameplay and localization;
unexpected gameplay mappings are failures for the Quarters under validation.

For full Quarter contracts, the foundation gate must be approved, implementing,
ready for review, or accepted before their materials enter this check. Other
unfinished Quarters' legacy mappings do not establish design expectations.

Run the focused regressions with:

```powershell
py -3 -m unittest discover -s project/tools/quarter_contracts/tests -p test_mapped_resource_pedia.py
```
