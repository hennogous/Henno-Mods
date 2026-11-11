# Retired AI handbook renderer

Retired from routine research and CI on 11 November 2026 at Henno's request.
Current knowledge is plain Markdown plus the concrete `civ6-ai` skill references.
Start at [CSC AI research](../../docs/civ6-ai/index.md).

The files below preserve the former Quartz projection/build implementation for
historical reproducibility. Do not run these commands or refresh its catalogue
as part of ordinary findings, roadmap or skill updates. The current public CSC
site uses its normal Quartz configuration and does not import this handbook.

---

# AI handbook build

The maintained content is [the handbook](../../docs/civ6-ai/index.md).
This tool prepares a source-linked projection and builds it with the existing
Quartz installation in `docs/`; there is no second site framework or lockfile.

```text
node project/tools/ai_knowledge/build.mjs --update-catalog
node project/tools/ai_knowledge/verify.mjs
node project/tools/ai_knowledge/serve.mjs
```

Use `--base-url=hennogous.github.io/Henno-Mods/ai` for the Pages build.
The output is `docs/.ai-handbook/site/`, the content projection is
`docs/.ai-handbook/content/`, and both are ignored. The generated evidence
library includes original source text with historical-status banners, source
paths and hashes. Native evidence databases and private chat transcripts are
not copied. `--update-catalog` updates the tracked source catalogue after source
review; ordinary builds fail if a catalogued file has changed.

`CSC_AI_PYTHON` can select a Python 3 executable. Otherwise the tool uses `python`
on Windows and `python3` elsewhere. Install the existing Quartz dependencies
with `npm ci` in `docs/` if needed.

The pinned Mermaid 11.4.0 standalone bundle retains its MIT licence and matches
this Quartz version's CDN import. A guarded postbuild substitution supplies the
local bundle so diagrams work without downloading a renderer. Changes to the
upstream Quartz Mermaid import deliberately fail this step for review.

The loopback-only reader runs on port8091. Stop with Ctrl+C. The build does not
run a game, modify mod content, create a commit or publish by itself. The existing
GitHub Pages workflow builds the handbook beside the player site after a push.
