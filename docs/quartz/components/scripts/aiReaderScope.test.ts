import test from "node:test"
import assert from "node:assert/strict"
import { filterAIReaderResults } from "./aiReaderScope"

test("historical matches cannot crowd out current guide chapters", () => {
  const results = Array.from({ length: 80 }, (_, i) => ({ slug: `sources/report-${i}` }))
  results.push({ slug: "guide/how-the-ai-decides" }, { slug: "index" }, { slug: "topics/native/district-choice" })
  assert.deepEqual(filterAIReaderResults(results, "guide").slice(0, 8), [
    { slug: "guide/how-the-ai-decides" }, { slug: "index" },
  ])
  assert.equal(results.length, 83)
})

test("full-library and ordinary CSC searches retain their complete candidates", () => {
  const results = [{ slug: "sources/report" }, { slug: "library" }, { slug: "guide/what-next" }]
  assert.deepEqual(filterAIReaderResults(results, "all"), results)
  assert.deepEqual(filterAIReaderResults(results), results)
})
