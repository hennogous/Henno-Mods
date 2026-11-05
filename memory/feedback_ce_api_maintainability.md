# CE contribution maintainability

5 November 2026. Henno made WildW's maintainability feedback a high priority.
WildW identified direct MinHook calls, C-style code in a C++ project, and
unlabelled native addresses in the earlier PR. Address all three before asking
Henno to review a replacement contribution.

- Read the closest implementation on CE `develop` first. Reuse its runtime,
  hooks, logging, Lua bindings and lifecycle conventions where they fit.
- Use CE's shared hook layer. If the existing helper cannot report failure or
  preserve grouped installation and rollback, agree on a small shared change.
- Use idiomatic C++ and isolate ABI-mandated C linkage or assembly. Explain
  ownership, lock and context lifetime, generation fences, bounds and cleanup
  at the code that depends on them.
- Name native functions, call sites and layout fields. Tie them to the pinned
  binary and evidence, with a nearby comment explaining the ABI or field role
  and any uncertainty. Keep CSC policy in CSC.

Review upstream fit separately from functional correctness. The qualified
`develop` port still uses direct MinHook calls and C. Its tests and readability
pass are a behavior reference for that refactor. The CE handoff records the
remaining work and the specific limitation of `Runtime::CreateHook`.
