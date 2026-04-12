--==========================================================================================================================
-- CSC: Register resource class names in Ruivo_CAO so tooltips show readable names
-- (MinRings, MustOwn, and the ring-band fix now live in MAB itself.)
--===========================================================================================================================
INSERT OR IGNORE INTO Ruivo_CAO (CustomAdjacentObject, Name) VALUES
    ('CLASS_CSC_BAKERS_BASE',   'LOC_CLASS_CSC_BAKERS_BASE_NAME'),
    ('CLASS_CSC_BAKERS_SPEC',   'LOC_CLASS_CSC_BAKERS_SPEC_NAME');
