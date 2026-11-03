"""Build a reproducible, source-linked content tree for the AI Quartz handbook.

Only Markdown/JSON is published. Native dumps, saves, chat transcripts and installed
mod packages remain in their evidence stores. No game or AI code is executed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
KB = ROOT / "project/docs/civ6-ai"
DEFAULT_STAGE = ROOT / "docs/.ai-handbook/content"
REPORT_PREFIXES = ("csc-ai-", "csc-native-", "civ6-industrial-", "civ6-district-",
                   "csc-future-", "csc-rh-", "csc-aiplus-", "csc-real-strategy-",
                   "csc-shared-native-", "native-custom-resourceclass-",
                   "native-resourceclass-", "csc-tailor-density-", "csc-map-material-",
                   "csc-continental-", "csc-implemented-materials-", "csc-material-abundance-",
                   "csc-offline-abundance-", "csc-offline-generation-", "csc-native-luxury-",
                   "csc-ui-exit-crash-", "csc-ancient-guidance-", "csc-civic-",
                   "csc-long-guidance-comparison-", "csc-research-influence-findings-")
INTEGRATIONS = ("csc-ai-", "csc-native-test-controller", "csc-material-map-assistance")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def title_of(body: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", body, re.M)
    return match.group(1).strip() if match else fallback


def collect() -> list[dict]:
    selected = {}
    for p in (ROOT / "project/docs/research/mods").glob("*.md"):
        if p.name.startswith(REPORT_PREFIXES):
            selected[p] = "report"
    for p in (ROOT / "project/docs/integrations").glob("*.md"):
        if p.name.startswith(INTEGRATIONS):
            selected[p] = "integration"
    for p in (ROOT / "memory").glob("*.md"):
        if ("ai_" in p.name or "_ai_" in p.name or "csc_ai" in p.name
                or p.name in ("session_native_ai_instrumentation_20261028.md",
                              "feedback_shadow_native_game_control.md")):
            selected[p] = "agent-note"
    for rel in ("project/tools/ai_baseline/full_game_controller/README.md",
                "project/tools/native_ai/README.md", "project/firetuner/FIRETUNER-PROTOCOL.md",
                "project/firetuner/CE-API-REPORT.md", "project/docs/research/mods/community-extension-modding.md"):
        p = ROOT / rel
        if p.is_file():
            selected[p] = "tool-reference"
    rows = []
    for path, kind in sorted(selected.items(), key=lambda x: x[0].as_posix()):
        body = read(path)
        # Stable across Windows autocrlf and Linux Pages checkout. Native artifacts
        # retain their own exact-byte hashes in the original investigation reports.
        canonical = body.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
        rel = path.relative_to(ROOT).as_posix()
        # Include the directory path in route identity so duplicate stems are safe.
        route = "sources/" + rel.removesuffix(".md") + ".md"
        date = re.search(r"(20\d{6})", path.name)
        rows.append({"path": rel, "title": title_of(body, path.stem), "kind": kind,
                     "date": date.group(1) if date else None, "bytes": len(canonical),
                     "sha256": hashlib.sha256(canonical).hexdigest(),
                     "hash_encoding": "UTF-8 without BOM; LF newlines", "site_path": route})
    return rows


LINK = re.compile(r"(?<!!)\[([^\]\n]+)\]\(<?([^\n)]+?)>?\)")


def rewrite_links(body: str, original: Path, destination: Path,
                  routes: dict[Path, Path], stage: Path) -> str:
    def replace(m):
        label, target = m.groups()
        target = target.strip()
        # Preserve external links, anchors and Codex thread citations.
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
            return m.group(0)
        file_part, sep, fragment = target.partition("#")
        source = (original.parent / unquote(file_part)).resolve()
        if source in routes:
            relative = os.path.relpath(routes[source], destination.parent).replace("\\", "/")
            return f"[{label}](<{relative}{sep}{fragment}>)"
        try:
            rel = source.relative_to(ROOT).as_posix()
        except ValueError:
            return label + " (local evidence reference)"
        if source.is_file():
            # Source code links remain source links, rather than copying packages.
            return f"[{label}](https://github.com/hennogous/Henno-Mods/blob/main/{rel}{sep}{fragment})"
        if original.is_relative_to(KB):
            raise ValueError(f"Broken maintained link in {original.relative_to(KB)}: {target}")
        return label + " (historical local reference)"
    return LINK.sub(replace, body)


def frontmatter(title: str, tags: list[str], **extra) -> str:
    fields = {"title": title, "tags": tags, **extra}
    return "---\n" + "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fields.items()) + "\n---\n\n"


def prepare(stage: Path, update_catalog: bool) -> dict:
    stage = stage.resolve()
    expected_parent = (ROOT / "docs/.ai-handbook").resolve()
    # Quartz itself cleans output recursively: constrain both content and output.
    if stage.parent != expected_parent or stage.name != "content":
        raise ValueError("Staging must be docs/.ai-handbook/content")
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    catalog = collect()
    catalog_path = KB / "data/source-catalog.json"
    serialized = json.dumps({"schema_version": 2, "sources": catalog}, ensure_ascii=False, indent=2) + "\n"
    if update_catalog:
        catalog_path.parent.mkdir(parents=True, exist_ok=True)
        catalog_path.write_text(serialized, encoding="utf-8")
    elif not catalog_path.is_file() or catalog_path.read_text(encoding="utf-8") != serialized:
        raise ValueError("Source catalog is stale. Run prepare.py --update-catalog after reviewing changed sources.")
    pages = sorted(p for p in KB.rglob("*.md") if "skill" not in p.relative_to(KB).parts)
    routes = {p.resolve(): stage / p.relative_to(KB) for p in pages}
    routes.update({(ROOT / r["path"]).resolve(): stage / r["site_path"] for r in catalog})
    for generated in ("findings.md", "evidence.md", "coverage.md", "diagrams.md"):
        routes[(KB / generated).resolve()] = stage / generated
    corrections_path = KB / "data/corrections.json"
    corrections = json.loads(read(corrections_path)) if corrections_path.is_file() else []
    for p in pages:
        dest = routes[p.resolve()]
        dest.parent.mkdir(parents=True, exist_ok=True)
        body = read(p)
        if not body.startswith("---\n"):
            title = title_of(body, p.stem)
            body = frontmatter(title, ["handbook"]) + re.sub(r"^#\s+[^\n]+\n", "", body, count=1)
        body = rewrite_links(body, p, dest, routes, stage)
        finding_route = os.path.relpath(stage / "findings.md", dest.parent).replace("\\", "/")
        body = re.sub(r"\[(AI-[NCH]\d{3})\](?!\()", lambda m: f"[{m[1]}]({finding_route}#{m[1].lower()})", body)
        dest.write_text(body, encoding="utf-8")
    for row in catalog:
        source = ROOT / row["path"]
        dest = stage / row["site_path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        banner = ("> [!warning] Historical evidence / implementation record\n"
                  "> This is an original source document. Its dated status, proposed next steps and live instructions are historical. "
                  "Use the [current handbook](/index) and [corrections](/topics/history/corrections-and-cautions) for reconciled understanding.\n\n")
        provenance = (f"Source: `{row['path']}` · normalized-text SHA-256 `{row['sha256']}` · "
                      f"[Repository source](https://github.com/hennogous/Henno-Mods/blob/main/{row['path']})\n\n")
        for correction in corrections:
            if row["path"] in correction["affected_sources"]:
                banner += (f"> [!important] {correction['id']} — later correction or qualification\n"
                           f"> {correction['summary']} See the [reconciled corrections page](/topics/history/corrections-and-cautions).\n\n")
        body = frontmatter(row["title"], ["evidence", row["kind"]]) + banner + provenance + re.sub(r"^#\s+[^\n]+\n", "", read(source), count=1)
        dest.write_text(rewrite_links(body, source, dest, routes, stage), encoding="utf-8")
    findings = []
    for p in sorted((KB / "data").glob("*-findings.json")):
        findings.extend(json.loads(read(p)))
    ids = {r["id"] for r in findings}
    if len(ids) != len(findings):
        raise ValueError("Duplicate finding IDs")
    for row in findings:
        if not (KB / row["topic"]).is_file():
            raise ValueError(f"Missing finding topic: {row['id']}: {row['topic']}")
        for dep in row.get("depends_on", []):
            if dep not in ids:
                raise ValueError(f"Unknown dependency {dep} from {row['id']}")
        for other in row.get("related", []):
            if other not in ids:
                raise ValueError(f"Unknown related finding {other} from {row['id']}")
        for source in row["sources"]:
            if not source.startswith(("thread:", "codex:")) and not (ROOT / source).is_file():
                raise ValueError(f"Missing finding source {source}")
    finding_lines = [frontmatter("Finding register", ["reference"]),
                     "Each finding has a stable ID. Evidence type and current standing are separate. "
                     "Accepted findings remain limited by their stated scope.\n"]
    for row in findings:
        finding_lines += [f"## {row['id']}\n", f"**{row['title']}**\n", row["statement"] + "\n",
                          f"**Standing:** {row['status']} · **Evidence:** {', '.join(row['evidence_types'])}\n",
                          f"**Scope:** {row['scope']}\n", f"**Limits:** {row['limits']}\n",
                          f"[Topic]({row['topic']})\n"]
        if row.get("depends_on"):
            finding_lines.append("**Depends on:** " + ", ".join(f"[{d}](#{d.lower()})" for d in row['depends_on']) + "\n")
        if row.get("related"):
            finding_lines.append("**Related:** " + ", ".join(f"[{d}](#{d.lower()})" for d in row['related']) + "\n")
        for source in row["sources"]:
            if source.startswith(("thread:", "codex:")):
                finding_lines.append(f"- [AI optimisation](codex://threads/{source.removeprefix('thread:')})\n")
            else:
                r = next((r for r in catalog if r["path"] == source), None)
                if r:
                    finding_lines.append(f"- [{r['title']}]({r['site_path']})\n")
    (stage / "findings.md").write_text("\n".join(finding_lines), encoding="utf-8")
    diagrams = [frontmatter("Diagram atlas", ["reference"]),
                "These diagrams are generated from the maintained explanations. Follow each topic for its evidence and limits. "
                "Use a diagram's expand button for a larger view.\n"]
    diagram_count = 0
    for page in pages:
        body = read(page)
        blocks = re.findall(r"```mermaid\s*\n(.*?)```", body, re.S)
        for index, block in enumerate(blocks, 1):
            diagram_count += 1
            rel = page.relative_to(KB).as_posix()
            title = title_of(body, page.stem)
            diagrams += [f"## {title}" + (f" — {index}" if len(blocks)>1 else "") + "\n",
                         f"[Read this explanation]({rel})\n", "```mermaid\n" + block.strip() + "\n```\n"]
    (stage / "diagrams.md").write_text("\n".join(diagrams), encoding="utf-8")
    lines = [frontmatter("Evidence library", ["reference"]),
             f"{len(catalog)} original documents are catalogued by path and content hash. "
             "These records preserve dated results; the topic pages explain our current understanding.\n",
             "| Document | Type | Date |\n|---|---|---|\n"]
    for row in sorted(catalog, key=lambda r: (r["kind"], r["date"] or "", r["title"])):
        lines.append(f"| [{row['title']}]({row['site_path']}) | {row['kind']} | {row['date'] or 'undated'} |\n")
    (stage / "evidence.md").write_text("".join(lines), encoding="utf-8")
    (stage / "data").mkdir(exist_ok=True)
    (stage / "data/source-catalog.json").write_text(serialized, encoding="utf-8")
    (stage / "data/findings.json").write_text(json.dumps(findings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name in ("thread-review.json", "corrections.json"):
        source = KB / "data" / name
        if source.is_file():
            shutil.copyfile(source, stage / "data" / name)
    summary = {"sources": len(catalog), "topics_and_guides": len(pages), "findings": len(findings),
               "maintained_diagrams": diagram_count,
               "markdown_pages": len(list(stage.rglob('*.md'))), "stage": str(stage)}
    (stage.parent / "preparation.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-catalog", action="store_true")
    args = parser.parse_args()
    print(json.dumps(prepare(DEFAULT_STAGE, args.update_catalog), indent=2))
