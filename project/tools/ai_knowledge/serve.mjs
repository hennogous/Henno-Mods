// Read-only loopback server for Quartz output; no game control or external binding.
import http from "node:http"
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..")
const site = path.join(root, "docs/.ai-handbook/site")
const types = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml", ".png": "image/png", ".woff2": "font/woff2" }
if (!fs.existsSync(path.join(site, "index.html"))) throw new Error("Build the handbook first.")
const server = http.createServer((req, res) => {
  let relative
  try { relative = decodeURIComponent(new URL(req.url, "http://localhost").pathname).replace(/^\/+/, "") }
  catch { res.writeHead(400).end(); return }
  let file = path.resolve(site, relative || "index.html")
  if (file !== site && !file.startsWith(site + path.sep)) { res.writeHead(403).end(); return }
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, "index.html")
  if (!fs.existsSync(file) && !path.extname(file)) file += ".html"
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404).end("Page not found"); return }
  res.writeHead(200, { "Content-Type": types[path.extname(file)] || "application/octet-stream" })
  fs.createReadStream(file).pipe(res)
})
server.listen(8091, "127.0.0.1", () => console.log("AI handbook: http://localhost:8091/ (Ctrl+C to stop)"))
for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => server.close(() => process.exit(0)))
