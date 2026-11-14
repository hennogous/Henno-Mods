# Lead with findings and keep qualification proportional

Henno, 14 November 2026: maintain accuracy, but stop repeatedly explaining what
an experiment does not prove. The presentation is irritating and obscures useful
learning. He also wants this habit checked in research decisions and code.

- Start updates with the useful finding, its practical implication and next step.
- State uncertainty plainly when it changes a conclusion or action. Keep detailed
  evidence scope in the supporting report; avoid repeating the evidence ladder.
- Accept useful partial results and make reasonable estimates. Reserve additional
  investigation for a question that can change implementation or interpretation.
- Review diagnostic stop conditions separately from game/native safety guards.
  A missing observation should be recorded and assessed against the affected
  metric, rather than automatically discarding a completed game or halting a
  campaign. Preserve failures and raw records when recovering an analysis.
- Do not weaken native write/layout checks, session ownership, or protection of
  Henno's active game to satisfy this preference.

Concrete example: the first no-CSC control completed turn 250 and clean shutdown,
but an unresolved diagnostic event assertion stopped the campaign. Report and
audit that observation gap; recover the completed game's useful measurements.
