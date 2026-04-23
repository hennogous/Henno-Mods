---
name: Write to memory proactively, mid-session
description: Henno explicitly called out that memory should be written as things happen, not batched or skipped
type: feedback
originSessionId: 6bb875f6-5123-4916-9ed4-ebe06470a02a
---
Write to memory when things happen — don't batch it to end-of-day or wait to be asked.

**Why:** Henno called this out directly. Context compaction kills unwritten learnings. The instruction "Text > Brain" and "Don't batch it" in CLAUDE.md are not suggestions.

**How to apply:**
- When a bug is fixed and the fix is non-obvious → write it to the relevant project memory immediately after the commit
- When a design decision is made (e.g. "use bounding-box centre to fix tile offset") → write it now
- When Henno confirms an approach works → update the relevant memory
- The project-specific memory (`~/.claude/projects/.../memory/`) is the primary place for CivAssetForge/CSC work; the global memory (`~/.claude/memory/`) is for cross-project patterns and feedback
- Don't treat memory writes as a separate task — fold them into the same turn as the work
