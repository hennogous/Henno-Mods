-- Mode marker only. Shared signals and assistance are loaded conditionally by
-- ModBuddy: Basic setting + no RH, or automatic RH compatibility. OFF adds no
-- tuning to the native AI and does not alter the independent resource pass.
CREATE TABLE IF NOT EXISTS CSC_AI_Profile (
    Id TEXT PRIMARY KEY,
    Mode TEXT NOT NULL
);
INSERT OR REPLACE INTO CSC_AI_Profile
        (   Id,         Mode   )
VALUES  (   'ACTIVE',   'OFF'   );
