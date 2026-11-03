-- Exact shared UI palette for both Quarter lenses and district placement.
-- Colours are normalized from the approved 8-bit hex values. Unready fills
-- use 30% for Base and 20% otherwise; ready fills use 60%. Edges/key are opaque.
-- The generic white Quarter colours remain only as an unmapped-key fallback.
INSERT OR REPLACE INTO Colors
        (   Type,                                    Red,           Green,         Blue,          Alpha   )
VALUES  (   'COLOR_CSC_LENS_QUARTER',                1.000000000,   1.000000000,   1.000000000,   0.60   ),
        (   'COLOR_CSC_LENS_QUARTER_EMPTY',          1.000000000,   1.000000000,   1.000000000,   0.20   ),
        (   'COLOR_CSC_LENS_QUARTER_OUTLINE',        1.000000000,   1.000000000,   1.000000000,   1.00   ),
        (   'COLOR_CSC_LENS_BASE_IMPROVED',          0.478431373,   0.215686275,   0.000000000,   0.60   ),
        (   'COLOR_CSC_LENS_BASE_UNIMPROVED',        0.478431373,   0.215686275,   0.000000000,   0.30   ),
        (   'COLOR_CSC_LENS_BASE_OUTLINE',           0.478431373,   0.215686275,   0.000000000,   1.00   ),
        (   'COLOR_CSC_LENS_LEGEND_BASE',            0.478431373,   0.215686275,   0.000000000,   1.00   ),
        (   'COLOR_CSC_LENS_SPEC_IMPROVED',          0.917647059,   0.529411765,   0.023529412,   0.60   ),
        (   'COLOR_CSC_LENS_SPEC_UNIMPROVED',        0.917647059,   0.529411765,   0.023529412,   0.20   ),
        (   'COLOR_CSC_LENS_SPEC_OUTLINE',           0.917647059,   0.529411765,   0.023529412,   1.00   ),
        (   'COLOR_CSC_LENS_LEGEND_SPEC',            0.917647059,   0.529411765,   0.023529412,   1.00   ),
        (   'COLOR_CSC_LENS_SALE_DISTRICT',          0.713725490,   0.658823529,   0.207843137,   0.60   ),
        (   'COLOR_CSC_LENS_SALE_UNREADY',           0.713725490,   0.658823529,   0.207843137,   0.20   ),
        (   'COLOR_CSC_LENS_SALE_OUTLINE',           0.713725490,   0.658823529,   0.207843137,   1.00   ),
        (   'COLOR_CSC_LENS_LEGEND_SALE',            0.713725490,   0.658823529,   0.207843137,   1.00   ),
        (   'COLOR_CSC_LENS_OUTLINE_BACK',           0.03,          0.04,          0.06,          0.75   ),
        (   'COLOR_CSC_LENS_LEGEND_QUARTER',         1.000000000,   1.000000000,   1.000000000,   1.00   ),
        (   'COLOR_CSC_LENS_IGNORE',                 0.25,          0.25,          0.25,          0.50   ),
        (   'COLOR_CSC_LENS_BAKERS_QUARTER',         0.372549020,   0.509803922,   0.109803922,   0.60   ),
        (   'COLOR_CSC_LENS_TAILORS_QUARTER',        0.564705882,   0.215686275,   0.666666667,   0.60   ),
        (   'COLOR_CSC_LENS_APOTHECARIES_QUARTER',   0.054901961,   0.329411765,   0.662745098,   0.60   ),
        (   'COLOR_CSC_LENS_CARPENTERS_QUARTER',     0.745098039,   0.419607843,   0.039215686,   0.60   ),
        (   'COLOR_CSC_LENS_STONEMASONS_QUARTER',    0.745098039,   0.419607843,   0.039215686,   0.60   ),
        (   'COLOR_CSC_LENS_BLACKSMITHS_QUARTER',    0.745098039,   0.419607843,   0.039215686,   0.60   ),
        (   'COLOR_CSC_LENS_BREWERS_QUARTER',        0.760784314,   0.686274510,   0.219607843,   0.60   ),
        (   'COLOR_CSC_LENS_GOLDSMITHS_QUARTER',     0.760784314,   0.686274510,   0.219607843,   0.60   ),
        (   'COLOR_CSC_LENS_FLOW_PRODUCTION',        0.537254902,   0.250980392,   0.000000000,   1.00   ),
        (   'COLOR_CSC_LENS_FLOW_GOLD',              0.992156863,   0.925490196,   0.364705882,   1.00   ),
        (   'COLOR_CSC_LENS_FLOW_FOOD',              0.274509804,   0.517647059,   0.098039216,   1.00   ),
        (   'COLOR_CSC_LENS_FLOW_CULTURE',           0.733333333,   0.266666667,   0.741176471,   1.00   ),
        (   'COLOR_CSC_LENS_FLOW_SCIENCE',           0.031372549,   0.450980392,   0.882352941,   1.00   ),
        (   'COLOR_CSC_LENS_FLOW_FAITH',             0.654901961,   0.745098039,   0.870588235,   1.00   );

-- Quarter identity colours. This table does not enable unimplemented lenses;
-- a Quarter still needs its normal material/adjacency configuration to appear.
CREATE TABLE IF NOT EXISTS CSC_LensQuarterColors
(
QuarterKey TEXT PRIMARY KEY NOT NULL,
ColorType TEXT NOT NULL
);

INSERT OR REPLACE INTO CSC_LensQuarterColors
        (   QuarterKey,       ColorType   )
VALUES  (   'BAKERS',         'COLOR_CSC_LENS_BAKERS_QUARTER'   ),
        (   'TAILORS',        'COLOR_CSC_LENS_TAILORS_QUARTER'   ),
        (   'APOTHECARIES',   'COLOR_CSC_LENS_APOTHECARIES_QUARTER'   ),
        (   'CARPENTERS',     'COLOR_CSC_LENS_CARPENTERS_QUARTER'   ),
        (   'STONEMASONS',    'COLOR_CSC_LENS_STONEMASONS_QUARTER'   ),
        (   'BLACKSMITHS',    'COLOR_CSC_LENS_BLACKSMITHS_QUARTER'   ),
        (   'BREWERS',        'COLOR_CSC_LENS_BREWERS_QUARTER'   ),
        (   'GOLDSMITHS',     'COLOR_CSC_LENS_GOLDSMITHS_QUARTER'   );

-- Derive the faint and opaque variants from each identity colour, so the
-- tile fill, edge sprites and legend cannot drift to a different hue.
INSERT OR REPLACE INTO Colors
        (   Type,   Red,   Green,   Blue,   Alpha   )
SELECT p.ColorType || '_EMPTY', c.Red, c.Green, c.Blue, 0.20
FROM CSC_LensQuarterColors p JOIN Colors c ON c.Type = p.ColorType;

INSERT OR REPLACE INTO Colors
        (   Type,   Red,   Green,   Blue,   Alpha   )
SELECT p.ColorType || '_OUTLINE', c.Red, c.Green, c.Blue, 1.00
FROM CSC_LensQuarterColors p JOIN Colors c ON c.Type = p.ColorType;

-- Deliveries follow their yield, independently of the static tile palette.
-- District yield membership comes from adjacency tags; Wonders use their mapping.
CREATE TABLE IF NOT EXISTS CSC_LensFlowYieldColors
(
YieldType TEXT PRIMARY KEY NOT NULL,
ColorType TEXT NOT NULL
);

INSERT OR REPLACE INTO CSC_LensFlowYieldColors
        (   YieldType,            ColorType   )
VALUES  (   'YIELD_PRODUCTION',   'COLOR_CSC_LENS_FLOW_PRODUCTION'   ),
        (   'YIELD_GOLD',         'COLOR_CSC_LENS_FLOW_GOLD'   ),
        (   'YIELD_FOOD',         'COLOR_CSC_LENS_FLOW_FOOD'   ),
        (   'YIELD_CULTURE',      'COLOR_CSC_LENS_FLOW_CULTURE'   ),
        (   'YIELD_SCIENCE',      'COLOR_CSC_LENS_FLOW_SCIENCE'   ),
        (   'YIELD_FAITH',        'COLOR_CSC_LENS_FLOW_FAITH'   );
