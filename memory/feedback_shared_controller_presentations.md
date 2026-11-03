# Repair presentation gaps in the shared controller

Henno clarified on 3 November 2026 that repeated popup stalls should be fixed in
the maintained shared controller so future runs do not rediscover them. Do not
leave a generally necessary presentation handler as a trial-only opt-in.

Natural Wonder discoveries and project-completion cinematics are distinct from
wonder-built/disaster presentations. The standard constructor now installs their
reviewed handlers automatically. See `full_game_controller/README.md` and
`project/docs/research/mods/csc-shared-native-presentation-recovery-20261103.md`.

Keep exact shipped UI-only acknowledgement, finite fresh observer proof,
visibility/stack admission, bounded queued acknowledgements and ambiguous-ACK
replay refusal. Verify actual progress beyond the blocked turn separately from
successful popup dismissal or safe cleanup. Preserve the single controller
owner and frozen experiment inputs while a worker is active.
