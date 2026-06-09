--==========================================================================================================================
-- CSC: Register resource class names in Ruivo_CAO so tooltips show readable names
-- (MinRings, MustOwn, and the ring-band fix now live in MAB itself.)
--===========================================================================================================================
INSERT OR IGNORE INTO Ruivo_CAO
    (CustomAdjacentObject,      Name,                           ArtdefOverlayEntry      )     VALUES
    ('CLASS_CSC_BAKERS_BASE',   'LOC_CLASS_CSC_BASE_NAME',      'CSC_Base_Materials'    ),
    ('CLASS_CSC_BAKERS_SPEC',   'LOC_CLASS_CSC_SPEC_NAME',      'CSC_Spec_Materials'    ),
    ('DISTRICT_CITY_CENTER',    'LOC_CLASS_CSC_SALES_NAME',     'CSC_Sales'             );