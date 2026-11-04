import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { pathToRoot } from "../util/path"

export default (() => {
  const Context: QuartzComponent = ({ fileData }: QuartzComponentProps) => {
    const slug = fileData.slug || "index"
    if (slug === "index" || slug.startsWith("guide/") || slug === "library") return null
    const historical = slug.startsWith("sources/") || slug.startsWith("topics/history/")
    const base = pathToRoot(slug)
    return <aside class="ai-page-context" aria-label="Reading context">
      <strong>{historical ? "Research record" : "Technical reference"}</strong>
      <span>{historical ? "Dated evidence and exploration. " : "Detailed evidence-backed explanation. "}
        <a href={`${base}/`}>Read the current guide</a> or <a href={`${base}/library`}>browse the library</a>.
      </span>
    </aside>
  }
  return Context
}) satisfies QuartzComponentConstructor
