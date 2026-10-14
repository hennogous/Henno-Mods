# Blender export runner defaults

Henno requested on 7 October 2026 that normal `export_assets.py` invocations
require only the blend directory. A bare quoted path is now accepted;
`--blend-directory` remains supported, and supplying both forms is rejected.
The mod root now defaults relative to the
script's repository; the prop library and Blender default to Shadow's specified
paths. Existing repository-local texconv selection and PATH fallback remain.
All four flags still support explicit overrides. Usage and paths are documented
in `project/docs/art/blender-scene-export.md`.

Validation: six existing runner tests pass; syntax, directory-only argument
parsing, default paths and explicit overrides checked without exporting assets.
