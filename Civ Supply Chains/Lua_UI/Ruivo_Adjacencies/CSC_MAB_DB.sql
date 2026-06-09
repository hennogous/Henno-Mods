--==========================================================================================================================
-- CSC: Register custom adjacent object names and overlay art for MAB tooltips/icons.
-- Material classes use material icons; sales classes use sales icons; the Quarter district itself uses the goods icon for customer-facing return yields.
--===========================================================================================================================
INSERT OR IGNORE INTO Ruivo_CAO
    (CustomAdjacentObject,          Name,                                       ArtdefOverlayEntry      )     VALUES
    ('CLASS_CSC_BAKERS_BASE',        'LOC_CLASS_CSC_BASE_NAME',                 'CSC_Base_Materials'    ),
    ('CLASS_CSC_BAKERS_SPEC',        'LOC_CLASS_CSC_SPEC_NAME',                 'CSC_Spec_Materials'    ),
    ('CLASS_CSC_BAKERS_SALES',       'LOC_CLASS_CSC_SALES_NAME',                'CSC_Sales'             ),
    ('DISTRICT_CSC_BAKERS_QUARTER',  'LOC_DISTRICT_CSC_BAKERS_QUARTER_NAME',    'CSC_Goods'             );
