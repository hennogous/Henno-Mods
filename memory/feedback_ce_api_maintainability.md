# CE contribution maintainability

5 November 2026. Henno reports WildW's concern about maintainability of code
written by AI assistants. Upstream API contributions need especially clear,
accurate comments and readable control flow, reviewed alongside correctness.
Explain purpose and reasoning: native ABI/in-out contracts and evidence,
qualification boundaries, ownership, thread/context lifetime, generation fences,
locking, units/limits, failure and cleanup behavior. Distinguish runtime proof
from source-only assumptions. Avoid boilerplate and comments that merely restate
syntax. Keep mod-specific policy outside the generic CE API. A README alone
does not replace useful comments beside fragile native code.
