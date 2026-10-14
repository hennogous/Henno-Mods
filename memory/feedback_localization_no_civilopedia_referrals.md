# Player-facing localization: no Civilopedia referrals

Henno's explicit preference, 13 October 2026: never tell players to consult a
Civilopedia page for requirements, effects or details. Describe relevant
information directly; normal linked service names are sufficient.

Removed all 17 such source sentences from Bakers, Tailors and Garden support,
and regenerated their SQL. The shared customer localization contract now
forbids these referrals. loc_md_to_sql.py rejects referral prose in regular
entries and raw SQL blocks; regression coverage includes both modes.
