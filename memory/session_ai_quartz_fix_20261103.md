# Quartz publication correction — 3 November 2026

Henno noticed failed Quartz jobs and requested documentation testing again.
This supersedes the earlier skip-docs-QA preference; see the updated
`feedback_ai_publishing.md` and handbook maintenance instructions.

Latest failed run41667866810 at fbe4f81 rendered the handbook successfully but
verification failed on `Uncatalogued correction source:
COR-006/project/docs/integrations/csc-ai-roadmap.md`. The roadmap deletion
reconciled links and finding sources but missed the correction register.
Removed that target from COR-006 while retaining its actual affected reports.

Earlier run41661593460 at4264f8a failed due to a stale source catalogue after the
shared-controller README changed. The subsequent819b67c run succeeded; it is a
different resolved failure, not a Quartz renderer bug.

Preparation now checks correction targets against the publication catalogue
before Quartz runs. Focused regressions exercise deletion of a corrected source,
rejection while its correction still references it, successful preparation after
reconciliation, removal of the retired generated page, and rejection of an
existing but unpublished source. CI runs these and prepares sources before
installing/building Quartz. The full verifier remains strict.

This is documentation/publishing work only; no game or AI tuning changed.
Run focused tests, the hosted-profile handbook build and verifier; commit/push
only this fix and wait for the Pages build/deploy result before reporting done.
