// Shared by actual search and focused checks; no change to ordinary CSC search.
export function filterAIReaderResults<T extends { slug: string }>(items: T[], scope?: string): T[] {
  return scope === "guide" ? items.filter((item) => item.slug === "index" || item.slug.startsWith("guide/")) : items
}
