import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { pathToRoot } from "../util/path"
import { classNames } from "../util/lang"

// A reading order, deliberately independent of the evidence directory structure.
const chapters = [
  ["index", "Start here"],
  ["guide/how-the-ai-decides", "How the AI decides"],
  ["guide/steering-the-ai", "Steering the AI"],
  ["guide/teaching-it-csc", "Teaching it CSC"],
  ["guide/what-next", "What we’re investigating"],
]

export default (() => {
  const Nav: QuartzComponent = ({ fileData, displayClass }: QuartzComponentProps) => {
    const base = pathToRoot(fileData.slug!)
    const link = (slug: string) => slug === "index" ? `${base}/` : `${base}/${slug}`
    return <nav class={classNames(displayClass, "ai-reader-nav")} aria-label="AI guide">
      <p class="ai-nav-label">Read the guide</p>
      <ol>{chapters.map(([slug, title]) => <li key={slug}>
        <a href={link(slug)} aria-current={fileData.slug === slug ? "page" : undefined}>{title}</a>
      </li>)}</ol>
      <a class="ai-library-link" href={link("library")}>Research library</a>
    </nav>
  }
  return Nav
}) satisfies QuartzComponentConstructor
