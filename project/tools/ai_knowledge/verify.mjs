// Verify the published projection, source integrity and maintained knowledge links.
import fs from "node:fs"
import path from "node:path"
import crypto from "node:crypto"
import { fileURLToPath } from "node:url"
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..")
const kb = path.join(root, "project/docs/civ6-ai")
const site = path.join(root, "docs/.ai-handbook/site")
const read = (p) => fs.readFileSync(p, "utf8").replace(/^\uFEFF/, "")
const profile = JSON.parse(read(path.join(root, "docs/.ai-handbook/build-profile.json")))
const sha = (p) => crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex")
function walk(dir) { return fs.readdirSync(dir, { withFileTypes: true }).flatMap(e => e.isDirectory() ? walk(path.join(dir, e.name)) : [path.join(dir, e.name)]) }
const errors = []
const warnings = []
const sources = JSON.parse(read(path.join(kb, "data/source-catalog.json"))).sources
const findings = fs.readdirSync(path.join(kb, "data")).filter(n => n.endsWith("-findings.json")).flatMap(n => JSON.parse(read(path.join(kb, "data", n))))
const ids = new Set(findings.map(f => f.id))
if (ids.size !== findings.length) errors.push("Finding IDs are not unique")
const corrections = JSON.parse(read(path.join(kb, "data/corrections.json")))
for (const c of corrections) for (const s of c.affected_sources) {
  if (!sources.some(r => r.path === s)) errors.push(`Uncatalogued correction source: ${c.id}/${s}`)
}
for (const s of sources) {
  const p = path.join(root, s.path)
  const contentHash = fs.existsSync(p) ? crypto.createHash("sha256").update(read(p).replace(/\r\n?/g,"\n"),"utf8").digest("hex") : null
  if (contentHash !== s.sha256) errors.push(`Changed/missing catalogued source: ${s.path}`)
}
for (const f of findings) {
  if (!/^AI-[NCH]\d{3}$/.test(f.id)) errors.push(`Invalid ID: ${f.id}`)
  if (!["accepted", "provisional", "superseded"].includes(f.status)) errors.push(`Invalid standing: ${f.id}`)
  for (const type of f.evidence_types) if (!["static", "runtime", "source", "inference"].includes(type)) errors.push(`Invalid evidence type: ${f.id}/${type}`)
  for (const key of ["title", "statement", "scope", "limits", "topic"]) if (!f[key]) errors.push(`Missing ${key}: ${f.id}`)
  if (!f.sources.length) errors.push(`Finding without sources: ${f.id}`)
  for (const d of f.depends_on || []) if (!ids.has(d)) errors.push(`Missing dependency ${f.id} -> ${d}`)
  for (const d of f.related || []) if (!ids.has(d)) errors.push(`Missing related finding ${f.id} -> ${d}`)
  for (const s of f.sources) {
    if (!s.startsWith("thread:") && !s.startsWith("codex:") && !sources.some(r => r.path === s)) errors.push(`Uncatalogued finding source: ${f.id}/${s}`)
  }
}
const maintained = walk(kb).filter(p => p.endsWith(".md"))
for (const p of maintained) {
  for (const m of read(p).matchAll(/\[?(AI-[NCH]\d{3})\]?/g)) if (!ids.has(m[1])) errors.push(`Unknown finding in ${path.relative(kb,p)}: ${m[1]}`)
  // A local-only source can otherwise turn into a broken GitHub link after push.
  // Require curated document/data references outside the handbook to be catalogued.
  for (const m of read(p).matchAll(/(?<!!)\[[^\]\n]+\]\(<?([^\n)]+?)>?\)/g)) {
    const target = m[1]
    if (/^[a-z][a-z0-9+.-]*:/i.test(target) || target.startsWith("#")) continue
    const filePart = decodeURIComponent(target.split("#")[0])
    const absolute = path.resolve(path.dirname(p), filePart)
    if (absolute.startsWith(kb + path.sep) || !/\.(md|json)$/i.test(filePart)) continue
    const rel = path.relative(root, absolute).replaceAll("\\", "/")
    if (!sources.some(s => s.path === rel)) errors.push(`Uncatalogued maintained reference: ${path.relative(kb,p)} -> ${rel}`)
  }
}
const html = walk(site).filter(p => p.endsWith(".html"))
// The reader surface must not accidentally regress to the research file tree.
const readerSlugs = ["index", "guide/how-the-ai-decides", "guide/steering-the-ai", "guide/teaching-it-csc", "guide/what-next", "library"]
for (const slug of readerSlugs) {
  const file = path.join(site, slug + ".html")
  if (!fs.existsSync(file)) { errors.push(`Missing reader page: ${slug}`); continue }
  const text = read(file)
  if (!text.includes('aria-label="AI guide"')) errors.push(`Missing chapter navigation: ${slug}`)
  if (!text.includes('aria-label="Search scope"')) errors.push(`Missing explicit library search scope: ${slug}`)
  if (/class="[^"]*\bexplorer\b/.test(text)) errors.push(`Research tree returned to reader page: ${slug}`)
  if (/class="[^"]*\bgraph\b/.test(text)) errors.push(`Research graph returned to reader page: ${slug}`)
}
const anchors = new Map(html.map(p => [p, new Set([...read(p).matchAll(/\bid="([^"]+)"/g)].map(m => m[1]))]))
let localLinks = 0
let diagrams = 0
for (const file of html) {
  const text = read(file)
  const historical = path.relative(site, file).replaceAll("\\", "/").startsWith("sources/")
  if (!text.includes('name="ai-handbook"')) errors.push(`Missing handbook identity: ${file}`)
  diagrams += [...text.matchAll(/class="mermaid"/g)].length
  for (const m of text.matchAll(/\b(?:href|src)="([^"]+)"/g)) {
    const target = m[1].replaceAll("&amp;", "&")
    if (!target || /^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(target)) continue
    let pathname, fragment
    try { [pathname, fragment] = target.split("#").map(decodeURIComponent) } catch { continue }
    pathname = pathname.split("?")[0]
    if (profile.basePath && (pathname === profile.basePath || pathname.startsWith(profile.basePath + "/"))) {
      pathname = pathname.slice(profile.basePath.length) || "/"
    }
    let resolved = pathname.startsWith("/") ? path.join(site, pathname) : path.resolve(path.dirname(file), pathname || path.basename(file))
    if (fs.existsSync(resolved) && fs.statSync(resolved).isDirectory()) resolved = path.join(resolved, "index.html")
    if (!fs.existsSync(resolved) && !path.extname(resolved)) resolved += ".html"
    localLinks++
    if (!fs.existsSync(resolved)) {
      (historical ? warnings : errors).push(`Missing local target ${path.relative(site,file)} -> ${target}`)
    } else if (fragment && resolved.endsWith(".html") && !anchors.get(resolved)?.has(fragment)) {
      (historical ? warnings : errors).push(`Missing anchor ${path.relative(site,file)} -> ${target}`)
    }
  }
}
const vendor = JSON.parse(read(path.join(root, "project/tools/ai_knowledge/vendor/provenance.json")))
if (sha(path.join(site, "static/mermaid-11.4.0.min.js")) !== vendor.sha256) errors.push("Mermaid vendor integrity mismatch")
const summary = { ok: errors.length === 0, sources: sources.length, findings: findings.length,
  maintained_markdown: maintained.length, html_pages: html.length, diagram_blocks: diagrams,
  checked_local_links: localLinks, historical_link_warnings: warnings.length, errors,
  warnings: warnings.slice(0, 40), checked_at: new Date().toISOString() }
fs.writeFileSync(path.join(root, "docs/.ai-handbook/verification.json"), JSON.stringify(summary,null,2)+"\n")
console.log(JSON.stringify(summary,null,2))
if (errors.length) process.exitCode = 1
